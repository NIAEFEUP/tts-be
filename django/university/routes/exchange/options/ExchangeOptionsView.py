import json
from rest_framework.views import APIView
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.db.models import Prefetch

from university.exchange.utils import curr_semester_weeks
from university.models import MarketplaceExchange, MarketplaceExchangeClass
from university.serializers.MarketplaceExchangeClassSerializer import MarketplaceExchangeClassSerializer

class ExchangeOptionsView(APIView):
    """
        Returns the course units the student is enrolled in and information about them such as the enrolled students and the available classes
    """
    def get(self, request):
         
        return HttpResponse()
