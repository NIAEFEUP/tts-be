import json
from django.http import HttpResponse, JsonResponse
from django.views import View

from university.exchange.utils import curr_semester_weeks
from university.models import MarketplaceExchange, MarketplaceExchangeClass

class DirectExchangeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse()

    def post(self, request, *args, **kwargs):
        return HttpResponse()
