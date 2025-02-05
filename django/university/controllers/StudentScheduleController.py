import json
import hashlib

from django.http.response import HttpResponse, JsonResponse

from university.controllers.ExchangeController import ExchangeController
from university.controllers.ClassController import ClassController
from university.controllers.SigarraController import SigarraController

from university.models import UserCourseUnits, Slot

class StudentScheduleController:
    @staticmethod
    def retrieveCourseUnitClasses(sigarra_controller, username):
        schedule = StudentScheduleController.getSchedule(username)
        schedule_data = schedule

        ExchangeController.update_schedule_accepted_exchanges(username, schedule_data)

        course_unit_classes = set()
        for scheduleItem in schedule_data:
            print("SCHEDULE ITEM: ", scheduleItem)
            course_unit_classes.add((scheduleItem["courseInfo"]["id"], scheduleItem["classInfo"]["name"]))
        
        return course_unit_classes

    @staticmethod
    def getSchedule(username):
        if len(UserCourseUnits.objects.filter(user_nmec = str(username))) == 0:
            return StudentScheduleController.retrieveScheduleFromSigarra(username)
        else:
            return StudentScheduleController.retrieveScheduleFromDatabase(username)
    
    @staticmethod
    def retrieveScheduleFromSigarra(username):
        sigarra_res = SigarraController().get_student_schedule(username)
            
        if sigarra_res.status_code != 200:
            return HttpResponse(status=sigarra_res.status_code)

        schedule_data = sigarra_res.data

        old_schedule = hashlib.sha256(json.dumps(schedule_data, sort_keys=True).encode()).hexdigest()

        ExchangeController.update_schedule_accepted_exchanges(username, schedule_data)

        new_schedule = hashlib.sha256(json.dumps(schedule_data, sort_keys=True).encode()).hexdigest()

        return schedule_data


    @staticmethod
    def retrieveScheduleFromDatabase(username):
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

        print("returned schedule wrong, right?: ", schedule)

        return schedule

    @staticmethod
    def getScheduleFromClass(class_):
        course_unit = class_.course_unit

        slot_ids = [sc.slot_id for sc in class_.slotclass_set.all()]
        slots = Slot.objects.filter(id__in=slot_ids)

        slot_list = list(map(ClassController.get_professors, slots))

        return {
                "courseInfo": {
                    'id': course_unit.id,
                    'course_unit_id': course_unit.id,
                    'acronym': course_unit.acronym,
                    'name': course_unit.name,
                    'url': course_unit.url
                },
                "classInfo": {
                    'id': class_.id,
                    'name': class_.name,
                    'filteredTeachers': [],
                    'slots': slot_list
                }
            }
