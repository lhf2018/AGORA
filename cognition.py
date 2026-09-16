# cognition.py — signal tiers, issue workbench, frameworks, decision briefing
"""Content-layer helpers for cognitive iteration (not raw feed plumbing)."""
from collections import defaultdict

from config import TOPIC_LEXICON, DOC_TYPE_LABELS, DOMAIN_LABELS

# ---------------------------------------------------------------------------
# Signal vs noise — reading order: fact → analysis → narrative
# ---------------------------------------------------------------------------
SIGNAL_TIERS = {
    "fact": {
        "id": "fact",
        "label": "一级事实",
        "short": "事实",
        "rank": 0,
        "hint": "官方披露、数据、政策原文——先立事实",
    },
    "analysis": {
        "id": "analysis",
        "label": "二级分析",
        "short": "分析",
        "rank": 1,
        "hint": "智库 / 研报 / 白皮书 / 论文——解释与框架",
    },
    "narrative": {
        "id": "narrative",
        "label": "三级叙事",
        "short": "叙事",
        "rank": 2,
        "hint": "媒体报道与电话会转述——叙事与情绪，后读",
    },
}

_FACT_DOC_TYPES = {"earnings", "announcement", "data", "policy"}
_ANALYSIS_DOC_TYPES = {"think_tank", "research", "whitepaper", "paper"}


def classify_signal(article):
    """Return signal tier id for an article dict."""
    doc = (article.get("source_type") or article.get("doc_type") or "").strip()
    kind = (article.get("link_kind") or "").strip()
    filing = (article.get("filing_type") or "").strip()

    if filing or kind == "official":
        return "fact"
    if doc in _FACT_DOC_TYPES:
        # earnings media reprints stay narrative unless official
        if doc == "earnings" and kind in ("media", "transcript"):
            return "narrative" if kind == "media" else "analysis"
        return "fact"
    if kind == "transcript":
        return "analysis"
    if doc in _ANALYSIS_DOC_TYPES:
        return "analysis"
    return "narrative"


def signal_meta(tier_id):
    return SIGNAL_TIERS.get(tier_id) or SIGNAL_TIERS["narrative"]


def enrich_signal(article):
    """Mutate/copy-friendly: attach signal_* fields."""
    if not article:
        return article
    tier = classify_signal(article)
    meta = signal_meta(tier)
    article["signal"] = tier
    article["signal_label"] = meta["label"]
    article["signal_short"] = meta["short"]
    article["signal_hint"] = meta["hint"]
    article["signal_rank"] = meta["rank"]
    return article


