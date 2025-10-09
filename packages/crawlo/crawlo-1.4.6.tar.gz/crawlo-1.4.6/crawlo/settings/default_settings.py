# -*- coding:UTF-8 -*-
"""
默认配置文件
包含 Crawlo 框架的所有默认设置项
"""
# 添加环境变量配置工具导入
from crawlo.utils.env_config import get_redis_config, get_runtime_config, get_version

# --------------------------------- 1. 框架基础配置 ------------------------------------

# 框架初始化控制
FRAMEWORK_INIT_ORDER = [
    'log_system',  # 日志系统
    'settings_system',  # 配置系统
    'core_components',  # 核心组件
    'extensions',  # 扩展组件
    'full_initialization'  # 完全初始化
]
FRAMEWORK_INIT_STATE = 'uninitialized'

# 项目基础配置
runtime_config = get_runtime_config()
PROJECT_NAME = runtime_config['PROJECT_NAME']  # 项目名称（用于日志、Redis Key 等标识）
VERSION = get_version()  # 项目版本号 - 从框架的__version__.py文件中读取，如果不存在则使用默认值
RUN_MODE = runtime_config['CRAWLO_MODE']  # 运行模式：standalone/distributed/auto
CONCURRENCY = runtime_config['CONCURRENCY']  # 并发数配置

# 爬虫模块配置
SPIDER_MODULES = []  # 爬虫模块列表
SPIDER_LOADER_WARN_ONLY = False  # 爬虫加载器是否只警告不报错

# --------------------------------- 2. 爬虫核心配置 ------------------------------------

# 下载器配置
DOWNLOADER = "crawlo.downloader.httpx_downloader.HttpXDownloader"  # 默认下载器
DOWNLOAD_DELAY = 0.5  # 请求延迟（秒）
RANDOMNESS = True  # 是否启用随机延迟
RANDOM_RANGE = [0.5, 1.5]  # 随机延迟范围因子，实际延迟 = DOWNLOAD_DELAY * RANDOM_RANGE[0] 到 DOWNLOAD_DELAY * RANDOM_RANGE[1]

# 调度器配置
DEPTH_PRIORITY = 1  # 深度优先级（负数表示深度优先，正数表示广度优先）
SCHEDULER_MAX_QUEUE_SIZE = 5000  # 调度器队列最大大小
BACKPRESSURE_RATIO = 0.9  # 背压触发阈值（队列大小达到最大容量的90%时触发背压控制）

# 请求生成控制
REQUEST_GENERATION_BATCH_SIZE = 10  # 请求生成批处理大小
REQUEST_GENERATION_INTERVAL = 0.01  # 请求生成间隔（秒）
ENABLE_CONTROLLED_REQUEST_GENERATION = False  # 是否启用受控请求生成

# 队列配置
QUEUE_TYPE = 'auto'  # 队列类型：memory/redis/auto
# SCHEDULER_QUEUE_NAME = f"crawlo:{PROJECT_NAME}:queue:requests"  # 调度器队列名称（遵循统一命名规范）
QUEUE_MAX_RETRIES = 3  # 队列操作最大重试次数
QUEUE_TIMEOUT = 300  # 队列操作超时时间（秒）

# --------------------------------- 3. 数据库和过滤器配置 ------------------------------------

# MySQL配置
MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'
MYSQL_DB = 'crawl_pro'
MYSQL_TABLE = 'crawlo'
MYSQL_BATCH_SIZE = 100
MYSQL_USE_BATCH = False  # 是否启用批量插入
# MySQL SQL生成行为控制配置
MYSQL_AUTO_UPDATE = False  # 是否使用 REPLACE INTO（完全覆盖已存在记录）
MYSQL_INSERT_IGNORE = False  # 是否使用 INSERT IGNORE（忽略重复数据）
MYSQL_UPDATE_COLUMNS = ()  # 冲突时需更新的列名；指定后 MYSQL_AUTO_UPDATE 失效

# Redis配置
redis_config = get_redis_config()
REDIS_HOST = redis_config['REDIS_HOST']
REDIS_PORT = redis_config['REDIS_PORT']
REDIS_PASSWORD = redis_config['REDIS_PASSWORD']
REDIS_DB = redis_config['REDIS_DB']

# 根据是否有密码生成不同的 URL 格式
if REDIS_PASSWORD:
    REDIS_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
else:
    REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# Redis key命名规范已封装到框架内部组件中，用户无需手动配置：
# - 请求去重: crawlo:{PROJECT_NAME}:filter:fingerprint
# - 数据项去重: crawlo:{PROJECT_NAME}:item:fingerprint
# - 请求队列: crawlo:{PROJECT_NAME}:queue:requests
# - 处理中队列: crawlo:{PROJECT_NAME}:queue:processing
# - 失败队列: crawlo:{PROJECT_NAME}:queue:failed

REDIS_TTL = 0  # 指纹过期时间（0 表示永不过期）
CLEANUP_FP = 0  # 程序结束时是否清理指纹（0=不清理）
FILTER_DEBUG = True  # 是否开启去重调试日志
DECODE_RESPONSES = True  # Redis 返回是否解码为字符串

