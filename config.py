# config.py
# 全球智库及认知网站配置文件
# 可随时添加、修改或删除信息源
# 建议：如果官方 rsshub.app 无法连接，请更换为以下公共镜像：
# https://rss.lilywhite.cc
# https://rsshub.pseudo.moe
# https://rss.cloudnative.love
from urllib.parse import quote

# Google News 站点 RSS（仅用于确认无官方 RSS 的源；尽量加 when: 降低噪音）
GNEWS_CN = "https://news.google.com/rss/search?q=site:{domain}+when:30d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
GNEWS_US = "https://news.google.com/rss/search?q=site:{domain}+when:7d&hl=en-US&gl=US&ceid=US:en"
GNEWS = GNEWS_US  # 适用于大多数国家智库官网的 Google News 站点订阅
GNEWS_SITE = "https://news.google.com/rss/search?q=site:{domain}+when:30d&hl=en-US&gl=US&ceid=US:en"


def gnews_cn(query):
    """自定义中文 Google News 查询（用于发言人、白皮书、带关键词的智库源）。"""
    return f"https://news.google.com/rss/search?q={quote(query)}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"


def gnews_en(query):
    """自定义英文 Google News 查询（用于 IMF/WB/IEA 等报告流）。"""
    return f"https://news.google.com/rss/search?q={quote(query)}&hl=en-US&gl=US&ceid=US:en"