# ---------------------------------------------------------------------------
# Framework library — reusable mental models
# ---------------------------------------------------------------------------
FRAMEWORK_LEXICON = [
    {
        "id": "capacity_cycle",
        "label": "产能周期",
        "domain": "industry",
        "summary": "供给扩张 → 价格/利润压力 → 出清 → 下一轮资本开支。适用于芯片、新能源、航运等重资产赛道。",
        "questions": ["当前处在扩产还是出清？", "谁在增加/削减资本开支？", "库存与价格是否背离？"],
        "topic_ids": ["chip", "energy", "trade"],
        "patterns": ["产能", "扩产", "过剩", "库存", "资本开支", "capex", "overcapacity", "utilization"],
    },
    {
        "id": "sanctions_chain",
        "label": "制裁传导",
        "domain": "geopolitics",
        "summary": "出口管制与金融制裁如何沿供应链、替代来源与合规成本传导到产业与盟友协调。",
        "questions": ["打击的是节点还是网络？", "有无替代供应商？", "盟友执行强度如何？"],
        "topic_ids": ["sanctions", "chip", "trade"],
        "patterns": ["制裁", "出口管制", "实体清单", "sanctions", "export control", "entity list", "合规"],
    },
    {
        "id": "deterrence_stability",
        "label": "威慑与稳定",
        "domain": "geopolitics",
        "summary": "能力、意图、沟通渠道三者是否匹配；危机中误判与红线管理。",
        "questions": ["信号是能力展示还是意图变化？", "沟通渠道是否畅通？", "第三方如何站队？"],
        "topic_ids": ["taiwan", "south_china_sea", "nato", "korea", "ukraine"],
        "patterns": ["威慑", "军演", "红线", "误判", "deterrence", "military exercise", "海峡", "台海"],
    },
    {
        "id": "monetary_regime",
        "label": "货币与利率体制",
        "domain": "macro",
        "summary": "通胀路径、中性利率与金融条件：政策转向如何重定价资产与汇率。",
        "questions": ["锚定的是通胀还是金融稳定？", "实际利率方向？", "美元流动性外溢？"],
        "topic_ids": ["fed", "eu", "trade"],
        "patterns": ["降息", "加息", "通胀", "FOMC", "利率", "yield", "inflation", "monetary"],
    },
    {
        "id": "ai_compute",
        "label": "算力与模型层",
        "domain": "tech",
        "summary": "训练/推理算力、模型能力边界与应用落地之间的瓶颈迁移。",
        "questions": ["瓶颈在芯片、电力还是数据？", "开源 vs 闭源格局？", "谁在买算力？"],
        "topic_ids": ["ai", "chip", "energy"],
        "patterns": ["大模型", "算力", "GPU", "推理", "训练", "foundation model", "inference", "token"],
    },
    {
        "id": "energy_transition",
        "label": "能源转型三角",
        "domain": "energy",
        "summary": "安全、可负担、低碳三难：政策、化石与可再生之间的再平衡。",
        "questions": ["短期保供还是长期减排优先？", "谁承担转型成本？", "关键矿物与电网瓶颈？"],
        "topic_ids": ["energy", "climate", "trade"],
        "patterns": ["碳中和", "可再生能源", "电网", "化石", "LNG", "net zero", "transition", "电力"],
    },
    {
        "id": "supply_fragment",
        "label": "供应链碎片化",
        "domain": "industry",
        "summary": "友岸/近岸、双轨标准与库存缓冲：效率让位于韧性时的成本结构。",
        "questions": ["迁徙是政治驱动还是成本驱动？", "冗余库存可持续吗？", "标准是否分裂？"],
        "topic_ids": ["trade", "chip", "asean", "india"],
        "patterns": ["供应链", "友岸", "近岸", "reshoring", "friend-shoring", "supply chain", "脱钩", "转移"],
    },
    {
        "id": "earnings_quality",
        "label": "财报质量",
        "domain": "industry",
        "summary": "收入质量、指引、回购与一次性项目：把叙事压回可审计数字。",
        "questions": ["增长来自量还是价？", "指引是否低于街预期？", "有无一次性收益？"],
        "topic_ids": ["chip", "ai", "fed"],
        "patterns": ["营收", "指引", "guidance", "eps", "毛利", "回购", "10-Q", "10-K", "业绩"],
    },
]

_FW_BY_ID = {f["id"]: f for f in FRAMEWORK_LEXICON}
_TOPIC_BY_ID = {t["id"]: t for t in TOPIC_LEXICON}


def get_framework(fid):
    return _FW_BY_ID.get(fid)


def get_topic(tid):
    return _TOPIC_BY_ID.get(tid)


def title_matches_patterns(title, patterns):
    if not title or not patterns:
        return False
    text = title
    lower = title.lower()
    for pattern in patterns:
        if not pattern:
            continue
        if pattern.isascii():
            if len(pattern.strip()) <= 3:
                import re
                if re.search(rf"(?<![A-Za-z]){re.escape(pattern.strip())}(?![A-Za-z])", text, re.I):
                    return True
            elif pattern.lower() in lower:
                return True
        elif pattern in text:
            return True
    return False


