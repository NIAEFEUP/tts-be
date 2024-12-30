import hashlib
from django.http import Http404
from django.http.response import HttpResponse, JsonResponse, json
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from university.controllers.SigarraController import SigarraController
from university.exchange.utils import convert_sigarra_schedule, curr_semester_weeks, get_student_schedule_url, update_schedule_accepted_exchanges

class StudentScheduleView(APIView):
    def get(self, request):
        sigarra_controller = SigarraController()
        
        try:
            sigarra_res = sigarra_controller.get_student_schedule(request.user.username)
            
            if sigarra_res.status_code != 200:
                return HttpResponse(status=sigarra_res.status_code)

            schedule_data = sigarra_res.data
            old_schedule = hashlib.sha256(json.dumps(schedule_data, sort_keys=True).encode()).hexdigest()

            update_schedule_accepted_exchanges(request.user.username, schedule_data)

            new_schedule = hashlib.sha256(json.dumps(schedule_data, sort_keys=True).encode()).hexdigest()
            sigarra_synchronized = old_schedule == new_schedule

            new_response = JsonResponse({"schedule": convert_sigarra_schedule(schedule_data), "noChanges": sigarra_synchronized}, safe=False)
            new_response.status_code = sigarra_res.status_code
            
            return new_response 
        
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": e}, safe=False)
    
    @staticmethod
    def retrieveCourseUnitClasses(sigarra_controller, username):
        sigarra_res = sigarra_controller.get_student_schedule(username)
            
        if sigarra_res.status_code != 200:
            return HttpResponse(status=sigarra_res.status_code)

        schedule_data = sigarra_res.data

        update_schedule_accepted_exchanges(username, schedule_data)

        course_unit_classes = set()
        for scheduleItem in schedule_data:
            course_unit_classes.add((scheduleItem["ocorrencia_id"], scheduleItem["turma_sigla"]))
        
        return course_unit_classes

