import os
import httpx
import asyncio
import json
import logging
import re
import unicodedata
import random
from typing import Optional, Dict, Any, Union
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY: Optional[str] = os.getenv("SERPER_API_KEY")
mcp = FastMCP("serper-mcp")

# 加载本地国家别名字典 (data/country_aliases.json)
# 简化索引：仅使用别名字典 ALIAS_MAP，并生成按字母序排列的别名列表 ALIAS_KEYS_SORTED。
# 使用自实现的 Quick Sort 对别名键进行排序，并用二分查找(binary search)做匹配查找。
ALIAS_MAP: Dict[str, str] = {}
ALIAS_KEYS_SORTED: list = []

_aliases_path = os.path.join(os.path.dirname(__file__), "data", "country_aliases.json")

# Quick Sort 实现（用于对别名字典键排序）
def quick_sort(arr: list) -> list:
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

# 二分查找（在已排序的列表中查找精确匹配）
def binary_search(arr: list, target: str) -> Optional[int]:
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return None

def normalize(text: str) -> str:
    """归一化国家/地区名称：NFKD、去重音、转小写、去标点、折叠空白"""
    if not text:
        return ""
    # Unicode normalize
    s = unicodedata.normalize("NFKD", text)
    # remove diacritics
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    # convert full-width to half-width and normalize spaces
    s = s.replace("\u3000", " ")
    s = s.strip().lower()
    # remove punctuation except spaces
    s = re.sub(r"[^\w\s'-]", " ", s, flags=re.UNICODE)
    # replace underscores and multiple spaces with single space
    s = re.sub(r"[_\s]+", " ", s).strip()
    return s

def _generate_variants(alias: str) -> set:
    """为 alias 生成若干变体以提高命中率（去标点、逗号重排等）"""
    variants = set()
    base = alias.strip()
    variants.add(base)
    # normalized base
    n = normalize(base)
    variants.add(n)
    # remove punctuation version
    variants.add(re.sub(r"[^\w\s]", "", n))
    # if contains comma, try reorder segments: "Korea, South" -> "south korea"
    if "," in base:
        parts = [p.strip() for p in base.split(",") if p.strip()]
        if len(parts) >= 2:
            reordered = " ".join(reversed(parts))
            variants.add(reordered)
            variants.add(normalize(reordered))
    # also add word-reordered variants for simple two-word names
    parts = n.split()
    if len(parts) == 2:
        variants.add(" ".join(reversed(parts)))
    return {v for v in variants if v}

try:
    with open(_aliases_path, "r", encoding="utf-8") as f:
        _forward = json.load(f)

    # 仅基于别名字典构建 ALIAS_MAP（normalized alias -> alpha2）
    for code, names in _forward.items():
        code_up = code.upper()
        if isinstance(names, list):
            iter_names = names
        else:
            iter_names = [names]
        for name in iter_names:
            if not isinstance(name, str):
                continue
            for variant in _generate_variants(name):
                key = normalize(variant)
                if not key:
                    continue
                # 后来的同名别名以最后一个为准（覆盖），保持简单明了
                ALIAS_MAP[key] = code_up

    # 使用 Quick Sort 对别名字典的键进行排序，供二分查找使用
    ALIAS_KEYS_SORTED = quick_sort(list(ALIAS_MAP.keys()))

except FileNotFoundError:
    logger.warning("国家别名字典未找到: %s", _aliases_path)
except Exception as e:
    logger.warning("加载国家别名字典失败: %s", e)

USER_AGENT = "serper_client/1.0"
API_ENDPOINTS = {
    "search": "https://google.serper.dev/search",
    "image_search": "https://google.serper.dev/images",
    "video_search": "https://google.serper.dev/videos",
    "place_search": "https://google.serper.dev/places",
    "maps_search": "https://google.serper.dev/maps",
    "news_search": "https://google.serper.dev/news",
    "lens_search": "https://google.serper.dev/lens",
    "scholar_search": "https://google.serper.dev/scholar",
    "shopping_search": "https://google.serper.dev/shopping",
    "patents_search": "https://google.serper.dev/patents",
    "scrape": "https://scrape.serper.dev",
}
HTTP_TIMEOUT = 30.0