def match_frameworks(title, limit=3):
    """Return framework stubs that match a title."""
    hits = []
    for fw in FRAMEWORK_LEXICON:
        if title_matches_patterns(title, fw.get("patterns") or []):
            hits.append({"id": fw["id"], "label": fw["label"], "domain": fw.get("domain")})
        if len(hits) >= limit:
            break
    return hits


def match_topics(title):
    hits = []
    for topic in TOPIC_LEXICON:
        if title_matches_patterns(title, topic.get("patterns") or []):
            hits.append({"id": topic["id"], "label": topic["label"]})
    return hits


def _article_card(a, extra=None):
    enrich_signal(a)
    card = {
        "title": a.get("title"),
        "link": a.get("link"),
        "source": a.get("source"),
        "source_cn": a.get("source_cn"),
        "icon": a.get("icon") or "",
        "published": a.get("published"),
        "published_timestamp": a.get("published_timestamp"),
        "description": a.get("description") or "",
        "source_type": a.get("source_type") or "",
        "source_type_label": a.get("source_type_label") or DOC_TYPE_LABELS.get(a.get("source_type") or "", ""),
        "domain": a.get("domain") or "",
        "domain_label": a.get("domain_label") or DOMAIN_LABELS.get(a.get("domain") or "", ""),
        "country": a.get("country") or "其他",
        "priority": a.get("priority", 2),
        "link_kind": a.get("link_kind") or "",
        "filing_type": a.get("filing_type") or "",
        "signal": a.get("signal"),
        "signal_label": a.get("signal_label"),
        "signal_short": a.get("signal_short"),
        "frameworks": match_frameworks(a.get("title") or ""),
    }
    if extra:
        card.update(extra)
    return card


def _sort_ts(a):
    return a.get("published_timestamp") or ""


# ---------------------------------------------------------------------------
# Issue workbench = timeline + positions + comparative pack (unified)
# ---------------------------------------------------------------------------
def _workbench_sections(cards, per_tier=8, per_country=5):
    """Shared sections for any lens: compare + positions + timeline."""
    cards = list(cards or [])
    cards.sort(key=lambda x: (0 if x.get("published_timestamp") else 1, _sort_ts(x)), reverse=True)
    timeline = sorted(cards, key=lambda x: (_sort_ts(x) or "9999", x.get("title") or ""))

    by_signal = {k: [] for k in ("fact", "analysis", "narrative")}
    for c in cards:
        by_signal.setdefault(c.get("signal") or "narrative", []).append(c)
    compare = []
    for tier_id in ("fact", "analysis", "narrative"):
        meta = signal_meta(tier_id)
        items = by_signal.get(tier_id) or []
        items = sorted(items, key=lambda x: (x.get("priority", 2), 0 if _sort_ts(x) else 1, _sort_ts(x)))
        compare.append({
            "signal": tier_id,
            "label": meta["label"],
            "short": meta["short"],
            "hint": meta["hint"],
            "count": len(items),
            "items": items[:per_tier],
        })

    by_country = defaultdict(list)
    for c in cards:
        by_country[c.get("country") or "其他"].append(c)
    positions = []
    for country, items in sorted(by_country.items(), key=lambda x: (-len(x[1]), x[0])):
        items_sorted = sorted(items, key=lambda x: (x.get("signal_rank", 9), x.get("priority", 2), _sort_ts(x)))
        source_names = []
        seen = set()
        for it in items_sorted:
            name = it.get("source_cn") or it.get("source") or ""
            if name and name not in seen:
                seen.add(name)
                source_names.append(name)
            if len(source_names) >= 4:
                break
        tier_counts = defaultdict(int)
        for it in items:
            tier_counts[it.get("signal") or "narrative"] += 1
        positions.append({
            "country": country,
            "count": len(items),
            "sources": source_names,
            "signal_counts": {
                "fact": tier_counts.get("fact", 0),
                "analysis": tier_counts.get("analysis", 0),
                "narrative": tier_counts.get("narrative", 0),
            },
            "items": items_sorted[:per_country],
        })

    return {
        "total": len(cards),
        "signal_counts": {
            "fact": len(by_signal.get("fact") or []),
            "analysis": len(by_signal.get("analysis") or []),
            "narrative": len(by_signal.get("narrative") or []),
        },
        "reading_path": [
            "先读「一级事实」（官方 / 数据 / 政策）",
            "再读「二级分析」对照解释",
            "最后扫「三级叙事」与各方表述，标记情绪与偏见",
        ],
        "timeline": timeline[:40],
        "compare": compare,
        "positions": positions,
        "items": cards[:24],
    }


