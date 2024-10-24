import base64
import json
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http.response import HttpResponse, JsonResponse
from rest_framework.views import APIView

from university.controllers.ClassController import ClassController
from university.controllers.ExchangeController import ExchangeController
from university.controllers.SigarraController import SigarraController
from university.models import MarketplaceExchange, MarketplaceExchangeClass
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

        if course_unit_name_filter:
            marketplace_exchanges = list(filter(
                lambda x: ExchangeController.courseUnitNameFilterInExchangeOptions(x.options, course_unit_name_filter),
                marketplace_exchanges
            ))

        return JsonResponse(ExchangeController.build_pagination_payload(request, marketplace_exchanges), safe=False)

    def getExchangeOptionClasses(self, options):
        classes = sum(list(map(lambda option: ClassController.get_classes(option.course_unit_id), options)), [])
        return filter(lambda currentClass: any(currentClass["name"] == option.class_issuer_goes_from for option in options), classes)

