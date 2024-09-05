from django.http import JsonResponse
from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import requests

class InfoView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return JsonResponse({
                "signed": True
            }, safe=False)
        else:
            return JsonResponse({
                "signed": False
            }, safe=False)
