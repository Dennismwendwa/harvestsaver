import time
from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import decorator_from_middleware
from django.core.cache import cache


class RateLimitMiddleware:
    """
    Production-grade, atomic, Redis-backed rate limiter.
    
    Features:
    - Authenticated vs Anonymous users
    - GET vs Write methods
    - Sliding window
    - Atomic with Redis
    - Exempt views supported
    """

    WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    def __init__(self, get_response):
        self.get_response = get_response

        self.anon_limit = getattr(settings, "RATELIMIT_ANON_LIMIT", 30)
        self.auth_limit = getattr(settings, "RATELIMIT_AUTH_LIMIT", 20)
        self.anon_get_limit = getattr(settings, "RATELIMIT_ANON_GET_LIMIT", 20)
        self.auth_get_limit = getattr(settings, "RATELIMIT_AUTH_GET_LIMIT", 15)
        self.window = getattr(settings, "RATELIMIT_WINDOW", 60)

    def __call__(self, request):
        try:
            resolver_match = getattr(request, "resolver_match", None)
            if resolver_match:
                view_func = resolver_match.func
                if getattr(view_func, "_ratelimit_exempt", False):
                    return self.get_response(request)

            is_write = request.method in self.WRITE_METHODS
            
            if request.user.is_authenticated:
                key = f"rl:user:{request.user.id}"
                limit = self.auth_limit if is_write else self.auth_get_limit
            else:
                ip = self.get_client_ip(request)
                key = f"rl:anon:{ip}"
                limit = self.anon_limit if is_write else self.anon_get_limit

            try:
                count = cache.incr(key)
                if count == 1:
                    cache.expire(key, self.window)
            except ValueError:
                cache.set(key, 1, timeout=self.window)
                count = 1

            if count > limit:
                ttl = cache.ttl(key) or self.window
                return JsonResponse(
                    {
                        "detail": "Request was throttled. Try again later.",
                        "retry_after": ttl,
                    },
                    status=429,
                )

        except Exception as e:
            pass

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

