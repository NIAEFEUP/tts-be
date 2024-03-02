from django.http.response import HttpResponse
from django.contrib.auth import authenticate, login
from tts_be.settings import JWT_KEY
from university.utils import get_student_schedule_url, build_student_schedule_dict, exchange_overlap
from university.models import Faculty
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
from django.http import JsonResponse
from django.core import serializers
from rest_framework.decorators import api_view
from django.db.models import Max
from django.db import transaction
import requests
import os 
import jwt
import json
from django.utils import timezone
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
def submit_direct_exchange(request):
    exchanges = request.POST.getlist('exchangeChoices[]')
    exchanges = list(map(lambda exchange : json.loads(exchange), exchanges))

    semana_ini = "20240101"
    semana_fim = "20240601"

    student_schedules = {}

    curr_student_schedule = requests.get(get_student_schedule_url(
        request.session["username"],
        semana_ini,
        semana_fim
    ), cookies=request.COOKIES)

    if(curr_student_schedule.status_code != 200):
        return HttpResponse(status=curr_student_schedule.status_code)

    # TODO We need to change the fetched schedule with the exchange information we have in our database

    student_schedules[request.session["username"]] = build_student_schedule_dict(json.loads(curr_student_schedule.content)["horario"])

    for curr_exchange in exchanges:
        print(curr_exchange)
        curr_username = curr_exchange["other_student"]
        if not(curr_username in student_schedules):
            schedule_request = requests.get(get_student_schedule_url(curr_username, semana_ini, semana_fim), cookies=request.COOKIES)
            if(schedule_request.status_code != 200):
                return HttpResponse(status=curr_student_schedule.status_code)

            schedule = json.loads(schedule_request.content)["horario"]
            student_schedules[curr_username] = build_student_schedule_dict(schedule)
    
    exchange = DirectExchange(accepted=False)

    inserted_exchanges = []
    for curr_exchange in exchanges:
        other_student = curr_exchange["other_student"]
        course_unit = curr_exchange["course_unit"]
        class_other_student_goes_to = curr_exchange["old_class"]
        class_auth_student_goes_to = curr_exchange["new_class"]
        
        # If participant is neither enrolled in that course unit or in that class
        other_student_valid = (class_auth_student_goes_to, course_unit) in student_schedules[other_student]
        auth_user_valid = (class_other_student_goes_to, course_unit) in student_schedules[request.session["username"]]
        if not(other_student_valid) or not(auth_user_valid):
            return JsonResponse({"error": "students-with-incorrect-classes"}, status=400)

        # Check of overlap
        other_student_overlap_param = student_schedules[request.session["username"]][(class_other_student_goes_to, course_unit)]
        auth_student_overlap_param = student_schedules[other_student][(class_auth_student_goes_to, course_unit)]

        if exchange_overlap(student_schedules, auth_student_overlap_param) or exchange_overlap(student_schedules, other_student_overlap_param):
            return JsonResponse({"error": "classes-overlap"}, status=400)
        
        # If no overlap, change it
        student_schedules[request.session["username"]][(class_auth_student_goes_to, course_unit)] = student_schedules[other_student][(class_auth_student_goes_to, course_unit)]
        student_schedules[other_student][(class_other_student_goes_to, course_unit)] = tmp

        del student_schedules[other_student][(class_auth_student_goes_to, course_unit)] # remove old class of other student
        del student_schedules[request.session["username"]][(class_other_student_goes_to, course_unit)] # remove old class of auth student
        # If there are any, return http error

        inserted_exchanges.append(DirectExchangeParticipants(
            participant=curr_exchange["other_student"],
            old_class=curr_exchange["new_class"], # This is not a typo, the old class of the authenticted student is the new class of the other student
            new_class=curr_exchange["other_class"],
            course_unit=curr_exchange["course_unit"],
            direct_exchange=exchange,
            accepted=False
        ))
    
    print("ie: ", inserted_exchanges)
    for inserted_exchange in inserted_exchanges:
        inserted_exchange.save()

    exchange.save()
    
    # 1. Create token
    token = jwt.encode({"username": request.session["username"], "exchange_id": exchange.id}, JWT_KEY, algorithm="HS256")
    print(token)
    
    # 2. Send confirmation email

    return HttpResponse()

@api_view(["POST"])
def verify_direct_exchange(request, token):
    exchange_info = jwt.decode(token, JWT_KEY, algorithms=["HS256"])
    
    participant = DirectExchangeParticipants.objects.filter(participant=request.session["username"])
    participant.update(accepted=True)

    all_participants = DirectExchangeParticipants.objects.filter(direct_exchange_id=exchange_info["exchange_id"])
    
    accepted_participants = 0
    for participant in all_participants:
        accepted_participants += participant.accepted

    if accepted_participants == len(all_participants):
        DirectExchange.objects.filter(id=int(exchange_info["exchange_id"])).update(accepted=True)

    return HttpResponse() 
