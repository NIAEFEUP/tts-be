from django.http.response import HttpResponse
from university.models import Faculty
from university.models import Course
from university.models import CourseUnit
from university.models import Class
from university.models import Slot
from university.models import Professor
from university.models import SlotProfessor
from university.models import CourseMetadata
from university.models import Statistics
from university.models import Info
from university.models import SlotClass
from university.response.errors import course_unit_not_found_error
from django.http import JsonResponse
from django.core import serializers
from rest_framework.decorators import api_view
from rest_framework import status
from django.db.models import Max
from django.db import transaction
from university.controllers.ClassController import ClassController
import json
import os
from django.utils import timezone
from django.forms.models import model_to_dict


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


@api_view(['GET'])
def course_unit_by_id(request, course_unit_id):
    course_unit = CourseUnit.objects.filter(id=course_unit_id).first()
    if (course_unit == None):
        return JsonResponse(course_unit_not_found_error(course_unit_id), status=status.HTTP_404_NOT_FOUND)

    return JsonResponse(model_to_dict(course_unit), safe=False)


"""
    Return all the units from a course/major.
    REQUEST: course_units/<int:course_id>/<int:year>/<int:semester>/
"""


@api_view(['GET'])
def course_units(request, course_id, year, semester):
    # Fetch CourseUnitYear model instances that match the attributes from the api url parameters.
    course_units_metadata = CourseMetadata.objects.filter(
        course__id=course_id, course_unit__semester=semester, course__year=year).select_related('course_unit').order_by('course_unit_year')

    json_data = list()

    # For each object in those course unit year objects we append the CourseUnit dictionary
    for course_unit_metadata in course_units_metadata:
        course_unit_metadata.__dict__.update(
            course_unit_metadata.course_unit.__dict__)

        del course_unit_metadata.__dict__["_state"]

        json_data.append(course_unit_metadata.__dict__)

    course = Course.objects.get(id=course_id)

    with transaction.atomic():
        statistics, created = Statistics.objects.select_for_update().get_or_create(
            course_unit_id=course_id,
            acronym=course.acronym,
            defaults={"visited_times": 0, "last_updated": timezone.now()},
        )
        statistics.visited_times += 1
        statistics.last_updated = timezone.now()
        statistics.save()

    return JsonResponse(json_data, safe=False)


"""
    Returns the classes of a course unit.
"""


@ api_view(['GET'])
def classes(request, course_unit_id):
    return JsonResponse(ClassController.get_classes(course_unit_id), safe=False)


"""
    Returns the statistics of the requests.
"""


@ api_view(['GET'])
def data(request):
    name = request.GET.get('name')
    password = request.GET.get('password')
    if name == os.environ['STATISTICS_NAME'] and password == os.environ['STATISTICS_PASS']:
        json_data = serializers.serialize("json", Statistics.objects.all())
        return HttpResponse(json_data, content_type='application/json')
    else:
        return HttpResponse(status=401)


"""
    Returns all the professors of a class of the class id
"""


@ api_view(["GET"])
def professor(request, slot):
    slot_professors = list(SlotProfessor.objects.filter(slot_id=slot).values())

    professors = []

    for slot_professor in slot_professors:
        professor = Professor.objects.get(id=slot_professor['professor_id'])
        professors.append({
            'id': professor.id,
            'acronym': professor.professor_acronym,
            'name': professor.professor_name
        })

    return JsonResponse(professors, safe=False)


"""
    Returns the contents of the info table
"""


@ api_view(["GET"])
def info(request):
    info = Info.objects.first()
    if info:
        json_data = {
            'date': timezone.localtime(info.date).strftime('%Y-%m-%d %H:%M:%S')
        }
        return JsonResponse(json_data, safe=False)
    else:
        return JsonResponse({}, safe=False)
