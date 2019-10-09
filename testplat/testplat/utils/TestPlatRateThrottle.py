from rest_framework.throttling import SimpleRateThrottle


class TpRateThrottle(SimpleRateThrottle):
    """访问频率限制"""
    scope = "test_plat"

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }
