from django.http import HttpResponse 
from django.views import View

from university.controllers.AdminExchangeStateChangeController import AdminExchangeStateChangeController

class AdminExchangeRequestAcceptView(View):
    def put(self, request, request_type, id):
        AdminExchangeStateChangeController().update_state_to(request_type, id, "treated")
    
        return HttpResponse(status=200)