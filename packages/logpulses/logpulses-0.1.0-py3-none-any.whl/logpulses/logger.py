import json
import time
import psutil
import platform
import uuid
import tracemalloc
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.datastructures import Headers
from typing import Callable


def get_device_id():
    """Get unique device identifier"""
    try:
        return str(uuid.UUID(int=uuid.getnode()))
    except Exception:
        return platform.node()


def get_system_metrics():
    """Get current system CPU and memory metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=False)
        mem_info = psutil.virtual_memory()
        return {
            "cpuUsage": f"{cpu_percent:.1f}%",
            "memoryUsage": {
                "total": f"{mem_info.total / (1024 ** 3):.2f} GB",
                "used": f"{mem_info.used / (1024 ** 3):.2f} GB",
                "available": f"{mem_info.available / (1024 ** 3):.2f} GB",
                "percent": f"{mem_info.percent:.1f}%",
            },
        }
    except Exception as e:
        return {"error": str(e)}


def get_active_network_info():
    """Get active network interface (prioritizes WiFi)"""
    try:
        net_io = psutil.net_io_counters(pernic=True)
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()

        wireless_keywords = ["wlan", "wi-fi", "wifi", "wireless", "802.11"]
        best_interface = None
        best_score = -1

        for iface_name, addrs in net_if_addrs.items():
            if iface_name.lower() == "lo" or iface_name.startswith("Loopback"):
                continue
            if iface_name in net_if_stats and not net_if_stats[iface_name].isup:
                continue

            for addr in addrs:
                if addr.family == psutil.AF_LINK:
                    continue
                if addr.family.name == "AF_INET" and addr.address != "127.0.0.1":
                    score = 0
                    if any(kw in iface_name.lower() for kw in wireless_keywords):
                        score += 100
                        interface_type = "WiFi"
                    elif (
                        "ethernet" in iface_name.lower() or "eth" in iface_name.lower()
                    ):
                        score += 50
                        interface_type = "Ethernet"
                    else:
                        interface_type = "Other"

                    if iface_name in net_io:
                        io_stats = net_io[iface_name]
                        if io_stats.bytes_sent > 0 or io_stats.bytes_recv > 0:
                            score += 10

                    if addr.address.startswith(("192.168.", "10.", "172.")):
                        score += 5

                    if score > best_score:
                        best_score = score
                        best_interface = {
                            "interface": iface_name,
                            "type": interface_type,
                            "ip": addr.address,
                            "netmask": addr.netmask,
                            "isActive": True,
                        }
                        if iface_name in net_io:
                            io_stats = net_io[iface_name]
                            best_interface.update(
                                {
                                    "bytesSent": f"{io_stats.bytes_sent / (1024**2):.2f} MB",
                                    "bytesRecv": f"{io_stats.bytes_recv / (1024**2):.2f} MB",
                                }
                            )

        return best_interface or {"error": "No active network interface found"}
    except Exception as e:
        return {"error": str(e)}


def get_memory_usage_delta(start_snapshot):
    """Calculate memory used by the current request"""
    try:
        current = tracemalloc.take_snapshot()
        stats = current.compare_to(start_snapshot, "lineno")
        total_kb = sum(stat.size_diff for stat in stats) / 1024
        return f"{total_kb:.2f} KB" if total_kb > 0 else "< 1 KB"
    except Exception:
        return "N/A"


def print_log(log_data):
    """Pretty print log data"""
    print("\n" + "=" * 80)
    print(json.dumps(log_data, indent=2, ensure_ascii=False))
    print("=" * 80 + "\n")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Universal middleware that logs ALL requests automatically.
    Works at the ASGI level to intercept and cache request body.

    ✅ NO DECORATORS NEEDED!
    ✅ Works with request.json()
    ✅ Works with request.body()
    ✅ Works with query parameters
    ✅ Works with all HTTP methods
    ✅ Gracefully handles empty bodies

    Usage:
        app = FastAPI()
        app.add_middleware(RequestLoggingMiddleware)

        # All routes work automatically!
        @app.post("/users")
        async def create_user(request: Request):
            data = await request.json()  # Works!
            return {"user": data}
    """

    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or []

    async def dispatch(self, request: Request, call_next):
        # Skip excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Start tracking
        tracemalloc.start()
        mem_snapshot = tracemalloc.take_snapshot()
        start_time = time.time()

        # Capture request info
        route_path = request.url.path
        method = request.method
        full_url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Cache request body
        body_bytes = await request.body()
        request_body_for_log = None
        body_size = len(body_bytes)

        # Parse request body for logging (gracefully handle empty/invalid bodies)
        query_params = dict(request.query_params)
        query_string = str(request.url.query) if request.url.query else ""
        query_size = len(query_string.encode("utf-8")) if query_string else 0

        # Calculate total request size (body + query params)
        request_size = body_size + query_size

        # Build comprehensive request data structure
        request_data = {}

        # Handle request body for methods that typically have bodies
        if method in ("POST", "PUT", "PATCH", "DELETE"):
            if body_bytes:
                try:
                    request_data["body"] = json.loads(body_bytes)
                except json.JSONDecodeError:
                    # Not valid JSON, log as text
                    request_data["body"] = body_bytes.decode("utf-8", errors="replace")[
                        :500
                    ]

            # Add query params if present (can coexist with body)
            if query_params:
                request_data["queryParams"] = query_params

            # If nothing was captured, mark as no data
            if not request_data:
                request_body_for_log = "No body or query parameters"
            else:
                request_body_for_log = request_data

        # Handle GET and HEAD methods (typically only query params)
        elif method in ("GET", "HEAD"):
            if query_params:
                request_body_for_log = {"queryParams": query_params}
            else:
                request_body_for_log = "No query parameters"

        # Handle OPTIONS, TRACE, CONNECT or any other methods
        else:
            if body_bytes:
                try:
                    request_data["body"] = json.loads(body_bytes)
                except json.JSONDecodeError:
                    request_data["body"] = body_bytes.decode("utf-8", errors="replace")[
                        :500
                    ]

            if query_params:
                request_data["queryParams"] = query_params

            if request_data:
                request_body_for_log = request_data
            else:
                request_body_for_log = "No data"

        # Response tracking
        status_code = 500
        response_body = None
        response_size = 0
        error_details = None

        try:
            # Call the next middleware/endpoint
            response = await call_next(request)
            status_code = response.status_code

            # Try to capture response body
            response_body_list = []
            async for chunk in response.body_iterator:
                response_body_list.append(chunk)

            response_body_bytes = b"".join(response_body_list)
            response_size = len(response_body_bytes)

            # Parse response body
            try:
                response_body = (
                    json.loads(response_body_bytes) if response_body_bytes else None
                )
            except json.JSONDecodeError:
                response_body = response_body_bytes.decode("utf-8", errors="replace")
                if len(response_body) > 1000:
                    response_body = response_body[:1000] + "... (truncated)"

            # If response indicates an error, capture it
            if status_code >= 400:
                error_details = {
                    "statusCode": status_code,
                    "type": "HTTP Error",
                    "message": (
                        response_body
                        if isinstance(response_body, str)
                        else (
                            response_body.get("detail", "Unknown error")
                            if isinstance(response_body, dict)
                            else "Error occurred"
                        )
                    ),
                    "responseBody": response_body,
                }

            # Recreate response with the captured body
            from starlette.responses import Response as StarletteResponse

            response = StarletteResponse(
                content=response_body_bytes,
                status_code=status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        except Exception as e:
            import traceback

            # Determine status code based on exception type
            if hasattr(e, "status_code"):
                status_code = e.status_code
            elif isinstance(e, ValueError):
                status_code = 400  # Bad Request
            elif isinstance(e, KeyError):
                status_code = 400  # Bad Request - Missing key
            elif isinstance(e, TypeError):
                status_code = 400  # Bad Request - Wrong type
            elif isinstance(e, PermissionError):
                status_code = 403  # Forbidden
            elif isinstance(e, FileNotFoundError):
                status_code = 404  # Not Found
            elif isinstance(e, TimeoutError):
                status_code = 504  # Gateway Timeout
            elif isinstance(e, ConnectionError):
                status_code = 503  # Service Unavailable
            else:
                status_code = 500  # Internal Server Error

            error_details = {
                "type": type(e).__name__,
                "message": str(e),
                "statusCode": status_code,
                "traceback": traceback.format_exc(),
                "failurePoint": "Request processing",
                "exceptionModule": type(e).__module__,
                "hasStatusCode": hasattr(e, "status_code"),
            }

            # Create error response
            error_response_body = {
                "error": type(e).__name__,
                "detail": str(e),
                "statusCode": status_code,
            }

            response = Response(
                content=json.dumps(error_response_body),
                status_code=status_code,
                media_type="application/json",
            )

        finally:
            # Calculate metrics
            processing_time = (time.time() - start_time) * 1000
            memory_used = get_memory_usage_delta(mem_snapshot)
            tracemalloc.stop()

            # Build log
            log_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "request": {
                    "route": route_path,
                    "method": method,
                    "fullUrl": full_url,
                    "clientIp": client_ip,
                    "userAgent": user_agent,
                    "size": (
                        {
                            "total": f"{request_size} bytes",
                            "body": f"{body_size} bytes",
                            "queryParams": f"{query_size} bytes",
                        }
                        if query_size > 0
                        else f"{request_size} bytes"
                    ),
                    "body": request_body_for_log,
                },
                "response": {
                    "status": status_code,
                    "success": status_code < 400,
                    "size": f"{response_size} bytes",
                    "body": (
                        response_body
                        if response_size < 5000
                        else "<response too large>"
                    ),
                },
                "performance": {
                    "processingTime": f"{processing_time:.2f} ms",
                    "memoryUsed": memory_used,
                },
                "system": get_system_metrics(),
                "network": get_active_network_info(),
                "server": {
                    "instanceId": get_device_id(),
                    "platform": platform.system(),
                    "hostname": platform.node(),
                },
            }

            # Add error details if request failed
            if error_details:
                log_data["error"] = error_details

                # Add failure analysis
                log_data["failureAnalysis"] = {
                    "statusCode": status_code,
                    "category": self._categorize_error(status_code),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

            print_log(log_data)

        return response

    def _categorize_error(self, status_code):
        """Categorize error based on status code"""
        error_categories = {
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Access denied",
            404: "Not Found - Resource doesn't exist",
            405: "Method Not Allowed - HTTP method not supported",
            408: "Request Timeout - Client took too long",
            409: "Conflict - Resource state conflict",
            410: "Gone - Resource permanently deleted",
            413: "Payload Too Large - Request body too big",
            415: "Unsupported Media Type - Invalid content type",
            422: "Unprocessable Entity - Validation error",
            429: "Too Many Requests - Rate limit exceeded",
            500: "Internal Server Error - Application error",
            501: "Not Implemented - Feature not available",
            502: "Bad Gateway - Upstream server error",
            503: "Service Unavailable - Server overloaded",
            504: "Gateway Timeout - Request timeout",
        }

        # Check exact match first
        if status_code in error_categories:
            return error_categories[status_code]

        # Fallback to range-based categorization
        if 400 <= status_code < 500:
            return "Client Error - Request issue"
        elif 500 <= status_code < 600:
            return "Server Error - Backend issue"
        else:
            return "Unknown Error"


# Decorator is now completely unnecessary - kept only for backward compatibility
def log_request(func: Callable):
    """
    This decorator is NO LONGER NEEDED!
    RequestLoggingMiddleware handles everything automatically.

    You can safely remove all @log_request decorators from your code.
    """
    return func  # Just pass through, do nothing
