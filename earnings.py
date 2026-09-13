# earnings.py — company tagging, link classification, calendar grouping
import re
from collections import defaultdict
from datetime import datetime
from urllib.parse import urlparse

# 长关键词优先匹配（按长度降序编译）
# market: us | cn | hk | private
# cik: SEC CIK（无前导零亦可，拉取时再 pad）
# cn_code: A 股六位代码（巨潮）
COMPANY_LEXICON = [
    {
        "id": "alphabet", "label": "Alphabet", "ticker": "GOOGL", "cik": "1652044",
        "market": "us", "patterns": ["Alphabet", "Google", "GOOGL", "GOOG", "谷歌"],
        "ir_url": "https://abc.xyz/investor/",
    },
    {
        "id": "microsoft", "label": "Microsoft", "ticker": "MSFT", "cik": "789019",
        "market": "us", "patterns": ["Microsoft", "MSFT", "微软", "Azure"],
        "ir_url": "https://www.microsoft.com/en-us/investor",
    },
    {
        "id": "nvidia", "label": "NVIDIA", "ticker": "NVDA", "cik": "1045810",
        "market": "us", "patterns": ["NVIDIA", "Nvidia", "NVDA", "英伟达"],
        "ir_url": "https://investor.nvidia.com/",
    },
    {
        "id": "amazon", "label": "Amazon", "ticker": "AMZN", "cik": "1018724",
        "market": "us", "patterns": ["Amazon", "AMZN", "亚马逊", "AWS"],
        "ir_url": "https://ir.aboutamazon.com/",
    },
    {
        "id": "meta", "label": "Meta", "ticker": "META", "cik": "1326801",
        "market": "us", "patterns": ["Meta Platforms", "Meta ", "Facebook", "META"],
        "ir_url": "https://investor.atmeta.com/",
    },
    {
        "id": "apple", "label": "Apple", "ticker": "AAPL", "cik": "320193",
        "market": "us", "patterns": ["Apple", "AAPL", "苹果"],
        "ir_url": "https://investor.apple.com/",
    },
    {
        "id": "tesla", "label": "Tesla", "ticker": "TSLA", "cik": "1318605",
        "market": "us", "patterns": ["Tesla", "TSLA", "特斯拉"],
        "ir_url": "https://ir.tesla.com/",
    },
    {
        "id": "tsmc", "label": "TSMC", "ticker": "TSM", "cik": "1046179",
        "market": "us", "patterns": ["TSMC", "Taiwan Semiconductor", "台积电"],
        "ir_url": "https://investor.tsmc.com/",
    },
    {
        "id": "asml", "label": "ASML", "ticker": "ASML", "cik": "937966",
        "market": "us", "patterns": ["ASML"],
        "ir_url": "https://www.asml.com/en/investors",
    },
    {
        "id": "broadcom", "label": "Broadcom", "ticker": "AVGO", "cik": "1730168",
        "market": "us", "patterns": ["Broadcom", "AVGO", "博通"],
        "ir_url": "https://investors.broadcom.com/",
    },
    {
        "id": "amd", "label": "AMD", "ticker": "AMD", "cik": "2488",
        "market": "us", "patterns": ["AMD", "Advanced Micro Devices"],
        "ir_url": "https://ir.amd.com/",
    },
    {
        "id": "intel", "label": "Intel", "ticker": "INTC", "cik": "50863",
        "market": "us", "patterns": ["Intel", "INTC", "英特尔"],
        "ir_url": "https://www.intc.com/",
    },
    {
        "id": "qualcomm", "label": "Qualcomm", "ticker": "QCOM", "cik": "804328",
        "market": "us", "patterns": ["Qualcomm", "QCOM", "高通"],
        "ir_url": "https://investor.qualcomm.com/",
    },
    {
        "id": "samsung", "label": "Samsung", "ticker": "005930.KS", "cik": None,
        "market": "kr", "patterns": ["Samsung", "三星"],
        "ir_url": "https://www.samsung.com/global/ir/",
    },
    {
        "id": "micron", "label": "Micron", "ticker": "MU", "cik": "723125",
        "market": "us", "patterns": ["Micron", "MU", "美光"],
        "ir_url": "https://investors.micron.com/",
    },
    {
        "id": "arm", "label": "ARM", "ticker": "ARM", "cik": "1973239",
        "market": "us", "patterns": ["Arm Holdings", "ARM Ltd", " ARM "],
        "ir_url": "https://investors.arm.com/",
    },
    {
        "id": "applied", "label": "Applied Materials", "ticker": "AMAT", "cik": "6951",
        "market": "us", "patterns": ["Applied Materials", "AMAT"],
        "ir_url": "https://ir.appliedmaterials.com/",
    },
    {
        "id": "ti", "label": "Texas Instruments", "ticker": "TXN", "cik": "97476",
        "market": "us", "patterns": ["Texas Instruments", "TXN"],
        "ir_url": "https://investor.ti.com/",
    },
    {
        "id": "netflix", "label": "Netflix", "ticker": "NFLX", "cik": "1065280",
        "market": "us", "patterns": ["Netflix", "NFLX"],
        "ir_url": "https://ir.netflix.net/",
    },
    {
        "id": "uber", "label": "Uber", "ticker": "UBER", "cik": "1543151",
        "market": "us", "patterns": ["Uber", "UBER"],
        "ir_url": "https://investor.uber.com/",
    },
    {
        "id": "airbnb", "label": "Airbnb", "ticker": "ABNB", "cik": "1559720",
        "market": "us", "patterns": ["Airbnb", "ABNB"],
        "ir_url": "https://investors.airbnb.com/",
    },
    {
        "id": "spotify", "label": "Spotify", "ticker": "SPOT", "cik": "1639920",
        "market": "us", "patterns": ["Spotify", "SPOT"],
        "ir_url": "https://investors.spotify.com/",
    },
    {
        "id": "snap", "label": "Snap", "ticker": "SNAP", "cik": "1564408",
        "market": "us", "patterns": ["Snap Inc", "Snapchat", "SNAP"],
        "ir_url": "https://investor.snap.com/",
    },
    {
        "id": "shopify", "label": "Shopify", "ticker": "SHOP", "cik": "1594805",
        "market": "us", "patterns": ["Shopify", "SHOP"],
        "ir_url": "https://investors.shopify.com/",
    },
    {
        "id": "paypal", "label": "PayPal", "ticker": "PYPL", "cik": "1633917",
        "market": "us", "patterns": ["PayPal", "PYPL"],
        "ir_url": "https://investor.pypl.com/",
    },
    {
        "id": "oracle", "label": "Oracle", "ticker": "ORCL", "cik": "1341439",
        "market": "us", "patterns": ["Oracle", "ORCL", "甲骨文"],
        "ir_url": "https://investor.oracle.com/",
    },
    {
        "id": "adobe", "label": "Adobe", "ticker": "ADBE", "cik": "796343",
        "market": "us", "patterns": ["Adobe", "ADBE"],
        "ir_url": "https://www.adobe.com/investor-relations.html",
    },
    {
        "id": "snowflake", "label": "Snowflake", "ticker": "SNOW", "cik": "1640147",
        "market": "us", "patterns": ["Snowflake", "SNOW"],
        "ir_url": "https://investors.snowflake.com/",
    },
    {
        "id": "palantir", "label": "Palantir", "ticker": "PLTR", "cik": "1321655",
        "market": "us", "patterns": ["Palantir", "PLTR"],
        "ir_url": "https://investors.palantir.com/",
    },
    {
        "id": "cloudflare", "label": "Cloudflare", "ticker": "NET", "cik": "1477333",
        "market": "us", "patterns": ["Cloudflare", "NET"],
        "ir_url": "https://cloudflare.net/",
    },
    {
        "id": "servicenow", "label": "ServiceNow", "ticker": "NOW", "cik": "1373715",
        "market": "us", "patterns": ["ServiceNow", "NOW"],
        "ir_url": "https://www.servicenow.com/company/investor-relations.html",
    },
    {
        "id": "openai", "label": "OpenAI", "ticker": None, "cik": None,
        "market": "private", "patterns": ["OpenAI"],
        "ir_url": "https://openai.com/",
    },
    {
        "id": "anthropic", "label": "Anthropic", "ticker": None, "cik": None,
        "market": "private", "patterns": ["Anthropic", "Claude"],
        "ir_url": "https://www.anthropic.com/",
    },
    {
        "id": "tencent", "label": "腾讯", "ticker": "0700.HK", "cik": "1293451",
        "market": "hk", "hk_code": "00700",
        "patterns": ["Tencent", "腾讯", "0700"],
        "ir_url": "https://www.tencent.com/en-us/investors.html",
    },
    {
        "id": "alibaba", "label": "阿里巴巴", "ticker": "BABA", "cik": "1577552",
        "market": "us", "hk_code": "09988",
        "patterns": ["Alibaba", "BABA", "阿里巴巴", "阿里"],
        "ir_url": "https://www.alibabagroup.com/en/ir",
    },
    {
        "id": "pdd", "label": "拼多多", "ticker": "PDD", "cik": "1808620",
        "market": "us",
        "patterns": ["Pinduoduo", "PDD", "拼多多"],
        "ir_url": "https://investor.pddholdings.com/",
    },
    {
        "id": "meituan", "label": "美团", "ticker": "3690.HK", "cik": None,
        "market": "hk", "hk_code": "03690",
        "patterns": ["Meituan", "美团"],
        "ir_url": "https://www.meituan.com/investor-relations",
    },
    {
        "id": "jd", "label": "京东", "ticker": "JD", "cik": "1540950",
        "market": "us", "hk_code": "09618",
        "patterns": ["JD.com", "京东", "JD "],
        "ir_url": "https://ir.jd.com/",
    },
    {
        "id": "baidu", "label": "百度", "ticker": "BIDU", "cik": "1329099",
        "market": "us", "hk_code": "09888",
        "patterns": ["Baidu", "百度", "BIDU"],
        "ir_url": "https://ir.baidu.com/",
    },
    {
        "id": "netease", "label": "网易", "ticker": "NTES", "cik": "1110646",
        "market": "us", "hk_code": "09999",
        "patterns": ["NetEase", "网易", "NTES"],
        "ir_url": "https://ir.netease.com/",
    },
    {
        "id": "xiaomi", "label": "小米", "ticker": "1810.HK", "cik": None,
        "market": "hk", "hk_code": "01810",
        "patterns": ["Xiaomi", "小米"],
        "ir_url": "https://ir.mi.com/",
    },
    {
        "id": "bilibili", "label": "哔哩哔哩", "ticker": "BILI", "cik": "1723690",
        "market": "us", "hk_code": "09626",
        "patterns": ["Bilibili", "哔哩哔哩", "B站"],
        "ir_url": "https://ir.bilibili.com/",
    },
    {
        "id": "kuaishou", "label": "快手", "ticker": "1024.HK", "cik": None,
        "market": "hk", "hk_code": "01024",
        "patterns": ["Kuaishou", "快手"],
        "ir_url": "https://ir.kuaishou.com/",
    },
    {
        "id": "li_auto", "label": "理想汽车", "ticker": "LI", "cik": "1791706",
        "market": "us", "hk_code": "02015",
        "patterns": ["Li Auto", "理想汽车"],
        "ir_url": "https://ir.lixiang.com/",
    },
    {
        "id": "xpeng", "label": "小鹏汽车", "ticker": "XPEV", "cik": "1810997",
        "market": "us", "hk_code": "09868",
        "patterns": ["XPeng", "小鹏"],
        "ir_url": "https://ir.xiaopeng.com/",
    },
    {
        "id": "smic", "label": "中芯国际", "ticker": "688981", "cik": None,
        "market": "cn", "cn_code": "688981", "hk_code": "00981",
        "patterns": ["SMIC", "中芯国际"],
        "ir_url": "https://www.smics.com/en/site/company_financial",
    },
    {
        "id": "huawei", "label": "华为", "ticker": None, "cik": None,
        "market": "private", "patterns": ["Huawei", "华为"],
        "ir_url": "https://www.huawei.com/cn/investors",
    },
    {
        "id": "cambricon", "label": "寒武纪", "ticker": "688256", "cik": None,
        "market": "cn", "cn_code": "688256",
        "patterns": ["Cambricon", "寒武纪"],
    },
    {
        "id": "haiguang", "label": "海光", "ticker": "688041", "cik": None,
        "market": "cn", "cn_code": "688041",
        "patterns": ["海光"],
    },
    {
        "id": "naura", "label": "北方华创", "ticker": "002371", "cik": None,
        "market": "cn", "cn_code": "002371",
        "patterns": ["NAURA", "北方华创"],
    },
    {
        "id": "will_semi", "label": "韦尔股份", "ticker": "603501", "cik": None,
        "market": "cn", "cn_code": "603501",
        "patterns": ["Will Semiconductor", "韦尔股份", "韦尔"],
    },
    {
        "id": "jcet", "label": "长电科技", "ticker": "600584", "cik": None,
        "market": "cn", "cn_code": "600584",
        "patterns": ["JCET", "长电科技"],
    },
    {
        "id": "montage", "label": "澜起科技", "ticker": "688008", "cik": None,
        "market": "cn", "cn_code": "688008",
        "patterns": ["Montage", "澜起科技", "澜起"],
    },
    {
        "id": "amec", "label": "中微公司", "ticker": "688012", "cik": None,
        "market": "cn", "cn_code": "688012",
        "patterns": ["AMEC", "中微公司", "中微"],
    },
    {
        "id": "gigadevice", "label": "兆易创新", "ticker": "603986", "cik": None,
        "market": "cn", "cn_code": "603986",
        "patterns": ["GigaDevice", "兆易创新", "兆易"],
    },
    {
        "id": "kingsoft_office", "label": "金山办公", "ticker": "688111", "cik": None,
        "market": "cn", "cn_code": "688111",
        "patterns": ["Kingsoft Office", "金山办公", "WPS"],
    },
    {
        "id": "iflytek", "label": "科大讯飞", "ticker": "002230", "cik": None,
        "market": "cn", "cn_code": "002230",
        "patterns": ["iFlytek", "科大讯飞", "讯飞"],
    },
    {
        "id": "catl", "label": "宁德时代", "ticker": "300750", "cik": None,
        "market": "cn", "cn_code": "300750",
        "patterns": ["CATL", "宁德时代"],
    },
    {
        "id": "byd", "label": "比亚迪", "ticker": "002594", "cik": None,
        "market": "cn", "cn_code": "002594", "hk_code": "01211",
        "patterns": ["BYD", "比亚迪"],
    },
    {
        "id": "luxshare", "label": "立讯精密", "ticker": "002475", "cik": None,
        "market": "cn", "cn_code": "002475",
        "patterns": ["Luxshare", "立讯精密", "立讯"],
    },
    {
        "id": "foxconn_ind", "label": "工业富联", "ticker": "601138", "cik": None,
        "market": "cn", "cn_code": "601138",
        "patterns": ["工业富联", "富士康工业互联网"],
    },
    {
        "id": "horizon", "label": "地平线", "ticker": "9660.HK", "cik": None,
        "market": "hk", "hk_code": "09660",
        "patterns": ["Horizon Robotics", "地平线"],
    },
]

