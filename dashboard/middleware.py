"""
Custom middleware for Car Service Management System
"""
from django.utils.deprecation import MiddlewareMixin


class DisableAdminCSRFMiddleware(MiddlewareMixin):
    """
    Middleware to disable CSRF protection for admin login.
    This is a workaround for CSRF issues when running behind nginx proxy.
    """
    def process_request(self, request):
        if request.path.startswith('/admin/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None
