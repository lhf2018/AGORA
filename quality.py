# quality.py — junk detection, title clustering, demotion helpers
import re
from difflib import SequenceMatcher

# 连续失败次数达到阈值 → 降权
DEMOTE_FAIL_STREAK = 5
# 单次抓取垃圾标题占比 ≥ 此值且至少 2 条垃圾 → 记噪音并可能降权
NOISE_RATIO_THRESHOLD = 0.5
NOISE_MIN_HITS = 2
# 累计噪音命中达到阈值 → 降权
DEMOTE_NOISE_TOTAL = 8
# 标题相似度阈值（同题合并）
SIMILARITY_THRESHOLD = 0.55

JUNK_EXACT = {
    'hello world!', 'hello world', 'test', 'sample page', 'untitled',
}

JUNK_PATTERNS = [
    re.compile(p, re.I) for p in [
        r'coupon\s*code',
        r'promo\s*code',
        r'\d+\s*%\s*off',
        r'discount\s*code',
        r'free\s*shipping',
        r'buy\s*now',
        r'click\s*here',
        r'subscribe\s*(now|today)',
        r'unsubscribe',
        r'newsletter\s*signup',
        r'we\s*are\s*hiring',
        r'job\s*opening',
        r'优惠码',
        r'打折|折扣券|满减',
        r'限时特惠|爆款直降',
        r'招聘启事|诚聘',
        r'点击订阅|退订',
        r'广告招租',
    ]
]


def is_junk_title(title):
    """Return True if title looks like spam / promo / placeholder."""
    if not title:
        return True
    t = title.strip()
    if len(t) < 4:
        return True
    if t.lower() in JUNK_EXACT:
        return True
    for pat in JUNK_PATTERNS:
        if pat.search(t):
            return True
    # 纯符号 / 过多感叹号
    if re.fullmatch(r'[\W_]+', t):
        return True
    if t.count('!') >= 3 or t.count('！') >= 3:
        return True
    return False


def normalize_for_sim(title):
    t = (title or '').lower()
    t = re.sub(r'https?://\S+', ' ', t)
    t = re.sub(r'[^\w\u4e00-\u9fff]+', ' ', t, flags=re.UNICODE)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def _char_ngrams(s, n=2):
    s = s.replace(' ', '')
    if len(s) < n:
        return {s} if s else set()
    return {s[i:i + n] for i in range(len(s) - n + 1)}


def title_similarity(a, b):
    """Hybrid similarity for CN/EN titles: SequenceMatcher + char bigram Jaccard."""
    na, nb = normalize_for_sim(a), normalize_for_sim(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    seq = SequenceMatcher(None, na, nb).ratio()
    ga, gb = _char_ngrams(na), _char_ngrams(nb)
    if not ga or not gb:
        jacc = 0.0
    else:
        jacc = len(ga & gb) / len(ga | gb)
    # 偏重 n-gram，对中文短标题更稳
    return 0.45 * seq + 0.55 * jacc


def cluster_articles(articles, threshold=SIMILARITY_THRESHOLD, window=48):
    """
    Greedy cluster by title similarity.
    Only compares each article with the next `window` newer-to-older neighbors
    (list is expected time-desc), keeping cost ~ O(n * window).
    Returns list of clusters:
      { primary: article, related: [article,...], size: int }
    """
    if not articles:
        return []

    items = list(articles)
    used = [False] * len(items)
    # 预计算归一化标题，避免重复处理
    norms = [normalize_for_sim(a.get('title') or '') for a in items]
    grams = [_char_ngrams(n) for n in norms]
    clusters = []

    for i, art in enumerate(items):
        if used[i]:
            continue
        used[i] = True
        related = []
        end = min(len(items), i + 1 + window)
        gi = grams[i]
        ni = norms[i]
        for j in range(i + 1, end):
            if used[j]:
                continue
            nj = norms[j]
            if not ni or not nj:
                continue
            li, lj = len(ni), len(nj)
            if min(li, lj) / max(li, lj) < 0.4:
                continue
            gj = grams[j]
            if gi and gj and not (gi & gj):
                continue
            # 内联相似度，少一次函数调用
            seq = SequenceMatcher(None, ni, nj).ratio()
            jacc = len(gi & gj) / len(gi | gj) if gi and gj else 0.0
            if 0.45 * seq + 0.55 * jacc >= threshold:
                used[j] = True
                related.append(items[j])
        clusters.append({
            'primary': art,
            'related': related,
            'size': 1 + len(related),
        })
    return clusters


def cluster_to_card(cluster):
    """Flatten cluster into API card shape for the frontend."""
    primary = dict(cluster['primary'])
    related = cluster['related']
    primary['cluster_size'] = cluster['size']
    primary['related'] = [
        {
            'title': r.get('title'),
            'link': r.get('link'),
            'source': r.get('source'),
            'source_cn': r.get('source_cn'),
            'published': r.get('published'),
            'published_timestamp': r.get('published_timestamp'),
            'country': r.get('country'),
            'description': r.get('description') or '',
            'icon': r.get('icon') or '',
        }
        for r in related
    ]
    return primary


def should_demote(consecutive_fails, noise_count, noise_ratio=0.0, noise_hits=0):
    """Decide whether a source should be demoted and why."""
    if consecutive_fails >= DEMOTE_FAIL_STREAK:
        return True, f'连续失败 {consecutive_fails} 次'
    if noise_count >= DEMOTE_NOISE_TOTAL:
        return True, f'累计噪音标题 {noise_count} 次'
    if noise_hits >= NOISE_MIN_HITS and noise_ratio >= NOISE_RATIO_THRESHOLD:
        return True, f'本批噪音占比 {noise_ratio:.0%}'
    return False, None
