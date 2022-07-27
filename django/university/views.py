from django.http.response import HttpResponse
from university.models import Faculty
from university.models import Course
from university.models import CourseUnit
from university.models import Schedule
from django.http import JsonResponse
from django.core import serializers
from rest_framework.decorators import api_view
from django.db.models import Max

import json
# Create your views here. 

def get_field(value):
    return value.field
    
@api_view(['GET'])
def faculty(request): 
    json_data = serializers.serialize('json', Faculty.objects.all())
    return HttpResponse(json_data, content_type="application/json")

"""
    Returns all the major/major. 
"""
@api_view(['GET'])
def course(request):
    json_data = list(Course.objects.values())
    return JsonResponse(json_data, safe=False)

"""
    Return all the units from a course/major. 
"""
@api_view(['GET'])
def course_units(request, course_id, semester): 
    json_data = list(CourseUnit.objects.filter(course=course_id, semester=semester).order_by('course_year').values())
    return JsonResponse(json_data, safe=False)

"""
    Returns the last year of a course.
"""
@api_view(['GET'])
def course_last_year(request, course_id):
    max_year = CourseUnit.objects.filter(course=course_id).aggregate(Max('course_year')).get('course_year__max')
    json_data = {"max_year": max_year}
    return JsonResponse(json_data, safe=False)


"""
    Get all the units of a course in a certain year. 
"""
@api_view(['GET'])
def course_units_by_year(request, course_id, year, semester): 
    json_data = list(CourseUnit.objects.filter(course=course_id, semester=semester, course_year=year).values())
    return JsonResponse(json_data, safe=False)


"""
"""
@api_view(['GET'])
def schedule(request, course_unit_id):
    json_data = list(Schedule.objects.filter(course_unit=course_unit_id).order_by('class_name').values())
    return JsonResponse(json_data, safe=False)
