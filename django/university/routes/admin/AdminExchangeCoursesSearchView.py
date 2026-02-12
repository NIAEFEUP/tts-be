from django.http import JsonResponse
from django.db import models
from django.db.models import Value
from django.db.models.functions import Replace
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from university.models import Course


class AdminExchangeCoursesSearchView(APIView):
    """Return courses filtered by search query.

    This endpoint requires authentication. It returns a JSON object with a
    `courses` array containing basic fields for each course.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        exchange_courses_list = settings.EXCHANGE_COURSES_LIST
        allowed_course_ids = [int(x.strip()) for x in exchange_courses_list.split(',') if x.strip()]

        courses_qs = Course.objects.filter(id__in=allowed_course_ids).values(
            "id", "name", "acronym", "course_type", "year", "faculty__acronym", "faculty__name"
        )

        q = request.GET.get('q', '').strip()
        limit = min(int(request.GET.get('limit', 10)), 100)  
        if q:
            courses_qs = courses_qs.annotate(clean_acronym=Replace('acronym', Value('.'), Value(''))).filter(
                models.Q(name__icontains=q) |
                models.Q(acronym__icontains=q) |
                models.Q(clean_acronym__icontains=q)
            )[:limit]  

        courses = []
        for c in courses_qs:
            c = dict(c)
            c["faculty_acronym"] = c.pop("faculty__acronym")
            c["faculty_name"] = c.pop("faculty__name")
            courses.append(c)

        return JsonResponse({"courses": courses}, safe=False)