# app.py
import os
import re
import time
import threading
import concurrent.futures
from copy import deepcopy
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from urllib.parse import urlparse, parse_qs, unquote

import feedparser
import requests
from flask import Flask, render_template, jsonify, request, Response
from flask_caching import Cache

from config import (
    THINK_TANKS_CONFIG,
    TOPIC_LEXICON,
    DOC_TYPE_LABELS,
    DOMAIN_LABELS,
    enrich_source,
    get_source_type,
    get_source_type_label,
    SOURCE_TYPE_LABELS,
)
import db
import quality
import earnings

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 120
cache = Cache(app)

DEFAULT_PER_PAGE = 24
MAX_PER_PAGE = 60
HIGH_INTERVAL_MIN = 10
NORMAL_INTERVAL_MIN = 30
RETENTION_DAYS = 30
SCHEDULER_TICK_SEC = 60

BRIEFING_SECTIONS = [
    {'domain': 'geopolitics', 'label': '地缘', 'limit': 5},
    {'domain': 'macro', 'label': '宏观金融', 'limit': 5},
    {'domain': 'tech', 'label': '科技', 'limit': 5},
    {'domain': 'energy', 'label': '能源气候', 'limit': 3},
    {'domain': 'industry', 'label': '产业', 'limit': 3},
    {'domain': 'health', 'label': '卫生健康', 'limit': 3},
    {'domain': 'general', 'label': '综合', 'limit': 3},
]

_TAG_RE = re.compile(r'<[^>]+>')
_WS_RE = re.compile(r'\s+')

_fetch_lock = threading.Lock()
_fetch_in_progress = False
_scheduler_started = False
_sources_lock = threading.Lock()
_sources_cache = None
_sources_cache_ts = 0.0
SOURCES_CACHE_TTL = 5.0


def make_naive(dt):
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def parse_pub_date(date_string):
    if not date_string:
        return None
    try:
        return make_naive(parsedate_to_datetime(date_string))
    except (TypeError, ValueError, IndexError, OverflowError):
        pass
    try:
        from dateutil import parser
        return make_naive(parser.parse(date_string))
    except (TypeError, ValueError, OverflowError):
        pass
    formats = [
        '%a, %d %b %Y %H:%M:%S %z',
        '%a, %d %b %Y %H:%M:%S GMT',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
    ]
    for fmt in formats:
        try:
            return make_naive(datetime.strptime(date_string, fmt))
        except ValueError:
            continue
    return None


def format_pub_date(date_string):
    parsed_date = parse_pub_date(date_string)
    if parsed_date:
        return parsed_date.strftime('%Y年%m月%d日 %H:%M')
    return '时间未知'


def normalize_link(link):
    """Normalize URL for dedup; unwrap Google redirect when possible."""
    if not link:
        return ''
    link = link.strip()
    try:
        parsed = urlparse(link)
        host = (parsed.netloc or '').lower()
        if 'google.' in host and parsed.path.startswith('/url'):
            qs = parse_qs(parsed.query)
            for key in ('url', 'q'):
                if key in qs and qs[key]:
                    return normalize_link(unquote(qs[key][0]))
        if 'news.google.com' in host:
            qs = parse_qs(parsed.query)
            if 'url' in qs and qs['url']:
                return normalize_link(unquote(qs['url'][0]))
        # strip fragment + common tracking params
        query = parse_qs(parsed.query, keep_blank_values=False)
        drop = {k for k in query if k.lower().startswith('utm_') or k.lower() in {
            'fbclid', 'gclid', 'ocid', 'ref', 'spm'
        }}
        for k in drop:
            query.pop(k, None)
        from urllib.parse import urlencode
        new_query = urlencode([(k, v) for k, vs in query.items() for v in vs], doseq=True)
        cleaned = parsed._replace(query=new_query, fragment='').geturl()
        return cleaned
    except Exception:
        return link.split('#')[0]


def clean_gnews_title(title, feed_url=''):
    """Strip Google News ' - Publisher' suffix from titles."""
    title = (title or '').strip()
    if not title:
        return title
    is_gnews = 'news.google.com' in (feed_url or '')
    if not is_gnews:
        return title
    cleaned = re.sub(r'\s+[-–—]\s+[^-–—]{1,80}$', '', title).strip()
    return cleaned or title


def clean_summary(raw, max_len=1000):
    """Strip HTML from RSS summary/description for card + reading mode."""
    if not raw:
        return ''
    text = _TAG_RE.sub(' ', str(raw))
    text = unescape(text)
    text = _WS_RE.sub(' ', text).strip()
    if len(text) > max_len:
        cut = text[:max_len]
        sp = cut.rfind(' ')
        if sp > max_len // 2:
            cut = cut[:sp]
        text = cut.rstrip('.,;:，。；：、 ') + '…'
    return text


def entry_summary(entry):
    raw = entry.get('summary') or entry.get('description') or ''
    if not raw and entry.get('content'):
        try:
            raw = entry.content[0].get('value', '')
        except (IndexError, AttributeError, TypeError, KeyError):
            raw = ''
    return clean_summary(raw)


def invalidate_sources_cache():
    global _sources_cache, _sources_cache_ts
    with _sources_lock:
        _sources_cache = None
        _sources_cache_ts = 0.0


