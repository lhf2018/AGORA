# db.py — SQLite persistence for Agora
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta

DEFAULT_DB_PATH = os.path.join('data', 'aggregator.db')
DEFAULT_RETENTION_DAYS = 30

_local = threading.local()
_db_path = DEFAULT_DB_PATH
_init_lock = threading.Lock()
_initialized = False


def configure(db_path=None):
    global _db_path, _initialized
    if db_path:
        _db_path = db_path
    _initialized = False


def _connect():
    os.makedirs(os.path.dirname(_db_path) or '.', exist_ok=True)
    conn = sqlite3.connect(_db_path, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA foreign_keys=ON')
    return conn


@contextmanager
def get_conn():
    init_db()
    conn = getattr(_local, 'conn', None)
    if conn is None:
        conn = _connect()
        _local.conn = conn
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def init_db(db_path=None):
    global _initialized
    if db_path:
        configure(db_path)
    if _initialized:
        return
    with _init_lock:
        if _initialized:
            return
        os.makedirs(os.path.dirname(_db_path) or '.', exist_ok=True)
        conn = _connect()
        try:
            conn.executescript(
                '''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    published_raw TEXT,
                    published TEXT,
                    published_at TEXT,
                    source TEXT,
                    source_cn TEXT,
                    icon TEXT,
                    category TEXT,
                    source_type TEXT,
                    source_type_label TEXT,
                    domain TEXT,
                    domain_label TEXT,
                    country TEXT,
                    priority INTEGER DEFAULT 2,
                    description TEXT,
                    fetched_at TEXT NOT NULL,
                    link_kind TEXT,
                    filing_type TEXT,
                    company_id TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_articles_published
                    ON articles(published_at DESC);
                CREATE INDEX IF NOT EXISTS idx_articles_country
                    ON articles(country);
                CREATE INDEX IF NOT EXISTS idx_articles_source_type
                    ON articles(source_type);
                CREATE INDEX IF NOT EXISTS idx_articles_fetched
                    ON articles(fetched_at);

                CREATE TABLE IF NOT EXISTS sources_state (
                    name TEXT PRIMARY KEY,
                    name_cn TEXT,
                    priority INTEGER DEFAULT 2,
                    last_fetched_at TEXT,
                    last_success_at TEXT,
                    last_error TEXT,
                    success_count INTEGER DEFAULT 0,
                    fail_count INTEGER DEFAULT 0,
                    last_article_count INTEGER DEFAULT 0,
                    noise_count INTEGER DEFAULT 0,
                    consecutive_fails INTEGER DEFAULT 0,
                    demoted INTEGER DEFAULT 0,
                    demoted_reason TEXT,
                    demoted_at TEXT
                );

                CREATE TABLE IF NOT EXISTS fetch_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    mode TEXT,
                    sources_total INTEGER DEFAULT 0,
                    sources_ok INTEGER DEFAULT 0,
                    sources_fail INTEGER DEFAULT 0,
                    articles_upserted INTEGER DEFAULT 0,
                    note TEXT
                );

                CREATE TABLE IF NOT EXISTS meta (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );

                CREATE TABLE IF NOT EXISTS custom_sources (
                    name TEXT PRIMARY KEY,
                    name_cn TEXT NOT NULL,
                    rss TEXT NOT NULL,
                    icon TEXT,
                    category TEXT DEFAULT '其他',
                    doc_type TEXT,
                    domain TEXT,
                    country TEXT DEFAULT '其他',
                    priority INTEGER DEFAULT 2,
                    description TEXT,
                    enabled INTEGER DEFAULT 1,
                    created_at TEXT,
                    updated_at TEXT
                );

                CREATE TABLE IF NOT EXISTS source_overrides (
                    name TEXT PRIMARY KEY,
                    enabled INTEGER,
                    rss TEXT,
                    name_cn TEXT,
                    icon TEXT,
                    category TEXT,
                    doc_type TEXT,
                    domain TEXT,
                    country TEXT,
                    priority INTEGER,
                    description TEXT,
                    updated_at TEXT
                );
                '''
            )
            conn.commit()
            _migrate_columns(conn)
            # 领域索引必须在列迁移之后创建（旧库 CREATE TABLE IF NOT EXISTS 不会加新列）
            conn.execute(
                'CREATE INDEX IF NOT EXISTS idx_articles_domain ON articles(domain)'
            )
            conn.commit()
            _local.conn = conn
            _initialized = True
        except Exception:
            conn.close()
            raise


def _migrate_columns(conn):
    """Add columns introduced after first deploy (SQLite has no IF NOT EXISTS for columns)."""
    # sources_state
    cols = {
        r[1]
        for r in conn.execute('PRAGMA table_info(sources_state)').fetchall()
    }
    alters = [
        ('noise_count', 'INTEGER DEFAULT 0'),
        ('consecutive_fails', 'INTEGER DEFAULT 0'),
        ('demoted', 'INTEGER DEFAULT 0'),
        ('demoted_reason', 'TEXT'),
        ('demoted_at', 'TEXT'),
    ]
    for name, typedef in alters:
        if name not in cols:
            conn.execute(f'ALTER TABLE sources_state ADD COLUMN {name} {typedef}')

    # articles
    art_cols = {
        r[1]
        for r in conn.execute('PRAGMA table_info(articles)').fetchall()
    }
    for name, typedef in (
        ('domain', 'TEXT'),
        ('domain_label', 'TEXT'),
        ('link_kind', 'TEXT'),
        ('filing_type', 'TEXT'),
        ('company_id', 'TEXT'),
    ):
        if name not in art_cols:
            conn.execute(f'ALTER TABLE articles ADD COLUMN {name} {typedef}')
    conn.commit()


def set_meta(key, value):
    with get_conn() as conn:
        conn.execute(
            'INSERT INTO meta(key, value) VALUES(?, ?) '
            'ON CONFLICT(key) DO UPDATE SET value=excluded.value',
            (key, value),
        )


def get_meta(key, default=None):
    with get_conn() as conn:
        row = conn.execute('SELECT value FROM meta WHERE key=?', (key,)).fetchone()
        return row['value'] if row else default


def upsert_articles(articles):
    """Insert or update articles by unique link. Returns (inserted, updated)."""
    if not articles:
        return 0, 0
    inserted = 0
    updated = 0
    now = datetime.utcnow().isoformat()
    sql = '''
        INSERT INTO articles (
            link, title, published_raw, published, published_at,
            source, source_cn, icon, category, source_type, source_type_label,
            domain, domain_label, country, priority, description, fetched_at,
            link_kind, filing_type, company_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(link) DO UPDATE SET
            title=excluded.title,
            published_raw=COALESCE(excluded.published_raw, articles.published_raw),
            published=COALESCE(excluded.published, articles.published),
            published_at=COALESCE(excluded.published_at, articles.published_at),
            source=excluded.source,
            source_cn=excluded.source_cn,
            icon=excluded.icon,
            category=excluded.category,
            source_type=excluded.source_type,
            source_type_label=excluded.source_type_label,
            domain=excluded.domain,
            domain_label=excluded.domain_label,
            country=excluded.country,
            priority=excluded.priority,
            description=excluded.description,
            fetched_at=excluded.fetched_at,
            link_kind=COALESCE(excluded.link_kind, articles.link_kind),
            filing_type=COALESCE(excluded.filing_type, articles.filing_type),
            company_id=COALESCE(excluded.company_id, articles.company_id)
    '''
    with get_conn() as conn:
        for a in articles:
            link = (a.get('link') or '').strip()
            title = (a.get('title') or '').strip()
            if not link or not title:
                continue
            exists = conn.execute(
                'SELECT 1 FROM articles WHERE link=?', (link,)
            ).fetchone()
            conn.execute(
                sql,
                (
                    link,
                    title,
                    a.get('published_raw') or '',
                    a.get('published') or '时间未知',
                    a.get('published_timestamp'),
                    a.get('source') or '',
                    a.get('source_cn') or '',
                    a.get('icon') or '',
                    a.get('category') or '',
                    a.get('source_type') or '',
                    a.get('source_type_label') or '',
                    a.get('domain') or '',
                    a.get('domain_label') or '',
                    a.get('country') or '',
                    a.get('priority', 2),
                    a.get('description') or '',
                    now,
                    a.get('link_kind') or '',
                    a.get('filing_type') or '',
                    a.get('company_id') or '',
                ),
            )
            if exists:
                updated += 1
            else:
                inserted += 1
    return inserted, updated


def record_source_fetch(
    name,
    name_cn,
    priority,
    ok,
    article_count=0,
    error=None,
    noise_hits=0,
    demote=False,
    demote_reason=None,
):
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        row = conn.execute(
            'SELECT * FROM sources_state WHERE name=?',
            (name,),
        ).fetchone()
        if row:
            success = (row['success_count'] or 0) + (1 if ok else 0)
            fail = (row['fail_count'] or 0) + (0 if ok else 1)
            noise = (row['noise_count'] or 0) + max(0, noise_hits)
            streak = 0 if ok else (row['consecutive_fails'] or 0) + 1
            demoted = 1 if demote or (row and row['demoted']) else 0
            # 干净成功一次即可解除降权（给源恢复机会）
            if ok and noise_hits == 0:
                demoted = 0
                demote_reason = None
            reason = demote_reason if demoted else None
            demoted_at = now if demoted and not (row and row['demoted']) else (
                None if not demoted else (row['demoted_at'] if row else None)
            )
            conn.execute(
                '''
                UPDATE sources_state SET
                    name_cn=?, priority=?, last_fetched_at=?,
                    last_success_at=CASE WHEN ? THEN ? ELSE last_success_at END,
                    last_error=?, success_count=?, fail_count=?,
                    last_article_count=?, noise_count=?, consecutive_fails=?,
                    demoted=?, demoted_reason=?, demoted_at=?
                WHERE name=?
                ''',
                (
                    name_cn,
                    priority,
                    now,
                    1 if ok else 0,
                    now,
                    None if ok else (error or 'error'),
                    success,
                    fail,
                    article_count,
                    noise,
                    streak,
                    demoted,
                    reason if demoted else None,
                    demoted_at,
                    name,
                ),
            )
        else:
            conn.execute(
                '''
                INSERT INTO sources_state (
                    name, name_cn, priority, last_fetched_at, last_success_at,
                    last_error, success_count, fail_count, last_article_count,
                    noise_count, consecutive_fails, demoted, demoted_reason, demoted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    name,
                    name_cn,
                    priority,
                    now,
                    now if ok else None,
                    None if ok else (error or 'error'),
                    1 if ok else 0,
                    0 if ok else 1,
                    article_count,
                    max(0, noise_hits),
                    0 if ok else 1,
                    1 if demote else 0,
                    demote_reason if demote else None,
                    now if demote else None,
                ),
            )


def get_due_source_names(
    configs,
    high_interval_min=10,
    normal_interval_min=30,
    demoted_interval_min=360,
):
    """Return config entries that are due for refresh. Demoted sources refresh rarely."""
    now = datetime.utcnow()
    with get_conn() as conn:
        rows = {
            r['name']: r
            for r in conn.execute('SELECT * FROM sources_state')
        }
    due = []
    for cfg in configs:
        name = cfg['name']
        base_priority = cfg.get('priority', 2)
        state = rows.get(name)
        demoted = bool(state and state['demoted'])
        if demoted:
            interval = demoted_interval_min
            sort_key = 9
        else:
            interval = high_interval_min if base_priority == 1 else normal_interval_min
            sort_key = base_priority

        if not state or not state['last_fetched_at']:
            due.append((sort_key, cfg))
            continue
        try:
            last = datetime.fromisoformat(state['last_fetched_at'])
        except ValueError:
            due.append((sort_key, cfg))
            continue
        if now - last >= timedelta(minutes=interval):
            due.append((sort_key, cfg))
    due.sort(key=lambda x: x[0])
    return [cfg for _, cfg in due]


def list_source_health(configs):
    """Merge config with sources_state for health panel."""
    with get_conn() as conn:
        states = {
            r['name']: dict(r)
            for r in conn.execute('SELECT * FROM sources_state')
        }
    items = []
    for cfg in configs:
        st = states.get(cfg['name'], {})
        success = st.get('success_count') or 0
        fail = st.get('fail_count') or 0
        total_attempts = success + fail
        items.append({
            'name': cfg['name'],
            'name_cn': cfg.get('name_cn', cfg['name']),
            'country': cfg.get('country', ''),
            'priority': cfg.get('priority', 2),
            'category': cfg.get('category', ''),
            'last_fetched_at': st.get('last_fetched_at'),
            'last_success_at': st.get('last_success_at'),
            'last_error': st.get('last_error'),
            'success_count': success,
            'fail_count': fail,
            'noise_count': st.get('noise_count') or 0,
            'consecutive_fails': st.get('consecutive_fails') or 0,
            'last_article_count': st.get('last_article_count') or 0,
            'demoted': bool(st.get('demoted')),
            'demoted_reason': st.get('demoted_reason'),
            'demoted_at': st.get('demoted_at'),
            'status': (
                'demoted' if st.get('demoted')
                else 'ok' if success and not (st.get('consecutive_fails') or 0)
                else 'failing' if (st.get('consecutive_fails') or 0) > 0 or fail > success
                else 'unknown'
            ),
            'success_rate': round(success / total_attempts, 3) if total_attempts else None,
        })
    # demoted / failing first
    order = {'demoted': 0, 'failing': 1, 'unknown': 2, 'ok': 3}
    items.sort(key=lambda x: (order.get(x['status'], 9), -(x['fail_count']), x['name_cn']))
    return items


def health_summary(configs):
    items = list_source_health(configs)
    return {
        'total': len(items),
        'ok': sum(1 for i in items if i['status'] == 'ok'),
        'failing': sum(1 for i in items if i['status'] == 'failing'),
        'demoted': sum(1 for i in items if i['status'] == 'demoted'),
        'unknown': sum(1 for i in items if i['status'] == 'unknown'),
        'sources': items,
    }


def start_fetch_log(mode, sources_total):
    started = datetime.utcnow().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            '''
            INSERT INTO fetch_logs (started_at, mode, sources_total)
            VALUES (?, ?, ?)
            ''',
            (started, mode, sources_total),
        )
        return cur.lastrowid


def finish_fetch_log(log_id, sources_ok, sources_fail, articles_upserted, note=''):
    with get_conn() as conn:
        conn.execute(
            '''
            UPDATE fetch_logs SET
                finished_at=?, sources_ok=?, sources_fail=?,
                articles_upserted=?, note=?
            WHERE id=?
            ''',
            (
                datetime.utcnow().isoformat(),
                sources_ok,
                sources_fail,
                articles_upserted,
                note,
                log_id,
            ),
        )


def article_count():
    with get_conn() as conn:
        row = conn.execute('SELECT COUNT(*) AS n FROM articles').fetchone()
        return row['n'] if row else 0


def latest_fetched_at():
    with get_conn() as conn:
        row = conn.execute(
            'SELECT MAX(fetched_at) AS t FROM articles'
        ).fetchone()
        return row['t'] if row and row['t'] else get_meta('last_fetch_finished_at')


def row_to_article(row):
    keys = row.keys()
    return {
        'title': row['title'],
        'link': row['link'],
        'published_raw': row['published_raw'] or '',
        'published': row['published'] or '时间未知',
        'published_timestamp': row['published_at'],
        'source': row['source'],
        'source_cn': row['source_cn'],
        'icon': row['icon'] or '',
        'category': row['category'] or '',
        'source_type': row['source_type'] or '',
        'source_type_label': row['source_type_label'] or '',
        'domain': row['domain'] if 'domain' in keys else '',
        'domain_label': row['domain_label'] if 'domain_label' in keys else '',
        'country': row['country'] or '',
        'priority': row['priority'] if row['priority'] is not None else 2,
        'description': row['description'] or '',
        'link_kind': (row['link_kind'] if 'link_kind' in keys else '') or '',
        'filing_type': (row['filing_type'] if 'filing_type' in keys else '') or '',
        'company_id': (row['company_id'] if 'company_id' in keys else '') or '',
    }


def query_articles(
    source_type='all',
    country='all',
    domain='all',
    days=None,
    page=1,
    per_page=24,
    topic_patterns=None,
    q=None,
    fetch_all=False,
    limit=None,
):
    """Query articles with filters. When fetch_all/topic/q, return full list for caller.

    days: int lookback window, or None/'all' for no time filter.
    """
    clauses = []
    params = []
    if source_type and source_type != 'all':
        clauses.append('source_type = ?')
        params.append(source_type)
    if domain and domain != 'all':
        clauses.append('domain = ?')
        params.append(domain)
    if country and country != 'all':
        clauses.append('country = ?')
        params.append(country)
    try:
        days_n = int(days) if days not in (None, '', 'all') else None
    except (TypeError, ValueError):
        days_n = None
    if days_n and days_n > 0:
        cutoff = (datetime.utcnow() - timedelta(days=days_n)).isoformat()
        # 有发布时间用 published_at；缺失时用抓取时间兜底
        clauses.append(
            '''(
                (published_at IS NOT NULL AND published_at <> '' AND published_at >= ?)
                OR
                ((published_at IS NULL OR published_at = '') AND fetched_at >= ?)
            )'''
        )
        params.extend([cutoff, cutoff])
    q = (q or '').strip()
    if q:
        clauses.append('title LIKE ?')
        params.append(f'%{q}%')

    where = (' WHERE ' + ' AND '.join(clauses)) if clauses else ''
    order = '''
        ORDER BY
            CASE WHEN published_at IS NULL OR published_at = '' THEN 1 ELSE 0 END,
            published_at DESC,
            fetched_at DESC
    '''

    with get_conn() as conn:
        if fetch_all or topic_patterns is not None or q:
            sql = f'SELECT * FROM articles{where}{order}'
            if limit:
                sql += ' LIMIT ?'
                rows = conn.execute(sql, [*params, limit]).fetchall()
            else:
                rows = conn.execute(sql, params).fetchall()
            return [row_to_article(r) for r in rows]

        total_row = conn.execute(
            f'SELECT COUNT(*) AS n FROM articles{where}',
            params,
        ).fetchone()
        total = total_row['n'] if total_row else 0
        total_pages = max(1, (total + per_page - 1) // per_page) if total else 1
        page = max(1, min(page, total_pages))
        offset = (page - 1) * per_page
        rows = conn.execute(
            f'SELECT * FROM articles{where}{order} LIMIT ? OFFSET ?',
            [*params, per_page, offset],
        ).fetchall()
        articles = [row_to_article(r) for r in rows]
        return articles, {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
        }


def iter_recent_titles(days=7):
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    with get_conn() as conn:
        rows = conn.execute(
            '''
            SELECT title, published_at FROM articles
            WHERE published_at IS NOT NULL AND published_at >= ?
            ''',
            (cutoff,),
        ).fetchall()
        return [{'title': r['title'], 'published_timestamp': r['published_at']} for r in rows]


def prune_old_articles(retention_days=DEFAULT_RETENTION_DAYS):
    cutoff = (datetime.utcnow() - timedelta(days=retention_days)).isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            '''
            DELETE FROM articles
            WHERE (published_at IS NOT NULL AND published_at <> '' AND published_at < ?)
               OR ((published_at IS NULL OR published_at = '') AND fetched_at < ?)
            ''',
            (cutoff, cutoff),
        )
        return cur.rowcount


def delete_articles_by_links(links):
    if not links:
        return 0
    with get_conn() as conn:
        cur = conn.executemany('DELETE FROM articles WHERE link=?', [(l,) for l in links])
        return cur.rowcount


def iter_all_article_titles(limit=5000):
    with get_conn() as conn:
        rows = conn.execute(
            'SELECT link, title FROM articles ORDER BY fetched_at DESC LIMIT ?',
            (limit,),
        ).fetchall()
        return [(r['link'], r['title']) for r in rows]


def _row_custom_source(row):
    if not row:
        return None
    return {
        'name': row['name'],
        'name_cn': row['name_cn'],
        'rss': row['rss'],
        'icon': row['icon'] or '',
        'category': row['category'] or '其他',
        'doc_type': row['doc_type'],
        'domain': row['domain'],
        'country': row['country'] or '其他',
        'priority': row['priority'] if row['priority'] is not None else 2,
        'description': row['description'] or '',
        'enabled': 1 if (row['enabled'] is None or row['enabled']) else 0,
        'created_at': row['created_at'],
        'updated_at': row['updated_at'],
    }


def list_custom_sources():
    with get_conn() as conn:
        rows = conn.execute(
            'SELECT * FROM custom_sources ORDER BY name_cn COLLATE NOCASE'
        ).fetchall()
        return [_row_custom_source(r) for r in rows]


def get_custom_source(name):
    with get_conn() as conn:
        row = conn.execute(
            'SELECT * FROM custom_sources WHERE name=?', (name,)
        ).fetchone()
        return _row_custom_source(row)


def upsert_custom_source(payload):
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        existing = conn.execute(
            'SELECT created_at FROM custom_sources WHERE name=?',
            (payload['name'],),
        ).fetchone()
        created = existing['created_at'] if existing else now
        conn.execute(
            '''
            INSERT INTO custom_sources (
                name, name_cn, rss, icon, category, doc_type, domain,
                country, priority, description, enabled, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                name_cn=excluded.name_cn,
                rss=excluded.rss,
                icon=excluded.icon,
                category=excluded.category,
                doc_type=excluded.doc_type,
                domain=excluded.domain,
                country=excluded.country,
                priority=excluded.priority,
                description=excluded.description,
                enabled=excluded.enabled,
                updated_at=excluded.updated_at
            ''',
            (
                payload['name'],
                payload.get('name_cn') or payload['name'],
                payload['rss'],
                payload.get('icon') or '',
                payload.get('category') or '其他',
                payload.get('doc_type'),
                payload.get('domain'),
                payload.get('country') or '其他',
                payload.get('priority', 2),
                payload.get('description') or '',
                1 if payload.get('enabled', True) else 0,
                created,
                now,
            ),
        )


def delete_custom_source(name):
    with get_conn() as conn:
        cur = conn.execute('DELETE FROM custom_sources WHERE name=?', (name,))
        return cur.rowcount


def list_source_overrides():
    with get_conn() as conn:
        rows = conn.execute('SELECT * FROM source_overrides').fetchall()
        return [dict(r) for r in rows]


def get_source_override(name):
    with get_conn() as conn:
        row = conn.execute(
            'SELECT * FROM source_overrides WHERE name=?', (name,)
        ).fetchone()
        return dict(row) if row else None


def upsert_source_override(payload):
    """Merge override row; None/missing keys leave existing DB values when updating."""
    now = datetime.utcnow().isoformat()
    name = payload['name']
    with get_conn() as conn:
        prev = conn.execute(
            'SELECT * FROM source_overrides WHERE name=?', (name,)
        ).fetchone()
        prev = dict(prev) if prev else {}

        def pick(key, default=None):
            if key in payload:
                return payload[key]
            return prev.get(key, default)

        enabled = pick('enabled')
        if enabled is not None:
            enabled = 1 if enabled not in (0, False, '0', 'false') else 0

        conn.execute(
            '''
            INSERT INTO source_overrides (
                name, enabled, rss, name_cn, icon, category, doc_type,
                domain, country, priority, description, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                enabled=excluded.enabled,
                rss=excluded.rss,
                name_cn=excluded.name_cn,
                icon=excluded.icon,
                category=excluded.category,
                doc_type=excluded.doc_type,
                domain=excluded.domain,
                country=excluded.country,
                priority=excluded.priority,
                description=excluded.description,
                updated_at=excluded.updated_at
            ''',
            (
                name,
                enabled,
                pick('rss'),
                pick('name_cn'),
                pick('icon'),
                pick('category'),
                pick('doc_type'),
                pick('domain'),
                pick('country'),
                pick('priority'),
                pick('description'),
                now,
            ),
        )


def delete_source_override(name):
    with get_conn() as conn:
        cur = conn.execute('DELETE FROM source_overrides WHERE name=?', (name,))
        return cur.rowcount