THINK_TANKS_CONFIG = [
    # ==================== 中国：直连 RSS（优先）====================
    {
        "name": "People's Daily Theory",
        "name_cn": "人民网·理论",
        "rss": "http://www.people.com.cn/rss/theory.xml",
        "icon": "http://www.people.com.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "权威政策理论与思想动态"
    },
    {
        "name": "People's Daily Opinion",
        "name_cn": "人民网·观点",
        "rss": "http://www.people.com.cn/rss/opinion.xml",
        "icon": "http://www.people.com.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "政策评论与深度观点"
    },
    {
        "name": "People's Daily Politics",
        "name_cn": "人民网·时政",
        "rss": "http://www.people.com.cn/rss/politics.xml",
        "icon": "http://www.people.com.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "中国时政与政策动态直连 RSS"
    },
    {
        "name": "People's Daily World",
        "name_cn": "人民网·国际",
        "rss": "http://www.people.com.cn/rss/world.xml",
        "icon": "http://www.people.com.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "国际时事与外交动态直连 RSS"
    },
    {
        "name": "People's Daily Finance",
        "name_cn": "人民网·财经",
        "rss": "http://www.people.com.cn/rss/finance.xml",
        "icon": "http://www.people.com.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 2,
        "description": "宏观经济与财经政策直连 RSS"
    },
    {
        "name": "Xinhua World",
        "name_cn": "新华网·国际",
        "rss": "http://www.news.cn/world/news_world.xml",
        "icon": "http://www.news.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "中国国际时事与外交动态"
    },
    {
        "name": "Xinhua Politics",
        "name_cn": "新华网·时政",
        "rss": "http://www.news.cn/politics/news_politics.xml",
        "icon": "http://www.news.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "中国时政与政策动态"
    },
    {
        "name": "Xinhua Fortune",
        "name_cn": "新华网·财经",
        "rss": "http://www.news.cn/fortune/news_fortune.xml",
        "icon": "http://www.news.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 2,
        "description": "财经与宏观政策动态"
    },
    {
        "name": "China Daily Opinion",
        "name_cn": "中国日报·评论",
        "rss": "http://www.chinadaily.com.cn/rss/opinion_rss.xml",
        "icon": "http://www.chinadaily.com.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "面向国际读者的中国政策评论"
    },
    {
        "name": "China Daily China",
        "name_cn": "中国日报·国内",
        "rss": "http://www.chinadaily.com.cn/rss/china_rss.xml",
        "icon": "http://www.chinadaily.com.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 2,
        "description": "中国国内政策与治理"
    },
    {
        "name": "China Daily World",
        "name_cn": "中国日报·国际",
        "rss": "http://www.chinadaily.com.cn/rss/world_rss.xml",
        "icon": "http://www.chinadaily.com.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "国际事务英文报道直连 RSS"
    },
    {
        "name": "China Daily Biz",
        "name_cn": "中国日报·商务",
        "rss": "http://www.chinadaily.com.cn/rss/bizchina_rss.xml",
        "icon": "http://www.chinadaily.com.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 2,
        "description": "中国商务与经济政策英文直连 RSS"
    },
    {
        "name": "SCMP China",
        "name_cn": "南华早报·中国",
        "rss": "https://www.scmp.com/rss/2/feed",
        "icon": "https://www.scmp.com/favicon.ico",
        "category": "认知网站",
        "country": "中国",
        "priority": 1,
        "description": "港媒对中国政策与时政的深度报道"
    },
    {
        "name": "SCMP Asia",
        "name_cn": "南华早报·亚洲",
        "rss": "https://www.scmp.com/rss/4/feed",
        "icon": "https://www.scmp.com/favicon.ico",
        "category": "认知网站",
        "country": "中国",
        "priority": 2,
        "description": "亚洲地缘与政策观察"
    },
    {
        "name": "FT Chinese",
        "name_cn": "FT中文网",
        "rss": "http://www.ftchinese.com/rss/news",
        "icon": "http://www.ftchinese.com/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "国际财经与地缘政治中文分析"
    },
    {
        "name": "Sinocism",
        "name_cn": "Sinocism",
        "rss": "https://sinocism.com/feed",
        "icon": "https://sinocism.com/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "中国政治与政策英文简报"
    },

    # ==================== 中国：官方文件 / 原始表态 ====================
    {
        "name": "MFA Spokesperson",
        "name_cn": "外交部发言人",
        "rss": gnews_cn('"外交部发言人" when:14d'),
        "icon": "https://www.mfa.gov.cn/favicon.ico",
        "category": "政策文件",
        "doc_type": "policy",
        "domain": "geopolitics",
        "country": "中国",
        "priority": 1,
        "description": "外交部例行记者会与发言人表态（官网无 RSS，精准关键词订阅）"
    },
    {
        "name": "SCIO White Papers",
        "name_cn": "国新办·白皮书",
        "rss": gnews_cn('site:scio.gov.cn 白皮书 when:365d'),
        "icon": "https://www.scio.gov.cn/favicon.ico",
        "category": "白皮书",
        "doc_type": "whitepaper",
        "domain": "geopolitics",
        "country": "中国",
        "priority": 1,
        "description": "国务院新闻办白皮书与官方政策文件"
    },

    # ==================== 中国智库（无官网 RSS：收紧 GNews）====================
    {
        "name": "CICIR",
        "name_cn": "中国现代国际关系研究院",
        "rss": gnews_cn('site:cicir.ac.cn (报告 OR 评论 OR 观点 OR 现代院) when:90d'),
        "icon": "https://www.cicir.ac.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "中国顶级国际关系与安全研究机构（官网无 RSS，关键词过滤）"
    },
    {
        "name": "Development Research Center",
        "name_cn": "国务院发展研究中心",
        "rss": gnews_cn('site:drc.gov.cn (研究 OR 报告 OR 调研) when:90d'),
        "icon": "http://www.drc.gov.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "中国政府核心决策咨询智库"
    },
    {
        "name": "CASS",
        "name_cn": "中国社会科学院",
        "rss": gnews_cn('site:cssn.cn (智库 OR 研究 OR 评论) when:30d'),
        "icon": "http://www.cssn.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "中国哲学社会科学研究最高殿堂"
    },
    {
        "name": "SIIS",
        "name_cn": "上海国际问题研究院",
        "rss": gnews_cn('"上海国际问题研究院" OR "Shanghai Institutes for International Studies" when:90d'),
        "icon": "http://www.siis.org.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "中国重要外交与地缘政治研究机构"
    },
    {
        "name": "CIIS",
        "name_cn": "中国国际问题研究院",
        "rss": gnews_cn('site:ciis.org.cn when:90d'),
        "icon": "https://www.ciis.org.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "中国外交部直属国际问题研究机构"
    },
    {
        "name": "CCIEE",
        "name_cn": "中国国际经济交流中心",
        "rss": gnews_cn('site:cciee.org.cn when:90d'),
        "icon": "http://www.cciee.org.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "国际经济政策与战略研究"
    },
    {
        "name": "CF40",
        "name_cn": "中国金融四十人论坛",
        "rss": gnews_cn('(site:cf40.com OR site:cf40.org.cn) when:30d'),
        "icon": "https://www.cf40.com/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "金融与宏观经济政策顶尖智库"
    },
    {
        "name": "Chongyang Institute",
        "name_cn": "中国人民大学重阳金融研究院",
        "rss": gnews_cn('(site:rdcy.ruc.edu.cn OR "重阳金融研究院") when:90d'),
        "icon": "http://www.ruc.edu.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "金融、宏观与全球治理研究"
    },
    {
        "name": "Fudan IIS",
        "name_cn": "复旦大学国际问题研究院",
        "rss": gnews_cn('site:iis.fudan.edu.cn when:90d'),
        "icon": "http://www.fudan.edu.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 2,
        "description": "国际问题综合研究"
    },
    {
        "name": "PKU IISS",
        "name_cn": "北京大学国际战略研究院",
        "rss": gnews_cn('site:iiss.pku.edu.cn when:90d'),
        "icon": "https://www.pku.edu.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 2,
        "description": "国际战略与安全研究"
    },
    {
        "name": "China Think Tanks",
        "name_cn": "中国智库网",
        "rss": gnews_cn('site:chinathinktanks.org.cn when:30d'),
        "icon": "http://www.chinathinktanks.org.cn/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 2,
        "description": "中国智库观点与实践聚合"
    },
    {
        "name": "Caixin",
        "name_cn": "财新网",
        "rss": gnews_cn('site:caixin.com when:7d'),
        "icon": "https://www.caixin.com/favicon.ico",
        "category": "中国智库",
        "country": "中国",
        "priority": 1,
        "description": "财经与公共政策深度报道（官网无公开 RSS，近 7 日站点订阅）"
    },
    # ==================== 北美地区 ====================
    # 美国顶级智库
    {
        "name": "Brookings Institution",
        "name_cn": "布鲁金斯学会",
        "rss": GNEWS_US.format(domain="brookings.edu"),
        "icon": "https://www.brookings.edu/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 1,
        "description": "美国最具影响力的智库之一"
    },
    {
        "name": "Carnegie Endowment for International Peace",
        "name_cn": "卡内基国际和平基金会",
        "rss": GNEWS_US.format(domain="carnegieendowment.org"),
        "icon": "https://carnegieendowment.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 1,
        "description": "国际事务研究顶级智库"
    },
    {
        "name": "Council on Foreign Relations",
        "name_cn": "外交关系委员会",
        "rss": "http://feeds.cfr.org/cfr_main",
        "icon": "https://www.cfr.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 1,
        "description": "美国外交政策权威机构"
    },
    {
        "name": "RAND Corporation",
        "name_cn": "兰德公司",
        "rss": "https://www.rand.org/pubs/research_reports.xml",
        "icon": "https://www.rand.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 1,
        "description": "全球知名政策研究机构"
    },
    {
        "name": "Peterson Institute for International Economics",
        "name_cn": "彼得森国际经济研究所",
        "rss": GNEWS_US.format(domain="piie.com"),
        "icon": "https://www.piie.com/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 1,
        "description": "国际经济政策权威"
    },
    {
        "name": "Center for Strategic and International Studies",
        "name_cn": "战略与国际研究中心",
        "rss": "https://www.csis.org/rss.xml",
        "icon": "https://www.csis.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 1,
        "description": "国家安全与战略研究"
    },
    {
        "name": "Heritage Foundation",
        "name_cn": "传统基金会",
        "rss": GNEWS_US.format(domain="heritage.org"),
        "icon": "https://www.heritage.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 1,
        "description": "保守派政策研究"
    },
    {
        "name": "American Enterprise Institute",
        "name_cn": "美国企业研究所",
        "rss": "https://www.aei.org/feed/",
        "icon": "https://www.aei.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 1,
        "description": "公共政策研究"
    },
    {
        "name": "Atlantic Council",
        "name_cn": "大西洋理事会",
        "rss": "https://www.atlanticcouncil.org/feed/",
        "icon": "https://www.atlanticcouncil.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 1,
        "description": "跨大西洋关系研究"
    },
    {
        "name": "Wilson Center",
        "name_cn": "威尔逊国际学者中心",
        "rss": GNEWS_US.format(domain="wilsoncenter.org"),
        "icon": "https://www.wilsoncenter.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 1,
        "description": "国际问题研究"
    },
    {
        "name": "Urban Institute",
        "name_cn": "城市研究所",
        "rss": GNEWS_US.format(domain="urban.org"),
        "icon": "https://www.urban.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "社会经济政策研究"
    },
    {
        "name": "Cato Institute",
        "name_cn": "卡托研究所",
        "rss": "https://www.cato.org/rss.xml",
        "icon": "https://www.cato.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "自由意志主义智库"
    },
    {
        "name": "Center for American Progress",
        "name_cn": "美国进步中心",
        "rss": GNEWS_US.format(domain="americanprogress.org"),
        "icon": "https://www.americanprogress.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "进步派政策研究"
    },
    {
        "name": "Hoover Institution",
        "name_cn": "胡佛研究所",
        "rss": "https://www.hoover.org/rss.xml",
        "icon": "https://www.hoover.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "斯坦福大学附属智库"
    },
    {
        "name": "Center for a New American Security",
        "name_cn": "新美国安全中心",
        "rss": GNEWS_US.format(domain="cnas.org"),
        "icon": "https://www.cnas.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 1,
        "description": "国防、印太安全与新兴技术政策"
    },
    {
        "name": "Hudson Institute",
        "name_cn": "哈德逊研究所",
        "rss": "https://www.hudson.org/rss.xml",
        "icon": "https://www.hudson.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 1,
        "description": "保守派外交与国防政策研究"
    },
    {
        "name": "German Marshall Fund",
        "name_cn": "德国马歇尔基金会",
        "rss": "https://www.gmfus.org/rss.xml",
        "icon": "https://www.gmfus.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 1,
        "description": "跨大西洋关系与全球民主"
    },
    {
        "name": "Quincy Institute",
        "name_cn": "昆西研究所",
        "rss": "https://quincyinst.org/feed/",
        "icon": "https://quincyinst.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 1,
        "description": "现实主义外交与克制战略"
    },
    {
        "name": "Defense Priorities",
        "name_cn": "国防优先事项",
        "rss": "https://www.defensepriorities.org/feed",
        "icon": "https://www.defensepriorities.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "有限军事干预与战略收缩"
    },
    {
        "name": "Stimson Center",
        "name_cn": "史汀生中心",
        "rss": GNEWS_US.format(domain="stimson.org"),
        "icon": "https://www.stimson.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "国际安全、防扩散与亚洲政策"
    },
    {
        "name": "New America",
        "name_cn": "新美国基金会",
        "rss": GNEWS_US.format(domain="newamerica.org"),
        "icon": "https://www.newamerica.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "科技、安全与社会政策创新"
    },
    {
        "name": "Center for Security and Emerging Technology",
        "name_cn": "安全与新兴技术中心",
        "rss": GNEWS_US.format(domain="cset.georgetown.edu"),
        "icon": "https://cset.georgetown.edu/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "AI、半导体与科技竞争政策"
    },
    {
        "name": "Foreign Policy Research Institute",
        "name_cn": "外交政策研究所",
        "rss": GNEWS_US.format(domain="fpri.org"),
        "icon": "https://www.fpri.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "历史视角下的美国外交"
    },
    {
        "name": "Middle East Institute",
        "name_cn": "中东研究所",
        "rss": GNEWS_US.format(domain="mei.edu"),
        "icon": "https://www.mei.edu/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "中东政治、安全与能源"
    },
    {
        "name": "Belfer Center",
        "name_cn": "贝尔弗中心",
        "rss": GNEWS_US.format(domain="belfercenter.org"),
        "icon": "https://www.belfercenter.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "哈佛肯尼迪学院安全与科技政策"
    },
    {
        "name": "Jamestown Foundation",
        "name_cn": "詹姆斯敦基金会",
        "rss": GNEWS_US.format(domain="jamestown.org"),
        "icon": "https://jamestown.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "欧亚安全与地缘政治分析"
    },
    {
        "name": "Manhattan Institute",
        "name_cn": "曼哈顿研究所",
        "rss": "https://www.manhattan-institute.org/rss.xml",
        "icon": "https://www.manhattan-institute.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "城市、经济与社会政策"
    },
    {
        "name": "Migration Policy Institute",
        "name_cn": "移民政策研究所",
        "rss": "https://www.migrationpolicy.org/rss.xml",
        "icon": "https://www.migrationpolicy.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "移民与难民政策研究"
    },
    {
        "name": "Aspen Institute",
        "name_cn": "阿斯彭研究所",
        "rss": "https://www.aspeninstitute.org/feed/",
        "icon": "https://www.aspeninstitute.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "领导力、民主与全球议题"
    },
    {
        "name": "National Bureau of Asian Research",
        "name_cn": "美国国家亚洲研究局",
        "rss": GNEWS_US.format(domain="nbr.org"),
        "icon": "https://www.nbr.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "亚洲安全与经济政策"
    },
    {
        "name": "Center for Strategic and Budgetary Assessments",
        "name_cn": "战略与预算评估中心",
        "rss": GNEWS_SITE.format(domain="csbaonline.org"),
        "icon": "https://csbaonline.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "美国国防预算与军事战略"
    },
    {
        "name": "R Street Institute",
        "name_cn": "R街研究所",
        "rss": GNEWS_SITE.format(domain="rstreet.org"),
        "icon": "https://www.rstreet.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "自由市场公共政策"
    },
    {
        "name": "Third Way",
        "name_cn": "第三条道路",
        "rss": GNEWS_SITE.format(domain="thirdway.org"),
        "icon": "https://www.thirdway.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "中间派进步政策"
    },
    {
        "name": "Information Technology and Innovation Foundation",
        "name_cn": "信息技术与创新基金会",
        "rss": GNEWS_SITE.format(domain="itif.org"),
        "icon": "https://www.itif.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "科技创新与产业政策"
    },
    {
        "name": "Bipartisan Policy Center",
        "name_cn": "两党政策中心",
        "rss": GNEWS.format(domain="bipartisanpolicy.org"),
        "icon": "https://bipartisanpolicy.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "跨党派公共政策对话"
    },
    {
        "name": "East-West Center",
        "name_cn": "东西方中心",
        "rss": GNEWS.format(domain="eastwestcenter.org"),
        "icon": "https://www.eastwestcenter.org/favicon.ico",
        "category": "美国智库",
        "country": "美国",
        "priority": 2,
        "description": "亚太与美国关系研究"
    },

    # 加拿大智库
    {
        "name": "Centre for International Governance Innovation",
        "name_cn": "国际治理创新中心",
        "rss": GNEWS.format(domain="cigionline.org"),
        "icon": "https://www.cigionline.org/favicon.ico",
        "category": "加拿大智库",
        "country": "加拿大",
        "priority": 1,
        "description": "国际治理与数字经济研究"
    },
    {
        "name": "Canadian Global Affairs Institute",
        "name_cn": "加拿大全球事务研究所",
        "rss": GNEWS.format(domain="cgai.ca"),
        "icon": "https://www.cgai.ca/favicon.ico",
        "category": "加拿大智库",
        "country": "加拿大",
        "priority": 1,
        "description": "加拿大外交与国防政策"
    },
    {
        "name": "Macdonald-Laurier Institute",
        "name_cn": "麦克唐纳-劳里尔研究所",
        "rss": GNEWS.format(domain="macdonaldlaurier.ca"),
        "icon": "https://www.macdonaldlaurier.ca/favicon.ico",
        "category": "加拿大智库",
        "country": "加拿大",
        "priority": 2,
        "description": "加拿大公共政策与国家安全"
    },
    {
        "name": "C.D. Howe Institute",
        "name_cn": "C.D.豪研究所",
        "rss": GNEWS.format(domain="cdhowe.org"),
        "icon": "https://www.cdhowe.org/favicon.ico",
        "category": "加拿大智库",
        "country": "加拿大",
        "priority": 2,
        "description": "加拿大经济与社会政策"
    },
    {
        "name": "Fraser Institute",
        "name_cn": "弗雷泽研究所",
        "rss": GNEWS.format(domain="fraserinstitute.org"),
        "icon": "https://www.fraserinstitute.org/favicon.ico",
        "category": "加拿大智库",
        "country": "加拿大",
        "priority": 2,
        "description": "自由市场与公共政策研究"
    },
    {
        "name": "Institute for Research on Public Policy",
        "name_cn": "公共政策研究研究所",
        "rss": GNEWS.format(domain="irpp.org"),
        "icon": "https://irpp.org/favicon.ico",
        "category": "加拿大智库",
        "country": "加拿大",
        "priority": 2,
        "description": "加拿大社会与经济政策"
    },
    {
        "name": "Asia Pacific Foundation of Canada",
        "name_cn": "加拿大亚太基金会",
        "rss": GNEWS.format(domain="asiapacific.ca"),
        "icon": "https://www.asiapacific.ca/favicon.ico",
        "category": "加拿大智库",
        "country": "加拿大",
        "priority": 2,
        "description": "加拿大与亚太关系"
    },
    {
        "name": "The Conference Board of Canada",
        "name_cn": "加拿大Conference Board",
        "rss": GNEWS.format(domain="conferenceboard.ca"),
        "icon": "https://www.conferenceboard.ca/favicon.ico",
        "category": "加拿大智库",
        "country": "加拿大",
        "priority": 2,
        "description": "加拿大经济与企业研究"
    },

    # ==================== 欧洲地区 ====================
    # 英国智库
    {
        "name": "Chatham House",
        "name_cn": "查塔姆研究所",
        "rss": GNEWS.format(domain="chathamhouse.org"),
        "icon": "https://www.chathamhouse.org/favicon.ico",
        "category": "英国智库",
        "country": "英国",
        "priority": 1,
        "description": "英国皇家国际事务研究所"
    },
    {
        "name": "International Institute for Strategic Studies",
        "name_cn": "国际战略研究所",
        "rss": GNEWS_SITE.format(domain="iiss.org"),
        "icon": "https://www.iiss.org/favicon.ico",
        "category": "英国智库",
        "country": "英国",
        "priority": 1,
        "description": "军事与战略研究"
    },
    {
        "name": "Royal United Services Institute",
        "name_cn": "英国皇家三军联合研究所",
        "rss": GNEWS.format(domain="rusi.org"),
        "icon": "https://rusi.org/favicon.ico",
        "category": "英国智库",
        "country": "英国",
        "priority": 1,
        "description": "国防与安全研究"
    },
    {
        "name": "Overseas Development Institute",
        "name_cn": "海外发展研究所",
        "rss": GNEWS.format(domain="odi.org"),
        "icon": "https://odi.org/favicon.ico",
        "category": "英国智库",
        "country": "英国",
        "priority": 2,
        "description": "国际发展研究"
    },
    {
        "name": "Policy Exchange",
        "name_cn": "政策交流",
        "rss": GNEWS.format(domain="policyexchange.org.uk"),
        "icon": "https://policyexchange.org.uk/favicon.ico",
        "category": "英国智库",
        "country": "英国",
        "priority": 2,
        "description": "英国政策研究"
    },
    {
        "name": "Institute for Government",
        "name_cn": "政府研究所",
        "rss": GNEWS.format(domain="instituteforgovernment.org.uk"),
        "icon": "https://www.instituteforgovernment.org.uk/favicon.ico",
        "category": "英国智库",
        "country": "英国",
        "priority": 2,
        "description": "政府治理研究"
    },
    {
        "name": "Centre for Economic Policy Research",
        "name_cn": "经济政策研究中心",
        "rss": GNEWS.format(domain="cepr.org"),
        "icon": "https://cepr.org/favicon.ico",
        "category": "英国智库",
        "country": "英国",
        "priority": 2,
        "description": "欧洲经济研究网络"
    },
    {
        "name": "Adam Smith Institute",
        "name_cn": "亚当·斯密研究所",
        "rss": GNEWS.format(domain="adamsmith.org"),
        "icon": "https://www.adamsmith.org/favicon.ico",
        "category": "英国智库",
        "country": "英国",
        "priority": 2,
        "description": "自由市场与古典自由主义"
    },

    # 德国智库
    {
        "name": "German Council on Foreign Relations",
        "name_cn": "德国外交关系委员会",
        "rss": GNEWS.format(domain="dgap.org"),
        "icon": "https://dgap.org/favicon.ico",
        "category": "德国智库",
        "country": "德国",
        "priority": 1,
        "description": "德国外交政策研究"
    },
    {
        "name": "Stiftung Wissenschaft und Politik",
        "name_cn": "德国国际与安全事务研究所",
        "rss": GNEWS.format(domain="swp-berlin.org"),
        "icon": "https://www.swp-berlin.org/favicon.ico",
        "category": "德国智库",
        "country": "德国",
        "priority": 1,
        "description": "德国顶级安全政策智库"
    },
    {
        "name": "Mercator Institute for China Studies",
        "name_cn": "墨卡托中国研究中心",
        "rss": GNEWS.format(domain="merics.org"),
        "icon": "https://merics.org/favicon.ico",
        "category": "德国智库",
        "country": "德国",
        "priority": 2,
        "description": "中国政治经济研究"
    },
    {
        "name": "Kiel Institute for the World Economy",
        "name_cn": "基尔世界经济研究所",
        "rss": GNEWS.format(domain="ifw-kiel.de"),
        "icon": "https://www.ifw-kiel.de/favicon.ico",
        "category": "德国智库",
        "country": "德国",
        "priority": 2,
        "description": "国际经济研究"
    },
    {
        "name": "ifo Institute",
        "name_cn": "伊福经济研究所",
        "rss": GNEWS.format(domain="ifo.de"),
        "icon": "https://www.ifo.de/favicon.ico",
        "category": "德国智库",
        "country": "德国",
        "priority": 2,
        "description": "德国经济景气与政策分析"
    },
    {
        "name": "German Institute for Economic Research",
        "name_cn": "德国经济研究所",
        "rss": GNEWS.format(domain="diw.de"),
        "icon": "https://www.diw.de/favicon.ico",
        "category": "德国智库",
        "country": "德国",
        "priority": 2,
        "description": "德国宏观经济与社会政策"
    },
    {
        "name": "Konrad Adenauer Foundation",
        "name_cn": "康拉德·阿登纳基金会",
        "rss": GNEWS.format(domain="kas.de"),
        "icon": "https://www.kas.de/favicon.ico",
        "category": "德国智库",
        "country": "德国",
        "priority": 2,
        "description": "德国外交与民主推广"
    },
    {
        "name": "Bertelsmann Stiftung",
        "name_cn": "贝塔斯曼基金会",
        "rss": GNEWS.format(domain="bti-project.org"),
        "icon": "https://www.bti-project.org/favicon.ico",
        "category": "德国智库",
        "country": "德国",
        "priority": 2,
        "description": "全球治理与转型指数"
    },

    # 法国智库
    {
        "name": "French Institute of International Relations",
        "name_cn": "法国国际关系研究所",
        "rss": GNEWS.format(domain="ifri.org"),
        "icon": "https://www.ifri.org/favicon.ico",
        "category": "法国智库",
        "country": "法国",
        "priority": 1,
        "description": "法国顶级国际关系智库"
    },
    {
        "name": "Foundation for Strategic Research",
        "name_cn": "法国战略研究基金会",
        "rss": GNEWS.format(domain="frstrategie.org"),
        "icon": "https://www.frstrategie.org/favicon.ico",
        "category": "法国智库",
        "country": "法国",
        "priority": 2,
        "description": "法国国防与战略研究"
    },
    {
        "name": "Institute for International and Strategic Relations",
        "name_cn": "法国国际与战略关系研究所",
        "rss": GNEWS.format(domain="iris-france.org"),
        "icon": "https://www.iris-france.org/favicon.ico",
        "category": "法国智库",
        "country": "法国",
        "priority": 2,
        "description": "法国外交与安全政策"
    },
    {
        "name": "Institut Montaigne",
        "name_cn": "蒙田研究所",
        "rss": GNEWS.format(domain="institutmontaigne.org"),
        "icon": "https://www.institutmontaigne.org/favicon.ico",
        "category": "法国智库",
        "country": "法国",
        "priority": 2,
        "description": "法国独立公共政策研究"
    },

    # 意大利智库
    {
        "name": "Istituto Affari Internazionali",
        "name_cn": "国际事务研究院",
        "rss": GNEWS.format(domain="iai.it"),
        "icon": "https://www.iai.it/favicon.ico",
        "category": "意大利智库",
        "country": "意大利",
        "priority": 1,
        "description": "意大利国际事务研究"
    },
    {
        "name": "Italian Institute for International Political Studies",
        "name_cn": "意大利国际政治研究学会",
        "rss": GNEWS.format(domain="ispionline.it"),
        "icon": "https://www.ispionline.it/favicon.ico",
        "category": "意大利智库",
        "country": "意大利",
        "priority": 2,
        "description": "地中海与欧洲安全研究"
    },
    {
        "name": "LUISS School of Government",
        "name_cn": "LUISS政府学院",
        "rss": GNEWS.format(domain="luiss.it"),
        "icon": "https://www.luiss.it/favicon.ico",
        "category": "意大利智库",
        "country": "意大利",
        "priority": 2,
        "description": "意大利政治与欧洲治理"
    },

    # 瑞典智库
    {
        "name": "Stockholm International Peace Research Institute",
        "name_cn": "斯德哥尔摩国际和平研究所",
        "rss": GNEWS.format(domain="sipri.org"),
        "icon": "https://www.sipri.org/favicon.ico",
        "category": "瑞典智库",
        "country": "瑞典",
        "priority": 1,
        "description": "全球和平与安全研究权威"
    },
    {
        "name": "Swedish Institute of International Affairs",
        "name_cn": "瑞典国际事务研究所",
        "rss": GNEWS.format(domain="ui.se"),
        "icon": "https://www.ui.se/favicon.ico",
        "category": "瑞典智库",
        "country": "瑞典",
        "priority": 2,
        "description": "北欧外交与安全政策"
    },
    {
        "name": "FOI Swedish Defence Research Agency",
        "name_cn": "瑞典国防研究局",
        "rss": GNEWS_SITE.format(domain="foi.se"),
        "icon": "https://www.foi.se/favicon.ico",
        "category": "瑞典智库",
        "country": "瑞典",
        "priority": 2,
        "description": "国防技术与安全研究"
    },
    {
        "name": "Stockholm Free World Forum",
        "name_cn": "斯德哥尔摩自由世界论坛",
        "rss": GNEWS.format(domain="frivarld.se"),
        "icon": "https://frivarld.se/favicon.ico",
        "category": "瑞典智库",
        "country": "瑞典",
        "priority": 2,
        "description": "民主、安全与地缘政治"
    },

    # 荷兰智库
    {
        "name": "Netherlands Institute of International Relations",
        "name_cn": "荷兰国际关系研究所",
        "rss": GNEWS.format(domain="clingendael.org"),
        "icon": "https://www.clingendael.org/favicon.ico",
        "category": "荷兰智库",
        "country": "荷兰",
        "priority": 2,
        "description": "荷兰顶级外交与安全智库"
    },
    {
        "name": "The Hague Centre for Strategic Studies",
        "name_cn": "海牙战略研究中心",
        "rss": GNEWS.format(domain="hcss.nl"),
        "icon": "https://hcss.nl/favicon.ico",
        "category": "荷兰智库",
        "country": "荷兰",
        "priority": 2,
        "description": "地缘政治与安全分析"
    },
    {
        "name": "Netherlands Scientific Council for Government Policy",
        "name_cn": "荷兰政府科学委员会",
        "rss": GNEWS_SITE.format(domain="wrr.nl"),
        "icon": "https://www.wrr.nl/favicon.ico",
        "category": "荷兰智库",
        "country": "荷兰",
        "priority": 2,
        "description": "荷兰长期政策研究"
    },

    # 西班牙智库
    {
        "name": "Elcano Royal Institute",
        "name_cn": "埃尔卡诺皇家研究所",
        "rss": GNEWS.format(domain="realinstitutoelcano.org"),
        "icon": "https://www.realinstitutoelcano.org/favicon.ico",
        "category": "西班牙智库",
        "country": "西班牙",
        "priority": 2,
        "description": "西班牙国际关系与欧洲研究"
    },
    {
        "name": "Barcelona Centre for International Affairs",
        "name_cn": "巴塞罗那国际事务中心",
        "rss": GNEWS.format(domain="cidob.org"),
        "icon": "https://www.cidob.org/favicon.ico",
        "category": "西班牙智库",
        "country": "西班牙",
        "priority": 2,
        "description": "地中海与全球治理"
    },

    # 挪威智库
    {
        "name": "Norwegian Institute of International Affairs",
        "name_cn": "挪威国际事务研究所",
        "rss": GNEWS.format(domain="nupi.no"),
        "icon": "https://www.nupi.no/favicon.ico",
        "category": "挪威智库",
        "country": "挪威",
        "priority": 2,
        "description": "北极、安全与和平研究"
    },
    {
        "name": "Fridtjof Nansen Institute",
        "name_cn": "弗里乔夫·南森研究所",
        "rss": GNEWS.format(domain="fni.no"),
        "icon": "https://www.fni.no/favicon.ico",
        "category": "挪威智库",
        "country": "挪威",
        "priority": 2,
        "description": "北极、能源与环境政策"
    },

    # 瑞士智库
    {
        "name": "Center for Security Studies",
        "name_cn": "苏黎世安全研究中心",
        "rss": GNEWS.format(domain="css.ethz.ch"),
        "icon": "https://css.ethz.ch/favicon.ico",
        "category": "瑞士智库",
        "country": "瑞士",
        "priority": 2,
        "description": "ETH苏黎世安全与战略研究"
    },
    {
        "name": "Avenir Suisse",
        "name_cn": "瑞士未来基金会",
        "rss": GNEWS.format(domain="avenir-suisse.ch"),
        "icon": "https://www.avenir-suisse.ch/favicon.ico",
        "category": "瑞士智库",
        "country": "瑞士",
        "priority": 2,
        "description": "瑞士经济与社会改革"
    },

    # 波兰智库
    {
        "name": "Polish Institute of International Affairs",
        "name_cn": "波兰国际事务研究所",
        "rss": GNEWS.format(domain="pism.pl"),
        "icon": "https://www.pism.pl/favicon.ico",
        "category": "波兰智库",
        "country": "波兰",
        "priority": 2,
        "description": "中东欧安全与欧盟政策"
    },
    {
        "name": "Centre for Eastern Studies",
        "name_cn": "东方研究中心",
        "rss": GNEWS.format(domain="osw.waw.pl"),
        "icon": "https://www.osw.waw.pl/favicon.ico",
        "category": "波兰智库",
        "country": "波兰",
        "priority": 2,
        "description": "东欧与俄罗斯研究"
    },

    # 奥地利智库
    {
        "name": "Institute for Human Sciences",
        "name_cn": "人文科学研究所",
        "rss": GNEWS.format(domain="iwm.at"),
        "icon": "https://www.iwm.at/favicon.ico",
        "category": "奥地利智库",
        "country": "奥地利",
        "priority": 2,
        "description": "中欧思想与公共政策"
    },
    {
        "name": "Austrian Institute of Economic Research",
        "name_cn": "奥地利经济研究所",
        "rss": GNEWS.format(domain="wifo.ac.at"),
        "icon": "https://www.wifo.ac.at/favicon.ico",
        "category": "奥地利智库",
        "country": "奥地利",
        "priority": 2,
        "description": "奥地利宏观经济分析"
    },

    # 比利时智库（欧盟）
    {
        "name": "Bruegel",
        "name_cn": "布鲁盖尔研究所",
        "rss": GNEWS.format(domain="bruegel.org"),
        "icon": "https://www.bruegel.org/favicon.ico",
        "category": "欧盟智库",
        "country": "比利时",
        "priority": 1,
        "description": "欧洲经济政策研究"
    },
    {
        "name": "Centre for European Policy Studies",
        "name_cn": "欧洲政策研究中心",
        "rss": GNEWS.format(domain="ceps.eu"),
        "icon": "https://www.ceps.eu/favicon.ico",
        "category": "欧盟智库",
        "country": "比利时",
        "priority": 2,
        "description": "欧盟政策研究"
    },
    {
        "name": "Egmont Institute",
        "name_cn": "埃格蒙特研究所",
        "rss": GNEWS.format(domain="egmontinstitute.be"),
        "icon": "https://www.egmontinstitute.be/favicon.ico",
        "category": "欧盟智库",
        "country": "比利时",
        "priority": 2,
        "description": "欧盟外交与非洲政策"
    },

    # ==================== 亚洲地区 ====================
    # 日本智库
    {
        "name": "Japan Institute of International Affairs",
        "name_cn": "日本国际问题研究所",
        "rss": GNEWS.format(domain="jiia.or.jp"),
        "icon": "https://www.jiia.or.jp/favicon.ico",
        "category": "日本智库",
        "country": "日本",
        "priority": 2,
        "description": "日本顶级国际关系智库"
    },
    {
        "name": "Asia Pacific Initiative",
        "name_cn": "亚太倡议",
        "rss": GNEWS.format(domain="apinitiative.org"),
        "icon": "https://apinitiative.org/favicon.ico",
        "category": "日本智库",
        "country": "日本",
        "priority": 2,
        "description": "亚太地区政策研究"
    },
    {
        "name": "Tokyo Foundation for Policy Research",
        "name_cn": "东京政策研究基金会",
        "rss": GNEWS_SITE.format(domain="tkfd.or.jp"),
        "icon": "https://www.tkfd.or.jp/favicon.ico",
        "category": "日本智库",
        "country": "日本",
        "priority": 2,
        "description": "日本外交与经济政策"
    },
    {
        "name": "Research Institute of Economy Trade and Industry",
        "name_cn": "日本经济产业研究所",
        "rss": GNEWS.format(domain="rieti.go.jp"),
        "icon": "https://www.rieti.go.jp/favicon.ico",
        "category": "日本智库",
        "country": "日本",
        "priority": 2,
        "description": "日本产业政策与创新"
    },
    {
        "name": "National Institute for Defense Studies",
        "name_cn": "日本防卫研究所",
        "rss": GNEWS.format(domain="nids.mod.go.jp"),
        "icon": "https://www.nids.mod.go.jp/favicon.ico",
        "category": "日本智库",
        "country": "日本",
        "priority": 2,
        "description": "日本防卫与安全战略"
    },

    # 韩国智库
    {
        "name": "Asan Institute for Policy Studies",
        "name_cn": "峨山政策研究院",
        "rss": GNEWS.format(domain="asaninst.org"),
        "icon": "https://en.asaninst.org/favicon.ico",
        "category": "韩国智库",
        "country": "韩国",
        "priority": 1,
        "description": "韩国顶级政策研究机构"
    },
    {
        "name": "Korea Institute for International Economic Policy",
        "name_cn": "韩国对外经济政策研究院",
        "rss": GNEWS.format(domain="kiep.go.kr"),
        "icon": "https://www.kiep.go.kr/favicon.ico",
        "category": "韩国智库",
        "country": "韩国",
        "priority": 2,
        "description": "国际经济政策研究"
    },
    {
        "name": "Korea Institute for National Unification",
        "name_cn": "韩国统一研究院",
        "rss": GNEWS.format(domain="kinu.or.kr"),
        "icon": "https://www.kinu.or.kr/favicon.ico",
        "category": "韩国智库",
        "country": "韩国",
        "priority": 2,
        "description": "朝鲜半岛统一与安全"
    },
    {
        "name": "Sejong Institute",
        "name_cn": "世宗研究所",
        "rss": GNEWS_SITE.format(domain="sejong.org"),
        "icon": "https://www.sejong.org/favicon.ico",
        "category": "韩国智库",
        "country": "韩国",
        "priority": 2,
        "description": "韩国外交与安全战略"
    },
    {
        "name": "Korea Development Institute",
        "name_cn": "韩国开发研究院",
        "rss": GNEWS.format(domain="kdi.re.kr"),
        "icon": "https://www.kdi.re.kr/favicon.ico",
        "category": "韩国智库",
        "country": "韩国",
        "priority": 2,
        "description": "韩国宏观经济与发展政策"
    },
    {
        "name": "Korea Economic Research Institute",
        "name_cn": "韩国经济研究院",
        "rss": GNEWS_SITE.format(domain="keri.org"),
        "icon": "https://www.keri.org/favicon.ico",
        "category": "韩国智库",
        "country": "韩国",
        "priority": 2,
        "description": "韩国产业与经济政策"
    },

    # 印度智库
    {
        "name": "Observer Research Foundation",
        "name_cn": "观察家研究基金会",
        "rss": GNEWS.format(domain="orfonline.org"),
        "icon": "https://www.orfonline.org/favicon.ico",
        "category": "印度智库",
        "country": "印度",
        "priority": 1,
        "description": "印度顶级智库"
    },
    {
        "name": "Gateway House",
        "name_cn": "门楼印度委员会",
        "rss": GNEWS.format(domain="gatewayhouse.in"),
        "icon": "https://www.gatewayhouse.in/favicon.ico",
        "category": "印度智库",
        "country": "印度",
        "priority": 2,
        "description": "印度外交与经济政策"
    },
    {
        "name": "Centre for Policy Research",
        "name_cn": "政策研究中心",
        "rss": GNEWS_SITE.format(domain="cprindia.org"),
        "icon": "https://cprindia.org/favicon.ico",
        "category": "印度智库",
        "country": "印度",
        "priority": 2,
        "description": "印度公共政策研究"
    },
    {
        "name": "Institute for Defence Studies and Analyses",
        "name_cn": "国防研究与分析研究所",
        "rss": GNEWS.format(domain="idsa.in"),
        "icon": "https://www.idsa.in/favicon.ico",
        "category": "印度智库",
        "country": "印度",
        "priority": 1,
        "description": "印度国防与战略研究"
    },
    {
        "name": "United Service Institution of India",
        "name_cn": "印度联合服务学会",
        "rss": GNEWS.format(domain="usiofindia.org"),
        "icon": "https://www.usiofindia.org/favicon.ico",
        "category": "印度智库",
        "country": "印度",
        "priority": 2,
        "description": "印度军事与安全事务"
    },
    {
        "name": "Carnegie India",
        "name_cn": "卡内基印度中心",
        "rss": GNEWS.format(domain="carnegieindia.org"),
        "icon": "https://carnegieindia.org/favicon.ico",
        "category": "印度智库",
        "country": "印度",
        "priority": 2,
        "description": "印度外交与科技政策"
    },

    # 印度尼西亚智库
    {
        "name": "Centre for Strategic and International Studies Jakarta",
        "name_cn": "雅加达战略与国际问题研究中心",
        "rss": GNEWS.format(domain="csis.or.id"),
        "icon": "https://www.csis.or.id/favicon.ico",
        "category": "印度尼西亚智库",
        "country": "印度尼西亚",
        "priority": 2,
        "description": "东南亚最大智库之一"
    },
    {
        "name": "Institute for Development of Economics and Finance",
        "name_cn": "印尼经济财政发展研究所",
        "rss": GNEWS.format(domain="indef.or.id"),
        "icon": "https://indef.or.id/favicon.ico",
        "category": "印度尼西亚智库",
        "country": "印度尼西亚",
        "priority": 2,
        "description": "印尼经济与发展政策"
    },

    # 马来西亚智库
    {
        "name": "Institute of Strategic and International Studies Malaysia",
        "name_cn": "马来西亚战略与国际问题研究所",
        "rss": GNEWS.format(domain="isis.org.my"),
        "icon": "https://www.isis.org.my/favicon.ico",
        "category": "马来西亚智库",
        "country": "马来西亚",
        "priority": 2,
        "description": "马来西亚外交与经济政策"
    },

    # 泰国智库
    {
        "name": "Thailand Development Research Institute",
        "name_cn": "泰国发展研究所",
        "rss": GNEWS.format(domain="tdri.or.th"),
        "icon": "https://www.tdri.or.th/favicon.ico",
        "category": "泰国智库",
        "country": "泰国",
        "priority": 2,
        "description": "泰国经济与发展政策"
    },

    # 菲律宾智库
    {
        "name": "Stratbase ADR Institute",
        "name_cn": "Stratbase战略研究所",
        "rss": GNEWS.format(domain="stratbase.org"),
        "icon": "https://stratbase.org/favicon.ico",
        "category": "菲律宾智库",
        "country": "菲律宾",
        "priority": 2,
        "description": "菲律宾外交与安全政策"
    },

    # 越南智库
    {
        "name": "Diplomatic Academy of Vietnam",
        "name_cn": "越南外交学院",
        "rss": GNEWS.format(domain="dav.edu.vn"),
        "icon": "https://dav.edu.vn/favicon.ico",
        "category": "越南智库",
        "country": "越南",
        "priority": 2,
        "description": "越南外交与国际关系"
    },

    # 巴基斯坦智库
    {
        "name": "Institute of Strategic Studies Islamabad",
        "name_cn": "伊斯兰堡战略研究所",
        "rss": GNEWS.format(domain="issi.org.pk"),
        "icon": "https://issi.org.pk/favicon.ico",
        "category": "巴基斯坦智库",
        "country": "巴基斯坦",
        "priority": 2,
        "description": "巴基斯坦安全与外交"
    },

    # 伊朗智库
    {
        "name": "Institute for Iran-Eurasia Studies",
        "name_cn": "伊朗欧亚研究所",
        "rss": GNEWS.format(domain="irstudies.org"),
        "icon": "https://irstudies.org/favicon.ico",
        "category": "伊朗智库",
        "country": "伊朗",
        "priority": 2,
        "description": "伊朗地区与外交研究"
    },

    # 新加坡智库
    {
        "name": "ISEAS-Yusof Ishak Institute",
        "name_cn": "尤索夫伊萨东南亚研究院",
        "rss": GNEWS.format(domain="iseas.edu.sg"),
        "icon": "https://www.iseas.edu.sg/favicon.ico",
        "category": "新加坡智库",
        "country": "新加坡",
        "priority": 2,
        "description": "东南亚研究权威"
    },
    {
        "name": "S. Rajaratnam School of International Studies",
        "name_cn": "拉惹勒南国际研究院",
        "rss": GNEWS.format(domain="rsis.edu.sg"),
        "icon": "https://www.rsis.edu.sg/favicon.ico",
        "category": "新加坡智库",
        "country": "新加坡",
        "priority": 2,
        "description": "安全与战略研究"
    },
    {
        "name": "Lee Kuan Yew School of Public Policy",
        "name_cn": "李光耀公共政策学院",
        "rss": GNEWS.format(domain="lkyspp.nus.edu.sg"),
        "icon": "https://lkyspp.nus.edu.sg/favicon.ico",
        "category": "新加坡智库",
        "country": "新加坡",
        "priority": 2,
        "description": "亚洲公共政策与治理"
    },

    # ==================== 中东地区 ====================
    # 以色列智库
    {
        "name": "Institute for National Security Studies",
        "name_cn": "国家安全研究所",
        "rss": GNEWS.format(domain="inss.org.il"),
        "icon": "https://www.inss.org.il/favicon.ico",
        "category": "以色列智库",
        "country": "以色列",
        "priority": 2,
        "description": "以色列安全与战略研究"
    },
    {
        "name": "Begin-Sadat Center for Strategic Studies",
        "name_cn": "贝京-萨达特战略研究中心",
        "rss": GNEWS.format(domain="besacenter.org"),
        "icon": "https://besacenter.org/favicon.ico",
        "category": "以色列智库",
        "country": "以色列",
        "priority": 2,
        "description": "中东战略研究"
    },
    {
        "name": "Mitvim Institute",
        "name_cn": "Mitvim外交政策研究所",
        "rss": GNEWS.format(domain="mitvim.org.il"),
        "icon": "https://mitvim.org.il/favicon.ico",
        "category": "以色列智库",
        "country": "以色列",
        "priority": 2,
        "description": "以色列进步派外交政策"
    },

    # 沙特智库
    {
        "name": "King Faisal Center for Research and Islamic Studies",
        "name_cn": "费萨尔国王研究中心",
        "rss": GNEWS.format(domain="kfcris.com"),
        "icon": "https://kfcris.com/favicon.ico",
        "category": "沙特智库",
        "country": "沙特阿拉伯",
        "priority": 2,
        "description": "伊斯兰世界研究"
    },
    {
        "name": "King Abdullah Petroleum Studies and Research Center",
        "name_cn": "阿卜杜拉石油研究智库",
        "rss": GNEWS.format(domain="kapsarc.org"),
        "icon": "https://www.kapsarc.org/favicon.ico",
        "category": "沙特智库",
        "country": "沙特阿拉伯",
        "priority": 2,
        "description": "能源经济与气候政策"
    },

    # 阿联酋智库
    {
        "name": "Emirates Policy Center",
        "name_cn": "阿联酋政策中心",
        "rss": GNEWS.format(domain="epc.ae"),
        "icon": "https://epc.ae/favicon.ico",
        "category": "阿联酋智库",
        "country": "阿联酋",
        "priority": 2,
        "description": "中东政策研究"
    },
    {
        "name": "Emirates Center for Strategic Studies and Research",
        "name_cn": "阿联酋战略研究与中心",
        "rss": GNEWS.format(domain="ecssr.ae"),
        "icon": "https://ecssr.ae/favicon.ico",
        "category": "阿联酋智库",
        "country": "阿联酋",
        "priority": 2,
        "description": "海湾安全与战略研究"
    },
    {
        "name": "TRENDS Research and Advisory",
        "name_cn": "TRENDS研究与咨询",
        "rss": GNEWS.format(domain="trendsresearch.org"),
        "icon": "https://trendsresearch.org/favicon.ico",
        "category": "阿联酋智库",
        "country": "阿联酋",
        "priority": 2,
        "description": "中东地缘政治分析"
    },

    # 卡塔尔智库
    {
        "name": "Arab Center for Research and Policy Studies",
        "name_cn": "阿拉伯研究与政策研究中心",
        "rss": GNEWS.format(domain="dohainstitute.org"),
        "icon": "https://www.dohainstitute.org/favicon.ico",
        "category": "卡塔尔智库",
        "country": "卡塔尔",
        "priority": 2,
        "description": "阿拉伯世界研究"
    },

    # 土耳其智库
    {
        "name": "Center for Economics and Foreign Policy Studies",
        "name_cn": "经济与外交政策研究中心",
        "rss": GNEWS.format(domain="edam.org.tr"),
        "icon": "https://edam.org.tr/favicon.ico",
        "category": "土耳其智库",
        "country": "土耳其",
        "priority": 2,
        "description": "土耳其外交政策"
    },
    {
        "name": "Foundation for Political Economic and Social Research",
        "name_cn": "SETA基金会",
        "rss": GNEWS.format(domain="setav.org"),
        "icon": "https://www.setav.org/favicon.ico",
        "category": "土耳其智库",
        "country": "土耳其",
        "priority": 2,
        "description": "土耳其外交与安全研究"
    },

    # 埃及智库
    {
        "name": "Al-Ahram Center for Political and Strategic Studies",
        "name_cn": "金字塔政治与战略研究中心",
        "rss": GNEWS.format(domain="acpss.ahram.org.eg"),
        "icon": "http://www.ahram.org.eg/favicon.ico",
        "category": "埃及智库",
        "country": "埃及",
        "priority": 2,
        "description": "埃及与中东战略研究"
    },

    # ==================== 大洋洲地区 ====================
    # 澳大利亚智库
    {
        "name": "Lowy Institute",
        "name_cn": "罗伊研究所",
        "rss": GNEWS.format(domain="lowyinstitute.org"),
        "icon": "https://www.lowyinstitute.org/favicon.ico",
        "category": "澳大利亚智库",
        "country": "澳大利亚",
        "priority": 1,
        "description": "澳大利亚顶级智库"
    },
    {
        "name": "Australian Strategic Policy Institute",
        "name_cn": "澳大利亚战略政策研究所",
        "rss": GNEWS.format(domain="aspi.org.au"),
        "icon": "https://www.aspi.org.au/favicon.ico",
        "category": "澳大利亚智库",
        "country": "澳大利亚",
        "priority": 2,
        "description": "战略与防务研究"
    },
    {
        "name": "Grattan Institute",
        "name_cn": "格拉顿研究所",
        "rss": GNEWS.format(domain="grattan.edu.au"),
        "icon": "https://grattan.edu.au/favicon.ico",
        "category": "澳大利亚智库",
        "country": "澳大利亚",
        "priority": 2,
        "description": "公共政策研究"
    },
    {
        "name": "United States Studies Centre",
        "name_cn": "美国研究中心",
        "rss": GNEWS.format(domain="ussc.edu.au"),
        "icon": "https://www.ussc.edu.au/favicon.ico",
        "category": "澳大利亚智库",
        "country": "澳大利亚",
        "priority": 2,
        "description": "澳美关系与印太战略"
    },

    # 新西兰智库
    {
        "name": "New Zealand Institute of International Affairs",
        "name_cn": "新西兰国际事务研究所",
        "rss": GNEWS_SITE.format(domain="nziia.org.nz"),
        "icon": "https://www.nziia.org.nz/favicon.ico",
        "category": "新西兰智库",
        "country": "新西兰",
        "priority": 2,
        "description": "新西兰外交政策"
    },

    # ==================== 拉丁美洲 ====================
    # 巴西智库
    {
        "name": "Fundação Getulio Vargas",
        "name_cn": "热图利奥·瓦加斯基金会",
        "rss": GNEWS.format(domain="fgv.br"),
        "icon": "https://portal.fgv.br/favicon.ico",
        "category": "巴西智库",
        "country": "巴西",
        "priority": 1,
        "description": "巴西经济与社会政策"
    },
    {
        "name": "Brazilian Center for International Relations",
        "name_cn": "巴西国际关系中心",
        "rss": GNEWS.format(domain="cebri.org"),
        "icon": "https://cebri.org/favicon.ico",
        "category": "巴西智库",
        "country": "巴西",
        "priority": 1,
        "description": "巴西外交政策"
    },
    {
        "name": "Institute of Applied Economic Research",
        "name_cn": "巴西应用经济研究所",
        "rss": GNEWS.format(domain="ipea.gov.br"),
        "icon": "https://www.ipea.gov.br/favicon.ico",
        "category": "巴西智库",
        "country": "巴西",
        "priority": 2,
        "description": "巴西宏观经济与公共政策"
    },
    {
        "name": "Alexandre de Gusmão Foundation",
        "name_cn": "亚历山大·古斯芒基金会",
        "rss": GNEWS.format(domain="funag.gov.br"),
        "icon": "https://funag.gov.br/favicon.ico",
        "category": "巴西智库",
        "country": "巴西",
        "priority": 2,
        "description": "巴西外交与国际关系"
    },

    # 阿根廷智库
    {
        "name": "Argentine Council for International Relations",
        "name_cn": "阿根廷国际关系委员会",
        "rss": GNEWS.format(domain="cari.org.ar"),
        "icon": "https://www.cari.org.ar/favicon.ico",
        "category": "阿根廷智库",
        "country": "阿根廷",
        "priority": 2,
        "description": "阿根廷国际关系研究"
    },
    {
        "name": "Centro de Estudios de Estado y Sociedad",
        "name_cn": "国家与社会研究中心",
        "rss": GNEWS.format(domain="cedes.org"),
        "icon": "https://www.cedes.org/favicon.ico",
        "category": "阿根廷智库",
        "country": "阿根廷",
        "priority": 2,
        "description": "阿根廷公共政策研究"
    },

    # 智利智库
    {
        "name": "Libertad y Desarrollo",
        "name_cn": "自由与发展研究所",
        "rss": GNEWS.format(domain="lyd.org"),
        "icon": "https://www.lyd.org/favicon.ico",
        "category": "智利智库",
        "country": "智利",
        "priority": 2,
        "description": "智利经济与社会政策"
    },
    {
        "name": "Centro de Estudios Publicos",
        "name_cn": "智利公共研究中心",
        "rss": GNEWS.format(domain="cepchile.cl"),
        "icon": "https://www.cepchile.cl/favicon.ico",
        "category": "智利智库",
        "country": "智利",
        "priority": 2,
        "description": "智利政治经济研究"
    },

    # 哥伦比亚智库
    {
        "name": "Fedesarrollo",
        "name_cn": "哥伦比亚发展基金会",
        "rss": GNEWS.format(domain="fedesarrollo.org.co"),
        "icon": "https://www.fedesarrollo.org.co/favicon.ico",
        "category": "哥伦比亚智库",
        "country": "哥伦比亚",
        "priority": 2,
        "description": "哥伦比亚经济与发展"
    },

    # 墨西哥智库
    {
        "name": "Mexican Council on Foreign Relations",
        "name_cn": "墨西哥外交关系委员会",
        "rss": GNEWS.format(domain="consejomexicano.org"),
        "icon": "https://www.consejomexicano.org/favicon.ico",
        "category": "墨西哥智库",
        "country": "墨西哥",
        "priority": 2,
        "description": "墨西哥外交政策"
    },
    {
        "name": "Mexican Institute for Competitiveness",
        "name_cn": "墨西哥竞争力研究所",
        "rss": GNEWS.format(domain="imco.org.mx"),
        "icon": "https://imco.org.mx/favicon.ico",
        "category": "墨西哥智库",
        "country": "墨西哥",
        "priority": 2,
        "description": "墨西哥经济改革与治理"
    },

    # ==================== 非洲地区 ====================
    # 南非智库
    {
        "name": "South African Institute of International Affairs",
        "name_cn": "南非国际事务研究所",
        "rss": GNEWS.format(domain="saiia.org.za"),
        "icon": "https://saiia.org.za/favicon.ico",
        "category": "南非智库",
        "country": "南非",
        "priority": 2,
        "description": "非洲国际关系研究"
    },
    {
        "name": "Institute for Security Studies",
        "name_cn": "安全研究所",
        "rss": GNEWS.format(domain="issafrica.org"),
        "icon": "https://issafrica.org/favicon.ico",
        "category": "南非智库",
        "country": "南非",
        "priority": 2,
        "description": "非洲安全研究"
    },

    # 尼日利亚智库
    {
        "name": "Nigerian Institute of International Affairs",
        "name_cn": "尼日利亚国际事务研究所",
        "rss": GNEWS_SITE.format(domain="niia.gov.ng"),
        "icon": "https://niia.gov.ng/favicon.ico",
        "category": "尼日利亚智库",
        "country": "尼日利亚",
        "priority": 2,
        "description": "尼日利亚外交政策"
    },

    # 肯尼亚智库
    {
        "name": "Kenya Institute for Public Policy Research and Analysis",
        "name_cn": "肯尼亚公共政策研究与分析研究所",
        "rss": GNEWS.format(domain="kippra.or.ke"),
        "icon": "https://www.kippra.or.ke/favicon.ico",
        "category": "肯尼亚智库",
        "country": "肯尼亚",
        "priority": 1,
        "description": "肯尼亚国家级政策智库"
    },
    {
        "name": "Institute of Economic Affairs Kenya",
        "name_cn": "肯尼亚经济事务研究所",
        "rss": GNEWS.format(domain="ieakenya.or.ke"),
        "icon": "https://www.ieakenya.or.ke/favicon.ico",
        "category": "肯尼亚智库",
        "country": "肯尼亚",
        "priority": 2,
        "description": "肯尼亚经济改革与治理研究"
    },
    {
        "name": "Partnership for African Social and Governance Research",
        "name_cn": "非洲社会治理研究伙伴组织",
        "rss": GNEWS.format(domain="pasgr.org"),
        "icon": "https://www.pasgr.org/favicon.ico",
        "category": "肯尼亚智库",
        "country": "肯尼亚",
        "priority": 2,
        "description": "非洲公共政策与社会研究"
    },

    # ==================== 国际组织 & 多边机构 ====================
    {
        "name": "International Crisis Group",
        "name_cn": "国际危机组织",
        "rss": GNEWS.format(domain="crisisgroup.org"),
        "icon": "https://www.crisisgroup.org/favicon.ico",
        "category": "国际组织",
        "country": "国际",
        "priority": 1,
        "description": "冲突预防与解决"
    },
    {
        "name": "International Committee of the Red Cross",
        "name_cn": "红十字国际委员会",
        "rss": GNEWS.format(domain="icrc.org"),
        "icon": "https://www.icrc.org/favicon.ico",
        "category": "国际组织",
        "country": "国际",
        "priority": 1,
        "description": "国际人道主义与冲突地区研究"
    },
    {
        "name": "Amnesty International",
        "name_cn": "大赦国际",
        "rss": GNEWS.format(domain="amnesty.org"),
        "icon": "https://www.amnesty.org/favicon.ico",
        "category": "国际组织",
        "country": "国际",
        "priority": 1,
        "description": "人权研究与倡导"
    },
    {
        "name": "Human Rights Watch",
        "name_cn": "人权观察",
        "rss": GNEWS.format(domain="hrw.org"),
        "icon": "https://www.hrw.org/favicon.ico",
        "category": "国际组织",
        "country": "国际",
        "priority": 1,
        "description": "全球人权调查与报告"
    },
    {
        "name": "United Nations University",
        "name_cn": "联合国大学",
        "rss": GNEWS.format(domain="unu.edu"),
        "icon": "https://unu.edu/favicon.ico",
        "category": "国际组织",
        "country": "国际",
        "priority": 2,
        "description": "全球治理与发展研究"
    },
    {
        "name": "OECD",
        "name_cn": "经合组织",
        "rss": GNEWS.format(domain="oecd.org"),
        "icon": "https://www.oecd.org/favicon.ico",
        "category": "国际组织",
        "country": "国际",
        "priority": 2,
        "description": "国际经济政策与合作"
    },
    {
        "name": "European Council on Foreign Relations",
        "name_cn": "欧洲对外关系委员会",
        "rss": "https://ecfr.eu/feed/",
        "icon": "https://ecfr.eu/favicon.ico",
        "category": "国际组织",
        "country": "国际",
        "priority": 1,
        "description": "欧洲外交政策与全球秩序"
    },
    {
        "name": "World Bank",
        "name_cn": "世界银行",
        "rss": gnews_en('site:worldbank.org (report OR "Working Paper" OR publication OR blog) when:30d'),
        "icon": "https://www.worldbank.org/favicon.ico",
        "category": "国际组织",
        "country": "国际",
        "priority": 1,
        "description": "世界银行报告与工作论文流"
    },
    {
        "name": "International Monetary Fund",
        "name_cn": "国际货币基金组织",
        "rss": gnews_en('site:imf.org ("Working Paper" OR Blog OR "Staff Discussion" OR "World Economic Outlook") when:30d'),
        "icon": "https://www.imf.org/favicon.ico",
        "category": "国际组织",
        "country": "国际",
        "priority": 1,
        "description": "IMF 工作论文、博客与 WEO 等报告流"
    },
    {
        "name": "United Nations Development Programme",
        "name_cn": "联合国开发计划署",
        "rss": GNEWS.format(domain="undp.org"),
        "icon": "https://www.undp.org/favicon.ico",
        "category": "国际组织",
        "country": "国际",
        "priority": 1,
        "description": "全球可持续发展"
    },
    {
        "name": "NATO",
        "name_cn": "北约",
        "rss": GNEWS.format(domain="nato.int"),
        "icon": "https://www.nato.int/favicon.ico",
        "category": "国际组织",
        "country": "国际",
        "priority": 1,
        "description": "跨大西洋安全与防务"
    },
    {
        "name": "Carnegie Europe",
        "name_cn": "卡内基欧洲中心",
        "rss": GNEWS.format(domain="carnegieeurope.eu"),
        "icon": "https://carnegieeurope.eu/favicon.ico",
        "category": "国际组织",
        "country": "国际",
        "priority": 2,
        "description": "欧洲外交与全球民主"
    },


    # ==================== 硬核原始文件 / 数据与机构报告流 ====================
    {
        "name": "WTO News",
        "name_cn": "世界贸易组织",
        "rss": "https://www.wto.org/library/rss/latest_news_e.xml",
        "icon": "https://www.wto.org/favicon.ico",
        "category": "国际组织",
        "country": "国际",
        "priority": 1,
        "description": "WTO 新闻与贸易政策动态（官方 RSS）"
    },
    {
        "name": "UN News",
        "name_cn": "联合国新闻",
        "rss": "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
        "icon": "https://news.un.org/favicon.ico",
        "category": "国际组织",
        "country": "国际",
        "priority": 1,
        "description": "联合国新闻中心官方 RSS"
    },
    {
        "name": "WHO News",
        "name_cn": "世界卫生组织",
        "rss": "https://www.who.int/rss-feeds/news-english.xml",
        "icon": "https://www.who.int/favicon.ico",
        "category": "国际组织",
        "country": "国际",
        "priority": 2,
        "description": "WHO 新闻与全球卫生政策"
    },
    {
        "name": "IEA Reports",
        "name_cn": "国际能源署·报告",
        "rss": gnews_en('site:iea.org (report OR analysis OR outlook OR "World Energy") when:30d'),
        "icon": "https://www.iea.org/favicon.ico",
        "category": "国际组织",
        "country": "国际",
        "priority": 1,
        "description": "IEA 能源报告与展望（官网 RSS 不稳定，报告向查询）"
    },
    {
        "name": "BIS Research",
        "name_cn": "国际清算银行",
        "rss": gnews_en('site:bis.org (working paper OR speech OR bulletin OR quarterly) when:30d'),
        "icon": "https://www.bis.org/favicon.ico",
        "category": "经济政策",
        "country": "国际",
        "priority": 1,
        "description": "BIS 工作论文、演讲与季报"
    },
    {
        "name": "Federal Reserve Press",
        "name_cn": "美联储·新闻",
        "rss": "https://www.federalreserve.gov/feeds/press_all.xml",
        "icon": "https://www.federalreserve.gov/favicon.ico",
        "category": "经济政策",
        "country": "美国",
        "priority": 1,
        "description": "美联储新闻稿官方 RSS"
    },
    {
        "name": "ECB Press",
        "name_cn": "欧洲央行·新闻",
        "rss": "https://www.ecb.europa.eu/rss/press.html",
        "icon": "https://www.ecb.europa.eu/favicon.ico",
        "category": "经济政策",
        "country": "国际",
        "priority": 1,
        "description": "欧洲央行新闻稿官方 RSS"
    },

    # ==================== 认知类网站 ====================
    {
        "name": "Project Syndicate",
        "name_cn": "报业辛迪加",
        "rss": "https://www.project-syndicate.org/rss",
        "icon": "https://www.project-syndicate.org/favicon.ico",
        "category": "认知网站",
        "country": "国际",
        "priority": 1,
        "description": "全球知名评论网站"
    },
    {
        "name": "Foreign Affairs",
        "name_cn": "外交事务",
        "rss": "https://www.foreignaffairs.com/feed",
        "icon": "https://www.foreignaffairs.com/favicon.ico",
        "category": "认知网站",
        "country": "美国",
        "priority": 1,
        "description": "顶级国际关系期刊"
    },
    {
        "name": "Foreign Policy",
        "name_cn": "外交政策",
        "rss": "https://foreignpolicy.com/feed/",
        "icon": "https://foreignpolicy.com/favicon.ico",
        "category": "认知网站",
        "country": "美国",
        "priority": 1,
        "description": "国际政治与政策"
    },
    {
        "name": "The Economist",
        "name_cn": "经济学人",
        "rss": "https://www.economist.com/feeds/print-sections/77/business.xml",
        "icon": "https://www.economist.com/favicon.ico",
        "category": "认知网站",
        "country": "英国",
        "priority": 1,
        "description": "全球政治经济分析"
    },
    {
        "name": "Harvard Kennedy School",
        "name_cn": "哈佛肯尼迪学院",
        "rss": "https://www.hks.harvard.edu/rss.xml",
        "icon": "https://www.harvard.edu/favicon.ico",
        "category": "认知网站",
        "country": "美国",
        "priority": 2,
        "description": "公共政策研究"
    },
    {
        "name": "MIT Technology Review",
        "name_cn": "麻省理工科技评论",
        "rss": "https://www.technologyreview.com/feed/",
        "icon": "https://www.technologyreview.com/favicon.ico",
        "category": "认知网站",
        "country": "美国",
        "priority": 2,
        "description": "科技创新分析"
    },
    {
        "name": "Wired",
        "name_cn": "连线杂志",
        "rss": "https://www.wired.com/feed/rss",
        "icon": "https://www.wired.com/favicon.ico",
        "category": "认知网站",
        "country": "美国",
        "priority": 2,
        "description": "科技与文化"
    },
    {
        "name": "Aeon",
        "name_cn": "万古杂志",
        "rss": "https://aeon.co/feed.rss",
        "icon": "https://aeon.co/favicon.ico",
        "category": "认知网站",
        "country": "国际",
        "priority": 2,
        "description": "深度思想与文化"
    },
    {
        "name": "Quartz",
        "name_cn": "石英",
        "rss": "https://qz.com/feed",
        "icon": "https://qz.com/favicon.ico",
        "category": "认知网站",
        "country": "美国",
        "priority": 2,
        "description": "商业与科技"
    },
    {
        "name": "Stratfor",
        "name_cn": "斯特拉福战略预测",
        "rss": "https://worldview.stratfor.com/rss.xml",
        "icon": "https://www.stratfor.com/favicon.ico",
        "category": "认知网站",
        "country": "美国",
        "priority": 1,
        "description": "地缘政治分析"
    },

    # ==================== 顶级学术期刊 ====================
    {
        "name": "Nature",
        "name_cn": "自然",
        "rss": "https://www.nature.com/nature.rss",
        "icon": "https://www.nature.com/favicon.ico",
        "category": "学术期刊",
        "country": "英国",
        "priority": 1,
        "description": "顶级科学期刊"
    },
    {
        "name": "Science",
        "name_cn": "科学",
        "rss": "https://www.sciencemag.org/rss/news_current.xml",
        "icon": "https://www.sciencemag.org/favicon.ico",
        "category": "学术期刊",
        "country": "美国",
        "priority": 1,
        "description": "顶级科学期刊"
    },
    {
        "name": "The Lancet",
        "name_cn": "柳叶刀",
        "rss": "https://www.thelancet.com/rss",
        "icon": "https://www.thelancet.com/favicon.ico",
        "category": "学术期刊",
        "country": "英国",
        "priority": 2,
        "description": "顶级医学期刊"
    },

    # ==================== 经济与政策分析 ====================
    {
        "name": "Peterson Institute for International Economics",
        "name_cn": "彼得森国际经济研究所",
        "rss": GNEWS_US.format(domain="piie.com"),
        "icon": "https://www.piie.com/favicon.ico",
        "category": "经济政策",
        "country": "美国",
        "priority": 1,
        "description": "国际经济政策"
    },
    {
        "name": "National Bureau of Economic Research",
        "name_cn": "美国国家经济研究局",
        "rss": "https://www.nber.org/rss/new.xml",
        "icon": "https://www.nber.org/favicon.ico",
        "category": "经济政策",
        "country": "美国",
        "priority": 2,
        "description": "经济研究权威"
    },
    # ==================== 补强：科技、安全与新兴力量 ====================
    {
        "name": "Vivekananda International Foundation",
        "name_cn": "维韦卡南达国际基金会",
        "rss": GNEWS.format(domain="vifindia.org"),
        "icon": "https://www.vifindia.org/favicon.ico",
        "category": "印度智库",
        "country": "印度",
        "priority": 2,
        "description": "印度核心国家安全与战略决策智库"
    },
    {
        "name": "The Diplomat",
        "name_cn": "外交官杂志",
        "rss": "https://thediplomat.com/feed/",
        "icon": "https://thediplomat.com/favicon.ico",
        "category": "认知网站",
        "country": "国际",
        "priority": 1,
        "description": "深度观察亚太地区政治、安全与文化的权威窗口"
    },
    {
        "name": "War on the Rocks",
        "name_cn": "岩石上的战争",
        "rss": "https://warontherocks.com/feed/",
        "icon": "https://warontherocks.com/favicon.ico",
        "category": "认知网站",
        "country": "美国",
        "priority": 1,
        "description": "职业战略家、军官和学者的高质量讨论平台"
    }
]