LINK_KIND_LABELS = {
    "official": "官方披露",
    "transcript": "电话会",
    "media": "报道",
}

LINK_KIND_RANK = {"official": 0, "transcript": 1, "media": 2}

_OFFICIAL_HOSTS = (
    "sec.gov",
    "cninfo.com.cn",
    "static.cninfo.com.cn",
    "sse.com.cn",
    "szse.cn",
    "hkexnews.hk",
    "hkex.com.hk",
)

_TRANSCRIPT_HOSTS = (
    "seekingalpha.com",
)


def _compile_patterns():
    compiled = []
    for co in COMPANY_LEXICON:
        pats = sorted(co["patterns"], key=len, reverse=True)
        regs = [re.compile(re.escape(p), re.I) for p in pats]
        compiled.append({**co, "_regs": regs})
    return compiled


_COMPILED = _compile_patterns()
_BY_ID = {c["id"]: c for c in COMPANY_LEXICON}


def get_company(company_id):
    return _BY_ID.get(company_id)


def companies_with_filings():
    """Companies that can be resolved to EDGAR / cninfo / HKEX."""
    out = []
    for c in COMPANY_LEXICON:
        if c.get("cik") or c.get("cn_code") or c.get("hk_code"):
            out.append(c)
    return out


def detect_company(title):
    """Return {id, label, ...} if title mentions a known company, else None."""
    if not title:
        return None
    for co in _COMPILED:
        for reg in co["_regs"]:
            if reg.search(title):
                return {
                    "id": co["id"],
                    "label": co["label"],
                    "ticker": co.get("ticker"),
                    "cik": co.get("cik"),
                    "market": co.get("market"),
                    "ir_url": co.get("ir_url"),
                    "cn_code": co.get("cn_code"),
                    "hk_code": co.get("hk_code"),
                }
    return None


