from django.http.response import HttpResponse

from university.controllers.ExchangeController import ExchangeController

class StudentScheduleController:
    @staticmethod
    def retrieveCourseUnitClasses(sigarra_controller, username):
        sigarra_res = sigarra_controller.get_student_schedule(username)
            
        if sigarra_res.status_code != 200:
            return HttpResponse(status=sigarra_res.status_code)

        schedule_data = sigarra_res.data

        ExchangeController.update_schedule_accepted_exchanges(username, schedule_data)

        ids = set()
        course_unit_classes = set()
        for scheduleItem in schedule_data:
            if scheduleItem["tipo"] != "T" or scheduleItem["tipo"] != 'O':
                if int(scheduleItem["ocorrencia_id"]) in ids:
                    continue
                else:
                    course_unit_classes.add((scheduleItem["ocorrencia_id"], scheduleItem["turma_sigla"]))
                    ids.add(int(scheduleItem["ocorrencia_id"]))
        
        return course_unit_classes

