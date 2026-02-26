import time
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings


class RateLimitMiddleware:
    """
    Global rate limiting middleware.
    - Anonymous users: default 5 requests/min
    - Authenticated users: default 20 requests/min
    - Returns 429 if limit exceeded
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.anonymous_limit = getattr(settings, "RATELIMIT_ANON_LIMIT", 5)
        self.authenticated_limit = getattr(settings, "RATELIMIT_AUTH_LIMIT", 20)
        self.window = getattr(settings, "RATELIMIT_WINDOW", 60) # SECONDS

    def __call__(self, request):
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return self.get_response(request)
        
        if getattr(getattr(request, "resolver_match", None), "func", None):
            view_func = request.resolver_match.func
            if getattr(view_func, "_ratelimit_exempt", False):
                return self.get_response(request)
            
        if request.user.is_authenticated:
            key = f"rl:user:{request.user.id}"
            limit = self.authenticated_limit
        else:
            ip = self.get_client_ip(request)
            key = f"rl:anon:{ip}"
            limit = self.anonymous_limit

        data = cache.get(key, {"count": 0, "start": time.time()})
        now = time.time()

        if now - data["start"] > self.window:
            data = {"count": 0, "start": now}

        data["count"] += 1
        cache.set(key, data, timeout=self.window)

        if data["count"] > limit:
            retry_after = int(self.window - (now - data["start"]))
            return JsonResponse(
                {
                    "detail": "Request was throttled. Try again later.",
                    "retry_after": retry_after
                },
                status=429
            )
        return self.get_response(request)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")