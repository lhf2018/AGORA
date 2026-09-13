# filings.py — pull official disclosures (SEC EDGAR + 巨潮 cninfo + 港交所披露易)
import json
import time
from datetime import datetime, timedelta

import requests

import earnings

SEC_UA = "Agora Cognition Aggregator contact@localhost"
SEC_HEADERS = {
    "User-Agent": SEC_UA,
    "Accept-Encoding": "gzip, deflate",
    "Accept": "application/json",
}

CNINFO_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.cninfo.com.cn",
    "Referer": "https://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search",
}

# Periodic + foreign issuer reports; 8-K/6-K filtered further
EDGAR_PERIODIC = {"10-K", "10-Q", "10-K/A", "10-Q/A", "20-F", "20-F/A", "40-F", "40-F/A"}
EDGAR_CURRENT = {"8-K", "8-K/A", "6-K", "6-K/A"}

# 8-K Item 2.02 = results of operations; also catch earnings keywords in items text
_EARNINGS_ITEM_HINTS = ("2.02", "2.01", "7.01", "9.01", "earnings", "results")

CNINFO_CATEGORY = (
    "category_ndbg_szsh;category_bndbg_szsh;"
    "category_yjdbg_szsh;category_sjdbg_szsh"
)

# 披露易：财务报表 + 业绩公告
HKEX_SEARCH_QUERIES = [
    # Financial Statements / ESG
    {"t1code": "40000", "t2code": "40100", "label": "年报"},
    {"t1code": "40000", "t2code": "40200", "label": "中期报告"},
    {"t1code": "40000", "t2code": "40300", "label": "季报"},
    # Results announcements
    {"t1code": "10000", "t2code": "13300", "label": "全年业绩"},
    {"t1code": "10000", "t2code": "13400", "label": "中期业绩"},
    {"t1code": "10000", "t2code": "13600", "label": "季度业绩"},
    {"t1code": "10000", "t2code": "13500", "label": "盈利警告"},
]

HKEX_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=en",
}

_cninfo_org_cache = None
_hkex_stock_cache = {}
_hkex_session = None


def pad_cik(cik):
    return str(int(str(cik).strip())).zfill(10)


def edgar_document_url(cik, accession, primary_document):
    cik_num = str(int(str(cik).strip()))
    acc = (accession or "").replace("-", "")
    doc = (primary_document or "").lstrip("/")
    if not acc or not doc:
        return f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={pad_cik(cik)}"
    return f"https://www.sec.gov/Archives/edgar/data/{cik_num}/{acc}/{doc}"


def _parse_ymd(s):
    if not s:
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except ValueError:
        return None


def _is_earnings_current_report(form, items):
    form = (form or "").upper()
    if form not in EDGAR_CURRENT and not form.startswith("8-K") and not form.startswith("6-K"):
        return False
    text = (items or "").lower()
    if not text.strip():
        # 6-K often empty items — keep recent ones (foreign earnings releases)
        return form.startswith("6-K")
    return any(h in text for h in _EARNINGS_ITEM_HINTS)


