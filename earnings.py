# earnings.py — company tagging + calendar grouping for earnings articles
import re
from collections import defaultdict

# 长关键词优先匹配（按长度降序）
COMPANY_LEXICON = [
    {"id": "alphabet", "label": "Alphabet", "patterns": ["Alphabet", "Google", "GOOGL", "GOOG", "谷歌"]},
    {"id": "microsoft", "label": "Microsoft", "patterns": ["Microsoft", "MSFT", "微软", "Azure"]},
    {"id": "nvidia", "label": "NVIDIA", "patterns": ["NVIDIA", "Nvidia", "NVDA", "英伟达"]},
    {"id": "amazon", "label": "Amazon", "patterns": ["Amazon", "AMZN", "亚马逊", "AWS"]},
    {"id": "meta", "label": "Meta", "patterns": ["Meta Platforms", "Meta ", "Facebook", "META"]},
    {"id": "apple", "label": "Apple", "patterns": ["Apple", "AAPL", "苹果"]},
    {"id": "tesla", "label": "Tesla", "patterns": ["Tesla", "TSLA", "特斯拉"]},
    {"id": "tsmc", "label": "TSMC", "patterns": ["TSMC", "Taiwan Semiconductor", "台积电"]},
    {"id": "asml", "label": "ASML", "patterns": ["ASML"]},
    {"id": "broadcom", "label": "Broadcom", "patterns": ["Broadcom", "AVGO", "博通"]},
    {"id": "amd", "label": "AMD", "patterns": ["AMD", "Advanced Micro Devices"]},
    {"id": "intel", "label": "Intel", "patterns": ["Intel", "INTC", "英特尔"]},
    {"id": "qualcomm", "label": "Qualcomm", "patterns": ["Qualcomm", "QCOM", "高通"]},
    {"id": "samsung", "label": "Samsung", "patterns": ["Samsung", "三星"]},
    {"id": "micron", "label": "Micron", "patterns": ["Micron", "MU", "美光"]},
    {"id": "arm", "label": "ARM", "patterns": ["Arm Holdings", "ARM Ltd", " ARM "]},
    {"id": "applied", "label": "Applied Materials", "patterns": ["Applied Materials", "AMAT"]},
    {"id": "ti", "label": "Texas Instruments", "patterns": ["Texas Instruments", "TXN"]},
    {"id": "netflix", "label": "Netflix", "patterns": ["Netflix", "NFLX"]},
    {"id": "uber", "label": "Uber", "patterns": ["Uber", "UBER"]},
    {"id": "airbnb", "label": "Airbnb", "patterns": ["Airbnb", "ABNB"]},
    {"id": "spotify", "label": "Spotify", "patterns": ["Spotify", "SPOT"]},
    {"id": "snap", "label": "Snap", "patterns": ["Snap Inc", "Snapchat", "SNAP"]},
    {"id": "shopify", "label": "Shopify", "patterns": ["Shopify", "SHOP"]},
    {"id": "paypal", "label": "PayPal", "patterns": ["PayPal", "PYPL"]},
    {"id": "oracle", "label": "Oracle", "patterns": ["Oracle", "ORCL", "甲骨文"]},
    {"id": "adobe", "label": "Adobe", "patterns": ["Adobe", "ADBE"]},
    {"id": "snowflake", "label": "Snowflake", "patterns": ["Snowflake", "SNOW"]},
    {"id": "palantir", "label": "Palantir", "patterns": ["Palantir", "PLTR"]},
    {"id": "cloudflare", "label": "Cloudflare", "patterns": ["Cloudflare", "NET"]},
    {"id": "servicenow", "label": "ServiceNow", "patterns": ["ServiceNow", "NOW"]},
    {"id": "openai", "label": "OpenAI", "patterns": ["OpenAI"]},
    {"id": "anthropic", "label": "Anthropic", "patterns": ["Anthropic", "Claude"]},
    {"id": "tencent", "label": "腾讯", "patterns": ["Tencent", "腾讯", "0700"]},
    {"id": "alibaba", "label": "阿里巴巴", "patterns": ["Alibaba", "BABA", "阿里巴巴", "阿里"]},
    {"id": "pdd", "label": "拼多多", "patterns": ["Pinduoduo", "PDD", "拼多多"]},
    {"id": "meituan", "label": "美团", "patterns": ["Meituan", "美团"]},
    {"id": "jd", "label": "京东", "patterns": ["JD.com", "京东", "JD "]},
    {"id": "baidu", "label": "百度", "patterns": ["Baidu", "百度", "BIDU"]},
    {"id": "netease", "label": "网易", "patterns": ["NetEase", "网易", "NTES"]},
    {"id": "xiaomi", "label": "小米", "patterns": ["Xiaomi", "小米"]},
    {"id": "bilibili", "label": "哔哩哔哩", "patterns": ["Bilibili", "哔哩哔哩", "B站"]},
    {"id": "smic", "label": "中芯国际", "patterns": ["SMIC", "中芯国际"]},
    {"id": "huawei", "label": "华为", "patterns": ["Huawei", "华为"]},
    {"id": "cambricon", "label": "寒武纪", "patterns": ["Cambricon", "寒武纪"]},
    {"id": "haiguang", "label": "海光", "patterns": ["海光"]},
]


def _compile_patterns():
    compiled = []
    for co in COMPANY_LEXICON:
        pats = sorted(co["patterns"], key=len, reverse=True)
        regs = [re.compile(re.escape(p), re.I) for p in pats]
        compiled.append({**co, "_regs": regs})
    return compiled


_COMPILED = _compile_patterns()


def detect_company(title):
    """Return {id, label} if title mentions a known company, else None."""
    if not title:
        return None
    for co in _COMPILED:
        for reg in co["_regs"]:
            if reg.search(title):
                return {"id": co["id"], "label": co["label"]}
    return None


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


def build_calendar(articles):
    """Group earnings articles by date, attach company tags."""
    by_date = defaultdict(list)
    company_counts = defaultdict(int)
    for art in articles:
        co = detect_company(art.get("title", ""))
        item = {
            "title": art.get("title"),
            "link": art.get("link"),
            "source": art.get("source"),
            "source_cn": art.get("source_cn"),
            "published": art.get("published"),
            "published_timestamp": art.get("published_timestamp"),
            "company": co["label"] if co else None,
            "company_id": co["id"] if co else None,
            "country": art.get("country"),
            "icon": art.get("icon"),
        }
        if co:
            company_counts[co["label"]] += 1
        by_date[article_date_key(art)].append(item)

    days = []
    for date in sorted(by_date.keys(), reverse=True):
        items = by_date[date]
        # 有公司名的排前面
        items.sort(key=lambda x: (0 if x.get("company") else 1, x.get("title") or ""))
        days.append({"date": date, "count": len(items), "items": items})

    companies = [
        {"label": k, "count": v}
        for k, v in sorted(company_counts.items(), key=lambda x: (-x[1], x[0]))
    ]
    return {
        "days": days,
        "total": sum(d["count"] for d in days),
        "companies": companies,
    }
