import hashlib
from django.http import Http404
from django.http.response import HttpResponse, JsonResponse, json
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from university.exchange.utils import convert_sigarra_schedule, curr_semester_weeks, get_student_schedule_url, update_schedule_accepted_exchanges

class StudentScheduleView(APIView):
    def get(self, request, format=None):

        (semana_ini, semana_fim) = curr_semester_weeks();

        try:
            response = requests.get(get_student_schedule_url(
                202108848, #request.session["username"],
                semana_ini,
                semana_fim
            ), cookies=request.COOKIES)

            if (response.status_code != 200):
                return HttpResponse(status=response.status_code)

            schedule_data = response.json()['horario']
            old_schedule = hashlib.sha256(json.dumps(schedule_data, sort_keys=True).encode()).hexdigest()

            update_schedule_accepted_exchanges(request.session["username"], schedule_data, request.COOKIES)

            new_schedule = hashlib.sha256(json.dumps(schedule_data, sort_keys=True).encode()).hexdigest()
            sigarra_synchronized = old_schedule == new_schedule

            new_response = JsonResponse({"schedule": convert_sigarra_schedule(schedule_data), "noChanges": sigarra_synchronized}, safe=False)
            new_response.status_code = response.status_code
            
            return new_response 
        
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": e}, safe=False)
