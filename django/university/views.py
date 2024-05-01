import random
import string
from datetime import datetime, timedelta
from django.utils import timezone
from django.http.response import HttpResponse
from tts_be.settings import JWT_KEY, VERIFY_EXCHANGE_TOKEN_EXPIRATION_SECONDS
from university.exchange.utils import course_unit_name, curr_semester_weeks, get_student_schedule_url, build_student_schedule_dict, exchange_overlap, build_student_schedule_dicts, get_unit_schedule_url, update_schedule_accepted_exchanges
from university.exchange.utils import ExchangeStatus, build_new_schedules, check_for_overlaps, convert_sigarra_schedule, build_marketplace_submission_schedule, incorrect_class_error, get_class_from_sigarra, create_marketplace_exchange_on_db
from university.models import Faculty, MarketplaceExchangeClass
from university.models import Course
from university.models import CourseUnit
from university.models import Schedule
from university.models import Professor
from university.models import ScheduleProfessor
from university.models import CourseMetadata
from university.models import DirectExchange
from university.models import DirectExchangeParticipants
from university.models import Statistics
from university.models import Info
from university.models import MarketplaceExchange
from django.http import JsonResponse
from django.core import serializers
from rest_framework.decorators import api_view
from django.db.models import Max
from django.db import transaction
import requests
import os 
import jwt
import json
import datetime
import time
from django.utils import timezone
from django.core.cache import cache
# Create your views here. 


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
    course_unit = CourseUnit.objects.get(pk=course_unit_id)
    faculty = course_unit.url.split('/')[3]
    schedules = list(Schedule.objects.filter(course_unit=course_unit_id).order_by('class_name').values())
    for schedule in schedules:
        schedule_professors = list(ScheduleProfessor.objects.filter(schedule=schedule['id']).values())
        professors_link = f'https://sigarra.up.pt/{faculty}/pt/{"hor_geral.composto_doc?p_c_doc=" if schedule["is_composed"] else "func_geral.FormView?p_codigo="}{schedule["professor_sigarra_id"]}'
        schedule['professors_link'] = professors_link
        del schedule['professor_sigarra_id']
        professors_information = []
        for schedule_professor in schedule_professors:
            professors_information.append({
                'acronym': Professor.objects.get(pk=schedule_professor['professor_sigarra_id']).professor_acronym,
                'name': Professor.objects.get(pk=schedule_professor['professor_sigarra_id']).professor_name
            })
        schedule['professor_information'] = professors_information
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

@api_view(["POST"])
def login(request):
    username = request.POST.get('pv_login')
    password = request.POST.get('pv_password')

    login_data = {
        'pv_login': username,
        'pv_password': password
    }

    if not username or not password:
        return JsonResponse({"error": "Missing credentials"}, safe=False)

    try:
        response = requests.post("https://sigarra.up.pt/feup/pt/mob_val_geral.autentica/", data=login_data)
        
        new_response = HttpResponse(response.content)
        new_response.status_code = response.status_code

        if response.status_code == 200:
            for cookie in response.cookies:
                new_response.set_cookie(cookie.name, cookie.value, httponly=True, secure=True)
            
            request.session["username"] = login_data["pv_login"]
            return new_response
        else:
            return new_response 
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": e}, safe=False)

@api_view(["POST"])
def logout(request):
    del request.session["username"]
    return HttpResponse(status=200)

"""
    Returns schedule of student
"""
@api_view(["GET"])
def student_schedule(request, student):

    (semana_ini, semana_fim) = curr_semester_weeks();

    try:
        response = requests.get(get_student_schedule_url(
            request.session["username"],
            semana_ini,
            semana_fim
        ), cookies=request.COOKIES)

        if(response.status_code != 200):
            return HttpResponse(status=response.status_code)

        schedule_data = response.json()['horario']

        update_schedule_accepted_exchanges(student, schedule_data, request.COOKIES)

        new_response = JsonResponse(convert_sigarra_schedule(schedule_data), safe=False)
        new_response.status_code = response.status_code
        return new_response 
        
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": e}, safe=False)


"""
    Returns all classes of a course unit from sigarra
""" 
@api_view(["GET"])
def schedule_sigarra(request, course_unit_id):
    (semana_ini, semana_fim) = curr_semester_weeks();

    try:
        response = requests.get(get_unit_schedule_url(
            course_unit_id, 
            semana_ini, 
            semana_fim
        ), cookies=request.COOKIES)

        if(response.status_code != 200):
            return HttpResponse(status=response.status_code)

        new_response = JsonResponse(convert_sigarra_schedule(response.json()['horario']), safe=False)
        new_response.status_code = response.status_code

        return new_response

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": e}, safe=False)
    
"""
    Returns all students enrolled in a course unit
""" 
@api_view(["GET"])
def students_per_course_unit(request, course_unit_id):

    try:
        url = f"https://sigarra.up.pt/feup/pt/mob_ucurr_geral.uc_inscritos?pv_ocorrencia_id={course_unit_id}"
        response = requests.get(url, cookies=request.COOKIES)

        if(response.status_code != 200):
            return HttpResponse(status=response.status_code)

        new_response = JsonResponse(response.json(), safe=False)

        new_response.status_code = response.status_code

        return new_response

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": e}, safe=False)

