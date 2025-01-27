import json
import jwt
import requests
import datetime

from django.http import HttpResponse, JsonResponse
from django.views import View

from university.controllers.AdminRequestFiltersController import AdminRequestFiltersController
from university.controllers.CourseUnitController import CourseUnitController 
from university.models import ExchangeUrgentRequests, ExchangeAdmin
from university.serializers.ExchangeUrgentRequestSerializer import ExchangeUrgentRequestSerializer

class ExchangeUrgentView(View):
    def __init__(self):
        self.filter_actions = {
            "activeCourse": self.filter_active_course,
            "activeCurricularYear": self.filter_active_curricular_year,
            "activeState": self.filter_active_state
        }

    def filter_active_course(self, exchanges, major_id):
        return list(
            filter(
                lambda exchange: len(list(
                    filter(
                        lambda course_unit: int(CourseUnitController.course_unit_major(course_unit.get("course_unit").get("id"))) == int(major_id), exchange.get("options"))
                    )) > 0,
                exchanges
            )
        )

    def filter_active_curricular_year(self, exchanges, curricular_year):
        return list(
            filter(
                lambda exchange: len(list(
                    filter(
                        lambda course_unit: int(CourseUnitController.course_unit_curricular_year(course_unit.get("course_unit").get("id"))) == int(curricular_year), exchange.get("options"))
                    )) > 0,
                exchanges
            )
        )

    def filter_active_state(self, exchanges, state):
        return []

    def get(self, request):
        is_admin = ExchangeAdmin.objects.filter(username=request.user.username).exists()
        if not(is_admin):
            return HttpResponse(status=403) 

        exchanges = list(map(lambda exchange: ExchangeUrgentRequestSerializer(exchange).data, ExchangeUrgentRequests.objects.all()))

        for filter in AdminRequestFiltersController.filter_values():
            if request.GET.get(filter):
                exchanges = self.filter_actions[filter](exchanges, request.GET.get(filter))


        return JsonResponse(exchanges, safe=False)
    