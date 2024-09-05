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
from university.exchange.utils import ExchangeStatus, build_new_schedules, create_direct_exchange_participants, convert_sigarra_schedule
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
    print("please, god: ", dict(request.session))
    sigarra_token_endpoint = 'https://sigarra.up.pt/auth/oidc/token'
    token = request.session.get("oidc_id_token")
    response = requests.get(
        sigarra_token_endpoint,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
    )

    print("status code: ", response.status_code)

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


@api_view(["POST"])
def login(request):
    # username = request.POST.get('pv_login')
    # password = request.POST.get('pv_password')

    login_data = {
        'pv_login': os.getenv("MOCK_USERNAME"),
        'pv_password': os.getenv("MOCK_PASSWORD")
    }

    # if not username or not password:
    #     return JsonResponse({"error": "Missing credentials"}, safe=False)

    if "username" in request.session:
        return HttpResponse()
    
    print("login data: ", login_data)

    try:
        response = requests.post("https://sigarra.up.pt/feup/pt/mob_val_geral.autentica/", data=login_data)

        new_response = HttpResponse(response.content)
        new_response.status_code = response.status_code

        if response.status_code == 200:
            for cookie in response.cookies:
                new_response.set_cookie(cookie.name, cookie.value, httponly=True, secure=True)
            
            # admin = ExchangeAdmin.objects.filter(username=username).exists()
            # request.session["admin"] = admin

            request.session["username"] = login_data["pv_login"]
            return new_response
        else:
            return new_response
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": e}, safe=False)


@api_view(["POST"])
def logout(request):

    try:
        del request.session["username"]
    except KeyError:
        pass

    try:
        del request.session["admin"]
    except KeyError:
        pass

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

        if (response.status_code != 200):
            return HttpResponse(status=response.status_code)

        schedule_data = response.json()['horario']
        old_schedule = hashlib.sha256(json.dumps(schedule_data, sort_keys=True).encode()).hexdigest()

        update_schedule_accepted_exchanges(student, schedule_data, request.COOKIES)

        new_schedule = hashlib.sha256(json.dumps(schedule_data, sort_keys=True).encode()).hexdigest()
        sigarra_synchronized = old_schedule == new_schedule

        new_response = JsonResponse({"schedule": convert_sigarra_schedule(schedule_data), "noChanges": sigarra_synchronized}, safe=False)
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

        if (response.status_code != 200):
            return HttpResponse(status=response.status_code)

        new_response = JsonResponse(response.json(), safe=False)

        new_response.status_code = response.status_code

        return new_response

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": e}, safe=False)
    
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
def submit_direct_exchange(request):

    (semana_ini, semana_fim) = curr_semester_weeks();

    student_schedules = {}

    marketplaceStartedExchangeId = request.POST.get("marketplace_exchange_id")

    curr_student_schedule = requests.get(get_student_schedule_url(
        request.session["username"],
        semana_ini,
        semana_fim
    ), cookies=request.COOKIES)

    if (curr_student_schedule.status_code != 200):
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

    marketplace_exchange = None
    if(marketplaceStartedExchangeId != None):
        marketplace_exchange = MarketplaceExchange.objects.filter(id=int(marketplaceStartedExchangeId)).first()

    exchange_model = DirectExchange(accepted=False, issuer=request.session["username"], marketplace_exchange=marketplace_exchange)

    (status, trailing) = build_new_schedules(
        student_schedules, exchanges, request.session["username"])
    if status == ExchangeStatus.STUDENTS_NOT_ENROLLED:
        return JsonResponse({"error": incorrect_class_error()}, status=400, safe=False)
    
    inserted_exchanges = []
    (status, trailing) = create_direct_exchange_participants(student_schedules, exchanges, inserted_exchanges, exchange_model, request.session["username"])
    if status == ExchangeStatus.CLASSES_OVERLAP:    
        return JsonResponse({"error": "classes-overlap"}, status=400, safe=False)

    exchange_model.save()
    
    tokens_to_generate = {}
    for inserted_exchange in inserted_exchanges:
        participant = inserted_exchange.participant;
        if not(participant in tokens_to_generate):
            token = jwt.encode({"username": participant, "exchange_id": exchange_model.id, "exp": (datetime.datetime.now() + datetime.timedelta(seconds=VERIFY_EXCHANGE_TOKEN_EXPIRATION_SECONDS)).timestamp()}, JWT_KEY, algorithm="HS256")
            tokens_to_generate[participant] = token
            html_message = render_to_string('confirm_exchange.html', {'confirm_link': f"{DOMAIN}tts/verify_direct_exchange/{token}"})
            send_mail(
                'Confirmação de troca',
                strip_tags(html_message),
                'tts@exchange.com',
                [f'up{participant}@up.pt'],
                fail_silently=False)
        inserted_exchange.save()
    
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
def is_admin(request):
    return JsonResponse({"admin" : request.session.get("admin", False)}, safe=False)

