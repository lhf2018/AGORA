# Agora

个人认知信息聚合器：智库、财报、研报、白皮书、政策、论文、数据、公告与媒体，统一进本地信息流。

[仓库地址](https://github.com/lhf2018/Think-Tank-Aggregation)

## 功能

- **290+ 信息源**，覆盖 **40+** 国家/地区（含能源气候、AI 政策、对华观察、台海等补强源）
- **认知 / 今日简报 / 财报专栏 / 收藏 / 源管理** 多视图
  - **认知**：主信息流，按领域 × 文体 × 国家 × 议题 × 时间筛选
  - **今日简报**：按领域挑选近 1–3 日要点；可复制 Markdown、打开分享页
  - **财报专栏**：官方披露优先 + 同公司同季事件聚合（见下）
  - **收藏**：稍后读 / 已读 / 未读（浏览器 localStorage，无需账号）
  - **源管理**：网页增删改自定义源、试抓、启停内置源
- **文体**：智库、财报、研报、白皮书、政策文件、科学论文、数据发布、公司公告、媒体
- **领域**：地缘、产业、宏观金融、科技、能源气候、卫生健康、综合
- **同题合并与时间线**：相似标题聚类；点「同题 N · 时间线」按发布时间看各方表述演变
- **卡片摘要 / 阅读模式**：展示 RSS 导语；点「展开」打开细读面板（摘要最长约 1000 字；多数源 RSS 本身仅为导语）
- **SQLite 持久化**：`data/aggregator.db`，重启秒开；历史约保留 30 天
- **增量抓取**：高优源约 10 分钟、普通源约 30 分钟；官方财报约每 6 小时；失败/噪音源自动降权
- **标题搜索**、议题词云、源健康度面板

### 财报专栏（官方原文）

目标：**少看转载，多看官方披露 PDF / 文件页**。

| 来源 | 内容 | 模块 |
|------|------|------|
| SEC EDGAR | 美股 / ADR：10-K、10-Q、20-F、业绩相关 8-K/6-K | `filings.py` |
| 巨潮资讯 | A 股年报 / 半年报 / 季报 PDF | `filings.py` |
| 港交所披露易 | 港股年报 / 中期 / 季报 / 业绩公告 PDF | `filings.py` |
| Seeking Alpha 等 | 电话会实录（标注「电话会」） | RSS |
| Google News 等 | 媒体报道（标注「报道」，优先级已下调） | RSS |

专栏能力：

- 按 **官方披露 / 电话会 / 报道** 筛选；公司 chip、近 3/7/30/120 天时间窗
- **事件聚合**（默认）：同公司同季（或约 14 日内）合成一条；主链优先官方；可展开「同事件 N」
- 每条可 **打开披露**；有 IR 页时显示 **IR**
- 网页按钮或 `POST /api/filings/trigger` 可强制刷新官方披露

关注公司清单见 `earnings.py` 的 `COMPANY_LEXICON`（含 `cik` / `cn_code` / `hk_code`）。

## 快速开始

```bash
git clone https://github.com/lhf2018/Think-Tank-Aggregation.git
cd Think-Tank-Aggregation

python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
# source venv/bin/activate

pip install -r requirements.txt
python app.py
```

浏览器打开：**http://localhost:5000**

首次空库会后台全量抓取（约 1–2 分钟）；有数据后重启即可直接浏览，后台继续增量更新。首次也会拉取关注公司的官方披露（EDGAR / 巨潮 / 披露易），耗时视网络而定。

可选：安装 git hook，避免 Cursor 自动注入 commit attribution：

```powershell
.\scripts\install-git-hooks.ps1
```

## 使用

| 视图 | 说明 |
|------|------|
| 认知 | 浏览全部内容；可用时间 / 领域 / 文体 / 国家 / 议题筛选 |
| 今日简报 | 近 24h–3 日要点；分享页与 Markdown 导出 |
| 财报专栏 | 官方优先；事件聚合；公司 / 类型 / 时间筛选；可刷新官方披露 |
| 收藏 | 查看「稍后」「已读」「未读」；在认知或专栏里点按钮打标 |
| 源管理 | 管理自定义源与内置源覆盖 |

卡片上可标记 **稍后 / 已读**；打开原文会记为已读。有摘要时点 **展开** 打开细读面板；同题条目可展开时间线。财报事件可展开「同事件」查看关联披露 / 电话会 / 报道。

## 项目结构

```
Think-Tank-Aggregation/
├── app.py              # Flask：抓取、调度、API、简报
├── db.py               # SQLite
├── config.py           # 主源配置 + 文体/领域映射
├── sources_extra.py    # 补充源（财报/政策/论文/扩展智库等）
├── quality.py          # 噪音过滤、同题聚类、降权
├── earnings.py         # 公司主数据、链接分类、日历与事件聚合
├── filings.py          # SEC EDGAR / 巨潮 / 港交所披露易
├── templates/
│   ├── index.html
│   └── briefing_share.html
├── data/               # aggregator.db（运行后生成，已 gitignore）
├── scripts/
│   ├── init_db.py
│   └── install-git-hooks.ps1
├── requirements.txt
├── TODO.md
└── README.md
```

## 添加信息源

优先在 `sources_extra.py` 追加，或写入 `config.py` 的 `THINK_TANKS_CONFIG`：

```python
{
    "name": "Example Institute",
    "name_cn": "示例机构",
    "rss": "https://example.com/feed.xml",
    "icon": "https://example.com/favicon.ico",
    "category": "美国智库",
    "doc_type": "think_tank",   # 可选，显式指定文体
    "domain": "geopolitics",    # 可选，显式指定领域
    "country": "美国",
    "priority": 1,              # 1 高优 / 2 普通
    "description": "…",
}
```

未写 `doc_type` / `domain` 时，由 `config.py` 的 `get_doc_type` / `get_domain` 按 category、名称等推断。

无官方 RSS 时，可用 `sources_extra.py` / `config.py` 中的 Google News 查询模板。也可在网页 **源管理** 中新增自定义源。

### 扩展财报关注公司

在 `earnings.py` 的 `COMPANY_LEXICON` 增加条目，字段示意：

| 字段 | 用途 |
|------|------|
| `cik` | SEC EDGAR 公司编号 |
| `cn_code` | A 股六位代码（巨潮） |
| `hk_code` | 港股五位代码（披露易，如 `00700`） |
| `ir_url` | 投资者关系页（专栏 IR 按钮） |
| `patterns` | 标题识别关键词 |

有 `cik` / `cn_code` / `hk_code` 之一即可进入官方披露拉取名单。

## API

| 接口 | 说明 |
|------|------|
| `GET /api/articles` | 文章列表（筛选见下） |
| `GET /api/articles/status` | 库是否就绪 / 是否在抓取 |
| `GET /api/earnings/calendar` | 财报日历 / 事件（见下） |
| `POST /api/filings/trigger` | 强制拉取官方披露（EDGAR / 巨潮 / 披露易） |
| `GET /api/briefing` | 今日简报 JSON |
| `GET /api/briefing.md` | 简报 Markdown（`download=1` 附件下载） |
| `GET /share/briefing` | 简报分享页 |
| `GET /api/topics` | 近 N 日议题 |
| `GET /api/feeds/health` | 源健康度 |
| `GET /api/sources` | 全部源配置 |
| `GET /api/stats` | 统计（含文体/领域） |
| `POST /api/fetch/trigger` | 触发增量抓取 |
| `GET/POST/PUT/DELETE /api/admin/sources…` | 源管理 |

### `GET /api/articles` 主要参数

| 参数 | 说明 |
|------|------|
| `page` / `per_page` | 分页（默认 24，最大 60；`pool=1` 时可达 400） |
| `days` | `3` / `7` / `30` / `all` |
| `domain` | 领域 id，如 `tech` |
| `source_type` / `doc_type` | 文体 id，如 `earnings` |
| `country` | 国家中文名 |
| `topic` | 议题 id |
| `q` | 标题关键词 |
| `merge` | `1` 同题合并（默认） |

### `GET /api/earnings/calendar`

| 参数 | 说明 |
|------|------|
| `days` | 时间窗，默认 `30`（可用 `120` 看季报窗口） |
| `company` | 公司名或 id，可选 |
| `kind` | `all` / `official` / `transcript` / `media` |
| `aggregate` | `1` 事件聚合（默认）；`0` 扁平列表 |

事件条目含 `related`、`related_counts`、`period_key`、`cluster_size`；主链 `link` 优先官方披露。

### `GET /api/briefing` / `briefing.md`

| 参数 | 说明 |
|------|------|
| `days` | `1` / `2` / `3`，默认 `1` |

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Flask、Flask-Caching、feedparser、requests、python-dateutil、SQLite |
| 前端 | Tailwind CSS（CDN）、原生 JS |
| 抓取 | `ThreadPoolExecutor` 分批并发；官方披露独立调度 |

## 常见问题

**首次一直加载？**  
空库全量抓取需 1–2 分钟，看终端日志即可。官方披露首次拉取可能再多几十秒到数分钟。

**部分源无文章？**  
RSS 失效、限流或 Google News 不可达时会跳过该源，不影响其他源。可在源状态面板查看。

**展开后仍有省略号？**  
细读显示的是入库的 RSS 导语。多数媒体 RSS 本身只给短摘要并以 `...` 收尾；完整正文需点「原文」。新抓取摘要最长约 1000 字，旧条目需该源再抓一次才会更新。

**财报为什么不是 PDF？**  
A 股巨潮与港股披露易多为 PDF；美股 EDGAR 主文档常为官方 HTML 文件页（仍是原文，不是媒体转载）。

**如何强制刷新？**  
`POST /api/fetch/trigger` 刷新 RSS；`POST /api/filings/trigger` 或专栏「刷新官方披露」刷新 SEC / 巨潮 / 披露易。也可等定时增量。

**国内 Google News 不稳定？**  
尽量改官方 RSS，或使用 `GNEWS_CN` 模板。财报主路径已不依赖 GNews。

**SEC / 披露易请求失败？**  
需可访问外网。SEC 要求合理 User-Agent；披露易 prefix 查询对会话较敏感，失败时看终端 `[filings]` 日志。

## 许可证

MIT License

## 贡献

欢迎 Issue / PR。新增源请优先官方 RSS，并说明来源。新增财报公司请补全 `cik` / `cn_code` / `hk_code` 中至少一项。

---

仅供学习与个人阅读聚合，请遵守各信息源版权与使用条款。
