from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import requests

from university.controllers.ExchangeController import ExchangeController
from university.controllers.SigarraController import SigarraController
from university.models import ExchangeExpirations

class InfoView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return JsonResponse({
                "signed": True,
                "username": request.user.username,
                "name": f"{request.user.first_name} {request.user.last_name}",
            }, safe=False)
        else:
            return JsonResponse({
                "signed": False
            }, safe=False)