@api_view(["GET"])
def export_exchanges(request):

    if not ExchangeAdmin.objects.filter(username=request.session["username"]).exists():
        response = HttpResponse()
        response.status_code = 403
        return response

    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="exchange_data.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(["student", "course_unit", "old_class", "new_class"])

    direct_exchange_ids = DirectExchangeParticipants.objects.filter(
        direct_exchange__accepted=True
    ).values_list('direct_exchange', flat=True)
    direct_exchanges = DirectExchange.objects.filter(id__in=direct_exchange_ids).order_by('date')

    for exchange in direct_exchanges:
        participants = DirectExchangeParticipants.objects.filter(direct_exchange=exchange).order_by('date')
        for participant in participants:
            writer.writerow([
                participant.participant,
                participant.course_unit_id,
                participant.old_class,
                participant.new_class
            ])

    return response

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

@api_view(["GET"])
def direct_exchange_history(request):
    username = request.session["username"]
    my_participations = DirectExchangeParticipants.objects.filter(
         participant = username,
    )

    direct_exchanges_id = list(map(lambda entry: entry.direct_exchange.id, my_participations))

    direct_exchanges = DirectExchange.objects.filter(
        Q(id__in = direct_exchanges_id)
    )

    exchanges_map = dict();
    for direct_exchange in direct_exchanges:
        exchanges_map[direct_exchange.id] = {
            'id' : direct_exchange.id,
            'class_exchanges' : [],
            'issuer' : direct_exchange.issuer,
            'status' : 'accepted' if direct_exchange.accepted else 'pending'
        }
        participants = DirectExchangeParticipants.objects.filter(direct_exchange = direct_exchange.id)
        for participant in participants:
            if(participant.participant == direct_exchange.issuer):
                continue
            exchanges_map[direct_exchange.id]['class_exchanges'].append({
                'course_unit' : participant.course_unit,
                'course_unit_id' : participant.course_unit_id,
                'old_class' : participant.old_class,
                'new_class' : participant.new_class,
                'accepted' : participant.accepted,
                'other_student' : participant.participant
            })

    # exchange_status_filter: str = request.GET.get('filter')
    # accepted_filter_values = ["pending", "accepted", "rejected"]
    # if exchange_status_filter != None and exchange_status_filter in accepted_filter_values:
    #     exchanges.filter(accepted=exchange_status_filter)  
    # 
    # paginator = Paginator(exchanges, 15)

    return JsonResponse(list(exchanges_map.values()), safe=False)

class DirectExchangeView(APIView):
    def delete(self, request):
        exchange_id = request.POST.get('exchange_id')
        exchange = DirectExchange.objects.get(pk=exchange_id)
        exchange_participants = DirectExchangeParticipants.objects.filter(direct_exchange=exchange_id)
        
        for participant in exchange_participants: 
            # avisar os participantes
            pass

        # Apagar a troca direta
        exchange.delete()
        return JsonResponse({"status": "refactoring"}, safe=False)
        
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