# 并发与重试相关配置（可通过环境变量调整）
SERPER_MAX_CONNECTIONS = int(os.getenv("SERPER_MAX_CONNECTIONS", "200"))
SERPER_KEEPALIVE = int(os.getenv("SERPER_KEEPALIVE", "20"))
SERPER_HTTP2 = os.getenv("SERPER_HTTP2", "0") == "1"
# 如果启用了 HTTP/2，确保环境中安装了 h2；否则回退为 False，避免 httpx 抛出 ImportError
if SERPER_HTTP2:
    try:
        import h2  # noqa: F401
    except Exception:
        logger.warning("SERPER_HTTP2 设置为启用，但未检测到 'h2' 包。将自动禁用 HTTP/2（请安装 httpx[http2] 以启用）。")
        SERPER_HTTP2 = False

# Serper 后端总体并发上限为每秒 300 请求；将默认全局并发上限适当调高为 200（可通过环境变量调整）
SERPER_MAX_CONCURRENT_REQUESTS = int(os.getenv("SERPER_MAX_CONCURRENT_REQUESTS", "200"))
SERPER_MAX_WORKERS = int(os.getenv("SERPER_MAX_WORKERS", "10"))
SERPER_RETRY_COUNT = int(os.getenv("SERPER_RETRY_COUNT", "3"))
SERPER_RETRY_BASE_DELAY = float(os.getenv("SERPER_RETRY_BASE_DELAY", "0.5"))

# per-endpoint 配置（通过环境变量传入 JSON 字符串，示例: '{"search":10,"scrape":2}'）
try:
    PER_ENDPOINT_MAX_CONCURRENT = json.loads(os.getenv("SERPER_ENDPOINT_CONCURRENCY", "{}"))
except Exception:
    PER_ENDPOINT_MAX_CONCURRENT = {}

# per-endpoint 是否允许重试，默认允许（用于避免对非幂等接口重试）
try:
    PER_ENDPOINT_ALLOW_RETRY = json.loads(os.getenv("SERPER_ENDPOINT_RETRYABLE", '{"search": true, "scrape": false}'))
except Exception:
    PER_ENDPOINT_ALLOW_RETRY = {}

# 请求并发信号量（在 startup_all 时初始化）
REQUEST_SEMAPHORE = None

# endpoint -> asyncio.Semaphore 映射（在 startup_all 中根据 PER_ENDPOINT_MAX_CONCURRENT 初始化）
ENDPOINT_SEMAPHORES: Dict[str, asyncio.Semaphore] = {}

# 全局 httpx AsyncClient 管理类
class AsyncHttpClientManager:
    _client: Optional[httpx.AsyncClient] = None
    _lock = asyncio.Lock()

    @classmethod
    async def startup(cls):
        async with cls._lock:
            if cls._client is None:
                limits = httpx.Limits(
                    max_connections=SERPER_MAX_CONNECTIONS,
                    max_keepalive_connections=SERPER_KEEPALIVE
                )
                timeout_obj = httpx.Timeout(
                    connect=5.0,
                    read=20.0,
                    write=10.0,
                    pool=30.0,
                    timeout=HTTP_TIMEOUT
                )
                cls._client = httpx.AsyncClient(
                    timeout=timeout_obj,
                    headers={"User-Agent": USER_AGENT},
                    limits=limits,
                    http2=SERPER_HTTP2
                )
                logger.info("httpx AsyncClient 已启动 (max_connections=%d, keepalive=%d, http2=%s, timeout=%s)",
                            SERPER_MAX_CONNECTIONS, SERPER_KEEPALIVE, SERPER_HTTP2, HTTP_TIMEOUT)

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        if cls._client is None:
            raise RuntimeError("AsyncHttpClientManager 未启动，请先调用startup()")
        return cls._client

    @classmethod
    async def shutdown(cls):
        async with cls._lock:
            if cls._client:
                await cls._client.aclose()
                logger.info("httpx AsyncClient 已关闭")
                cls._client = None


# 全局线程池执行器管理
class ThreadPoolManager:
    _executor: Optional[ThreadPoolExecutor] = None
    _max_workers = SERPER_MAX_WORKERS

    @classmethod
    def startup(cls, max_workers: int = 10):
        if cls._executor is None:
            cls._executor = ThreadPoolExecutor(max_workers=cls._max_workers)
            logger.info(f"线程池启动，最大工作线程数: {cls._max_workers}")

    @classmethod
    def get_executor(cls) -> ThreadPoolExecutor:
        if cls._executor is None:
            raise RuntimeError("ThreadPoolManager 未启动，请先调用startup()")
        return cls._executor

    @classmethod
    def shutdown(cls):
        if cls._executor:
            cls._executor.shutdown(wait=True)
            logger.info("线程池已关闭")
            cls._executor = None


