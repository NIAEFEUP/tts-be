import hashlib
import json
from django.http.response import HttpResponse, JsonResponse
import requests
from rest_framework.views import APIView

from university.models import StudentCourseMetadata, DirectExchange, DirectExchangeParticipants

from university.controllers.ClassController import ClassController
from university.controllers.SigarraController import SigarraController
from university.controllers.ExchangeController import ExchangeController
from university.controllers.StudentController import StudentController
from university.exchange.utils import convert_sigarra_schedule

from university.models import UserCourseUnits

class StudentScheduleView(APIView):
    def get(self, request, nmec=""):
        username = nmec if nmec != "" else request.user.username
        
        try:
            student_course_units = list(UserCourseUnits.objects.filter(user_nmec=username))

            new_response = None

            if len(student_course_units) == 0:
                new_response = self.fetch_from_sigarra(request, username)
            else:
                new_response = self.fetch_from_db(request, username)

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

    def fetch_from_db(self, request, username):
        course_units = UserCourseUnits.objects.filter(user_nmec = username)
        class_ids = list(map(lambda course_unit: course_unit.class_field.id, course_units))

        schedule = []
        for course_unit in course_units:
            classes = ClassController.get_classes(course_unit.course_unit.id)
            classes = list(filter(lambda class_: class_["id"] in class_ids, classes))

            for class_ in classes:
                for slot in class_["slots"]:
                    schedule.append({
                        "courseInfo": {
                            'id': course_unit.course_unit.id,
                            'course_unit_id': course_unit.course_unit.id,
                            'acronym': course_unit.course_unit.acronym,
                            'name': course_unit.course_unit.name,
                            'url': course_unit.course_unit.url
                        },
                        "classInfo": {
                            'id': class_["id"],
                            'name': class_["name"],
                            'filteredTeachers': [],
                            'slots': [slot]
                        }
                    })

        return JsonResponse({
                "schedule": schedule,
                "noChanges": len(DirectExchangeParticipants.objects.filter(
                    participant_nmec=username,
                    direct_exchange__accepted=True
                )) == 0
            }, 
            safe=False
        )

    def fetch_from_sigarra(self, request, username):
        sigarra_res = SigarraController().get_student_schedule(username)
            
        if sigarra_res.status_code != 200:
            return HttpResponse(status=sigarra_res.status_code)

        schedule_data = sigarra_res.data

        old_schedule = hashlib.sha256(json.dumps(schedule_data, sort_keys=True).encode()).hexdigest()

        ExchangeController.update_schedule_accepted_exchanges(username, schedule_data)

        new_schedule = hashlib.sha256(json.dumps(schedule_data, sort_keys=True).encode()).hexdigest()

        sigarra_synchronized = old_schedule == new_schedule

        new_response = JsonResponse({"schedule": convert_sigarra_schedule(schedule_data), "noChanges": sigarra_synchronized}, safe=False)
        new_response.status_code = sigarra_res.status_code

        return new_response