# ---------------------------------------------------------------------------
# 补充源（财报 / 研报 / 白皮书 / 政策 / 论文 / 数据 / 公告 / 媒体）
# ---------------------------------------------------------------------------
from sources_extra import EXTRA_SOURCES

_EXISTING_NAMES = {s["name"] for s in THINK_TANKS_CONFIG}
for _src in EXTRA_SOURCES:
    if _src["name"] not in _EXISTING_NAMES:
        THINK_TANKS_CONFIG.append(_src)


# 按国家/地区统计
def get_country_stats():
    stats = {}
    for tank in THINK_TANKS_CONFIG:
        country = tank.get("country", "其他")
        stats[country] = stats.get(country, 0) + 1
    return stats


# ---------- 文体（文档类型）----------
DOC_TYPE_LABELS = {
    "think_tank": "智库",
    "earnings": "财报",
    "research": "研报",
    "whitepaper": "白皮书",
    "policy": "政策文件",
    "paper": "科学论文",
    "media": "媒体",
    "data": "数据发布",
    "announcement": "公司公告",
}

# 兼容旧字段名
SOURCE_TYPE_LABELS = DOC_TYPE_LABELS

# ---------- 领域 ----------
DOMAIN_LABELS = {
    "geopolitics": "地缘",
    "industry": "产业",
    "macro": "宏观金融",
    "tech": "科技",
    "energy": "能源气候",
    "health": "卫生健康",
    "general": "综合",
}