def error_response(message: str, status_code: Optional[int] = None, extra: Optional[Dict[str, Any]] = None) -> str:
    result: Dict[str, Any] = {
        "success": False,
        "error": True,
        "message": message,
    }
    if status_code is not None:
        result["status_code"] = status_code
    if extra:
        result.update(extra)
    return json.dumps(result, ensure_ascii=False, indent=4)


def success_response(query_details: Dict[str, Any], results: Dict[str, Any]) -> str:
    return json.dumps({
        "success": True,
        "query_details": query_details,
        "results": results,
    }, ensure_ascii=False, indent=4)


def get_country_code_alpha2(country_name: Optional[str]) -> str:
    """
    国家代码解析（已简化）：
    - 仅基于别名字典 ALIAS_MAP 进行查找，使用 ALIAS_KEYS_SORTED + 二分查找匹配别名键。
    - 优先在别名字典中查找传入参数（归一化后）；若命中则返回对应 alpha2。
    - 如果传入为两字母 ISO2 则作为后备直接返回大写。
    - 未找到则默认返回 'US'。
    """
    # 处理空输入：直接使用默认 US
    if not country_name:
        return "US"

    name = country_name.strip()
    if not name:
        return "US"

    # 归一化并首先在 ALIAS_MAP 中查找（O(1)）
    norm = normalize(name)
    if norm in ALIAS_MAP:
        return ALIAS_MAP[norm]

    # 对大规模别名列表，使用已排序键列表 + 二分查找
    if ALIAS_KEYS_SORTED:
        idx = binary_search(ALIAS_KEYS_SORTED, norm)
        if idx is not None:
            return ALIAS_MAP.get(ALIAS_KEYS_SORTED[idx], "US")

    # 如果已经是两字母 ISO2，作为后备直接返回大写
    if len(name) == 2 and name.isalpha():
        return name.upper()

    # 再尝试归一化的大写形式（例如传入 'USA'）
    u_norm = normalize(name.upper())
    if u_norm in ALIAS_MAP:
        return ALIAS_MAP[u_norm]
    if ALIAS_KEYS_SORTED:
        idx = binary_search(ALIAS_KEYS_SORTED, u_norm)
        if idx is not None:
            return ALIAS_MAP.get(ALIAS_KEYS_SORTED[idx], "US")

    logger.info("未找到国家名称 '%s'，使用默认国家码 US。", country_name)
    return "US"


def validate_search_num(num_val: int) -> int:
    if 1 <= num_val <= 100:
        return num_val
    logger.warning("搜索数量 %d 超出范围(1-100)，使用默认值10。", num_val)
    return 10

def validate_general_search_num(num_val: int) -> int:
    if 1 <= num_val <= 10:
        return num_val
    logger.warning("搜索数量 %d 超出范围(1-10)，使用默认值10。", num_val)
    return 10


def map_search_time_to_tbs_param(time_period_str: Optional[str]) -> Optional[str]:
    if not time_period_str:
        return None
    s = time_period_str.strip().lower()
    mapping = {
        "小时": "qdr:h", "hour": "qdr:h",
        "天": "qdr:d", "day": "qdr:d",
        "周": "qdr:w", "week": "qdr:w",
        "月": "qdr:m", "month": "qdr:m",
        "年": "qdr:y", "year": "qdr:y",
    }
    for k, v in mapping.items():
        if k in s:
            return v
    logger.info("未识别的时间偏好 '%s'，忽略时间过滤。", time_period_str)
    return None


