from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from django.conf import settings

from university.models import CourseUnit, CourseMetadata

from exchange.models import ExchangeAdmin, ExchangeAdminCourseUnits

class AdminExchangeCourseUnitsView(APIView):
    def get(self, request):
        # Allow admins to view other admins' course units
        admin_username = request.GET.get('admin_username', request.user.username)
        
        admin_exchange_course_units = ExchangeAdminCourseUnits.objects.filter(exchange_admin__username=admin_username)
        course_units = list(CourseUnit.objects.filter(id__in=admin_exchange_course_units.values_list("course_unit_id", flat=True)).values())

        return JsonResponse(course_units, safe=False)

    def post(self, request):
        exchange_courses_list = settings.EXCHANGE_COURSES_LIST
        allowed_course_ids = [int(x.strip()) for x in exchange_courses_list.split(',') if x.strip()]

        course_unit_id = request.data.get('course_unit_id')
        admin_username = request.data.get('admin_username', request.user.username)
        if not course_unit_id:
            return JsonResponse({'error': 'course_unit_id required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course_unit = CourseUnit.objects.get(id=course_unit_id)
        except CourseUnit.DoesNotExist:
            return JsonResponse({'error': 'Course unit not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the course unit belongs to an allowed course
        course_metadata = CourseMetadata.objects.filter(course_unit=course_unit).first()
        if not course_metadata or course_metadata.course.id not in allowed_course_ids:
            return JsonResponse({'error': 'Course unit not allowed for exchange'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            admin = ExchangeAdmin.objects.get(username=admin_username)
        except ExchangeAdmin.DoesNotExist:
            return JsonResponse({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)

        if ExchangeAdminCourseUnits.objects.filter(exchange_admin=admin, course_unit=course_unit).exists():
            return JsonResponse({'error': 'Course unit already assigned'}, status=status.HTTP_400_BAD_REQUEST)

        ExchangeAdminCourseUnits.objects.create(exchange_admin=admin, course_unit=course_unit)
        return JsonResponse({'success': True})

    def delete(self, request, course_unit_id=None):
        if not course_unit_id:
            return JsonResponse({'error': 'course_unit_id required'}, status=status.HTTP_400_BAD_REQUEST)

        admin_username = request.GET.get('admin_username', request.user.username)

        try:
            admin = ExchangeAdmin.objects.get(username=admin_username)
            course_unit = CourseUnit.objects.get(id=course_unit_id)
            relation = ExchangeAdminCourseUnits.objects.get(exchange_admin=admin, course_unit=course_unit)
            relation.delete()
            return JsonResponse({'success': True})
        except (ExchangeAdmin.DoesNotExist, CourseUnit.DoesNotExist, ExchangeAdminCourseUnits.DoesNotExist):
            return JsonResponse({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)