def classify_link(link, source="", filing_type=None):
    """Classify a URL into official / transcript / media."""
    if filing_type and str(filing_type).strip():
        return "official"
    host = ""
    try:
        host = (urlparse(link or "").netloc or "").lower()
        if host.startswith("www."):
            host = host[4:]
    except Exception:
        host = ""
    src = (source or "").lower()
    if any(host == h or host.endswith("." + h) for h in _OFFICIAL_HOSTS):
        return "official"
    if "sec.gov" in (link or "").lower() or "cninfo.com.cn" in (link or "").lower():
        return "official"
    if "hkexnews.hk" in (link or "").lower() or "hkex.com.hk" in (link or "").lower():
        return "official"
    if any(host == h or host.endswith("." + h) for h in _TRANSCRIPT_HOSTS):
        return "transcript"
    if "transcript" in src or "seeking alpha" in src or "seekingalpha" in src:
        return "transcript"
    if host.endswith("investor.") or "/investor" in (link or "").lower():
        # company IR pages — treat as official-ish
        if any(k in (link or "").lower() for k in (
            "sec.gov", "10-k", "10-q", "earnings", "financial", "quarterly", "annual"
        )):
            return "official"
    return "media"


def link_kind_label(kind):
    return LINK_KIND_LABELS.get(kind or "media", "报道")