# 本周议题词表
TOPIC_LEXICON = [
    {"id": "taiwan", "label": "台海", "patterns": ["台海", "两岸", "台湾海峡", "Taiwan Strait", "Taiwan"]},
    {"id": "sanctions", "label": "制裁", "patterns": ["制裁", "sanctions", "Sanction", "出口管制", "export control"]},
    {"id": "ai", "label": "AI", "patterns": ["人工智能", "大模型", "生成式", "ChatGPT", "generative AI", "AI", "A.I."]},
    {"id": "ukraine", "label": "俄乌", "patterns": ["乌克兰", "俄乌", "Ukraine", "Russia-Ukraine", "克里米亚"]},
    {"id": "middle_east", "label": "中东", "patterns": ["加沙", "以色列", "伊朗", "哈马斯", "中东", "Gaza", "Israel", "Iran", "Hamas"]},
    {"id": "south_china_sea", "label": "南海", "patterns": ["南海", "南中国海", "South China Sea"]},
    {"id": "trade", "label": "贸易", "patterns": ["关税", "贸易战", "供应链", "关税壁垒", "tariff", "trade war", "supply chain"]},
    {"id": "climate", "label": "气候", "patterns": ["气候", "碳中和", "减排", "climate", "net zero", "decarbon"]},
    {"id": "energy", "label": "能源", "patterns": ["能源", "石油", "天然气", "OPEC", "energy", "oil price", "LNG"]},
    {"id": "chip", "label": "芯片", "patterns": ["芯片", "半导体", "晶圆", "semiconductor", "chip", "TSMC", "ASML"]},
    {"id": "nato", "label": "北约", "patterns": ["北约", "NATO"]},
    {"id": "fed", "label": "美联储", "patterns": ["美联储", "降息", "加息", "Federal Reserve", "interest rate", "FOMC"]},
    {"id": "eu", "label": "欧洲", "patterns": ["欧盟", "欧洲央行", "European Union", "ECB", "Brussels"]},
    {"id": "korea", "label": "半岛", "patterns": ["朝核", "朝鲜", "半岛", "North Korea", "Kim Jong"]},
    {"id": "asean", "label": "东盟", "patterns": ["东盟", "东南亚", "ASEAN", "Southeast Asia"]},
    {"id": "india", "label": "印度", "patterns": ["印度", "印太", "India", "Indo-Pacific"]},
    {"id": "cyber", "label": "网络", "patterns": ["网络安全", "网络攻击", "cyber", "ransomware", "黑客"]},
    {"id": "space", "label": "太空", "patterns": ["太空", "航天", "卫星", "space force", "satellite"]},
]