def get_runtime_sources(include_disabled=False):
    """Builtin config + DB overrides/customs. Cached briefly for fetch loops."""
    global _sources_cache, _sources_cache_ts
    now = time.time()
    with _sources_lock:
        if (
            not include_disabled
            and _sources_cache is not None
            and (now - _sources_cache_ts) < SOURCES_CACHE_TTL
        ):
            return list(_sources_cache)

    overrides = {o['name']: o for o in db.list_source_overrides()}
    customs = db.list_custom_sources()
    merged = []
    seen = set()

    for base in THINK_TANKS_CONFIG:
        feed = deepcopy(base)
        name = feed['name']
        seen.add(name)
        ov = overrides.get(name)
        enabled = True
        if ov:
            if ov.get('enabled') is not None and int(ov['enabled']) == 0:
                enabled = False
            for key in (
                'rss', 'name_cn', 'icon', 'category', 'doc_type',
                'domain', 'country', 'priority', 'description',
            ):
                val = ov.get(key)
                if val is not None and val != '':
                    feed[key] = val
        feed['origin'] = 'builtin'
        feed['enabled'] = enabled
        enrich_source(feed)
        if include_disabled or enabled:
            merged.append(feed)

    for row in customs:
        name = row['name']
        if name in seen:
            continue
        seen.add(name)
        feed = {
            'name': row['name'],
            'name_cn': row['name_cn'],
            'rss': row['rss'],
            'icon': row.get('icon') or '',
            'category': row.get('category') or '其他',
            'doc_type': row.get('doc_type') or None,
            'domain': row.get('domain') or None,
            'country': row.get('country') or '其他',
            'priority': row.get('priority') if row.get('priority') is not None else 2,
            'description': row.get('description') or '',
            'origin': 'custom',
            'enabled': bool(row.get('enabled', 1)),
        }
        enrich_source(feed)
        if include_disabled or feed['enabled']:
            merged.append(feed)

    if not include_disabled:
        with _sources_lock:
            _sources_cache = list(merged)
            _sources_cache_ts = time.time()
    return merged


def runtime_stats(sources):
    country_stats = {}
    category_stats = {}
    doc_type_stats = {}
    domain_stats = {}
    for s in sources:
        if not s.get('enabled', True):
            continue
        c = s.get('country', '其他') or '其他'
        country_stats[c] = country_stats.get(c, 0) + 1
        cat = s.get('category', '其他') or '其他'
        category_stats[cat] = category_stats.get(cat, 0) + 1
        dt = s.get('doc_type') or get_source_type(s)
        doc_type_stats[dt] = doc_type_stats.get(dt, 0) + 1
        d = s.get('domain') or 'general'
        domain_stats[d] = domain_stats.get(d, 0) + 1
    return {
        'country_stats': country_stats,
        'category_stats': category_stats,
        'doc_type_stats': doc_type_stats,
        'domain_stats': domain_stats,
    }


def fetch_feed(feed_info):
    """Fetch one RSS source. Returns (articles, error_or_None, noise_hits)."""
    articles = []
    noise_hits = 0
    try:
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )
        }
        response = requests.get(feed_info['rss'], headers=headers, timeout=15)
        if response.status_code != 200:
            return [], f'status {response.status_code}', 0

        feed = feedparser.parse(response.content)
        seen_links = set()

        for entry in feed.entries[:12]:
            if not hasattr(entry, 'link') or not hasattr(entry, 'title'):
                continue
            raw_title = (entry.title or '').strip()
            title = clean_gnews_title(raw_title, feed_info.get('rss', ''))
            if quality.is_junk_title(title) or quality.is_junk_title(raw_title):
                noise_hits += 1
                continue
            link = normalize_link(entry.link)
            if not link or link in seen_links:
                continue
            seen_links.add(link)

            pub_date_str = entry.get('published', entry.get('pubDate', ''))
            pub_timestamp = parse_pub_date(pub_date_str)
            category = feed_info.get('category', '其他')
            articles.append({
                'title': title,
                'link': link,
                'published_raw': pub_date_str,
                'published': format_pub_date(pub_date_str),
                'published_timestamp': pub_timestamp.isoformat() if pub_timestamp else None,
                'source': feed_info['name'],
                'source_cn': feed_info['name_cn'],
                'icon': feed_info.get('icon', ''),
                'category': category,
                'source_type': feed_info.get('doc_type') or get_source_type(feed_info),
                'source_type_label': feed_info.get('doc_type_label') or get_source_type_label(feed_info),
                'domain': feed_info.get('domain') or '',
                'domain_label': feed_info.get('domain_label') or '',
                'country': feed_info.get('country', '其他'),
                'priority': feed_info.get('priority', 2),
                'description': entry_summary(entry),
            })
            if len(articles) >= 5:
                break
        return articles, None, noise_hits
    except Exception as e:
        return [], type(e).__name__, noise_hits