def fetch_edgar_for_company(company, lookback_days=180, max_items=12):
    """Return article-shaped dicts for one company's recent EDGAR filings."""
    cik = company.get("cik")
    if not cik:
        return []
    url = f"https://data.sec.gov/submissions/CIK{pad_cik(cik)}.json"
    try:
        resp = requests.get(url, headers=SEC_HEADERS, timeout=25)
        if resp.status_code != 200:
            print(f"[filings] EDGAR {company.get('label')}: status {resp.status_code}")
            return []
        data = resp.json()
    except Exception as e:
        print(f"[filings] EDGAR {company.get('label')}: {type(e).__name__}")
        return []

    recent = (data.get("filings") or {}).get("recent") or {}
    forms = recent.get("form") or []
    if not forms:
        return []

    accession = recent.get("accessionNumber") or []
    filing_date = recent.get("filingDate") or []
    primary = recent.get("primaryDocument") or []
    items_list = recent.get("items") or []
    report_date = recent.get("reportDate") or []

    cutoff = datetime.utcnow() - timedelta(days=lookback_days)
    # Annual forms keep longer window
    annual_cutoff = datetime.utcnow() - timedelta(days=max(lookback_days, 400))

    out = []
    for i, form in enumerate(forms):
        form_u = (form or "").upper()
        fdate = _parse_ymd(filing_date[i] if i < len(filing_date) else "")
        if not fdate:
            continue

        keep = False
        if form_u in EDGAR_PERIODIC or form_u.rstrip("/A") in {"10-K", "10-Q", "20-F", "40-F"}:
            cut = annual_cutoff if "10-K" in form_u or "20-F" in form_u or "40-F" in form_u else cutoff
            keep = fdate >= cut
        elif form_u in EDGAR_CURRENT or form_u.startswith("8-K") or form_u.startswith("6-K"):
            items = items_list[i] if i < len(items_list) else ""
            keep = fdate >= cutoff and _is_earnings_current_report(form_u, items)
        if not keep:
            continue

        acc = accession[i] if i < len(accession) else ""
        doc = primary[i] if i < len(primary) else ""
        link = edgar_document_url(cik, acc, doc)
        rdate = report_date[i] if i < len(report_date) else ""
        period = f" · 报告期 {rdate}" if rdate else ""
        ticker = company.get("ticker") or ""
        title = f"{company['label']} {form_u}{period}"
        if ticker:
            title = f"{company['label']} ({ticker}) {form_u}{period}"

        pub_iso = fdate.strftime("%Y-%m-%dT00:00:00")
        out.append({
            "title": title,
            "link": link,
            "published_raw": filing_date[i] if i < len(filing_date) else "",
            "published": f"{fdate.year}年{fdate.month:02d}月{fdate.day:02d}日",
            "published_timestamp": pub_iso,
            "source": "SEC EDGAR",
            "source_cn": "SEC·官方披露",
            "icon": "https://www.sec.gov/favicon.ico",
            "category": "财报",
            "source_type": "earnings",
            "source_type_label": "财报",
            "domain": "industry",
            "domain_label": "产业",
            "country": "美国" if company.get("market") == "us" else (
                "中国" if company.get("market") in ("cn", "hk") else "国际"
            ),
            "priority": 1,
            "description": f"SEC {form_u} 原文 · accession {acc}",
            "link_kind": "official",
            "filing_type": form_u,
            "company_id": company["id"],
        })
        if len(out) >= max_items:
            break

    return out


def _load_cninfo_org_map():
    global _cninfo_org_cache
    if _cninfo_org_cache is not None:
        return _cninfo_org_cache
    mapping = {}
    for path, column in (
        ("szse_stock.json", "szse"),
        ("sse_stock.json", "sse"),
    ):
        url = f"http://www.cninfo.com.cn/new/data/{path}"
        try:
            resp = requests.get(url, headers={"User-Agent": CNINFO_HEADERS["User-Agent"]}, timeout=30)
            if resp.status_code != 200:
                continue
            stock_list = (resp.json() or {}).get("stockList") or []
            for row in stock_list:
                code = str(row.get("code") or "").strip()
                org = str(row.get("orgId") or "").strip()
                if code and org:
                    mapping[code] = {"orgId": org, "column": column}
        except Exception as e:
            print(f"[filings] cninfo list {path}: {type(e).__name__}")
    _cninfo_org_cache = mapping
    return mapping


def _cninfo_column_for_code(code):
    if code.startswith("6"):
        return "sse"
    return "szse"


