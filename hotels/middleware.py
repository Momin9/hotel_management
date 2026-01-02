from .signals import set_current_user

class CurrentUserMiddleware:
    """Middleware to track current user for activity logging"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set current user in thread-local storage
        if hasattr(request, 'user') and request.user.is_authenticated:
            set_current_user(request.user)
        else:
            set_current_user(None)
        
        response = self.get_response(request)
        return response