# 过滤器配置
DEFAULT_DEDUP_PIPELINE = 'crawlo.pipelines.memory_dedup_pipeline.MemoryDedupPipeline'  # 默认使用内存过滤器和去重管道
FILTER_CLASS = 'crawlo.filters.memory_filter.MemoryFilter'

# Bloom过滤器配置
BLOOM_FILTER_CAPACITY = 1000000  # Bloom过滤器容量
BLOOM_FILTER_ERROR_RATE = 0.001  # Bloom过滤器错误率

# --------------------------------- 4. 中间件配置 ------------------------------------

# 框架中间件列表（框架默认中间件 + 用户自定义中间件）
MIDDLEWARES = [
    # === 请求预处理阶段 ===
    'crawlo.middleware.request_ignore.RequestIgnoreMiddleware',  # 1. 忽略无效请求
    'crawlo.middleware.download_delay.DownloadDelayMiddleware',  # 2. 控制请求频率
    'crawlo.middleware.default_header.DefaultHeaderMiddleware',  # 3. 添加默认请求头
    'crawlo.middleware.offsite.OffsiteMiddleware',  # 5. 站外请求过滤

    # === 响应处理阶段 ===
    'crawlo.middleware.retry.RetryMiddleware',  # 6. 失败请求重试
    'crawlo.middleware.response_code.ResponseCodeMiddleware',  # 7. 处理特殊状态码
    'crawlo.middleware.response_filter.ResponseFilterMiddleware',  # 8. 响应内容过滤
]

# --------------------------------- 5. 管道配置 ------------------------------------

# 框架数据处理管道列表（框架默认管道 + 用户自定义管道）
PIPELINES = [
    'crawlo.pipelines.console_pipeline.ConsolePipeline',
]

# --------------------------------- 6. 扩展配置 ------------------------------------

# 框架扩展组件列表（框架默认扩展 + 用户自定义扩展）
EXTENSIONS = [
    'crawlo.extension.log_interval.LogIntervalExtension',  # 定时日志
    'crawlo.extension.log_stats.LogStats',  # 统计信息
    'crawlo.extension.logging_extension.CustomLoggerExtension',  # 自定义日志
]

# --------------------------------- 7. 日志与监控配置 ------------------------------------

# 日志配置
LOG_LEVEL = None  # 日志级别: DEBUG/INFO/WARNING/ERROR，默认为None，由用户在项目settings中设置
STATS_DUMP = True  # 是否周期性输出统计信息
LOG_FILE = None  # 日志文件路径，将在项目配置中设置
LOG_FORMAT = '%(asctime)s - [%(name)s] - %(levelname)s: %(message)s'
LOG_ENCODING = 'utf-8'
LOG_MAX_BYTES = 10 * 1024 * 1024  # 日志轮转大小（字节）
LOG_BACKUP_COUNT = 5  # 日志备份数量

# 日志间隔配置
INTERVAL = 60  # 日志输出间隔（秒）

# 内存监控配置
MEMORY_MONITOR_ENABLED = False  # 是否启用内存监控
MEMORY_MONITOR_INTERVAL = 60  # 内存监控检查间隔（秒）
MEMORY_WARNING_THRESHOLD = 80.0  # 内存使用率警告阈值（百分比）
MEMORY_CRITICAL_THRESHOLD = 90.0  # 内存使用率严重阈值（百分比）

# 性能分析配置
PERFORMANCE_PROFILER_ENABLED = False  # 是否启用性能分析
PERFORMANCE_PROFILER_OUTPUT_DIR = 'profiling'  # 性能分析输出目录
PERFORMANCE_PROFILER_INTERVAL = 300  # 性能分析间隔（秒）

# 健康检查配置
HEALTH_CHECK_ENABLED = True  # 是否启用健康检查

# --------------------------------- 8. 网络请求配置 ------------------------------------

# 默认请求头配置
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
}  # 默认请求头

# 默认User-Agent（使用现代浏览器的User-Agent）
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"

# 是否启用随机User-Agent功能（默认禁用，用户可根据需要启用）
RANDOM_USER_AGENT_ENABLED = False  # 是否启用随机用户代理

# 站外过滤配置
ALLOWED_DOMAINS = []  # 允许的域名列表

# 代理配置（通用版，支持静态代理列表和动态代理API两种模式）
PROXY_LIST = []  # 静态代理列表配置
PROXY_API_URL = ""  # 动态代理API配置
# 代理提取配置，用于指定如何从API返回的数据中提取代理地址
# 可选值：
# - 字符串：直接作为字段名使用，如 "proxy"（默认值）
# - 字典：包含type和value字段，支持多种提取方式
#   - {"type": "field", "value": "data"}：从指定字段提取
#   - {"type": "jsonpath", "value": "$.data[0].proxy"}：使用JSONPath表达式提取
#   - {"type": "custom", "function": your_function}：使用自定义函数提取
PROXY_EXTRACTOR = "proxy"  # 代理提取配置
# 代理失败处理配置
PROXY_MAX_FAILED_ATTEMPTS = 3  # 代理最大失败尝试次数，超过此次数将标记为失效