def _record_feed_result(feed, articles, err, noise_hits):
    total_seen = len(articles) + noise_hits
    noise_ratio = (noise_hits / total_seen) if total_seen else 0.0
    # peek current streak for demotion decision
    with db.get_conn() as conn:
        row = conn.execute(
            'SELECT consecutive_fails, noise_count FROM sources_state WHERE name=?',
            (feed['name'],),
        ).fetchone()
    prev_streak = (row['consecutive_fails'] or 0) if row else 0
    prev_noise = (row['noise_count'] or 0) if row else 0
    next_streak = 0 if not err else prev_streak + 1
    next_noise = prev_noise + noise_hits
    demote, reason = quality.should_demote(
        consecutive_fails=next_streak,
        noise_count=next_noise,
        noise_ratio=noise_ratio,
        noise_hits=noise_hits,
    )
    db.record_source_fetch(
        feed['name'],
        feed.get('name_cn', ''),
        feed.get('priority', 2),
        ok=(err is None),
        article_count=len(articles),
        error=err,
        noise_hits=noise_hits,
        demote=demote,
        demote_reason=reason,
    )
    return demote, reason


def fetch_sources(feeds, mode='incremental'):
    """Concurrent fetch for given feeds; upsert into SQLite."""
    if not feeds:
        return {'sources_ok': 0, 'sources_fail': 0, 'upserted': 0}

    log_id = db.start_fetch_log(mode, len(feeds))
    ok = 0
    fail = 0
    upserted = 0
    demoted_n = 0
    batch_size = 10

    print(f"[{mode}] 抓取 {len(feeds)} 个源...")

    for i in range(0, len(feeds), batch_size):
        batch = feeds[i:i + batch_size]
        batch_articles = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_map = {executor.submit(fetch_feed, feed): feed for feed in batch}
            for future in concurrent.futures.as_completed(future_map):
                feed = future_map[future]
                articles, err, noise_hits = future.result()
                demoted, reason = _record_feed_result(feed, articles, err, noise_hits)
                if demoted:
                    demoted_n += 1
                if err:
                    fail += 1
                    try:
                        print(f"  fail {feed['name']}: {err}")
                    except UnicodeEncodeError:
                        print(f"  fail feed: {err}")
                else:
                    ok += 1
                    batch_articles.extend(articles)
                    if noise_hits:
                        try:
                            print(f"  noise {feed['name']}: {noise_hits} junk titles")
                        except UnicodeEncodeError:
                            pass
        inserted, updated = db.upsert_articles(batch_articles)
        upserted += inserted + updated
        cache.clear()
        time.sleep(0.3)

    note = f'demoted+={demoted_n}' if demoted_n else ''
    db.finish_fetch_log(log_id, ok, fail, upserted, note=note)
    db.set_meta('last_fetch_finished_at', datetime.utcnow().isoformat())
    pruned = db.prune_old_articles(RETENTION_DAYS)
    print(
        f"[{mode}] 完成: ok={ok} fail={fail} "
        f"articles+={upserted} pruned={pruned} demoted~{demoted_n} db_total={db.article_count()}"
    )
    return {'sources_ok': ok, 'sources_fail': fail, 'upserted': upserted}


def run_fetch_job(mode='incremental', force_all=False):
    global _fetch_in_progress
    with _fetch_lock:
        if _fetch_in_progress:
            return False
        _fetch_in_progress = True

    try:
        sources = get_runtime_sources()
        if force_all or db.article_count() == 0:
            feeds = list(sources)
            mode = 'full'
        else:
            feeds = db.get_due_source_names(
                sources,
                high_interval_min=HIGH_INTERVAL_MIN,
                normal_interval_min=NORMAL_INTERVAL_MIN,
            )
            if not feeds:
                print('[incremental] 无到期源，跳过')
                return True
        fetch_sources(feeds, mode=mode)
        return True
    finally:
        _fetch_in_progress = False


def start_background_fetch(force_all=False):
    threading.Thread(
        target=run_fetch_job,
        kwargs={'mode': 'startup', 'force_all': force_all},
        daemon=True,
    ).start()


def scheduler_loop():
    while True:
        time.sleep(SCHEDULER_TICK_SEC)
        try:
            run_fetch_job(mode='incremental', force_all=False)
        except Exception as e:
            print(f'[scheduler] error: {type(e).__name__}: {e}')


def start_scheduler():
    global _scheduler_started
    if _scheduler_started:
        return
    _scheduler_started = True
    threading.Thread(target=scheduler_loop, daemon=True, name='agora-scheduler').start()
    print(
        f'定时增量已启动：高优每 {HIGH_INTERVAL_MIN} 分钟，'
        f'普通每 {NORMAL_INTERVAL_MIN} 分钟'
    )


def get_topic_by_id(topic_id):
    if not topic_id or topic_id == 'all':
        return None
    for topic in TOPIC_LEXICON:
        if topic['id'] == topic_id or topic['label'] == topic_id:
            return topic
    return None


def title_matches_topic(title, topic):
    if not title or not topic:
        return False
    text = title
    text_lower = title.lower()
    for pattern in topic.get('patterns', []):
        if not pattern:
            continue
        if pattern.isascii() and len(pattern.strip()) <= 3:
            if re.search(rf'(?<![A-Za-z]){re.escape(pattern.strip())}(?![A-Za-z])', text, re.I):
                return True
        elif pattern.isascii():
            if pattern.lower() in text_lower:
                return True
        elif pattern in text:
            return True
    return False