async def execute_serper_request(
    api_url: str,
    payload: Dict[str, Any],
    api_name: str
) -> Union[Dict[str, Any], None]:
    """
    执行对 Serper API 的异步请求，包含并发控制与重试策略。
    返回解析后的 JSON 或错误描述字典，或 None（当缺少 API_KEY 时）。
    """
    if not API_KEY:
        logger.error("未配置SERPER_API_KEY，无法调用 %s 接口。", api_name)
        return None

    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json",
    }

    try:
        client = AsyncHttpClientManager.get_client()
    except RuntimeError as e:
        logger.error("HTTP客户端未启动: %s", e)
        return {"error": True, "message": f"{api_name}接口请求失败，HTTP客户端未启动。"}

    logger.info("准备调用 %s 接口，payload: %s", api_name, payload)

    # 选择用于该端点的 semaphore（优先 per-endpoint，其次全局 REQUEST_SEMAPHORE）
    sem = ENDPOINT_SEMAPHORES.get(api_name, REQUEST_SEMAPHORE)
    # 该端点是否允许重试（默认 True）
    retry_allowed = PER_ENDPOINT_ALLOW_RETRY.get(api_name, True)

    attempt = 0
    while True:
        try:
            # 并发控制（如果已在 startup_all 中初始化）
            if REQUEST_SEMAPHORE:
                async with REQUEST_SEMAPHORE:
                    response = await client.post(api_url, json=payload, headers=headers)
            else:
                response = await client.post(api_url, json=payload, headers=headers)

            # 检查 HTTP 状态
            response.raise_for_status()

            # 解析返回 JSON
            try:
                result = response.json()
            except Exception as e:
                logger.error("%s接口JSON解析错误: %s", api_name, e)
                return {"error": True, "message": f"{api_name}接口响应解析失败: {e}"}

            return result

        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response is not None else None
            logger.warning("%s 接口返回 HTTP 错误 %s (尝试 %d/%d)", api_name, status, attempt + 1, SERPER_RETRY_COUNT)
            # 对 5xx 做重试（仅在端点允许重试时）
            if retry_allowed and status and 500 <= status < 600 and attempt < SERPER_RETRY_COUNT:
                attempt += 1
                delay = SERPER_RETRY_BASE_DELAY * (2 ** (attempt - 1)) + random.uniform(0, 0.1)
                logger.info("对 %s 接口在 %s 秒后重试 (HTTP %s)", api_name, round(delay, 2), status)
                await asyncio.sleep(delay)
                continue
            logger.error("%s接口HTTP错误 %s %s: %s", api_name, status, e.request.url if e.request else "", e)
            return {
                "error": True,
                "message": f"{api_name}接口HTTP状态错误: {status}",
                "status_code": status
            }

        except httpx.RequestError as e:
            logger.warning("%s 接口请求错误 (尝试 %d/%d): %s", api_name, attempt + 1, SERPER_RETRY_COUNT, e)
            if retry_allowed and attempt < SERPER_RETRY_COUNT:
                attempt += 1
                delay = SERPER_RETRY_BASE_DELAY * (2 ** (attempt - 1)) + random.uniform(0, 0.1)
                logger.info("对 %s 接口在 %s 秒后重试 (请求错误)", api_name, round(delay, 2))
                await asyncio.sleep(delay)
                continue
            logger.error("%s接口请求错误: %s", api_name, e)
            return {"error": True, "message": f"{api_name}接口请求错误: {e}"}

        except Exception as e:
            logger.exception("%s接口未知错误: %s", api_name, e)
            return {"error": True, "message": f"{api_name}接口未知错误: {e}"}


async def generic_serper_search(
    api_name_key: str,
    q: Optional[str] = None,
    url: Optional[str] = None,
    num: Optional[int] = None,
    page: Optional[int] = None,
    country: Optional[str] = None,
    time: Optional[str] = None,
    include_markdown: Optional[bool] = None,
    extra_params: Optional[Dict[str, Any]] = None,
    search_type: Optional[str] = None
) -> str:
    if not API_KEY:
        return error_response("环境变量SERPER_API_KEY未设置，接口无法调用。")
    api_url = API_ENDPOINTS.get(api_name_key)
    if not api_url:
        return error_response(f"未知API_KEY '{api_name_key}'，无法处理请求。")
    payload: Dict[str, Any] = {}
    if q is not None:
        payload["q"] = q
    if url is not None:
        if api_name_key in {"lens_search", "scrape"}:
            payload["url"] = url
        else:
            logger.warning("url参数在接口%s中未使用", api_name_key)
    if num is not None:
        if search_type == "general":
            payload["num"] = validate_general_search_num(num)
        else:
            payload["num"] = validate_search_num(num)
    if page is not None and api_name_key not in {"lens_search", "scrape"}:
        payload["page"] = page
    country_code = get_country_code_alpha2(country)
    if country_code:
        payload["gl"] = country_code
    logger.info("country param '%s' -> resolved country_code: %s", country, country_code)

    tbs_val = map_search_time_to_tbs_param(time)
    if tbs_val:
        payload["tbs"] = tbs_val
    if include_markdown is not None and api_name_key == "scrape":
        if include_markdown:
            payload["includeMarkdown"] = True
    if extra_params:
        # 不允许 extra_params 覆盖或设置 gl 参数（防止外部传入非 ISO2 值覆盖解析结果）
        sanitized = {k: v for k, v in extra_params.items() if k.lower() != "gl"}
        payload.update(sanitized)

    # 最终验证 gl，确保为合法的 ISO2 大写字符串；使用 get_country_code_alpha2 进行规范化或移除
    gl_val = payload.get("gl")
    if gl_val is not None:
        resolved = None
        # 如果已经是 ASCII 两字母代码，直接规范为大写
        if isinstance(gl_val, str) and re.fullmatch(r"[A-Za-z]{2}", gl_val):
            resolved = gl_val.upper()
        else:
            # 否则尝试用别名字典解析（支持中文/英文/ISO3等）
            resolved = get_country_code_alpha2(str(gl_val))
        if resolved:
            payload["gl"] = resolved
        else:
            logger.warning("无效的 gl 值 '%s'，已移除（无法解析为 ISO2）", gl_val)
            payload.pop("gl", None)

    if api_name_key == "scrape" and ("url" not in payload or not payload["url"].strip()):
        return error_response("参数 url 必填且不能为空字符串。")
    result = await execute_serper_request(api_url, payload, api_name_key)
    if result is None:
        return error_response(f"{api_name_key}请求失败，接口响应为空。")
    if isinstance(result, dict) and result.get("error"):
        return json.dumps({
            "success": False,
            "query_details": payload,
            "error": result.get("error"),
            "message": result.get("message", "未知错误"),
            "status_code": result.get("status_code", None),
        }, ensure_ascii=False, indent=4)
    return success_response(payload, result)


