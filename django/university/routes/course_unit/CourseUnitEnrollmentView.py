import json
from rest_framework.views import APIView
from university.models import CourseUnitEnrollments, CourseUnitEnrollmentOptions, UserCourseUnits, ExchangeAdmin
from university.serializers.CourseUnitEnrollmentsSerializer import CourseUnitEnrollmentsSerializer
from university.controllers.CourseUnitController import CourseUnitController
from university.controllers.AdminRequestFiltersController import AdminRequestFiltersController

from django.utils import timezone
from django.core.paginator import Paginator

from django.db import transaction

from django.http import HttpResponse, JsonResponse

class CourseUnitEnrollmentView(APIView):
    def __init__(self):
        self.filter_actions = {
            "activeCourse": self.filter_active_course,
            "activeCurricularYear": self.filter_active_curricular_year,
            "activeStates": self.filter_active_state
        }

    def filter_active_course(self, exchanges, major_id):
        return list(
            filter(
                lambda exchange: len(list(
                    filter(
                        lambda course_unit: int(CourseUnitController.course_unit_major(course_unit.get("course_unit").get("id"))) == int(major_id), exchange.get("options"))
                    )) > 0,
                exchanges
            )
        )

    def filter_active_curricular_year(self, exchanges, curricular_year):
        return list(
            filter(
                lambda exchange: len(list(
                    filter(
                        lambda course_unit: int(CourseUnitController.course_unit_curricular_year(course_unit.get("course_unit").get("id"))) == int(curricular_year), exchange.get("options"))
                    )) > 0,
                exchanges
            )
        )

    def filter_active_state(self, exchanges, state):
        states = state.split(",")
        return list(
            filter(
                lambda exchange: exchange.get("admin_state") in states,
                exchanges
            )
        )

    def get(self, request):
        is_admin = ExchangeAdmin.objects.filter(username=request.user.username).exists()
        if not(is_admin):
            return HttpResponse(status=403) 

        enrollments = list(map(lambda enrollment: CourseUnitEnrollmentsSerializer(enrollment).data, CourseUnitEnrollments.objects.all().order_by('date')))

        paginator = Paginator(enrollments, 48)
        page_number = request.GET.get("page")
        enrollments = [x for x in paginator.get_page(page_number if page_number != None else 1)]

        for filter in AdminRequestFiltersController.filter_values():
            if request.GET.get(filter):
                enrollments = self.filter_actions[filter](enrollments, request.GET.get(filter))

        return JsonResponse({
            "enrollments": enrollments,
            "total_pages": paginator.num_pages
        }, safe=False)

    def post(self, request):
        enrollments = request.POST.getlist("enrollCourses[]")

        student_course_units = list(UserCourseUnits.objects.filter(user_nmec=request.user.username).all())

        with transaction.atomic():
            course_unit_enrollment = CourseUnitEnrollments.objects.create(
                user_nmec=request.user.username,
                accepted=False,
                admin_state="untreated",
                date=timezone.now()
            )
            course_unit_enrollment.save()

            models_to_save = []
            for enrollment in enrollments:
                enrollment_metadata = json.loads(enrollment) 

                if enrollment_metadata["enrolling"] and len(list(filter(lambda x: x.course_unit_id == enrollment_metadata["course_unit_id"], student_course_units))) > 0:
                    return JsonResponse({"error": "Não te podes inscrever a disciplinas em que já tens uma inscrição!"}, status=400)

                db_enrollment = CourseUnitEnrollmentOptions(
                    course_unit_id=enrollment_metadata["course_unit_id"],
                    course_unit_enrollment=course_unit_enrollment,
                    enrolling=enrollment_metadata["enrolling"],
                    date=timezone.now()
                )
                models_to_save.append(db_enrollment)

            CourseUnitEnrollmentOptions.objects.bulk_create(models_to_save)
        
        return HttpResponse(status=200)