def get_doc_type(feed_or_category):
    """解析文体。可传入源 dict，或旧的 category 字符串。"""
    if isinstance(feed_or_category, dict):
        explicit = feed_or_category.get("doc_type") or feed_or_category.get("source_type")
        if explicit in DOC_TYPE_LABELS:
            return explicit
        category = feed_or_category.get("category", "其他")
        name = (feed_or_category.get("name") or "").lower()
        name_cn = feed_or_category.get("name_cn") or ""
    else:
        category = feed_or_category or "其他"
        name = ""
        name_cn = ""

    # 显式 category 映射
    if category in ("政策文件", "官方文件"):
        return "policy"
    if category in ("财报",):
        return "earnings"
    if category in ("公司公告",):
        return "announcement"
    if category in ("研报", "经济政策"):
        return "research"
    if category in ("白皮书", "国际组织"):
        return "whitepaper"
    if category in ("科学论文", "学术期刊"):
        return "paper"
    if category in ("数据发布",):
        return "data"
    if category in ("媒体", "认知网站"):
        return "media"

    # 新闻机构更像媒体
    media_hints = (
        "people", "xinhua", "china daily", "ft chinese", "scmp", "caixin",
        "sinocism", "reuters", "techcrunch", "verge", "wired", "quartz",
        "project syndicate", "foreign affairs", "foreign policy",
    )
    if any(h in name for h in media_hints) or any(
        h in name_cn for h in ("人民网", "新华", "中国日报", "财新", "南华")
    ):
        return "media"

    # 期刊
    if any(h in name for h in ("nature", "science", "lancet", "nejm", "pnas", "arxiv", "biorxiv")):
        return "paper"

    # 央行/数据机构
    if any(h in name for h in ("federal reserve", "ecb", "bls", "bea", "nber", "bis")):
        if "press" in name or "news" in name:
            return "announcement" if "sec" in name else "data"
        return "research"

    if category == "国际组织":
        return "whitepaper"
    return "think_tank"


