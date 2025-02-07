import json

from university.controllers.SigarraController import SigarraController
from university.controllers.StudentScheduleController import StudentScheduleController

from university.models import UserCourseUnits, Class, StudentCourseMetadata, Course

class StudentController:
    """
        This class will contain methods to manipulate student data that is not on sigarra.

        Handling of student data hosted in sigarra will be done in SigarraController while the handling
        of student data hosted inside our database will be done here.
    """

    @staticmethod
    def student_class(nmec, course_unit_id):
        potential_user_class = UserCourseUnits.objects.filter(user_nmec=nmec, course_unit_id__id=course_unit_id)

        if potential_user_class.exists():
            return potential_user_class.first().class_field
        else:
            return None

    @staticmethod
    def populate_user_course_unit_data(nmec: int, erase_previous: bool = False):
        if(erase_previous):
            UserCourseUnits.objects.filter(user_nmec=nmec).delete()

        course_units = StudentScheduleController.retrieveCourseUnitClasses(SigarraController(), nmec)
        
        for item in course_units:
            (course_unit_id, class_acronym) = item

            corresponding_class = Class.objects.filter(course_unit__id=course_unit_id, name=class_acronym.split("+")[0]).first()

            if not corresponding_class:
                continue
            
            user_course_unit = UserCourseUnits(
                user_nmec=nmec,
                course_unit_id=course_unit_id, 
                class_field=corresponding_class
            )
            user_course_unit.save()

    @staticmethod
    def populate_course_metadata(nmec, erase_previous: bool = False):
        if(erase_previous):
            StudentCourseMetadata.objects.filter(nmec=nmec).delete()

        sigarra_controller = SigarraController()

        student_festid = sigarra_controller.get_student_festid(nmec)

        if student_festid is not None:
            models_to_save = []

            for item in student_festid:
                course = Course.objects.filter(
                    faculty_id = item["faculty"],
                    name = item["course_name"]
                )

                if len(course) == 0:
                    continue
                    
                models_to_save.append(
                    StudentCourseMetadata(
                        nmec = nmec,
                        fest_id = item["fest_id"],
                        course = course.get()
                    )
                )

            StudentCourseMetadata.objects.bulk_create(models_to_save)