def _match_articles_for_topic(topic, articles):
    topic = topic or {}
    patterns = topic.get("patterns") or []
    return [a for a in articles if title_matches_patterns(a.get("title") or "", patterns)]


def _match_articles_for_framework(fw, articles):
    fw = fw or {}
    matched = []
    seen = set()
    for a in articles:
        title = a.get("title") or ""
        hit = title_matches_patterns(title, fw.get("patterns") or [])
        if not hit:
            for tid in fw.get("topic_ids") or []:
                topic = _TOPIC_BY_ID.get(tid)
                if topic and title_matches_patterns(title, topic.get("patterns") or []):
                    hit = True
                    break
        if not hit:
            continue
        link = a.get("link") or ""
        if link in seen:
            continue
        seen.add(link)
        matched.append(a)
    return matched


def build_issue_workbench(topic, articles, days=7, per_tier=8, per_country=5):
    """Unified issue desk: timeline, country positions, L1/L2/L3 compare pack."""
    topic = topic or {}
    tid = topic.get("id")
    matched = _match_articles_for_topic(topic, articles)
    cards = [_article_card(a) for a in matched]
    sections = _workbench_sections(cards, per_tier=per_tier, per_country=per_country)

    related_fw = []
    for fw in FRAMEWORK_LEXICON:
        if tid and tid in (fw.get("topic_ids") or []):
            related_fw.append({
                "id": fw["id"],
                "label": fw["label"],
                "summary": fw["summary"],
                "domain": fw.get("domain"),
            })
        elif any(title_matches_patterns(c.get("title") or "", fw.get("patterns") or []) for c in cards[:30]):
            related_fw.append({
                "id": fw["id"],
                "label": fw["label"],
                "summary": fw["summary"],
                "domain": fw.get("domain"),
            })
    seen_fw = set()
    fw_out = []
    for f in related_fw:
        if f["id"] in seen_fw:
            continue
        seen_fw.add(f["id"])
        fw_out.append(f)

    return {
        "topic": {"id": topic.get("id"), "label": topic.get("label")},
        "days": days,
        **sections,
        "frameworks": fw_out[:6],
    }


def list_issue_summaries(articles, days=7, limit=16):
    """Topic list with counts + signal mix for workbench index."""
    rows = []
    for topic in TOPIC_LEXICON:
        matched = [a for a in articles if title_matches_patterns(a.get("title") or "", topic.get("patterns") or [])]
        if not matched:
            continue
        tiers = defaultdict(int)
        for a in matched:
            tiers[classify_signal(a)] += 1
        fw_ids = [
            fw["id"] for fw in FRAMEWORK_LEXICON
            if topic["id"] in (fw.get("topic_ids") or [])
        ]
        rows.append({
            "id": topic["id"],
            "label": topic["label"],
            "count": len(matched),
            "signal_counts": {
                "fact": tiers.get("fact", 0),
                "analysis": tiers.get("analysis", 0),
                "narrative": tiers.get("narrative", 0),
            },
            "framework_ids": fw_ids,
        })
    rows.sort(key=lambda x: (-x["count"], x["label"]))
    return {"days": days, "topics": rows[:limit]}