@mcp.tool(name="serper-general-search")
async def serper_general_search(
    search_key_words: str,
    search_country: Optional[str] = None,
    search_num: int = 10,
    page: int = 1,
    search_time: Optional[str] = None,
) -> str:
    """
    通用搜索接口。
    参数:
        search_key_words: 搜索关键词（必填）
        search_country: 国家名称（可选），支持中文或英文国家名
        search_num: 返回结果数量，1~10，默认10
        page: 页数，默认为1
        search_time: 时间过滤，如“小时”，“天”，“周”，“月”，“年”，可选
    返回:
        JSON格式字符串，包含查询参数和搜索结果。
    """
    return await generic_serper_search("search", q=search_key_words, country=search_country, num=search_num, page=page, time=search_time, search_type="general")


@mcp.tool(name="serper-image-search")
async def serper_image_search(
    search_key_words: str,
    search_country: Optional[str] = None,
    search_num: int = 10,
    page: int = 1,
    search_time: Optional[str] = None,
) -> str:
    """
    图片搜索接口。
    参数含义与通用搜索接口相同。
    """
    return await generic_serper_search("image_search", q=search_key_words, country=search_country, num=search_num, page=page, time=search_time)


@mcp.tool(name="serper-video-search")
async def serper_video_search(
    search_key_words: str,
    search_country: Optional[str] = None,
    search_num: int = 10,
    page: int = 1,
    search_time: Optional[str] = None,
) -> str:
    """
    视频搜索接口。
    参数含义与通用搜索接口相同。
    """
    return await generic_serper_search("video_search", q=search_key_words, country=search_country, num=search_num, page=page, time=search_time)


@mcp.tool(name="serper-place-search")
async def serper_place_search(
    search_key_words: str,
    search_country: Optional[str] = None,
    page: int = 1,
) -> str:
    """
    地点搜索接口。
    参数:
        search_key_words: 搜索关键词
        search_country: 国家名称（可选）
        page: 页数，默认为1
    """
    return await generic_serper_search("place_search", q=search_key_words, country=search_country, page=page)


@mcp.tool(name="serper-maps-search")
async def serper_maps_search(
    search_key_words: str,
    page: int = 1,
    ll: Optional[str] = None,
    placeId: Optional[str] = None,
    cid: Optional[str] = None
) -> str:
    """
    地图搜索接口。
    参数:
        q: 搜索关键词
        page: 页数，默认为1
        ll: GPS坐标和缩放级别 (可选)
        placeId: 地点ID (可选)
        cid: 客户ID (可选)
    """
    extra = {}
    if ll:
        extra["ll"] = ll
    if placeId:
        extra["placeId"] = placeId
    if cid:
        extra["cid"] = cid
    return await generic_serper_search("maps_search", q=search_key_words, page=page, extra_params=extra)


@mcp.tool(name="serper-news-search")
async def serper_news_search(
    search_key_words: str,
    search_country: Optional[str] = None,
    search_num: int = 10,
    page: int = 1,
    search_time: Optional[str] = None,
) -> str:
    """
    新闻搜索接口。
    参数同通用搜索接口。
    """
    return await generic_serper_search("news_search", q=search_key_words, country=search_country, num=search_num, page=page, time=search_time)


