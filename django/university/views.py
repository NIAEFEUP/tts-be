from django.http.response import HttpResponse
from university.models import Faculty
from university.models import Course
from university.models import CourseUnit
from university.models import Schedule
from university.models import Professor
from university.models import ScheduleProfessor
from university.models import CourseMetadata
from university.models import Statistics
from django.http import JsonResponse
from django.core import serializers
from rest_framework.decorators import api_view
from django.db.models import Max
from django.db import transaction
from university.stats import statistics, cache_statistics
import json
import os 
from django.utils import timezone
# Create your views here. 

"""
    Initialization of statistics.
"""

DEFAULT_YEAR = 2022
statistics(Course.objects.filter(year=DEFAULT_YEAR).values(), DEFAULT_YEAR)

def get_field(value):
    return value.field
    
@api_view(['GET'])
def faculty(request): 
    json_data = list(Faculty.objects.values())
    return JsonResponse(json_data, safe=False)

"""
    Returns all the major/major.  
    REQUEST: http://localhost:8000/course/<int:year>
"""
@api_view(['GET'])
def course(request, year):
    json_data = list(Course.objects.filter(year=year).values())
    return JsonResponse(json_data, safe=False)

"""
    Return all the units from a course/major. 
    REQUEST: course_units/<int:course_id>/<int:year>/<int:semester>/
"""

@api_view(['GET'])
def course_units(request, course_id, year, semester): 
    # Fetch CourseUnitYear model instances that match the attributes from the api url parameters.
    course_units_metadata = CourseMetadata.objects.filter(course__id = course_id, course_unit__semester = semester, course__year = year).select_related('course_unit').order_by('course_unit_year')

    json_data = list()

    # For each object in those course unit year objects we append the CourseUnit dictionary
    for course_units in course_units_metadata:
        course_units.__dict__.update(course_units.course_unit.__dict__)
        del course_units.__dict__["_state"]
        json_data.append(course_units.__dict__)
    
    course = Course.objects.get(id = course_id)

    with transaction.atomic():
        statistics, created = Statistics.objects.select_for_update().get_or_create(
            course_unit_id = course_id, 
            acronym = course.acronym,
            defaults = {"visited_times": 0, "last_updated": timezone.now()},
        )
        statistics.visited_times += 1
        statistics.last_updated = timezone.now()
        statistics.save()

    return JsonResponse(json_data, safe=False)

"""
    Returns the last year of a course.
"""
@api_view(['GET'])
def course_units_by_year(request, course_id, year, semester): 
    course_units_metadata = CourseMetadata.objects.filter(course__id = course_id, course_unit__semester = semester, course__year = year).select_related('course_unit')

    json_data = list()

    # For each object in those course unit year objects we append the CourseUnit dictionary
    for course_units in course_units_metadata:
        course_units.__dict__.update(course_units.course_unit.__dict__)
        del course_units.__dict__["_state"]
        json_data.append(course_units.__dict__)

    return JsonResponse(json_data, safe=False)

"""
    Returns the last year of a course.
"""
@api_view(['GET'])
def course_last_year(request, course_id):
    max_year = CourseMetadata.objects.filter(course__id=course_id).aggregate(Max('course_unit_year')).get('course_unit_year__max')
    json_data = {"max_year": max_year}
    return JsonResponse(json_data, safe=False)

"""
    Returns the schedule of a course unit.
"""
@api_view(['GET'])
def schedule(request, course_unit_id):
    schedules = list(Schedule.objects.filter(course_unit=course_unit_id).order_by('class_name').values())
    for schedule in schedules:
        schedule_professors = list(ScheduleProfessor.objects.filter(schedule=schedule['id']).values())
        acronyms = []
        for schedule_professor in schedule_professors:
            acronyms.append(Professor.objects.get(pk=schedule_professor['professor_sigarra_id']).professor_acronym)
        schedule['professor_acronyms'] = acronyms
    return JsonResponse(schedules, safe=False)

"""
    Returns the statistics of the requests.
"""
@api_view(['GET'])
def data(request):
    name = request.GET.get('name')
    password = request.GET.get('password')
    if name == os.environ['STATISTICS_NAME'] and password == os.environ['STATISTICS_PASS']:
        json_data = serializers.serialize("json", Statistics.objects.all())
        return HttpResponse(json_data, content_type='application/json')
    else:
       return HttpResponse(status=401)

"""
    Returns all the professors of a class of the schedule id
""" 

@api_view(["GET"])
def professor(request, schedule):
    schedule_professors = list(ScheduleProfessor.objects.filter(schedule=schedule).values())
    professors = []
    for schedule_professor in schedule_professors:
        professor = Professor.objects.get(pk=schedule_professor['professor_sigarra_id'])
        professors.append({
            'sigarra_id': professor.sigarra_id,
            'professor_acronym': professor.professor_acronym,
            'professor_name': professor.professor_name
        })
    return JsonResponse(professors, safe=False)
