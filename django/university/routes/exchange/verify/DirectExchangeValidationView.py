from django.http import HttpResponse, JsonResponse
from django.views import View

from university.controllers.ExchangeValidationController import ExchangeValidationController

class DirectExchangeValidationView(View):
    def get(self, request, id):
        validation = ExchangeValidationController().validate_direct_exchange(id)

        print("VALIDATION: ", validation.status)

        if validation.status:
            return HttpResponse(status=200)

        return JsonResponse({"error": validation.message}, status=400, safe=False)