def paginate_items(items, page, per_page):
    total = len(items)
    total_pages = max(1, (total + per_page - 1) // per_page) if total else 1
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
    }


def extract_topics(days=7, limit=20):
    cache_key = f'topics_{days}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    recent = db.iter_recent_titles(days=days)
    scored = []
    for topic in TOPIC_LEXICON:
        count = sum(1 for a in recent if title_matches_topic(a.get('title', ''), topic))
        if count > 0:
            scored.append({
                'id': topic['id'],
                'label': topic['label'],
                'count': count,
            })
    scored.sort(key=lambda x: (-x['count'], x['label']))
    payload = {
        'days': days,
        'article_pool': len(recent),
        'topics': scored[:limit],
    }
    cache.set(cache_key, payload, timeout=120)
    return payload


def bootstrap():
    db.init_db()
    count = db.article_count()
    junk_links = [
        link for link, title in db.iter_all_article_titles()
        if quality.is_junk_title(title)
    ]
    if junk_links:
        removed = db.delete_articles_by_links(junk_links)
        print(f'已清理噪音标题文章 {removed} 篇')
        count = db.article_count()
    scrubbed = scrub_mistaken_summaries()
    if scrubbed:
        print(f'已清除误写入的源简介摘要 {scrubbed} 篇')
    backfilled = backfill_article_taxonomy()
    if backfilled:
        print(f'已回填领域/文体标签 {backfilled} 篇')
    print(f'数据库就绪：{db.DEFAULT_DB_PATH}，已有 {count} 篇文章')
    start_background_fetch(force_all=(count == 0))
    start_scheduler()


def scrub_mistaken_summaries():
    """旧版本把源简介写进了文章 description，启动时清掉。"""
    blurbs = {
        (s.get('name'), (s.get('description') or '').strip())
        for s in THINK_TANKS_CONFIG
        if (s.get('description') or '').strip()
    }
    if not blurbs:
        return 0
    cleared = 0
    with db.get_conn() as conn:
        for name, blurb in blurbs:
            cur = conn.execute(
                'UPDATE articles SET description=? WHERE source=? AND description=?',
                ('', name, blurb),
            )
            cleared += cur.rowcount
    return cleared


def backfill_article_taxonomy():
    """用当前源配置回填旧文章的 domain / source_type。"""
    by_name = {s['name']: s for s in get_runtime_sources(include_disabled=True)}
    updated = 0
    with db.get_conn() as conn:
        rows = conn.execute(
            'SELECT id, source, source_type, domain FROM articles'
        ).fetchall()
        for row in rows:
            feed = by_name.get(row['source'])
            if not feed:
                continue
            dt = feed.get('doc_type') or get_source_type(feed)
            dl = feed.get('doc_type_label') or get_source_type_label(feed)
            domain = feed.get('domain') or ''
            domain_label = feed.get('domain_label') or ''
            if (
                row['source_type'] == dt
                and (row['domain'] or '') == domain
            ):
                continue
            conn.execute(
                '''
                UPDATE articles SET
                    source_type=?, source_type_label=?,
                    domain=?, domain_label=?
                WHERE id=?
                ''',
                (dt, dl, domain, domain_label, row['id']),
            )
            updated += 1
    return updated


def build_briefing(days=1):
    """今日简报：按领域取同题合并后的要点 + 议题热点。"""
    days = max(1, min(int(days or 1), 3))
    rows = db.query_articles(days=days, fetch_all=True, limit=600)
    clusters = quality.cluster_articles(rows)
    cards = [quality.cluster_to_card(c) for c in clusters]

    def sort_key(a):
        pri = a.get('priority') if a.get('priority') is not None else 2
        ts = a.get('published_timestamp') or ''
        return (pri, 0 if ts else 1, ts)

    by_domain = {}
    for card in cards:
        d = card.get('domain') or 'general'
        by_domain.setdefault(d, []).append(card)

    sections = []
    picked_links = set()
    for spec in BRIEFING_SECTIONS:
        items = sorted(by_domain.get(spec['domain'], []), key=sort_key)
        picked = []
        for it in items:
            link = it.get('link') or ''
            if link in picked_links:
                continue
            picked_links.add(link)
            picked.append({
                'title': it.get('title'),
                'link': link,
                'source': it.get('source'),
                'source_cn': it.get('source_cn'),
                'icon': it.get('icon') or '',
                'published': it.get('published'),
                'published_timestamp': it.get('published_timestamp'),
                'description': it.get('description') or '',
                'source_type_label': it.get('source_type_label') or '',
                'domain_label': it.get('domain_label') or '',
                'country': it.get('country') or '',
                'cluster_size': it.get('cluster_size') or 1,
                'related': it.get('related') or [],
                'priority': it.get('priority', 2),
            })
            if len(picked) >= spec['limit']:
                break
        if picked:
            sections.append({
                'domain': spec['domain'],
                'label': spec['label'],
                'count': len(picked),
                'items': picked,
            })

    topics_payload = extract_topics(days=max(days, 1), limit=10)
    earnings_rows = [
        a for a in cards
        if (a.get('source_type') or '') == 'earnings'
    ][:8]
    earnings_items = []
    for a in earnings_rows:
        co = earnings.detect_company(a.get('title') or '')
        earnings_items.append({
            'title': a.get('title'),
            'link': a.get('link'),
            'source_cn': a.get('source_cn'),
            'published': a.get('published'),
            'description': a.get('description') or '',
            'company': (co or {}).get('label') if co else None,
        })

    total_items = sum(s['count'] for s in sections)
    return {
        'days': days,
        'generated_at': datetime.utcnow().isoformat(),
        'article_pool': len(rows),
        'cluster_pool': len(cards),
        'total_items': total_items,
        'topics': topics_payload.get('topics') or [],
        'sections': sections,
        'earnings': earnings_items,
        'cached_at': db.latest_fetched_at(),
    }


