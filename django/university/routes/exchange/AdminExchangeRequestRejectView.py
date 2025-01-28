from django.http import HttpResponse, JsonResponse
from django.views import View

from university.models import DirectExchange, ExchangeUrgentRequests, CourseUnitEnrollments

from university.controllers.AdminRequestFiltersController import AdminRequestFiltersController
from university.controllers.CourseUnitController import CourseUnitController 
from university.models import ExchangeUrgentRequests, ExchangeAdmin
from university.serializers.ExchangeUrgentRequestSerializer import ExchangeUrgentRequestSerializer

class AdminExchangeRequestRejectView(View):
    def put(self, request, request_type, id):
        if request_type == "direct_exchange":
            DirectExchange.objects.filter(id=id).update(admin_state="rejected", accepted=False)
        elif request_type == "urgent_exchange":
            ExchangeUrgentRequests.objects.filter(id=id).update(admin_state="rejected", accepted=False) 
        elif request_type == "enrollment":
            CourseUnitEnrollments.objects.filter(id=id).update(admin_state="rejected", accepted=False)

        return HttpResponse(status=200)