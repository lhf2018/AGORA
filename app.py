# app.py
import os
import re
import time
import threading
import concurrent.futures
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse, parse_qs, unquote

import feedparser
import requests
from flask import Flask, render_template, jsonify, request
from flask_caching import Cache

from config import (
    THINK_TANKS_CONFIG,
    TOPIC_LEXICON,
    DOC_TYPE_LABELS,
    DOMAIN_LABELS,
    get_country_stats,
    get_category_stats,
    get_doc_type_stats,
    get_domain_stats,
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

_fetch_lock = threading.Lock()
_fetch_in_progress = False
_scheduler_started = False


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
                'description': feed_info.get('description', ''),
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
        if force_all or db.article_count() == 0:
            feeds = list(THINK_TANKS_CONFIG)
            mode = 'full'
        else:
            feeds = db.get_due_source_names(
                THINK_TANKS_CONFIG,
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
    backfilled = backfill_article_taxonomy()
    if backfilled:
        print(f'已回填领域/文体标签 {backfilled} 篇')
    print(f'数据库就绪：{db.DEFAULT_DB_PATH}，已有 {count} 篇文章')
    start_background_fetch(force_all=(count == 0))
    start_scheduler()


def backfill_article_taxonomy():
    """用当前源配置回填旧文章的 domain / source_type。"""
    by_name = {s['name']: s for s in THINK_TANKS_CONFIG}
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


@app.route('/')
def index():
    return render_template('index.html')


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
    summary = db.health_summary(THINK_TANKS_CONFIG)
    return jsonify(summary)


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
        'description': s.get('description', '')
    } for s in THINK_TANKS_CONFIG]
    return jsonify(sources)


@app.route('/api/stats')
def get_stats():
    return jsonify({
        'total_sources': len(THINK_TANKS_CONFIG),
        'article_count': db.article_count(),
        'country_stats': get_country_stats(),
        'category_stats': get_category_stats(),
        'doc_type_stats': get_doc_type_stats(),
        'domain_stats': get_domain_stats(),
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


if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    print(f'已加载 {len(THINK_TANKS_CONFIG)} 个信息源')
    print(f'覆盖国家和地区: {len(get_country_stats())} 个')
    db.init_db()
    bootstrap()
    # use_reloader=False：避免双进程重复抓取；定时线程已在 bootstrap 中启动
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