def article_date_key(article):
    """YYYY-MM-DD from published_timestamp / published / fetched."""
    ts = article.get("published_timestamp") or ""
    if ts and len(ts) >= 10:
        return ts[:10]
    pub = article.get("published") or ""
    m = re.search(r"(\d{4}-\d{2}-\d{2})", pub)
    if m:
        return m.group(1)
    return "未知"


def enrich_article_meta(art):
    """Ensure link_kind / company fields; classify from link if missing."""
    kind = (art.get("link_kind") or "").strip()
    if not kind:
        kind = classify_link(
            art.get("link"),
            source=art.get("source") or "",
            filing_type=art.get("filing_type"),
        )
    co = None
    cid = art.get("company_id")
    if cid and cid in _BY_ID:
        base = _BY_ID[cid]
        co = {
            "id": base["id"],
            "label": base["label"],
            "ticker": base.get("ticker"),
            "ir_url": base.get("ir_url"),
        }
    elif not cid:
        co = detect_company(art.get("title", ""))
    return kind, co


def _parse_item_date(item):
    key = item.get("_date") or article_date_key(item)
    try:
        return datetime.strptime(key[:10], "%Y-%m-%d")
    except ValueError:
        return None


def infer_period_key(item):
    """Rough fiscal-period bucket for clustering (e.g. 2026Q2 / 2026FY / date)."""
    title = item.get("title") or ""
    filing = (item.get("filing_type") or "").upper()
    text = f"{title} {filing}"

    m = re.search(r"报告期\s*(\d{4})-(\d{2})", title)
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
        return f"{y}Q{(mo - 1) // 3 + 1}"

    m = re.search(r"\b(20\d{2})\s*[年\-/]?\s*Q([1-4])\b", text, re.I)
    if m:
        return f"{m.group(1)}Q{m.group(2)}"
    m = re.search(r"\bQ([1-4])\s*[FY/\s']*(20\d{2})\b", text, re.I)
    if m:
        return f"{m.group(2)}Q{m.group(1)}"

    y_m = re.search(r"(20\d{2})", text)
    year = y_m.group(1) if y_m else None
    if year:
        if any(k in text for k in ("10-K", "20-F", "年报", "年度报告", "Annual Report", "FY")):
            return f"{year}FY"
        if any(k in text for k in ("半年报", "半年度", "中期", "Interim", "H1", "1H")):
            return f"{year}H1"
        if any(k in text for k in ("一季", "Q1", "1Q")):
            return f"{year}Q1"
        if any(k in text for k in ("三季", "Q3", "3Q")):
            return f"{year}Q3"
        if any(k in text for k in ("二季", "Q2", "2Q", "10-Q")):
            # 10-Q alone: use report month if present else date quarter
            pass

    dt = _parse_item_date(item)
    if dt:
        return f"{dt.year}Q{(dt.month - 1) // 3 + 1}"
    return item.get("_date") or "未知"


