from django.http import HttpResponse, JsonResponse
from django.views import View

from university.controllers.ExchangeValidationController import ExchangeValidationController

from exchange.models import DirectExchange

class DirectExchangeValidationView(View):
    def get(self, request, id):
        validation = ExchangeValidationController().validate_direct_exchange(id)

        if validation.status:
            return HttpResponse(status=200)

        ExchangeValidationController().cancel_exchange(DirectExchange.objects.get(id=id))
        return JsonResponse({"error": validation.message}, status=400, safe=False)
