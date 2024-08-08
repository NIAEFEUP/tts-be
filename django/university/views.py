from django.http.response import HttpResponse
from university.models import Faculty
from university.models import Course
from university.models import CourseUnit
from university.models import Class
from university.models import Slot
from university.models import Professor
from university.models import SlotProfessor
from university.models import CourseMetadata
from university.models import Info
from university.models import SlotClass
from university.response.errors import course_unit_not_found_error
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status
from django.db.models import Max
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
    for course_units in course_units_metadata:
        course_units.__dict__.update(course_units.course_unit.__dict__)
        del course_units.__dict__["_state"]
        json_data.append(course_units.__dict__)

    return JsonResponse(json_data, safe=False)


"""
    Returns the classes of a course unit.
"""


@api_view(['GET'])
def classes(request, course_unit_id):
    classes = list(Class.objects.filter(
        course_unit=course_unit_id).order_by('name').values())
    for class_obj in classes:
        slot_ids = SlotClass.objects.filter(
            class_field=class_obj['id']).values_list('slot_id', flat=True)
        slots = list(Slot.objects.filter(id__in=slot_ids).values())

        for slot_obj in slots:
            slot_professors = list(SlotProfessor.objects.filter(
                slot_id=slot_obj['id']).values())

            professors = []

            for slot_professor in slot_professors:
                professor = Professor.objects.get(
                    id=slot_professor['professor_id'])
                professors.append({
                    'id': professor.id,
                    'acronym': professor.professor_acronym,
                    'name': professor.professor_name
                })

            slot_obj['professors'] = professors

        class_obj['slots'] = slots

    return JsonResponse(classes, safe=False)


"""
    Returns all the professors of a class of the class id
"""


@api_view(["GET"])
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


@api_view(["GET"])
def info(request):
    info = Info.objects.first()
    if info:
        json_data = {
            'date': timezone.localtime(info.date).strftime('%Y-%m-%d %H:%M:%S')
        }
        return JsonResponse(json_data, safe=False)
    else:
        return JsonResponse({}, safe=False)
