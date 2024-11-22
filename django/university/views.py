import csv
from django.contrib.sessions.models import Session
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import send_mail
from datetime import datetime, timedelta
from types import new_class
from django.utils import timezone
from django.http.response import HttpResponse
from rest_framework.views import APIView
from django.core.paginator import Paginator
from tts_be.settings import JWT_KEY, VERIFY_EXCHANGE_TOKEN_EXPIRATION_SECONDS, DOMAIN
from university.exchange.utils import course_unit_name, course_unit_by_id, curr_semester_weeks, get_student_data, get_student_schedule_url, build_student_schedule_dict, build_student_schedule_dicts, get_unit_schedule_url, update_schedule_accepted_exchanges
from university.exchange.utils import ExchangeStatus, build_new_schedules, convert_sigarra_schedule, build_marketplace_submission_schedule, incorrect_class_error, get_class_from_sigarra, create_marketplace_exchange_on_db
from university.exchange.utils import course_unit_name, curr_semester_weeks, get_student_schedule_url, build_student_schedule_dict, exchange_overlap, build_student_schedule_dicts, get_unit_schedule_url, update_schedule_accepted_exchanges
from university.exchange.utils import ExchangeStatus, build_new_schedules, convert_sigarra_schedule, build_marketplace_submission_schedule, incorrect_class_error, get_class_from_sigarra, create_marketplace_exchange_on_db
from university.models import Faculty, MarketplaceExchangeClass
from university.exchange.utils import course_unit_name, curr_semester_weeks, get_student_schedule_url, build_student_schedule_dict, build_student_schedule_dicts, get_unit_schedule_url, update_schedule, update_schedule_accepted_exchanges
from university.exchange.utils import ExchangeStatus, build_new_schedules, convert_sigarra_schedule
from university.models import Faculty
from university.models import Course
from university.models import CourseUnit
from university.models import Professor
from university.models import SlotProfessor
from university.models import CourseMetadata
from university.models import DirectExchange
from university.models import DirectExchangeParticipants
from university.models import Info
from university.models import MarketplaceExchange, ExchangeAdmin
from university.models import Info
from university.controllers.ClassController import ClassController
from university.response.errors import course_unit_not_found_error
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.db.models import Max, Q
from django.db import transaction
from django.shortcuts import redirect
import requests
import jwt
import json
import datetime
import time
from django.core.cache import cache
import hashlib
# Create your views here. 
from rest_framework import status

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

    return JsonResponse(json_data, safe=False)



"""
    Returns the classes of a course unit.
"""
@ api_view(['GET'])
def classes(request, course_unit_id):
    return JsonResponse(ClassController.get_classes(course_unit_id), safe=False)

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

"""
    Returns student data
"""    
@api_view(["GET"])
def student_data(request, codigo):
    try:
        response = get_student_data(codigo, request.COOKIES)

        if(response.status_code != 200):
            return HttpResponse(status=response.status_code)

        new_response = JsonResponse(response.json(), safe=False)

        new_response.status_code = response.status_code

        return new_response

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": e}, safe=False)

"""
    Verifies if course units have the correct hash
"""
@api_view(['GET'])
def get_course_unit_hashes(request):

    ids_param = request.query_params.get('ids', '')

    try:
        course_unit_ids = [int(id) for id in ids_param.split(',') if id]
    except ValueError:
        return JsonResponse({'error': 'Invalid ID format'}, status=400)

    results = {}

    for course_unit_id in course_unit_ids:
        try:
            course_unit = CourseUnit.objects.get(id=course_unit_id)
            results[course_unit_id] = course_unit.hash
        except CourseUnit.DoesNotExist:
            results[course_unit_id] = None

    return JsonResponse(results, safe=False)