def fetch_cninfo_for_company(company, lookback_days=400, max_items=10):
    """Return article-shaped dicts for A-share periodic reports (PDF)."""
    code = (company.get("cn_code") or company.get("ticker") or "").strip()
    if not code or len(code) != 6 or not code.isdigit():
        return []

    org_map = _load_cninfo_org_map()
    meta = org_map.get(code)
    if not meta:
        print(f"[filings] cninfo no orgId for {code}")
        return []

    column = meta.get("column") or _cninfo_column_for_code(code)
    org_id = meta["orgId"]
    se_end = datetime.utcnow().strftime("%Y-%m-%d")
    se_start = (datetime.utcnow() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

    payload = {
        "pageNum": "1",
        "pageSize": str(max(max_items, 20)),
        "column": column,
        "tabName": "fulltext",
        "plate": "",
        "stock": f"{code},{org_id}",
        "searchkey": "",
        "secid": "",
        "category": CNINFO_CATEGORY,
        "trade": "",
        "seDate": f"{se_start}~{se_end}",
        "sortName": "",
        "sortType": "",
        "isHLtitle": "true",
    }
    try:
        resp = requests.post(
            "https://www.cninfo.com.cn/new/hisAnnouncement/query",
            headers=CNINFO_HEADERS,
            data=payload,
            timeout=30,
        )
        if resp.status_code != 200:
            print(f"[filings] cninfo {company.get('label')}: status {resp.status_code}")
            return []
        data = resp.json() or {}
    except Exception as e:
        print(f"[filings] cninfo {company.get('label')}: {type(e).__name__}")
        return []

    anns = data.get("announcements") or []
    out = []
    for ann in anns:
        adjunct = (ann.get("adjunctUrl") or "").strip()
        if not adjunct:
            continue
        if not adjunct.lower().endswith(".pdf"):
            # still accept; cninfo usually gives PDF for periodic reports
            pass
        link = adjunct if adjunct.startswith("http") else f"https://static.cninfo.com.cn/{adjunct}"
        title_raw = (ann.get("announcementTitle") or "").strip()
        # strip HTML emphasis tags sometimes present
        title_raw = title_raw.replace("<em>", "").replace("</em>", "")
        ts_ms = ann.get("announcementTime")
        fdate = None
        if isinstance(ts_ms, (int, float)):
            try:
                fdate = datetime.utcfromtimestamp(ts_ms / 1000.0)
            except (OverflowError, OSError, ValueError):
                fdate = None
        if not fdate:
            continue

        filing_type = "季报"
        if "年度报告" in title_raw and "摘要" not in title_raw:
            filing_type = "年报"
        elif "半年度" in title_raw or "中期" in title_raw:
            filing_type = "半年报"
        elif "一季" in title_raw:
            filing_type = "一季报"
        elif "三季" in title_raw:
            filing_type = "三季报"

        pub_iso = fdate.strftime("%Y-%m-%dT00:00:00")
        out.append({
            "title": title_raw or f"{company['label']} {filing_type}",
            "link": link,
            "published_raw": str(ts_ms or ""),
            "published": f"{fdate.year}年{fdate.month:02d}月{fdate.day:02d}日",
            "published_timestamp": pub_iso,
            "source": "CNINFO",
            "source_cn": "巨潮·官方披露",
            "icon": "http://www.cninfo.com.cn/favicon.ico",
            "category": "财报",
            "source_type": "earnings",
            "source_type_label": "财报",
            "domain": "industry",
            "domain_label": "产业",
            "country": "中国",
            "priority": 1,
            "description": f"巨潮资讯 {filing_type} PDF",
            "link_kind": "official",
            "filing_type": filing_type,
            "company_id": company["id"],
        })
        if len(out) >= max_items:
            break
    return out


def normalize_hk_code(code):
    raw = str(code or "").strip().upper().replace(".HK", "")
    digits = "".join(ch for ch in raw if ch.isdigit())
    if not digits:
        return ""
    return digits.zfill(5)


def _hkex_session_get():
    global _hkex_session
    if _hkex_session is None:
        _hkex_session = requests.Session()
        _hkex_session.headers.update(HKEX_HEADERS)
        try:
            # Prefer ZH landing — prefix.do is more reliable afterwards
            _hkex_session.get(
                "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=zh",
                timeout=25,
            )
        except Exception:
            pass
    return _hkex_session


def resolve_hkex_stock_id(hk_code):
    """Map 5-digit HK code -> disclosure stockId via prefix.do."""
    code = normalize_hk_code(hk_code)
    if not code:
        return None
    if code in _hkex_stock_cache:
        return _hkex_stock_cache[code]
    sess = _hkex_session_get()
    try:
        # lang=E often returns empty body; ZH is reliable for prefix lookup
        resp = sess.get(
            "https://www1.hkexnews.hk/search/prefix.do",
            params={"lang": "ZH", "callback": "callback", "type": "A", "name": code},
            timeout=20,
        )
        text = (resp.content or b"").decode("utf-8", errors="replace").strip()
        if not text:
            resp = sess.get(
                "https://www1.hkexnews.hk/search/prefix.do",
                params={"lang": "E", "callback": "callback", "type": "A", "name": code},
                timeout=20,
            )
            text = (resp.content or b"").decode("utf-8", errors="replace").strip()
        # callback({...});
        start = text.find("(")
        end = text.rfind(")")
        if start < 0 or end <= start:
            raise ValueError("unexpected prefix payload")
        data = json.loads(text[start + 1:end])
        for row in data.get("stockInfo") or []:
            if normalize_hk_code(row.get("code")) == code:
                sid = row.get("stockId")
                if sid is not None:
                    _hkex_stock_cache[code] = int(sid)
                    return _hkex_stock_cache[code]
        rows = data.get("stockInfo") or []
        if rows and rows[0].get("stockId") is not None:
            _hkex_stock_cache[code] = int(rows[0]["stockId"])
            return _hkex_stock_cache[code]
    except Exception as e:
        print(f"[filings] HKEX prefix {code}: {type(e).__name__}")
    _hkex_stock_cache[code] = None
    return None


def _parse_hkex_datetime(s):
    # e.g. 25/08/2026 16:53
    if not s:
        return None
    for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            return datetime.strptime(s.strip()[:16], fmt)
        except ValueError:
            continue
    return None


def fetch_hkex_for_company(company, lookback_days=400, max_items=12):
    """Return article-shaped dicts from HKEX 披露易 (PDF/HTML filings)."""
    code = normalize_hk_code(company.get("hk_code") or "")
    if not code:
        return []
    stock_id = resolve_hkex_stock_id(code)
    if not stock_id:
        print(f"[filings] HKEX no stockId for {code}")
        return []

    sess = _hkex_session_get()
    to_d = datetime.utcnow()
    fr_d = to_d - timedelta(days=lookback_days)
    fr = fr_d.strftime("%Y%m%d")
    to = to_d.strftime("%Y%m%d")

    seen = set()
    collected = []
    for q in HKEX_SEARCH_QUERIES:
        params = {
            "lang": "E",
            "category": "0",
            "market": "SEHK",
            "searchType": "1",
            "documentType": "-1",
            "t1code": q["t1code"],
            "t2Gcode": "-2",
            "t2code": q["t2code"],
            "stockId": str(stock_id),
            "from": fr,
            "to": to,
            "title": "",
            "rowRange": "50",
        }
        try:
            resp = sess.get(
                "https://www1.hkexnews.hk/search/titleSearchServlet.do",
                params=params,
                timeout=30,
            )
            if resp.status_code != 200:
                continue
            rows = json.loads((resp.json() or {}).get("result") or "[]")
        except Exception as e:
            print(f"[filings] HKEX {company.get('label')} {q['label']}: {type(e).__name__}")
            continue

        for row in rows:
            link_path = (row.get("FILE_LINK") or "").strip()
            if not link_path:
                continue
            link = (
                link_path
                if link_path.startswith("http")
                else f"https://www1.hkexnews.hk{link_path}"
            )
            if link in seen:
                continue
            fdate = _parse_hkex_datetime(row.get("DATE_TIME") or "")
            if not fdate or fdate < fr_d:
                continue
            seen.add(link)
            title = (row.get("TITLE") or "").strip() or f"{company['label']} {q['label']}"
            filing_type = q["label"]
            upper = title.upper()
            if "ANNUAL" in upper or "年報" in title or "年报" in title:
                filing_type = "年报"
            elif "INTERIM" in upper or "中期" in title or "半年" in title:
                filing_type = "中期报告" if "REPORT" in upper or "報告" in title or "报告" in title else "中期业绩"
            elif "QUARTER" in upper or "季度" in title:
                filing_type = "季报" if "REPORT" in upper or "報告" in title else "季度业绩"
            elif "PROFIT WARNING" in upper or "盈利警告" in title:
                filing_type = "盈利警告"
            elif "RESULT" in upper or "業績" in title or "业绩" in title:
                filing_type = "业绩公告"

            pub_iso = fdate.strftime("%Y-%m-%dT%H:%M:%S")
            collected.append({
                "title": f"{company['label']} ({code}) {title}",
                "link": link,
                "published_raw": row.get("DATE_TIME") or "",
                "published": f"{fdate.year}年{fdate.month:02d}月{fdate.day:02d}日",
                "published_timestamp": pub_iso,
                "source": "HKEX News",
                "source_cn": "披露易·官方披露",
                "icon": "https://www.hkex.com.hk/favicon.ico",
                "category": "财报",
                "source_type": "earnings",
                "source_type_label": "财报",
                "domain": "industry",
                "domain_label": "产业",
                "country": "中国",
                "priority": 1,
                "description": f"港交所披露易 {filing_type} · {row.get('FILE_TYPE') or 'DOC'}",
                "link_kind": "official",
                "filing_type": filing_type,
                "company_id": company["id"],
                "_sort": fdate,
            })
        time.sleep(0.05)

    collected.sort(key=lambda x: x.get("_sort") or datetime.min, reverse=True)
    out = []
    for row in collected[:max_items]:
        row.pop("_sort", None)
        out.append(row)
    return out


def fetch_all_official_filings(delay_sec=0.15):
    """Fetch EDGAR + cninfo + HKEX for watchlist companies. Returns article list."""
    articles = []
    companies = earnings.companies_with_filings()
    print(f"[filings] 拉取官方披露：{len(companies)} 家公司")
    for co in companies:
        batch = []
        if co.get("cik"):
            batch.extend(fetch_edgar_for_company(co))
            time.sleep(delay_sec)  # SEC fair-access courtesy
        if co.get("cn_code") or (co.get("market") == "cn" and co.get("ticker")):
            batch.extend(fetch_cninfo_for_company(co))
            time.sleep(0.05)
        if co.get("hk_code"):
            batch.extend(fetch_hkex_for_company(co))
            time.sleep(0.08)
        articles.extend(batch)
        if batch:
            try:
                print(f"  {co['label']}: +{len(batch)}")
            except UnicodeEncodeError:
                print(f"  company: +{len(batch)}")
    print(f"[filings] 合计 {len(articles)} 条官方披露")
    return articles
