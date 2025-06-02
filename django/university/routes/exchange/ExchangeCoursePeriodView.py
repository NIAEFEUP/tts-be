import json
import jwt
import requests
import datetime


from django.http import HttpResponse, JsonResponse
from django.views import View
from django.utils import timezone

from exchange.models import ExchangeExpirations, ExchangeAdmin, ExchangeAdminCourses
from university.models import CourseUnit, Course


class ExchangeCoursePeriodView(View):
    def post(self, request, course_id):
        start_date_str = request.POST.get('startDate')
        end_date_str = request.POST.get('endDate')

        is_course_admin = ExchangeAdminCourses.objects.filter(
            exchange_admin__username=request.user.username, 
            course=course_id
        ).exists()

        if not is_course_admin:
            return HttpResponse(status=403)

        if not course_id or not start_date_str or not end_date_str:
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        try:
            start_date = timezone.make_aware(
                datetime.datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            )
            end_date = timezone.make_aware(
                datetime.datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            )
        except ValueError as e:
            return JsonResponse({"error": f"Invalid date format: {str(e)}"}, status=400)

        if start_date >= end_date:
            return JsonResponse({"error": "Start date must be before end date"}, status=400)
        
        admin_course_units = CourseUnit.objects.filter(course__id=course_id)

        for course_unit in admin_course_units:
            course_unit_id = course_unit.id

            if ExchangeExpirations.objects.filter(
                course_unit_id=course_unit_id,
                active_date__lt=end_date,   
                end_date__gt=start_date      
            ).exists():
                return JsonResponse({"error": "This exchange period overlaps with an existing period for this course unit"}, safe=False, status=400)

            exchange_expiration = ExchangeExpirations(
                course_unit_id=course_unit_id,
                active_date=start_date,
                end_date=end_date
            )
            exchange_expiration.save()

        return JsonResponse({"success": True}, safe=False)
    
 