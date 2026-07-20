class DebugAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only log when hitting your API endpoints (optional filter)
        if request.path.startswith('/api/'):
            auth_header = request.META.get('HTTP_AUTHORIZATION', 'NO HEADER')
            print(f"--- DEBUG AUTH --- Path: {request.path}")
            print(f"Authorization header: '{auth_header}'")
            print(f"User: {request.user}  (authenticated: {request.user.is_authenticated})")
        return self.get_response(request)