def briefing_window_label(days):
    return {1: '今日', 2: '近2日', 3: '近3日'}.get(int(days or 1), f'近{days}日')


def briefing_to_markdown(payload):
    """Render briefing payload as shareable Markdown."""
    days = payload.get('days') or 1
    lines = [f"# Agora {briefing_window_label(days)}简报", '']
    gen = (payload.get('generated_at') or '')[:16].replace('T', ' ')
    meta = f"{payload.get('total_items', 0)} 条要点"
    if gen:
        meta = f"生成于 {gen} UTC · {meta}"
    lines.append(f"> {meta}")
    lines.append('')

    topics = payload.get('topics') or []
    if topics:
        labels = ' · '.join(
            f"{t.get('label')}({t.get('count')})" for t in topics[:8]
        )
        lines.append(f"**热点议题** {labels}")
        lines.append('')

    earnings = payload.get('earnings') or []
    if earnings:
        lines.append('## 财报速览')
        lines.append('')
        for it in earnings:
            co = f"**{it['company']}** · " if it.get('company') else ''
            src = it.get('source_cn') or it.get('source') or ''
            title = (it.get('title') or '').replace('[', '\\[').replace(']', '\\]')
            link = it.get('link') or ''
            tail = f" — {src}" if src else ''
            if link:
                lines.append(f"- {co}[{title}]({link}){tail}")
            else:
                lines.append(f"- {co}{title}{tail}")
            desc = (it.get('description') or '').strip()
            if desc:
                lines.append(f"  - {desc}")
        lines.append('')

    for sec in payload.get('sections') or []:
        lines.append(f"## {sec.get('label') or '综合'}")
        lines.append('')
        for it in sec.get('items') or []:
            src = it.get('source_cn') or it.get('source') or ''
            title = (it.get('title') or '').replace('[', '\\[').replace(']', '\\]')
            link = it.get('link') or ''
            cluster = ''
            if (it.get('cluster_size') or 1) > 1:
                cluster = f" 〔同题 {it['cluster_size']}〕"
            tail = f" — {src}{cluster}" if src or cluster else cluster
            if link:
                lines.append(f"- [{title}]({link}){tail}")
            else:
                lines.append(f"- {title}{tail}")
            desc = (it.get('description') or '').strip()
            if desc:
                lines.append(f"  - {desc}")
        lines.append('')

    lines.append('---')
    lines.append('*由 [Agora](/) 生成*')
    return '\n'.join(lines).rstrip() + '\n'


def get_briefing_payload(days=1):
    """Shared loader for JSON / Markdown / share page."""
    days = max(1, min(int(days or 1), 3))
    if db.article_count() == 0:
        return {
            'loading': True,
            'days': days,
            'sections': [],
            'topics': [],
            'earnings': [],
            'total_items': 0,
            'generated_at': datetime.utcnow().isoformat(),
        }
    cache_key = f'briefing:{days}'
    payload = cache.get(cache_key)
    if payload is None:
        payload = build_briefing(days=days)
        cache.set(cache_key, payload, timeout=90)
    out = dict(payload)
    out['loading'] = False
    out['fetching'] = _fetch_in_progress
    out['window_label'] = briefing_window_label(days)
    return out


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/share/briefing')
def share_briefing():
    days = request.args.get('days', 1, type=int)
    payload = get_briefing_payload(days)
    return render_template(
        'briefing_share.html',
        briefing=payload,
        markdown=briefing_to_markdown(payload) if not payload.get('loading') else '',
        share_path=f"/share/briefing?days={payload.get('days') or 1}",
    )


@app.route('/api/briefing.md')
def get_briefing_markdown():
    days = request.args.get('days', 1, type=int)
    payload = get_briefing_payload(days)
    if payload.get('loading'):
        return Response(
            '# Agora 简报\n\n数据准备中，请稍后重试。\n',
            mimetype='text/markdown; charset=utf-8',
            status=503,
        )
    md = briefing_to_markdown(payload)
    download = request.args.get('download') == '1'
    headers = {}
    if download:
        label = briefing_window_label(payload.get('days') or 1)
        headers['Content-Disposition'] = (
            f'attachment; filename="agora-briefing-{label}.md"'
        )
    return Response(md, mimetype='text/markdown; charset=utf-8', headers=headers)


@app.route('/api/articles/status')
def get_articles_status():
    total = db.article_count()
    ready = total > 0
    return jsonify({
        'ready': ready,
        'loading': (not ready) and _fetch_in_progress,
        'fetching': _fetch_in_progress,
        'total': total,
        'cached_at': db.latest_fetched_at(),
    })


@app.route('/api/articles')
def get_articles():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', DEFAULT_PER_PAGE, type=int)
    source_type = request.args.get('source_type', 'all')
    # 兼容 doc_type 参数名
    if request.args.get('doc_type'):
        source_type = request.args.get('doc_type', 'all')
    country = request.args.get('country', 'all')
    domain = request.args.get('domain', 'all')
    topic = request.args.get('topic', 'all')
    days_raw = (request.args.get('days') or 'all').strip().lower()
    q = (request.args.get('q') or '').strip()
    merge = request.args.get('merge', '1') != '0'

    per_page = max(1, min(per_page, MAX_PER_PAGE))
    page = max(1, page)
    # 客户端本地筛选（已读/稍后）可一次拉更大池
    if request.args.get('pool') == '1':
        per_page = max(1, min(request.args.get('per_page', 400, type=int), 400))
        page = 1
    if days_raw in ('', 'all', '0'):
        days = None
    else:
        try:
            days = max(1, min(int(days_raw), 365))
        except ValueError:
            days = None

    total = db.article_count()
    if total == 0:
        if not _fetch_in_progress:
            start_background_fetch(force_all=True)
        return jsonify({
            'articles': [],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': 0,
                'total_pages': 1,
                'has_prev': False,
                'has_next': False,
            },
            'loading': True,
            'message': '正在首次聚合全球智库文章，完成后将持久化到本地数据库...',
        })

    topic_def = get_topic_by_id(topic)
    days_key = days if days else 'all'
    # 有搜索 / 议题 / 同题合并时取出匹配集再处理
    need_full = bool(q) or bool(topic_def) or merge
    if need_full:
        cache_key = f"feed:{source_type}:{domain}:{country}:{topic}:{days_key}:{q}:{'m' if merge else 'r'}"
        cards = cache.get(cache_key)
        if cards is None:
            limit = None if q or topic_def else 400
            rows = db.query_articles(
                source_type=source_type,
                country=country,
                domain=domain,
                days=days,
                q=q or None,
                fetch_all=True,
                limit=limit,
            )
            if topic_def:
                rows = [a for a in rows if title_matches_topic(a.get('title', ''), topic_def)]
            if merge:
                clusters = quality.cluster_articles(rows)
                cards = [quality.cluster_to_card(c) for c in clusters]
            else:
                cards = rows
            cache.set(cache_key, cards, timeout=90)
        page_items, pagination = paginate_items(cards, page, per_page)
    else:
        page_items, pagination = db.query_articles(
            source_type=source_type,
            country=country,
            domain=domain,
            days=days,
            page=page,
            per_page=per_page,
            q=None,
        )
        for a in page_items:
            a['cluster_size'] = 1
            a['related'] = []

    return jsonify({
        'articles': page_items,
        'pagination': pagination,
        'loading': False,
        'fetching': _fetch_in_progress,
        'topic': topic,
        'q': q,
        'domain': domain,
        'days': days_key,
        'merge': merge,
        'cached_at': db.latest_fetched_at(),
    })


@app.route('/api/earnings/calendar')
def earnings_calendar():
    days_raw = (request.args.get('days') or '30').strip().lower()
    if days_raw in ('', 'all', '0'):
        days = None
    else:
        try:
            days = max(1, min(int(days_raw), 365))
        except ValueError:
            days = 30
    company = (request.args.get('company') or '').strip()
    rows = db.query_articles(
        source_type='earnings',
        days=days,
        fetch_all=True,
        limit=500,
    )
    cal = earnings.build_calendar(rows)
    if company:
        filtered = []
        for day in cal['days']:
            items = [
                it for it in day['items']
                if (it.get('company') or '') == company
                or (it.get('company_id') or '') == company
            ]
            if items:
                filtered.append({'date': day['date'], 'count': len(items), 'items': items})
        cal['days'] = filtered
        cal['total'] = sum(d['count'] for d in filtered)
    cal['days_filter'] = days if days else 'all'
    cal['company'] = company or 'all'
    cal['loading'] = False
    cal['fetching'] = _fetch_in_progress
    return jsonify(cal)


@app.route('/api/feeds/health')
def feeds_health():
    summary = db.health_summary(get_runtime_sources(include_disabled=True))
    return jsonify(summary)


@app.route('/api/briefing')
def get_briefing():
    days = request.args.get('days', 1, type=int)
    payload = get_briefing_payload(days)
    if payload.get('loading') and not _fetch_in_progress:
        start_background_fetch(force_all=True)
    return jsonify(payload)


@app.route('/api/topics')
def get_topics():
    days = request.args.get('days', 7, type=int)
    days = max(1, min(days, 30))
    limit = request.args.get('limit', 20, type=int)
    limit = max(1, min(limit, 40))

    if db.article_count() == 0:
        return jsonify({
            'loading': True,
            'days': days,
            'article_pool': 0,
            'topics': [],
        })

    payload = extract_topics(days=days, limit=limit)
    payload['loading'] = False
    return jsonify(payload)