def _item_to_public(item):
    out = {k: v for k, v in item.items() if not k.startswith("_")}
    return out


def _cluster_company_items(items, window_days=14):
    """Greedy cluster same-company items by period key + date proximity."""
    scored = []
    for it in items:
        dt = _parse_item_date(it)
        scored.append((dt or datetime.min, it))
    scored.sort(key=lambda x: x[0], reverse=True)

    clusters = []  # list of {period, items, anchor_dt}
    for dt, it in scored:
        period = infer_period_key(it)
        placed = False
        for cl in clusters:
            same_period = cl["period"] == period and period != "未知"
            near = False
            if dt and cl.get("anchor_dt"):
                near = abs((dt - cl["anchor_dt"]).days) <= window_days
            if same_period or near:
                cl["items"].append(it)
                # keep earliest as secondary anchors; prefer official for anchor_dt
                if it.get("link_kind") == "official" and dt:
                    if (not cl.get("anchor_dt")) or dt > cl["anchor_dt"]:
                        # keep the latest official as display anchor
                        cl["anchor_dt"] = dt
                placed = True
                break
        if not placed:
            clusters.append({
                "period": period,
                "items": [it],
                "anchor_dt": dt,
            })
    return clusters


def _pick_primary(items):
    ranked = sorted(
        items,
        key=lambda x: (
            LINK_KIND_RANK.get(x.get("link_kind") or "media", 9),
            0 if x.get("filing_type") else 1,
            x.get("published_timestamp") or "",
        ),
    )
    return ranked[0]


