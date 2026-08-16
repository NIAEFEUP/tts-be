from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from django.conf import settings

from university.models import Course

from exchange.models import ExchangeAdmin, ExchangeAdminCourses

class AdminExchangeCoursesView(APIView):
    def get(self, request):
        admin_username = request.GET.get('admin_username', request.user.username)
        
        admin_exchange_courses = ExchangeAdminCourses.objects.filter(exchange_admin__username=admin_username)
        courses = list(Course.objects.filter(id__in=admin_exchange_courses.values_list("course_id", flat=True)).values())

        return JsonResponse(courses, safe=False)

    def post(self, request):
        exchange_courses_list = settings.EXCHANGE_COURSES_LIST
        allowed_course_ids = [int(x.strip()) for x in exchange_courses_list.split(',') if x.strip()]

        course_id = request.data.get('course_id')
        admin_username = request.data.get('admin_username', request.user.username)
        if not course_id:
            return JsonResponse({'error': 'course_id required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        if course.id not in allowed_course_ids:
            return JsonResponse({'error': 'Course not allowed for exchange'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            admin = ExchangeAdmin.objects.get(username=admin_username)
        except ExchangeAdmin.DoesNotExist:
            return JsonResponse({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)

        if ExchangeAdminCourses.objects.filter(exchange_admin=admin, course=course).exists():
            return JsonResponse({'error': 'Course already assigned'}, status=status.HTTP_400_BAD_REQUEST)

        ExchangeAdminCourses.objects.create(exchange_admin=admin, course=course)
        return JsonResponse({'success': True})

    def delete(self, request, course_id=None):
        if not course_id:
            return JsonResponse({'error': 'course_id required'}, status=status.HTTP_400_BAD_REQUEST)

        admin_username = request.GET.get('admin_username', request.user.username)

        try:
            admin = ExchangeAdmin.objects.get(username=admin_username)
            course = Course.objects.get(id=course_id)
            relation = ExchangeAdminCourses.objects.get(exchange_admin=admin, course=course)
            relation.delete()
            return JsonResponse({'success': True})
        except (ExchangeAdmin.DoesNotExist, Course.DoesNotExist, ExchangeAdminCourses.DoesNotExist):
            return JsonResponse({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
