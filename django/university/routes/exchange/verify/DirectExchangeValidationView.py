from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist

from university.controllers.ExchangeValidationController import ExchangeValidationController
from exchange.models import DirectExchange

class DirectExchangeValidationView(View):
    """
        Read-only check used by admins to see whether a direct exchange is still valid.

        It only reports the result and never changes the exchange state. An admin who wants to
        discard an invalid exchange must reject it explicitly.
    """
    def get(self, request, id):
        try:
            exchange = DirectExchange.objects.get(id=id)
        except ObjectDoesNotExist:
            return JsonResponse({"valid": False, "error": "Exchange not found"}, status=404)

        validation = ExchangeValidationController().validate_direct_exchange(id)

        if validation.status:
            # validate_direct_exchange stores a new last_validated timestamp
            exchange.refresh_from_db(fields=["last_validated"])
            return JsonResponse({
                "valid": True,
                "last_validated": exchange.last_validated.isoformat() if exchange.last_validated else None
            }, status=200)

        return JsonResponse({"valid": False, "error": validation.message}, status=400)
