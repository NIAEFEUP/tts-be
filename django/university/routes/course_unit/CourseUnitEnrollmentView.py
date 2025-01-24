import json
from rest_framework.views import APIView
from university.models import CourseUnitEnrollments

from django.http import HttpResponse 

class CourseUnitEnrollmentView(APIView):
    def post(self, request):
        enrollments = request.POST.getlist("enrollCourses[]")

        models_to_save = []
        for enrollment in enrollments:
            enrollment_metadata = json.loads(enrollment)

            db_enrollment = CourseUnitEnrollments(
                user_nmec=request.user.username,
                course_unit_id=enrollment_metadata["course_unit_id"],
                class_field_id=enrollment_metadata["class_id"],
                accepted=False
            )
            models_to_save.append(db_enrollment)

        CourseUnitEnrollments.objects.bulk_create(models_to_save)
        
        return HttpResponse(status=200)