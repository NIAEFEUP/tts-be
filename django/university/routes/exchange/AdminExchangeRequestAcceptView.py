from django.http import HttpResponse 
from django.views import View

from university.controllers.AdminExchangeStateChangeController import AdminExchangeStateChangeController
from university.models import DirectExchange, ExchangeUrgentRequests, CourseUnitEnrollments

class AdminExchangeRequestAcceptView(View):
    def put(self, request, request_type, id):
        AdminExchangeStateChangeController().update_state_to(request_type, id, "treated")

        if request_type == "direct_exchange":
            DirectExchange.objects.filter(id=id).update(accepted=True)
        elif request_type == "urgent_exchange":
            ExchangeUrgentRequests.objects.filter(id=id).update(accepted=True)
        elif request_type == "enrollment":
            CourseUnitEnrollments.objects.filter(id=id).update(accepted=True)
        
        return HttpResponse(status=200)