def build_events_from_items(enriched, kind_filter="all", window_days=14):
    """Collapse enriched items into company earnings events."""
    by_company = defaultdict(list)
    orphans = []
    for it in enriched:
        cid = it.get("company_id")
        if cid:
            by_company[cid].append(it)
        else:
            orphans.append(it)

    events = []
    for cid, items in by_company.items():
        for cl in _cluster_company_items(items, window_days=window_days):
            members = cl["items"]
            kinds = {m.get("link_kind") or "media" for m in members}
            if kind_filter and kind_filter not in ("", "all"):
                if kind_filter not in kinds:
                    continue
            primary = _pick_primary(members)
            # If filtering to a kind, prefer a primary of that kind when available
            if kind_filter and kind_filter not in ("", "all"):
                typed = [m for m in members if m.get("link_kind") == kind_filter]
                if typed:
                    primary = _pick_primary(typed)
            related = [
                _item_to_public(m)
                for m in sorted(
                    members,
                    key=lambda x: (
                        LINK_KIND_RANK.get(x.get("link_kind") or "media", 9),
                        x.get("published_timestamp") or "",
                    ),
                )
                if (m.get("link") or "") != (primary.get("link") or "")
            ]
            counts = defaultdict(int)
            for m in members:
                counts[m.get("link_kind") or "media"] += 1
            event = _item_to_public(primary)
            event.update({
                "is_event": True,
                "period_key": cl["period"],
                "related": related,
                "related_counts": {
                    "official": counts.get("official", 0),
                    "transcript": counts.get("transcript", 0),
                    "media": counts.get("media", 0),
                    "total": len(members),
                },
                "cluster_size": len(members),
            })
            events.append(event)

    # orphans stay as single-item events (optionally filtered)
    for it in orphans:
        kind = it.get("link_kind") or "media"
        if kind_filter and kind_filter not in ("", "all") and kind != kind_filter:
            continue
        event = _item_to_public(it)
        event.update({
            "is_event": True,
            "period_key": infer_period_key(it),
            "related": [],
            "related_counts": {
                "official": 1 if kind == "official" else 0,
                "transcript": 1 if kind == "transcript" else 0,
                "media": 1 if kind == "media" else 0,
                "total": 1,
            },
            "cluster_size": 1,
        })
        events.append(event)

    return events


