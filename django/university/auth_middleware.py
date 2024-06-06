import re
from django.http import HttpResponseForbidden

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth_paths = [
            'logout/',
            re.compile(r'^/student_schedule/\d+/$'),
            re.compile(r'^/schedule_sigarra/\d+/$'),
            re.compile(r'^/class_sigarra_schedule/\d+/.+/$'),
            'submit_direct_exchange/',
            re.compile(r'^/verify_direct_exchange/.+/$'),
            re.compile(r'^/students_per_course_unit/\d+/$'),
            'is_admin/',
            'export/',
            'direct_exchange/history/',
        ]

    def __call__(self, request):

        if not request.path in self.auth_paths:
            return self.get_response(request)

        if not request.user.is_authenticated:
            return HttpResponseForbidden

        return self.get_response(request)

