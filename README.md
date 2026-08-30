# Agora

个人认知信息聚合器：智库、财报、研报、白皮书、政策、论文、数据、公告与媒体，统一进本地信息流。

[仓库地址](https://github.com/lhf2018/Think-Tank-Aggregation)

## 功能

- **260+ 信息源**，覆盖 **40+** 国家/地区
- **认知 / 财报专栏 / 收藏** 三视图
  - **认知**：主信息流，按领域 × 文体 × 国家 × 议题 × 时间筛选
  - **财报专栏**：按日议程，识别公司名，支持公司过滤
  - **收藏**：稍后读 / 已读 / 未读（浏览器 localStorage，无需账号）
- **文体**：智库、财报、研报、白皮书、政策文件、科学论文、数据发布、公司公告、媒体
- **领域**：地缘、产业、宏观金融、科技、能源气候、卫生健康、综合
- **同题合并**：相似标题聚类，展示「同题 N」
- **SQLite 持久化**：`data/aggregator.db`，重启秒开；历史约保留 30 天
- **增量抓取**：高优源约 10 分钟、普通源约 30 分钟；失败/噪音源自动降权
- **标题搜索**、议题词云、源健康度面板

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

首次空库会后台全量抓取（约 1–2 分钟）；有数据后重启即可直接浏览，后台继续增量更新。

可选：安装 git hook，避免 Cursor 自动注入 commit attribution：

```powershell
.\scripts\install-git-hooks.ps1
```

## 使用

| 视图 | 说明 |
|------|------|
| 认知 | 浏览全部内容；可用时间 / 领域 / 文体 / 国家 / 议题筛选 |
| 财报专栏 | 财报相关内容按日期排列，可点公司 chip 过滤 |
| 收藏 | 查看「稍后」「已读」「未读」；在认知或专栏里点按钮打标 |

卡片上可标记 **稍后 / 已读**；打开原文会记为已读。

## 项目结构

```
Think-Tank-Aggregation/
├── app.py              # Flask：抓取、调度、API
├── db.py               # SQLite
├── config.py           # 主源配置 + 文体/领域映射
├── sources_extra.py    # 补充源（财报/政策/论文等）
├── quality.py          # 噪音过滤、同题聚类、降权
├── earnings.py         # 公司识别与财报日历
├── templates/index.html
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

无官方 RSS 时，可用 `sources_extra.py` / `config.py` 中的 Google News 查询模板。

## API

| 接口 | 说明 |
|------|------|
| `GET /api/articles` | 文章列表（筛选见下） |
| `GET /api/articles/status` | 库是否就绪 / 是否在抓取 |
| `GET /api/earnings/calendar` | 财报按日议程 |
| `GET /api/topics` | 近 N 日议题 |
| `GET /api/feeds/health` | 源健康度 |
| `GET /api/sources` | 全部源配置 |
| `GET /api/stats` | 统计（含文体/领域） |
| `POST /api/fetch/trigger` | 触发增量抓取 |

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
| `days` | 时间窗，默认 `30` |
| `company` | 公司名或 id，可选 |

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Flask、Flask-Caching、feedparser、requests、python-dateutil、SQLite |
| 前端 | Tailwind CSS（CDN）、原生 JS |
| 抓取 | `ThreadPoolExecutor` 分批并发 |

## 常见问题

**首次一直加载？**  
空库全量抓取需 1–2 分钟，看终端日志即可。

**部分源无文章？**  
RSS 失效、限流或 Google News 不可达时会跳过该源，不影响其他源。可在源状态面板查看。

**如何强制刷新？**  
`POST /api/fetch/trigger`，或等定时增量。

**国内 Google News 不稳定？**  
尽量改官方 RSS，或使用 `GNEWS_CN` 模板。

## 许可证

MIT License

## 贡献

欢迎 Issue / PR。新增源请优先官方 RSS，并说明来源。

---

仅供学习与个人阅读聚合，请遵守各信息源版权与使用条款。