def build_framework_detail(framework, articles, days=14, limit=24):
    fw = framework or {}
    matched = []
    for a in articles:
        title = a.get("title") or ""
        if title_matches_patterns(title, fw.get("patterns") or []):
            matched.append(a)
            continue
        # also pull via related topics
        for tid in fw.get("topic_ids") or []:
            topic = _TOPIC_BY_ID.get(tid)
            if topic and title_matches_patterns(title, topic.get("patterns") or []):
                matched.append(a)
                break

    # dedupe by link
    seen = set()
    uniq = []
    for a in matched:
        link = a.get("link") or ""
        if link in seen:
            continue
        seen.add(link)
        uniq.append(a)

    cards = [_article_card(a) for a in uniq]
    cards.sort(key=lambda x: (x.get("signal_rank", 9), x.get("priority", 2), 0 if _sort_ts(x) else 1, _sort_ts(x)))

    by_signal = {k: [] for k in ("fact", "analysis", "narrative")}
    for c in cards:
        by_signal.setdefault(c.get("signal") or "narrative", []).append(c)

    return {
        "framework": {
            "id": fw.get("id"),
            "label": fw.get("label"),
            "domain": fw.get("domain"),
            "domain_label": DOMAIN_LABELS.get(fw.get("domain") or "", ""),
            "summary": fw.get("summary"),
            "questions": fw.get("questions") or [],
            "topic_ids": fw.get("topic_ids") or [],
            "topics": [
                {"id": t, "label": (_TOPIC_BY_ID.get(t) or {}).get("label") or t}
                for t in (fw.get("topic_ids") or [])
            ],
        },
        "days": days,
        "total": len(cards),
        "signal_counts": {
            "fact": len(by_signal.get("fact") or []),
            "analysis": len(by_signal.get("analysis") or []),
            "narrative": len(by_signal.get("narrative") or []),
        },
        "compare": [
            {
                "signal": tier,
                "label": signal_meta(tier)["label"],
                "hint": signal_meta(tier)["hint"],
                "count": len(by_signal.get(tier) or []),
                "items": (by_signal.get(tier) or [])[:8],
            }
            for tier in ("fact", "analysis", "narrative")
        ],
        "items": cards[:limit],
    }


def list_frameworks(articles=None, days=14):
    """Framework index; optional article pool for hit counts."""
    articles = articles or []
    out = []
    for fw in FRAMEWORK_LEXICON:
        count = 0
        if articles:
            detail_total = 0
            for a in articles:
                title = a.get("title") or ""
                if title_matches_patterns(title, fw.get("patterns") or []):
                    detail_total += 1
                    continue
                for tid in fw.get("topic_ids") or []:
                    topic = _TOPIC_BY_ID.get(tid)
                    if topic and title_matches_patterns(title, topic.get("patterns") or []):
                        detail_total += 1
                        break
            count = detail_total
        out.append({
            "id": fw["id"],
            "label": fw["label"],
            "domain": fw.get("domain"),
            "domain_label": DOMAIN_LABELS.get(fw.get("domain") or "", ""),
            "summary": fw["summary"],
            "questions": fw.get("questions") or [],
            "topic_ids": fw.get("topic_ids") or [],
            "count": count,
        })
    out.sort(key=lambda x: (-x.get("count", 0), x["label"]))
    return {"days": days, "frameworks": out}


# ---------------------------------------------------------------------------
# Decision briefing — actionable layer on top of domain briefing
# ---------------------------------------------------------------------------
def _why_matters(item, topic_hits, fw_hits):
    bits = []
    sig = item.get("signal")
    if sig == "fact":
        bits.append("一级事实，优先核实原文")
    elif sig == "analysis":
        bits.append("分析层，对照既有框架")
    else:
        bits.append("叙事层，注意情绪与转述偏差")
    if item.get("filing_type") or item.get("link_kind") == "official":
        bits.append("含官方披露链接")
    if fw_hits:
        bits.append("触及框架：" + "、".join(f["label"] for f in fw_hits[:2]))
    if topic_hits:
        bits.append("议题：" + "、".join(t["label"] for t in topic_hits[:2]))
    domain = item.get("domain_label") or ""
    if domain:
        bits.append(domain)
    return " · ".join(bits)