@app.route('/api/sources')
def get_sources():
    sources = [{
        'name': s['name'],
        'name_cn': s['name_cn'],
        'category': s.get('category', '其他'),
        'source_type': s.get('doc_type') or get_source_type(s),
        'source_type_label': s.get('doc_type_label') or get_source_type_label(s),
        'domain': s.get('domain', ''),
        'domain_label': s.get('domain_label', ''),
        'country': s.get('country', '其他'),
        'icon': s.get('icon', ''),
        'description': s.get('description', ''),
        'origin': s.get('origin', 'builtin'),
        'enabled': s.get('enabled', True),
    } for s in get_runtime_sources()]
    return jsonify(sources)


@app.route('/api/stats')
def get_stats():
    sources = get_runtime_sources()
    st = runtime_stats(sources)
    return jsonify({
        'total_sources': len(sources),
        'article_count': db.article_count(),
        'country_stats': st['country_stats'],
        'category_stats': st['category_stats'],
        'doc_type_stats': st['doc_type_stats'],
        'domain_stats': st['domain_stats'],
        'source_type_labels': SOURCE_TYPE_LABELS,
        'doc_type_labels': DOC_TYPE_LABELS,
        'domain_labels': DOMAIN_LABELS,
    })


@app.route('/api/fetch/trigger', methods=['POST'])
def trigger_fetch():
    """Manual refresh endpoint (incremental for due sources)."""
    if not _fetch_in_progress:
        start_background_fetch(force_all=False)
    return jsonify({'ok': True, 'fetching': True})


def _validate_source_payload(data, require_name=True):
    data = data or {}
    name = (data.get('name') or '').strip()
    name_cn = (data.get('name_cn') or '').strip()
    rss = (data.get('rss') or '').strip()
    if require_name and not name:
        return None, 'name 必填'
    if require_name and not name_cn:
        return None, 'name_cn 必填'
    if require_name and not rss:
        return None, 'rss 必填'
    if rss and not (rss.startswith('http://') or rss.startswith('https://')):
        return None, 'rss 须为 http(s) URL'
    doc_type = (data.get('doc_type') or data.get('source_type') or '').strip() or None
    if doc_type and doc_type not in DOC_TYPE_LABELS:
        return None, f'无效文体: {doc_type}'
    domain = (data.get('domain') or '').strip() or None
    if domain and domain not in DOMAIN_LABELS:
        return None, f'无效领域: {domain}'
    try:
        priority = int(data.get('priority', 2))
    except (TypeError, ValueError):
        priority = 2
    priority = 1 if priority == 1 else 2
    enabled = data.get('enabled', True)
    if isinstance(enabled, str):
        enabled = enabled.lower() not in ('0', 'false', 'no', 'off')
    payload = {
        'name': name,
        'name_cn': name_cn or name,
        'rss': rss,
        'icon': (data.get('icon') or '').strip(),
        'category': (data.get('category') or '其他').strip() or '其他',
        'doc_type': doc_type,
        'domain': domain,
        'country': (data.get('country') or '其他').strip() or '其他',
        'priority': priority,
        'description': (data.get('description') or '').strip(),
        'enabled': bool(enabled),
    }
    return payload, None


@app.route('/api/admin/sources')
def admin_list_sources():
    sources = get_runtime_sources(include_disabled=True)
    health = {
        h['name']: h for h in db.list_source_health(sources)
    }
    q = (request.args.get('q') or '').strip().lower()
    origin = (request.args.get('origin') or 'all').strip().lower()
    items = []
    for s in sources:
        if origin in ('builtin', 'custom') and s.get('origin') != origin:
            continue
        if q:
            blob = f"{s.get('name','')} {s.get('name_cn','')} {s.get('country','')} {s.get('rss','')}".lower()
            if q not in blob:
                continue
        h = health.get(s['name'], {})
        items.append({
            'name': s['name'],
            'name_cn': s.get('name_cn'),
            'rss': s.get('rss'),
            'icon': s.get('icon') or '',
            'category': s.get('category') or '',
            'doc_type': s.get('doc_type') or get_source_type(s),
            'doc_type_label': s.get('doc_type_label') or get_source_type_label(s),
            'domain': s.get('domain') or '',
            'domain_label': s.get('domain_label') or '',
            'country': s.get('country') or '',
            'priority': s.get('priority', 2),
            'description': s.get('description') or '',
            'origin': s.get('origin', 'builtin'),
            'enabled': bool(s.get('enabled', True)),
            'status': h.get('status', 'unknown'),
            'last_error': h.get('last_error'),
            'last_fetched_at': h.get('last_fetched_at'),
            'success_count': h.get('success_count', 0),
            'fail_count': h.get('fail_count', 0),
        })
    return jsonify({
        'total': len(items),
        'sources': items,
        'doc_type_labels': DOC_TYPE_LABELS,
        'domain_labels': DOMAIN_LABELS,
    })


@app.route('/api/admin/sources', methods=['POST'])
def admin_create_source():
    payload, err = _validate_source_payload(request.get_json(silent=True), require_name=True)
    if err:
        return jsonify({'ok': False, 'error': err}), 400
    builtin_names = {s['name'] for s in THINK_TANKS_CONFIG}
    if payload['name'] in builtin_names or db.get_custom_source(payload['name']):
        return jsonify({'ok': False, 'error': '源名称已存在'}), 409
    db.upsert_custom_source(payload)
    invalidate_sources_cache()
    cache.clear()
    return jsonify({'ok': True, 'source': payload})


