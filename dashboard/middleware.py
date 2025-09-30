"""
Custom middleware for Car Service Management System
"""
from django.utils.deprecation import MiddlewareMixin


class DisableAdminCSRFMiddleware(MiddlewareMixin):
    """
    Middleware to disable CSRF protection for admin login only.
    This is a workaround for CSRF issues when running behind nginx proxy.
    """
    def process_request(self, request):
        # Only disable CSRF for admin login page, not all admin URLs
        if request.path == '/admin/login/' or request.path.startswith('/admin/login'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None
