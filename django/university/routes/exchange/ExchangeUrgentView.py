import json
import jwt
import requests
import datetime

from django.http import HttpResponse, JsonResponse
from django.views import View

from university.models import ExchangeUrgentRequests, ExchangeAdmin
from university.serializers.ExchangeUrgentRequestSerializer import ExchangeUrgentRequestSerializer

class ExchangeUrgentView(View):
    def get(self, request):
        is_admin = ExchangeAdmin.objects.filter(username=request.user.username).exists()
        if not(is_admin):
            return HttpResponse(status=403) 

        exchanges = map(lambda exchange: ExchangeUrgentRequestSerializer(exchange).data, ExchangeUrgentRequests.objects.all())

        return JsonResponse(list(exchanges), safe=False)
    