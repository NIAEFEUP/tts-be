import re

from django.http import HttpResponseForbidden

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth_paths = [
            '/logout/',
            re.compile(r'^/student_schedule/\d+/$'),
            re.compile(r'^/schedule_sigarra/\d+/$'),
            re.compile(r'^/class_sigarra_schedule/\d+/.+/$'),
            '/submit_direct_exchange/',
            re.compile(r'^/verify_direct_exchange/.+/$'),
            re.compile(r'^/students_per_course_unit/\d+/$'),
            '/is_admin/',
            '/export/',
            '/direct_exchange/history/',
        ]

    def __call__(self, request):

        in_paths = False

        for path in self.auth_paths:
            if isinstance(path, str) and request.path == path:
                in_paths = True
                break
            elif isinstance(path, re.Pattern) and path.match(request.path):
                in_paths = True
                break

        if not in_paths:
            return self.get_response(request)

        if not request.session["username"]:
            return HttpResponseForbidden()

        return self.get_response(request)

