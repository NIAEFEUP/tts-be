from university.models import CourseMetadata

class CourseUnitController:
    @staticmethod
    def course_unit_curricular_year(course_unit_id):
        course_metadata = CourseMetadata.objects.filter(course_unit_id=course_unit_id).get()

        return course_metadata.course_unit_year

    @staticmethod
    def course_unit_major(course_unit_id):
        course_metadata = CourseMetadata.objects.filter(course_unit_id=course_unit_id).get()

        return course_metadata.course.id