@mcp.tool(name="serper-lens-search")
async def serper_lens_search(
    image_url: str,
    search_country: Optional[str] = None,
) -> str:
    """
    Lens图片搜索接口。
    参数:
        image_url: 图片URL（必填）
        search_country: 国家名称（可选）
    """
    return await generic_serper_search("lens_search", url=image_url, country=search_country)


@mcp.tool(name="serper-scholar-search")
async def serper_scholar_search(
    search_key_words: str,
    search_country: Optional[str] = None,
) -> str:
    """
    学术搜索接口。
    参数:
        search_key_words: 查询关键词
        search_country: 国家名称（可选）
    """
    return await generic_serper_search("scholar_search", q=search_key_words, country=search_country)


@mcp.tool(name="serper-shopping-search")
async def serper_shopping_search(
    search_key_words: str,
    page: int = 1,
    search_country: Optional[str] = None
) -> str:
    """
    购物搜索接口。
    参数:
        search_key_words: 搜索关键词
        page: 页数，默认为1
        search_country: 国家名称（可选）
    """
    return await generic_serper_search("shopping_search", q=search_key_words, num=40, page=page, country=search_country)


@mcp.tool(name="serper-patents-search")
async def serper_patents_search(
    search_key_words: str,
    page: int = 1,
    search_num: int = 10,
    search_country: Optional[str] = None,
) -> str:
    """
    专利搜索接口。
    参数:
        search_key_words: 搜索关键词
        page: 页数，默认为1
        search_num: 返回结果数量，1~100，默认10
        search_country: 国家名称（可选）
    """
    return await generic_serper_search("patents_search", q=search_key_words, num=search_num, page=page, country=search_country)


@mcp.tool(name="serper-scrape")
async def serper_scrape(
    url: str,
    include_markdown: bool = False,
) -> str:
    """
    网页内容抓取接口。
    参数:
        url: 目标网页URL（必填）
        include_markdown: 是否返回Markdown格式内容（默认为False）
    返回:
        JSON字符串，包含网页内容和（可选）Markdown文本。
    """
    return await generic_serper_search("scrape", url=url, include_markdown=include_markdown)


# 示例：同步阻塞函数，通过线程池异步调用
async def run_blocking_task_in_threadpool(blocking_func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    executor = ThreadPoolManager.get_executor()
    return await loop.run_in_executor(executor, lambda: blocking_func(*args, **kwargs))


async def startup_all():
    global REQUEST_SEMAPHORE
    await AsyncHttpClientManager.startup()
    ThreadPoolManager.startup(max_workers=SERPER_MAX_WORKERS)
    # 初始化请求并发信号量
    REQUEST_SEMAPHORE = asyncio.Semaphore(SERPER_MAX_CONCURRENT_REQUESTS)
    logger.info("已初始化请求并发控制，最大并发请求数: %d，线程池最大工作线程: %d", SERPER_MAX_CONCURRENT_REQUESTS, SERPER_MAX_WORKERS)
    # 可以扩展这里做更多初始化


async def shutdown_all():
    await AsyncHttpClientManager.shutdown()
    ThreadPoolManager.shutdown()
    # 可以扩展这里做更多清理


def main():
    """
    The main synchronous entry point for the MCP server.
    Manages the asyncio event loop to run async setup/teardown around the blocking mcp.run() call.
    """
    if not API_KEY:
        logger.error(
            "警告：环境变量SERPER_API_KEY未设置，启动后所有接口调用均不可用。"
            "请在.env文件或环境变量中配置。"
        )
    else:
        logger.info("加载到SERPER_API_KEY，准备启动Serper MCP工具接口服务。")

    # Manually manage the event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Run the async startup tasks
        loop.run_until_complete(startup_all())
        logger.info("Serper MCP 工具服务已启动。")

        # Now, run the blocking MCP server loop
        mcp.run(transport="stdio")

    except KeyboardInterrupt:
        logger.info("接收到中断信号，正在关闭服务...")
    finally:
        logger.info("开始关闭异步资源...")
        # Run the async shutdown tasks
        loop.run_until_complete(shutdown_all())
        loop.close()
        logger.info("Serper MCP工具接口服务已安全关闭。")

# This block is for direct execution via 'python -m serper_toolkit.server'
if __name__ == "__main__":
    main()
