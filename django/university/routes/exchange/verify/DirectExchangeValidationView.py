from django.http import HttpResponse, JsonResponse
from django.views import View

from university.controllers.ExchangeValidationController import ExchangeValidationController

class DirectExchangeValidationView(View):
    def get(self, request, id):
        ExchangeValidationController().validate_direct_exchange(id)
        return HttpResponse()