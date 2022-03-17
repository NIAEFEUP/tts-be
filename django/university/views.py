from django.http.response import HttpResponse
from university.models import Faculty
from university.models import Course
from university.models import CourseUnit
from university.models import Schedule
from django.http import JsonResponse
from django.core import serializers
from rest_framework.decorators import api_view
import json
# Create your views here. 

@api_view(['GET'])
def faculty(request): 
    json_data = serializers.serialize('json', Faculty.objects.all())
    return HttpResponse(json_data, content_type="application/json")

@api_view(['GET'])
def course(request):
    json_data = serializers.serialize('json', Course.objects.all())
    return HttpResponse(json_data, content_type="application/json")


@api_view(['GET'])
def course_units(request, course_id, semester):
    json_data = serializers.serialize('json', CourseUnit.objects.filter(course=course_id, semester=semester))
    return HttpResponse(json_data, content_type="application/json")

@api_view(['GET'])
def schedule(request, course_unit_id):
    json_data = serializers.serialize('json', Schedule.objects.filter(course_unit=course_unit_id))
    return HttpResponse(json_data, content_type="application/json")


def course_units_by_year(request, course_id, semester): 
    query_result = list(CourseUnit.objects.filter(course=course_id, semester=semester).order_by('course_year'))  
    number_of_years = query_result[-1].course_year

    res = []
    for _ in range(number_of_years): 
        res.append([])

    print(res)
    for course_unit in query_result: 
        res[course_unit.course_year-1].append(course_unit) 

    print(res)
    json_data = serializers.serialize('json', res)   
    return HttpResponse(json_data, content_type="application/json")