def decorate_briefing_item(item):
    enrich_signal(item)
    title = item.get("title") or ""
    topics = match_topics(title)
    frameworks = match_frameworks(title)
    item["topics"] = topics
    item["frameworks"] = frameworks
    item["why_matters"] = _why_matters(item, topics, frameworks)
    return item


def build_decision_briefing(base_payload):
    """Upgrade a domain briefing payload into a decision briefing."""
    payload = dict(base_payload or {})
    sections = []
    all_fw = {}
    all_topics = {}
    fact_n = analysis_n = narrative_n = 0

    for sec in payload.get("sections") or []:
        items = []
        for it in sec.get("items") or []:
            decorate_briefing_item(it)
            items.append(it)
            sig = it.get("signal")
            if sig == "fact":
                fact_n += 1
            elif sig == "analysis":
                analysis_n += 1
            else:
                narrative_n += 1
            for f in it.get("frameworks") or []:
                all_fw[f["id"]] = f
            for t in it.get("topics") or []:
                all_topics[t["id"]] = t
        # prefer fact then analysis within section
        items.sort(key=lambda x: (x.get("signal_rank", 9), x.get("priority", 2)))
        sections.append({**sec, "items": items})

    earnings = []
    for it in payload.get("earnings") or []:
        decorate_briefing_item(it)
        earnings.append(it)

    follow_ups = []
    for t in list(all_topics.values())[:5]:
        follow_ups.append({
            "type": "lens",
            "kind": "situation",
            "id": t["id"],
            "label": f"打开透镜：{t['label']}",
        })
    for f in list(all_fw.values())[:4]:
        follow_ups.append({
            "type": "lens",
            "kind": "model",
            "id": f["id"],
            "label": f"打开透镜：{f['label']}",
        })
    if fact_n:
        follow_ups.append({
            "type": "hint",
            "id": "read_facts",
            "label": f"本窗有 {fact_n} 条一级事实——建议先读完再看叙事",
        })

    payload["mode"] = "decision"
    payload["sections"] = sections
    payload["earnings"] = earnings
    payload["decision"] = {
        "signal_counts": {
            "fact": fact_n,
            "analysis": analysis_n,
            "narrative": narrative_n,
        },
        "frameworks": list(all_fw.values())[:8],
        "topics": list(all_topics.values())[:10],
        "lenses": (
            [{"kind": "situation", **t} for t in list(all_topics.values())[:8]]
            + [{"kind": "model", **f} for f in list(all_fw.values())[:6]]
        ),
        "follow_ups": follow_ups,
        "reading_path": [
            "扫一眼信号计数：事实是否足够支撑叙事？",
            "打开相关透镜，看各方表述与时间线",
            "若有自检问题，用问题清单校准判断",
        ],
    }
    return payload


# ---------------------------------------------------------------------------
# Lens — unified situation (issue) + model (framework)
# ---------------------------------------------------------------------------
LENS_KINDS = {
    "situation": {"id": "situation", "label": "事态", "hint": "事实 → 分析 → 叙事 · 各方表述 · 时间线"},
    "model": {"id": "model", "label": "模型", "hint": "事实 → 分析 → 叙事 · 各方表述 · 时间线"},
}


def resolve_lens(lens_id, kind=None):
    """Return (kind, raw_dict) or (None, None)."""
    if not lens_id:
        return None, None
    kind = (kind or "").strip() or None
    if kind == "situation" or kind is None:
        topic = get_topic(lens_id)
        if topic:
            return "situation", topic
    if kind == "model" or kind is None:
        fw = get_framework(lens_id)
        if fw:
            return "model", fw
    return None, None


