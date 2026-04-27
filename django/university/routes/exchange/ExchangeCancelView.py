from django.http import HttpResponse
from django.views import View

from university.controllers.ExchangeValidationController import ExchangeValidationController

from exchange.models import DirectExchange, DirectExchangeParticipants, ExchangeAdmin, MarketplaceExchange

class ExchangeCancelView(View):
    def put(self, request, request_type, id):
        username = request.user.username
        is_admin = ExchangeAdmin.objects.filter(username=username).exists()

        if request_type == "direct":
            try:
                exchange = DirectExchange.objects.get(id=id)
            except DirectExchange.DoesNotExist:
                return HttpResponse(status=404)
            is_participant = DirectExchangeParticipants.objects.filter(
                direct_exchange=exchange, participant_nmec=username
            ).exists()
            if not is_admin and not is_participant:
                return HttpResponse(status=403)
            ExchangeValidationController().cancel_exchange(exchange)

        elif request_type == "marketplace":
            try:
                exchange = MarketplaceExchange.objects.get(id=id)
            except MarketplaceExchange.DoesNotExist:
                return HttpResponse(status=404)
            if not is_admin and exchange.issuer_nmec != username:
                return HttpResponse(status=403)
            ExchangeValidationController().cancel_exchange(exchange)

        return HttpResponse(status=200)
