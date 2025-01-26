import base64
import json
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http.response import HttpResponse, JsonResponse
from rest_framework.views import APIView

from university.controllers.ClassController import ClassController
from university.controllers.ExchangeController import ExchangeController
from university.controllers.SigarraController import SigarraController
from university.models import DirectExchange, DirectExchangeParticipants, MarketplaceExchange, MarketplaceExchangeClass
from university.serializers.MarketplaceExchangeClassSerializer import MarketplaceExchangeClassSerializer

class StudentSentExchangesView(APIView):
    def get(self, request):
        course_unit_name_filter = request.query_params.get('courseUnitNameFilter', None)

        marketplace_exchanges = list(MarketplaceExchange.objects.prefetch_related(
            Prefetch(
                'marketplaceexchangeclass_set',
                queryset=MarketplaceExchangeClass.objects.all(),
                to_attr='options'
            )
        ).filter(issuer_nmec=request.user.username).all())

        direct_exchanges = list(DirectExchange.objects.prefetch_related(
            Prefetch(
                'directexchangeparticipants_set',
                queryset=DirectExchangeParticipants.objects.all(),
                to_attr='options'
            )
        ).filter(
            directexchangeparticipants__participant_nmec=request.user.username
        ).all())

        exchanges = marketplace_exchanges + direct_exchanges
        # exchanges = sorted(exchanges, key=lambda request: request.date)

        if course_unit_name_filter:
            marketplace_exchanges = list(filter(
                lambda x: ExchangeController.courseUnitNameFilterInExchangeOptions(x.options, course_unit_name_filter),
                exchanges
            ))

        return JsonResponse(self.build_pagination_payload(request, marketplace_exchanges), safe=False)

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
                "type": ExchangeController.getExchangeType(exchange).toString(),
                "issuer_name": exchange.issuer_name,
                "issuer_nmec": exchange.issuer_nmec,
                "accepted": exchange.accepted,
                "options": ExchangeController.getOptionsDependinOnExchangeType(exchange),
                "date": exchange.date
            } for exchange in page_obj]
        }
