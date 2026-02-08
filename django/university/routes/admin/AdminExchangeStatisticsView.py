from rest_framework.views import APIView
from django.http import JsonResponse


from exchange.models import DirectExchange
from exchange.models import MarketplaceExchange
from exchange.models import ExchangeUrgentRequests

class AdminExchangeStatisticsView(APIView):
    def get(self, request):


        direct_exchanges = DirectExchange.objects.all()
        marketplace_exchanges = MarketplaceExchange.objects.all()
        urgent_requests = ExchangeUrgentRequests.objects.all()

        total_requests = direct_exchanges.count() + marketplace_exchanges.count() + urgent_requests.count()

        accepted_count = len(list(filter(lambda exchange: exchange.accepted == 1, direct_exchanges)))
        accepted_count += len(list(filter(lambda exchange: exchange.accepted == 1, marketplace_exchanges)))

        rejected_count = len(list(filter(lambda exchange: exchange.accepted == 0, direct_exchanges)))
        rejected_count += len(list(filter(lambda exchange: exchange.accepted == 0, marketplace_exchanges)))

        pending_count = total_requests - (accepted_count + rejected_count)


        statistics = {
            'total_exchanges': total_requests,
            'accepted_exchanges': accepted_count,
            'rejected_exchanges': rejected_count,
            'pending_exchanges': pending_count
        }

        return JsonResponse(statistics, safe=False)
