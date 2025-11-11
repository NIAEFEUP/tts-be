from django.http import JsonResponse
from django.db import models
from django.db.models import Case, When, IntegerField
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from university.models import CourseUnit


class AdminExchangeCourseUnitsSearchView(APIView):
    """Return course units filtered by search query.

    This endpoint requires authentication. It returns a JSON object with a
    `course_units` array containing basic fields for each course unit.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        exchange_courses_list = settings.EXCHANGE_COURSES_LIST
        allowed_course_ids = [int(x.strip()) for x in exchange_courses_list.split(',') if x.strip()]

        course_units_qs = CourseUnit.objects.filter(coursemetadata__course__id__in=allowed_course_ids).distinct().values(
            "id", "name", "acronym", "course__name", "course__acronym", "semester", "year"
        )

        q = request.GET.get('q', '').strip()
        limit = min(int(request.GET.get('limit', 10)), 100) 
        if q:
            course_units_qs = course_units_qs.annotate(
                priority=Case(
                    When(acronym__iexact=q, then=4),
                    When(course__acronym__iexact=q, then=3),
                    When(acronym__icontains=q, then=2),
                    When(course__acronym__icontains=q, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ).filter(
                models.Q(name__icontains=q) |
                models.Q(acronym__icontains=q) |
                models.Q(course__name__icontains=q) |
                models.Q(course__acronym__icontains=q)
            ).order_by('-priority', 'acronym')[:limit]  

        course_units = []
        for cu in course_units_qs:
            cu = dict(cu)
            cu["course_name"] = cu.pop("course__name")
            cu["course_acronym"] = cu.pop("course__acronym")
            course_units.append(cu)

        return JsonResponse({"course_units": course_units}, safe=False)