from django.core.paginator import Paginator
from django.http.response import HttpResponse, JsonResponse
from rest_framework.views import APIView
from django.db.models import Prefetch

from university.controllers.ExchangeController import DirectExchangePendingMotive
from university.controllers.SigarraController import SigarraController
from university.models import DirectExchange, DirectExchangeParticipants
from university.serializers.DirectExchangeParticipantsSerializer import DirectExchangeParticipantsSerializer
from university.serializers.MarketplaceExchangeClassSerializer import MarketplaceExchangeClassSerializer

class StudentReceivedExchangesView(APIView):
    def get(self, request):
        exchanges = DirectExchange.objects.prefetch_related(
            Prefetch(
                'directexchangeparticipants_set',
                queryset=DirectExchangeParticipants.objects.all(),
                to_attr='options'
            )
        ).filter(
            directexchangeparticipants__participant_nmec=request.user.username
        ).all()

        return JsonResponse(self.build_pagination_payload(request, exchanges), safe=False)

    def build_pagination_payload(self, request, exchanges):
        page_number = request.GET.get("page")
        paginator = Paginator(exchanges, 10)
        page_obj = paginator.get_page(page_number if page_number != None else 1)

        return {
            "page": {
                "current": page_obj.number,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
            "data": [{
                "id": exchange.id,
                "type": "directexchange",
                "issuer_name": exchange.issuer_name,
                "issuer_nmec": exchange.issuer_nmec,
                "accepted": exchange.accepted,
                "pending_motive": DirectExchangePendingMotive.get_value(DirectExchangePendingMotive.get_pending_motive(request.user.username, exchange)),
                "options": [
                    DirectExchangeParticipantsSerializer(participant).data for participant in exchange.options
                ],
                "date": exchange.date
            } for exchange in page_obj]
        }

        