def list_lenses(articles, days=14, kind=None, limit=40):
    """Unified index: situations + models with hit counts."""
    kind = (kind or "all").strip() or "all"
    items = []
    if kind in ("all", "situation"):
        for row in list_issue_summaries(articles, days=days, limit=limit).get("topics") or []:
            items.append({
                "id": row["id"],
                "kind": "situation",
                "kind_label": LENS_KINDS["situation"]["label"],
                "label": row["label"],
                "count": row["count"],
                "signal_counts": row.get("signal_counts") or {},
                "summary": "",
            })
    if kind in ("all", "model"):
        for row in list_frameworks(articles, days=days).get("frameworks") or []:
            items.append({
                "id": row["id"],
                "kind": "model",
                "kind_label": LENS_KINDS["model"]["label"],
                "label": row["label"],
                "count": row.get("count") or 0,
                "domain": row.get("domain"),
                "domain_label": row.get("domain_label"),
                "summary": row.get("summary") or "",
            })
    items.sort(key=lambda x: (-(x.get("count") or 0), 0 if x.get("kind") == "situation" else 1, x.get("label") or ""))
    if kind == "all":
        items = items[:limit]
    return {
        "days": days,
        "kind": kind,
        "kinds": list(LENS_KINDS.values()),
        "lenses": items,
    }


def build_lens_detail(lens_id, articles, days=14, kind=None):
    """One workbench for every lens: compare + positions + timeline (+ questions if any)."""
    resolved_kind, raw = resolve_lens(lens_id, kind=kind)
    if not raw:
        return None

    if resolved_kind == "situation":
        matched = _match_articles_for_topic(raw, articles)
        cards = [_article_card(a) for a in matched]
        sections = _workbench_sections(cards)
        related = []
        for fw in FRAMEWORK_LEXICON:
            if raw.get("id") in (fw.get("topic_ids") or []):
                related.append({"id": fw["id"], "kind": "model", "label": fw["label"]})
            elif any(title_matches_patterns(c.get("title") or "", fw.get("patterns") or []) for c in cards[:30]):
                related.append({"id": fw["id"], "kind": "model", "label": fw["label"]})
        seen = set()
        related_out = []
        for r in related:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            related_out.append(r)
        lens = {
            "id": raw.get("id"),
            "kind": "situation",
            "label": raw.get("label"),
            "summary": "",
            "questions": [],
        }
        return {
            "kind": "situation",
            "kind_label": LENS_KINDS["situation"]["label"],
            "lens": lens,
            "days": days,
            "related_lenses": related_out[:8],
            "topic": {"id": raw.get("id"), "label": raw.get("label")},
            "frameworks": [{"id": r["id"], "label": r["label"]} for r in related_out[:6]],
            **sections,
        }

    matched = _match_articles_for_framework(raw, articles)
    cards = [_article_card(a) for a in matched]
    sections = _workbench_sections(cards)
    related = [
        {"id": t, "kind": "situation", "label": (_TOPIC_BY_ID.get(t) or {}).get("label") or t}
        for t in (raw.get("topic_ids") or [])
    ]
    lens = {
        "id": raw.get("id"),
        "kind": "model",
        "label": raw.get("label"),
        "domain": raw.get("domain"),
        "domain_label": DOMAIN_LABELS.get(raw.get("domain") or "", ""),
        "summary": raw.get("summary") or "",
        "questions": raw.get("questions") or [],
    }
    return {
        "kind": "model",
        "kind_label": LENS_KINDS["model"]["label"],
        "lens": lens,
        "days": days,
        "related_lenses": related,
        "framework": {
            "id": raw.get("id"),
            "label": raw.get("label"),
            "domain": raw.get("domain"),
            "domain_label": lens["domain_label"],
            "summary": lens["summary"],
            "questions": lens["questions"],
            "topic_ids": raw.get("topic_ids") or [],
            "topics": related,
        },
        **sections,
    }
