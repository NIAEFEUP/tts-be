from django.http import HttpResponse
from django.views import View

from university.controllers.AdminExchangeStateChangeController import AdminExchangeStateChangeController

class AdminExchangeRequestRejectView(View):
    def put(self, request, request_type, id):
        AdminExchangeStateChangeController().update_state_to(request_type, id, "rejected")
        
        return HttpResponse(status=200)