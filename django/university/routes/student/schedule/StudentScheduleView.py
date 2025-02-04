import hashlib
import json
from django.http.response import HttpResponse, JsonResponse
import requests
from rest_framework.views import APIView

from university.models import StudentCourseMetadata

from university.controllers.SigarraController import SigarraController
from university.controllers.ExchangeController import ExchangeController
from university.controllers.StudentController import StudentController
from university.exchange.utils import convert_sigarra_schedule

from university.models import UserCourseUnits

class StudentScheduleView(APIView):
    def get(self, request, nmec=""):
        sigarra_controller = SigarraController()
        
        try:
            sigarra_res = sigarra_controller.get_student_schedule(request.user.username if nmec == "" else int(nmec))
            
            if sigarra_res.status_code != 200:
                return HttpResponse(status=sigarra_res.status_code)

            schedule_data = sigarra_res.data

            old_schedule = hashlib.sha256(json.dumps(schedule_data, sort_keys=True).encode()).hexdigest()

            ExchangeController.update_schedule_accepted_exchanges(request.user.username, schedule_data)

            new_schedule = hashlib.sha256(json.dumps(schedule_data, sort_keys=True).encode()).hexdigest()

            sigarra_synchronized = old_schedule == new_schedule

            new_response = JsonResponse({"schedule": convert_sigarra_schedule(schedule_data), "noChanges": sigarra_synchronized}, safe=False)
            new_response.status_code = sigarra_res.status_code

            if(nmec == ""):
                if len(StudentCourseMetadata.objects.filter(nmec = request.user.username)) == 0:
                    StudentController.populate_course_metadata(
                        request.user.username,
                    )

                if len(UserCourseUnits.objects.filter(user_nmec = request.user.username)) == 0:
                    StudentController.populate_user_course_unit_data(
                        request.user.username, 
                    ) 

            return new_response 
        
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": e}, safe=False)