def get_domain(feed_or_category):
    """解析领域。"""
    if isinstance(feed_or_category, dict):
        explicit = feed_or_category.get("domain")
        if explicit in DOMAIN_LABELS:
            return explicit
        category = feed_or_category.get("category", "")
        country = feed_or_category.get("country", "")
        name = (feed_or_category.get("name") or "").lower()
        desc = (feed_or_category.get("description") or "") + category
    else:
        category = feed_or_category or ""
        country = ""
        name = ""
        desc = category

    text = f"{name} {desc} {category}".lower()
    if any(k in text for k in ("health", "lancet", "nejm", "biorxiv", "医学", "卫生", "疫情")):
        return "health"
    if any(k in text for k in ("energy", "iea", "oil", "气候", "碳", "ipcc", "climate")):
        return "energy"
    if any(k in text for k in ("arxiv", "ai", "tech", "半导体", "芯片", "science", "nature", "pnas", "verge", "techcrunch")):
        return "tech"
    if any(k in text for k in ("fed", "imf", "world bank", "oecd", "nber", "bls", "bea", "宏观", "金融", "econ", "piie", "cf40")):
        return "macro"
    if any(k in text for k in ("industry", "mckinsey", "deloitte", "miit", "产业", "制造", "sec 8-k", "cninfo", "财报")):
        return "industry"
    if category in ("经济政策", "数据发布", "研报", "财报"):
        return "macro"
    if category in ("科学论文", "学术期刊"):
        return "tech"
    if category in ("白皮书",) and "气候" in desc:
        return "energy"
    if category in ("媒体", "国际媒体", "新闻"):
        return "general"
    if "智库" in category or category in ("政策文件", "官方文件"):
        return "geopolitics"
    return "general"


