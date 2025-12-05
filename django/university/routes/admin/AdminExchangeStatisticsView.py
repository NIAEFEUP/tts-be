from rest_framework.views import APIView
from django.http import JsonResponse


from exchange.models import DirectExchange
from exchange.models import MarketplaceExchange
from exchange.models import ExchangeUrgentRequests

class AdminExchangeStatisticsView(APIView):
    def get(self, request):


        #total requests
        total_requests = DirectExchange.objects.count()
        total_requests += MarketplaceExchange.objects.count()
        total_requests += ExchangeUrgentRequests.objects.count()

        #accepted requests
        accepted_count = DirectExchange.objects.filter(accepted=1).count()
        accepted_count += MarketplaceExchange.objects.filter(accepted=1).count()
        
        #rejected requests
        rejected_count = DirectExchange.objects.filter(accepted=0).count()
        rejected_count += MarketplaceExchange.objects.filter(accepted=0).count()

        #pending requestsx
        pending_count = total_requests - (accepted_count + rejected_count)


        statistics = {
            'total_exchanges': total_requests,
            'accepted_exchanges': accepted_count,
            'rejected_exchanges': rejected_count,
            'pending_exchanges': pending_count
        }

        return JsonResponse(statistics, safe=False)
