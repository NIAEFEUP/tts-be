from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import requests

class FederatedLogin(View):
    def get(self, request):
        return redirect('http://localhost:3100/tts/')
    
    def post(self, request):
        key = "_shibsession_64656661756c7468747470733a2f2f6e692e66652e75702e70742f747473"
        
        if key in request.COOKIES:
            value = request.COOKIES[key]
            headers = {'Cookie': f'{key}={value}'}
            session = requests.get('http://httpd/Shibboleth.sso/Session', headers=headers)
            print("current session is: ", session.json())

        return HttpResponse()
