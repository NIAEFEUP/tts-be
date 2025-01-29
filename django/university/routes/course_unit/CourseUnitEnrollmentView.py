import json
from rest_framework.views import APIView
from university.models import CourseUnitEnrollments, CourseUnitEnrollmentOptions, UserCourseUnits

from django.db import transaction

from django.http import HttpResponse, JsonResponse

class CourseUnitEnrollmentView(APIView):
    def post(self, request):
        enrollments = request.POST.getlist("enrollCourses[]")

        student_course_units = list(UserCourseUnits.objects.filter(user_nmec=request.user.username).all())

        with transaction.atomic():
            course_unit_enrollment = CourseUnitEnrollments.objects.create(
                user_nmec=request.user.username,
                accepted=False
            )
            course_unit_enrollment.save()

            models_to_save = []
            for enrollment in enrollments:
                enrollment_metadata = json.loads(enrollment) 

                if len(list(filter(lambda x: x.course_unit_id == enrollment_metadata["course_unit_id"], student_course_units))) > 0:
                    return JsonResponse({"error": "Não te podes inscrever a disciplinas em que já tens uma inscrição!"}, status=400)

                db_enrollment = CourseUnitEnrollmentOptions(
                    course_unit_id=enrollment_metadata["course_unit_id"],
                    class_field_id=enrollment_metadata["class_id"],
                    course_unit_enrollment=course_unit_enrollment
                )
                models_to_save.append(db_enrollment)

            CourseUnitEnrollmentOptions.objects.bulk_create(models_to_save)
        
        return HttpResponse(status=200)