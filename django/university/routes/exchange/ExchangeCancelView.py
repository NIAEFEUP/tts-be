from django.http import HttpResponse 
from django.views import View

from university.controllers.AdminExchangeStateChangeController import AdminExchangeStateChangeController
from university.controllers.ExchangeValidationController import ExchangeValidationController
from university.models import DirectExchange, MarketplaceExchange

class ExchangeCancelView(View):
    def put(self, request, request_type, id):
        
        if request_type == "direct":
            ExchangeValidationController().cancel_exchange(DirectExchange.objects.get(id=id))

        if request_type == "marketplace":
            ExchangeValidationController().cancel_exchange(MarketplaceExchange.objects.get(id=id))

        return HttpResponse(status=200)