def build_calendar(articles, kind_filter="all", aggregate=True, window_days=14):
    """Group earnings articles by date.

    aggregate=True (default): company earnings events with related coverage.
    aggregate=False: flat item list (legacy).
    """
    company_counts = defaultdict(int)
    kind_counts = defaultdict(int)

    enriched = []
    for art in articles:
        kind, co = enrich_article_meta(art)
        kind_counts[kind] += 1
        ir_url = (co or {}).get("ir_url") or art.get("ir_url") or ""
        item = {
            "title": art.get("title"),
            "link": art.get("link"),
            "source": art.get("source"),
            "source_cn": art.get("source_cn"),
            "published": art.get("published"),
            "published_timestamp": art.get("published_timestamp"),
            "description": art.get("description") or "",
            "company": co["label"] if co else None,
            "company_id": co["id"] if co else None,
            "country": art.get("country"),
            "icon": art.get("icon"),
            "link_kind": kind,
            "link_kind_label": link_kind_label(kind),
            "filing_type": art.get("filing_type") or "",
            "ir_url": ir_url,
            "_date": article_date_key(art),
        }
        enriched.append(item)

    if aggregate:
        events = build_events_from_items(
            enriched, kind_filter=kind_filter, window_days=window_days
        )
        by_date = defaultdict(list)
        for ev in events:
            date_key = article_date_key(ev)
            if ev.get("company"):
                company_counts[ev["company"]] += 1
            by_date[date_key].append(ev)
        days = []
        for date in sorted(by_date.keys(), reverse=True):
            items = by_date[date]
            items.sort(
                key=lambda x: (
                    LINK_KIND_RANK.get(x.get("link_kind") or "media", 9),
                    0 if x.get("company") else 1,
                    -(x.get("cluster_size") or 1),
                    x.get("title") or "",
                )
            )
            days.append({"date": date, "count": len(items), "items": items})
        return {
            "days": days,
            "total": sum(d["count"] for d in days),
            "companies": [
                {"label": k, "count": v}
                for k, v in sorted(company_counts.items(), key=lambda x: (-x[1], x[0]))
            ],
            "kind_counts": {
                "official": kind_counts.get("official", 0),
                "transcript": kind_counts.get("transcript", 0),
                "media": kind_counts.get("media", 0),
            },
            "aggregate": True,
            "event_count": sum(d["count"] for d in days),
        }

    by_date = defaultdict(list)
    for item in enriched:
        if kind_filter and kind_filter not in ("", "all"):
            if item.get("link_kind") != kind_filter:
                continue
        if item.get("company"):
            company_counts[item["company"]] += 1
        by_date[item["_date"]].append(item)

    days = []
    for date in sorted(by_date.keys(), reverse=True):
        items = by_date[date]
        for it in items:
            it.pop("_date", None)
        items.sort(
            key=lambda x: (
                LINK_KIND_RANK.get(x.get("link_kind") or "media", 9),
                0 if x.get("company") else 1,
                x.get("title") or "",
            )
        )
        days.append({"date": date, "count": len(items), "items": items})

    return {
        "days": days,
        "total": sum(d["count"] for d in days),
        "companies": [
            {"label": k, "count": v}
            for k, v in sorted(company_counts.items(), key=lambda x: (-x[1], x[0]))
        ],
        "kind_counts": {
            "official": kind_counts.get("official", 0),
            "transcript": kind_counts.get("transcript", 0),
            "media": kind_counts.get("media", 0),
        },
        "aggregate": False,
    }

