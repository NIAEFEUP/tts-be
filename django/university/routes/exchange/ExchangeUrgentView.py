import json
import jwt
import requests
import datetime

from django.http import HttpResponse, JsonResponse
from django.views import View

from university.models import ExchangeUrgentRequests
from university.serializers.ExchangeUrgentRequestSerializer import ExchangeUrgentRequestSerializer

class ExchangeUrgentView(View):
    def get(self, request):
        exchanges = map(lambda exchange: ExchangeUrgentRequestSerializer(exchange).data, ExchangeUrgentRequests.objects.all())

        return JsonResponse(list(exchanges), safe=False)
    