"""
Gets schedule from a specific class from a course unit from sigarra
"""
@api_view(["GET"])
def class_sigarra_schedule(request, course_unit_id, class_name):

    try:
        # return HttpResponse(status=response.status_code)
        class_schedule_response = get_class_from_sigarra(course_unit_id, class_name, request.COOKIES)
        
        (class_schedule, theoretical_schedule) = class_schedule_response
        new_response = JsonResponse(convert_sigarra_schedule(class_schedule + theoretical_schedule), safe=False)

        return new_response

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": e}, safe=False)

@api_view(["POST"])
def submit_marketplace_exchange_request(request):
    exchanges = request.POST.getlist('exchangeChoices[]')
    exchanges = list(map(lambda exchange : json.loads(exchange), exchanges))

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

    (status, curr_student_schedule) = build_marketplace_submission_schedule(student_schedules, exchanges, request.COOKIES, curr_student)
    if status == ExchangeStatus.STUDENTS_NOT_ENROLLED:
         return JsonResponse({"error": incorrect_class_error()}, status=400, safe=False)
    
    if exchange_overlap(student_schedules, curr_student):
        return JsonResponse({"error": "classes-overlap"}, status=400, safe=False)
    
    create_marketplace_exchange_on_db(exchanges, curr_student)
    
    return JsonResponse({"success": True}, safe=False)

@api_view(["POST"])
def submit_direct_exchange(request):

    (semana_ini, semana_fim) = curr_semester_weeks();

    student_schedules = {}

    curr_student_schedule = requests.get(get_student_schedule_url(
        request.session["username"],
        semana_ini,
        semana_fim
    ), cookies=request.COOKIES)

    if(curr_student_schedule.status_code != 200):
        return HttpResponse(status=curr_student_schedule.status_code)

    username = request.session["username"]
    schedule_data = json.loads(curr_student_schedule.content)["horario"]

    student_schedules[username] = build_student_schedule_dict(schedule_data)

    exchange_choices = request.POST.getlist('exchangeChoices[]')
    exchanges = list(map(lambda exchange : json.loads(exchange), exchange_choices))

    # Add the other students schedule to the dictionary
    (status, trailing) = build_student_schedule_dicts(student_schedules, exchanges, semana_ini, semana_fim, request.COOKIES)
    if status == ExchangeStatus.FETCH_SCHEDULE_ERROR:
        return HttpResponse(status=trailing)

    for student in student_schedules.keys():
        student_schedule = list(student_schedules[student].values())
        update_schedule_accepted_exchanges(student, student_schedule, request.COOKIES)
        student_schedules[student] = build_student_schedule_dict(student_schedule)

    exchange_model = DirectExchange(accepted=False)

    (status, trailing) = build_new_schedules(student_schedules, exchanges, request.session["username"])
    if status == ExchangeStatus.STUDENTS_NOT_ENROLLED:
        return JsonResponse({"error": incorrect_class_error()}, status=400, safe=False)
    
    inserted_exchanges = []
    (status, trailing) = check_for_overlaps(student_schedules, exchanges, inserted_exchanges, exchange_model, request.session["username"])
    if status == ExchangeStatus.CLASSES_OVERLAP:    
        return JsonResponse({"error": "classes-overlap"}, status=400, safe=False)
    
    exchange_model.save()
    
    tokens_to_generate = {}
    for inserted_exchange in inserted_exchanges:
        participant = inserted_exchange.participant;
        if not(participant in tokens_to_generate):
            token = jwt.encode({"username": participant, "exchange_id": exchange_model.id, "exp": (datetime.datetime.now() + datetime.timedelta(seconds=VERIFY_EXCHANGE_TOKEN_EXPIRATION_SECONDS)).timestamp()}, JWT_KEY, algorithm="HS256")
            tokens_to_generate[participant] = token
        inserted_exchange.save()
    
    # 2. Send confirmation email

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
            DirectExchange.objects.filter(id=int(exchange_info["exchange_id"])).update(accepted=True)

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
        return HttpResponse(status=500)


@api_view(["GET"])
def marketplace_exchange(request):
    exchanges = MarketplaceExchange.objects.all()

    exchanges_json = json.loads(serializers.serialize('json', exchanges))

    exchanges_map = dict()
    for exchange in exchanges_json:
        exchange_id = exchange['pk']  
        exchange_fields = exchange['fields']  

        if exchange_id and exchanges_map.get(exchange_id):
            exchanges_map[exchange_id]['class_exchanges'].append(exchange_fields)
        elif exchange_id:
            exchanges_map[exchange_id] = {
                'id' : exchange_id,
                'issuer' : exchange_fields.get('issuer'),
                'accepted' : exchange_fields.get('accepted'),
                'date' : exchange_fields.get('date'),
                'class_exchanges' : []
            }

    for exchange_id, exchange in exchanges_map.items():
        class_exchanges = MarketplaceExchangeClass.objects.filter(marketplace_exchange=exchange_id)
        class_exchanges_json = json.loads(serializers.serialize('json', class_exchanges))
        class_exchanges_json = list(map(lambda entry: entry['fields'], class_exchanges_json))  
        for class_exchange in class_exchanges_json:
            exchange['class_exchanges'].append({
                'course_unit' : class_exchange.get('course_unit_name'),
                'old_class' : class_exchange.get('old_class'),
                'new_class' : class_exchange.get('new_class')
            })

    print("Resultado do pedido GET: ", list(exchanges_map.values()))

    return JsonResponse(list(exchanges_map.values()), safe=False)