# 代理使用示例：
# 1. 静态代理列表：
#    PROXY_LIST = ["http://proxy1:8080", "http://proxy2:8080"]
#    PROXY_API_URL = ""  # 不使用动态代理
#
# 2. 动态代理API（默认字段提取）：
#    PROXY_LIST = []  # 不使用静态代理
#    PROXY_API_URL = "http://api.example.com/get_proxy"
#    PROXY_EXTRACTOR = "proxy"  # 从"proxy"字段提取
#
# 3. 动态代理API（自定义字段提取）：
#    PROXY_LIST = []  # 不使用静态代理
#    PROXY_API_URL = "http://api.example.com/get_proxy"
#    PROXY_EXTRACTOR = "data"  # 从"data"字段提取
#
# 4. 动态代理API（嵌套字段提取）：
#    PROXY_LIST = []  # 不使用静态代理
#    PROXY_API_URL = "http://api.example.com/get_proxy"
#    PROXY_EXTRACTOR = {"type": "field", "value": "result"}  # 从"result"字段提取

# 下载器通用配置
DOWNLOAD_TIMEOUT = 30  # 下载超时时间（秒）
VERIFY_SSL = True  # 是否验证SSL证书
CONNECTION_POOL_LIMIT = 100  # 连接池大小限制
CONNECTION_POOL_LIMIT_PER_HOST = 20  # 每个主机的连接池大小限制
DOWNLOAD_MAXSIZE = 10 * 1024 * 1024  # 最大下载大小（字节）
DOWNLOAD_STATS = True  # 是否启用下载统计
DOWNLOAD_WARN_SIZE = 1024 * 1024  # 下载警告大小（字节）
DOWNLOAD_RETRY_TIMES = 3  # 下载重试次数
MAX_RETRY_TIMES = 3  # 最大重试次数

# 下载器健康检查
DOWNLOADER_HEALTH_CHECK = True  # 是否启用下载器健康检查
HEALTH_CHECK_INTERVAL = 60  # 健康检查间隔（秒）
REQUEST_STATS_ENABLED = True  # 是否启用请求统计
STATS_RESET_ON_START = False  # 启动时是否重置统计

# HttpX 下载器专用配置
HTTPX_HTTP2 = True  # 是否启用HTTP/2支持
HTTPX_FOLLOW_REDIRECTS = True  # 是否自动跟随重定向

# AioHttp 下载器专用配置
AIOHTTP_AUTO_DECOMPRESS = True  # 是否自动解压响应
AIOHTTP_FORCE_CLOSE = False  # 是否强制关闭连接

# Curl-Cffi 特有配置
CURL_BROWSER_TYPE = "chrome"  # 浏览器指纹模拟（仅 CurlCffi 下载器有效）
CURL_BROWSER_VERSION_MAP = {  # 自定义浏览器版本映射（可覆盖默认行为）
    "chrome": "chrome136",
    "edge": "edge101",
    "safari": "safari184",
    "firefox": "firefox135",
}

# Selenium 下载器配置
SELENIUM_BROWSER_TYPE = "chrome"  # 浏览器类型: chrome, firefox, edge
SELENIUM_HEADLESS = True  # 是否无头模式
SELENIUM_TIMEOUT = 30  # 超时时间（秒）
SELENIUM_LOAD_TIMEOUT = 10  # 页面加载超时时间（秒）
SELENIUM_WINDOW_WIDTH = 1920  # 窗口宽度
SELENIUM_WINDOW_HEIGHT = 1080  # 窗口高度
SELENIUM_WAIT_FOR_ELEMENT = None  # 等待特定元素选择器
SELENIUM_ENABLE_JS = True  # 是否启用JavaScript
SELENIUM_PROXY = None  # 代理设置
SELENIUM_SINGLE_BROWSER_MODE = True  # 单浏览器多标签页模式
SELENIUM_MAX_TABS_PER_BROWSER = 10  # 单浏览器最大标签页数量

# Playwright 下载器配置
PLAYWRIGHT_BROWSER_TYPE = "chromium"  # 浏览器类型: chromium, firefox, webkit
PLAYWRIGHT_HEADLESS = True  # 是否无头模式
PLAYWRIGHT_TIMEOUT = 30000  # 超时时间（毫秒）
PLAYWRIGHT_LOAD_TIMEOUT = 10000  # 页面加载超时时间（毫秒）
PLAYWRIGHT_VIEWPORT_WIDTH = 1920  # 视口宽度
PLAYWRIGHT_VIEWPORT_HEIGHT = 1080  # 视口高度
PLAYWRIGHT_WAIT_FOR_ELEMENT = None  # 等待特定元素选择器
PLAYWRIGHT_PROXY = None  # 代理设置
PLAYWRIGHT_SINGLE_BROWSER_MODE = True  # 单浏览器多标签页模式
PLAYWRIGHT_MAX_PAGES_PER_BROWSER = 10  # 单浏览器最大页面数量

# 通用优化配置
CONNECTION_TTL_DNS_CACHE = 300  # DNS缓存TTL（秒）
CONNECTION_KEEPALIVE = True  # 是否启用HTTP连接保持