def get_doc_type_label(feed_or_category):
    return DOC_TYPE_LABELS.get(get_doc_type(feed_or_category), "智库")


def get_domain_label(feed_or_category):
    return DOMAIN_LABELS.get(get_domain(feed_or_category), "综合")


# 兼容旧 API
def get_source_type(category):
    return get_doc_type(category)


def get_source_type_label(category):
    return get_doc_type_label(category)


def get_category_stats():
    stats = {}
    for tank in THINK_TANKS_CONFIG:
        category = tank.get("category", "其他")
        stats[category] = stats.get(category, 0) + 1
    return stats


def get_doc_type_stats():
    stats = {}
    for tank in THINK_TANKS_CONFIG:
        dt = get_doc_type(tank)
        stats[dt] = stats.get(dt, 0) + 1
    return stats


def get_domain_stats():
    stats = {}
    for tank in THINK_TANKS_CONFIG:
        d = get_domain(tank)
        stats[d] = stats.get(d, 0) + 1
    return stats


def enrich_source(feed):
    """为源配置补全文体/领域字段（不改原 dict 引用副作用：会写回）。"""
    feed["doc_type"] = get_doc_type(feed)
    feed["doc_type_label"] = DOC_TYPE_LABELS[feed["doc_type"]]
    feed["domain"] = get_domain(feed)
    feed["domain_label"] = DOMAIN_LABELS[feed["domain"]]
    # 兼容旧前端字段
    feed["source_type"] = feed["doc_type"]
    feed["source_type_label"] = feed["doc_type_label"]
    return feed


for _feed in THINK_TANKS_CONFIG:
    enrich_source(_feed)