@app.route('/api/admin/sources/test', methods=['POST'])
def admin_test_source():
    data = request.get_json(silent=True) or {}
    rss = (data.get('rss') or '').strip()
    name = (data.get('name') or 'Test Feed').strip() or 'Test Feed'
    if not rss.startswith(('http://', 'https://')):
        return jsonify({'ok': False, 'error': 'rss 须为 http(s) URL'}), 400
    feed = {
        'name': name,
        'name_cn': data.get('name_cn') or name,
        'rss': rss,
        'icon': data.get('icon') or '',
        'category': data.get('category') or '其他',
        'country': data.get('country') or '其他',
        'priority': 2,
        'doc_type': data.get('doc_type'),
        'domain': data.get('domain'),
    }
    enrich_source(feed)
    articles, err, noise = fetch_feed(feed)
    return jsonify({
        'ok': err is None,
        'error': err,
        'noise_hits': noise,
        'count': len(articles),
        'samples': [
            {
                'title': a.get('title'),
                'link': a.get('link'),
                'published': a.get('published'),
                'description': (a.get('description') or '')[:160],
            }
            for a in articles[:3]
        ],
    })


@app.route('/api/admin/sources/<path:name>', methods=['PUT'])
def admin_update_source(name):
    name = unquote(name).strip()
    data = request.get_json(silent=True) or {}
    data['name'] = name
    builtin = next((s for s in THINK_TANKS_CONFIG if s['name'] == name), None)
    custom = db.get_custom_source(name)

    if builtin:
        # override fields on builtin; enabled can disable
        ov = {
            'name': name,
            'enabled': 1 if data.get('enabled', True) not in (False, 0, '0', 'false') else 0,
        }
        for key in ('rss', 'name_cn', 'icon', 'category', 'doc_type', 'domain', 'country', 'description'):
            if key in data and data[key] is not None:
                ov[key] = data[key]
        if 'priority' in data:
            try:
                ov['priority'] = 1 if int(data['priority']) == 1 else 2
            except (TypeError, ValueError):
                ov['priority'] = 2
        if ov.get('rss') and not str(ov['rss']).startswith(('http://', 'https://')):
            return jsonify({'ok': False, 'error': 'rss 须为 http(s) URL'}), 400
        db.upsert_source_override(ov)
        invalidate_sources_cache()
        cache.clear()
        return jsonify({'ok': True, 'origin': 'builtin'})

    if not custom:
        return jsonify({'ok': False, 'error': '源不存在'}), 404

    payload, err = _validate_source_payload({**custom, **data, 'name': name}, require_name=True)
    if err:
        return jsonify({'ok': False, 'error': err}), 400
    db.upsert_custom_source(payload)
    invalidate_sources_cache()
    cache.clear()
    return jsonify({'ok': True, 'origin': 'custom', 'source': payload})


@app.route('/api/admin/sources/<path:name>', methods=['DELETE'])
def admin_delete_source(name):
    name = unquote(name).strip()
    builtin = next((s for s in THINK_TANKS_CONFIG if s['name'] == name), None)
    if builtin:
        # 内置源：禁用并清除覆盖中的字段改动（保留 disabled）
        db.upsert_source_override({'name': name, 'enabled': 0})
        invalidate_sources_cache()
        cache.clear()
        return jsonify({'ok': True, 'action': 'disabled'})
    if not db.get_custom_source(name):
        return jsonify({'ok': False, 'error': '源不存在'}), 404
    db.delete_custom_source(name)
    invalidate_sources_cache()
    cache.clear()
    return jsonify({'ok': True, 'action': 'deleted'})


@app.route('/api/admin/sources/<path:name>/fetch', methods=['POST'])
def admin_fetch_one(name):
    name = unquote(name).strip()
    sources = get_runtime_sources(include_disabled=True)
    feed = next((s for s in sources if s['name'] == name), None)
    if not feed:
        return jsonify({'ok': False, 'error': '源不存在'}), 404
    if not feed.get('enabled', True):
        return jsonify({'ok': False, 'error': '源已禁用'}), 400
    if _fetch_in_progress:
        return jsonify({'ok': False, 'error': '全局抓取进行中，请稍后再试'}), 409

    def _job():
        global _fetch_in_progress
        with _fetch_lock:
            if _fetch_in_progress:
                return
            _fetch_in_progress = True
        try:
            fetch_sources([feed], mode='manual')
            cache.clear()
        finally:
            _fetch_in_progress = False

    threading.Thread(target=_job, daemon=True).start()
    return jsonify({'ok': True, 'fetching': True, 'name': name})


if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    sources = get_runtime_sources()
    print(f'已加载 {len(sources)} 个信息源')
    print(f'覆盖国家和地区: {len(runtime_stats(sources)["country_stats"])} 个')
    db.init_db()
    bootstrap()
    # use_reloader=False：避免双进程重复抓取；定时线程已在 bootstrap 中启动
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
