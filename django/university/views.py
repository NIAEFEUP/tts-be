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
    
@api_view(["POST"])
def submit_marketplace_exchange_request(request):
    exchanges = request.POST.getlist('exchangeChoices[]')
    exchanges = list(map(lambda exchange: json.loads(exchange), exchanges))

    print("Marketplace exchange: ", exchanges)

    (semana_ini, semana_fim) = curr_semester_weeks()
    curr_student = request.session["username"]

    curr_student_schedule = requests.get(get_student_schedule_url(
        request.session["username"],
        semana_ini,
        semana_fim
    ), cookies=request.COOKIES)

    if(curr_student_schedule.status_code != 200):
        return HttpResponse(status=curr_student_schedule.status_code)
    
    student_schedules = {}
    student_schedules[curr_student] = build_student_schedule_dict(json.loads(curr_student_schedule.content)["horario"])
    
    student_schedule = list(student_schedules[curr_student].values())
    update_schedule_accepted_exchanges(curr_student, student_schedule, request.COOKIES)
    student_schedules[curr_student] = build_student_schedule_dict(student_schedule)

    (status, new_marketplace_schedule) = build_marketplace_submission_schedule(student_schedules, exchanges, request.COOKIES, curr_student)
    print("Student schedules: ", student_schedules[curr_student])
    if status == ExchangeStatus.STUDENTS_NOT_ENROLLED:
         return JsonResponse({"error": incorrect_class_error()}, status=400, safe=False)

    if exchange_overlap(student_schedules, curr_student):
        return JsonResponse({"error": "classes-overlap"}, status=400, safe=False)
    
    create_marketplace_exchange_on_db(exchanges, curr_student)
    
    return JsonResponse({"success": True}, safe=False)

@api_view(["POST"])
def verify_direct_exchange(request, token):
    try:
        exchange_info = jwt.decode(token, JWT_KEY, algorithms=["HS256"])
    
        token_seconds_elapsed = time.time() - exchange_info["exp"]
        if token_seconds_elapsed > VERIFY_EXCHANGE_TOKEN_EXPIRATION_SECONDS:
            return JsonResponse({"verified": False}, safe=False, status=403)

        participant = DirectExchangeParticipants.objects.filter(participant=request.session["username"])
        participant.update(accepted=True)

        all_participants = DirectExchangeParticipants.objects.filter(direct_exchange_id=exchange_info["exchange_id"])
    
        accepted_participants = 0
        for participant in all_participants:
            accepted_participants += participant.accepted

        if accepted_participants == len(all_participants):
            direct_exchange = DirectExchange.objects.filter(id=int(exchange_info["exchange_id"]))
            direct_exchange.update(accepted=True)

            marketplace_exchange = direct_exchange.first().marketplace_exchange

            if(marketplace_exchange != None):
                direct_exchange_object = direct_exchange.first()
                direct_exchange_object.marketplace_exchange = None
                direct_exchange_object.save()
                marketplace_exchange.delete()

        if cache.get(token) != None:
            return JsonResponse({"verified": False}, safe=False, status=403)
    
        # Blacklist token since this token is usable only once
        cache.set(
            key=token,
            value=token,
            timeout=VERIFY_EXCHANGE_TOKEN_EXPIRATION_SECONDS - token_seconds_elapsed
        )

        return JsonResponse({"verified": True}, safe=False)

    except Exception as e:
        print("Error: ", e)
        return HttpResponse(status=500)

@api_view(["GET"])
def marketplace_exchange(request):
    exchanges = MarketplaceExchange.objects.all()

    exchanges_json = json.loads(serializers.serialize('json', exchanges))

    exchanges_map = dict()
    for exchange in exchanges_json:
        exchange_id = exchange['pk']  
        exchange_fields = exchange['fields']  

        student = get_student_data(exchange_fields["issuer"], request.COOKIES)

        if(student.json()["codigo"] == request.session["username"]):
            continue

        if exchange_id and exchanges_map.get(exchange_id):
            exchanges_map[exchange_id]['class_exchanges'].append(exchange_fields)
        elif exchange_id:
            exchanges_map[exchange_id] = {
                'id' : exchange_id,
                'issuer' :  student.json(),
                'accepted' : exchange_fields.get('accepted'),
                'date' : exchange_fields.get('date'),
                'class_exchanges' : []
            }

    for exchange_id, exchange in exchanges_map.items():
        class_exchanges = MarketplaceExchangeClass.objects.filter(marketplace_exchange=exchange_id)
        
        for class_exchange in class_exchanges:
            course_unit = course_unit_by_id(class_exchange.course_unit_id)
            print("current class exchange is: ", class_exchange)
            exchange['class_exchanges'].append({
                'course_unit' : course_unit.name,
                'course_unit_id': class_exchange.course_unit_id,
                'course_unit_acronym': course_unit.acronym,
                'old_class' : class_exchange.old_class,
                'new_class' : class_exchange.new_class,
            })

    return JsonResponse(list(exchanges_map.values()), safe=False)

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
