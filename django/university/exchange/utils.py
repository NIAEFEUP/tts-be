from datetime import date
import copy
from university.models import CourseMetadata, CourseUnit, DirectExchangeParticipants, MarketplaceExchange, MarketplaceExchangeClass, Professor, DirectExchange
from enum import Enum
import json
import requests

class ExchangeStatus(Enum):
    FETCH_SCHEDULE_ERROR = 1
    STUDENTS_NOT_ENROLLED = 2
    CLASSES_OVERLAP = 3
    SUCCESS = 4

def get_student_data(username, cookies):
    url = f"https://sigarra.up.pt/feup/pt/mob_fest_geral.perfil?pv_codigo={username}"
    response = requests.get(url, cookies=cookies)
    return response

def get_student_schedule_url(username, semana_ini, semana_fim):
    return f"https://sigarra.up.pt/feup/pt/mob_hor_geral.estudante?pv_codigo={username}&pv_semana_ini={semana_ini}&pv_semana_fim={semana_fim}" 

def create_marketplace_exchange_on_db(exchanges, curr_student):
    marketplace_exchange = MarketplaceExchange.objects.create(issuer=curr_student, accepted=False)
    for exchange in exchanges:
        course_unit = course_unit_by_id(exchange["course_unit_id"])
        MarketplaceExchangeClass.objects.create(marketplace_exchange=marketplace_exchange, course_unit_acronym=course_unit.acronym, course_unit_id=exchange["course_unit_id"], course_unit_name=exchange["course_unit"], old_class=exchange["old_class"], new_class=exchange["new_class"])
   

def build_marketplace_submission_schedule(schedule, submission, cookies, auth_student):
    for exchange in submission:
        course_unit = exchange["course_unit"]
        class_auth_student_goes_to = exchange["old_class"]
        class_auth_student_goes_from = exchange["new_class"]

        print("schedule is: ", schedule[auth_student])
        
        auth_user_valid = (class_auth_student_goes_from, course_unit) in schedule[auth_student]
        if not(auth_user_valid):
            return (ExchangeStatus.STUDENTS_NOT_ENROLLED, None)

        # print("Class from sigarra: ", get_class_from_sigarra(schedule[auth_student][(class_auth_student_goes_from, course_unit)]["ocorrencia_id"], class_auth_student_goes_to, cookies)[0])

        schedule[auth_student][(class_auth_student_goes_to, course_unit)] = get_class_from_sigarra(schedule[auth_student][(class_auth_student_goes_from, course_unit)]["ocorrencia_id"], class_auth_student_goes_to, cookies)[0][0]# get class schedule
        del schedule[auth_student][(class_auth_student_goes_from, course_unit)] # remove old class of other student

    return (ExchangeStatus.SUCCESS, None) 

def get_unit_schedule_url(ocorrencia_id, semana_ini, semana_fim):
    return f"https://sigarra.up.pt/feup/pt/mob_hor_geral.ucurr?pv_ocorrencia_id={ocorrencia_id}&pv_semana_ini={semana_ini}&pv_semana_fim={semana_fim}"

def build_new_schedules(student_schedules, exchanges, auth_username):
    for curr_exchange in exchanges:
        print("Other student is: ", curr_exchange["other_student"])
        print("Auth student is: ", auth_username)
        other_student = curr_exchange["other_student"]
        course_unit = course_unit_by_id(curr_exchange["course_unit_id"])
        course_unit = course_unit.acronym
        class_auth_student_goes_to = curr_exchange["old_class"]
        class_other_student_goes_to = curr_exchange["new_class"] # The other student goes to its new class

        print("auth student goes to: ", class_auth_student_goes_to)
        print("other student goes to: ", class_other_student_goes_to)
        
        print("what in the hell? ", student_schedules[other_student])
        print("course unit: ", course_unit)
        
        # If participant is neither enrolled in that course unit or in that class
        other_student_valid = (class_auth_student_goes_to, course_unit) in student_schedules[other_student]
        auth_user_valid = (class_other_student_goes_to, course_unit) in student_schedules[auth_username]
        
        print("other studenet valid: ", other_student_valid)
        print("auth studenet valid: ", auth_user_valid)

        if not(other_student_valid) or not(auth_user_valid):
            return (ExchangeStatus.STUDENTS_NOT_ENROLLED, None)

        # Change schedule
        tmp = student_schedules[auth_username][(class_other_student_goes_to, course_unit)]
        student_schedules[auth_username][(class_auth_student_goes_to, course_unit)] = student_schedules[other_student][(class_auth_student_goes_to, course_unit)]
        student_schedules[other_student][(class_other_student_goes_to, course_unit)] = tmp

        del student_schedules[other_student][(class_auth_student_goes_to, course_unit)] # remove old class of other student
        del student_schedules[auth_username][(class_other_student_goes_to, course_unit)] # remove old class of auth student

    return (ExchangeStatus.SUCCESS, None)     

def build_student_schedule_dicts(student_schedules, exchanges, semana_ini, semana_fim, cookies):
    for curr_exchange in exchanges:
        curr_username = curr_exchange["other_student"]
        if not(curr_username in student_schedules):
            schedule_request = requests.get(get_student_schedule_url(curr_username, semana_ini, semana_fim), cookies=cookies)
            if(schedule_request.status_code != 200):
                return (ExchangeStatus.FETCH_SCHEDULE_ERROR, schedule_request.status_code)

            schedule = json.loads(schedule_request.content)["horario"]

            student_schedules[curr_username] = build_student_schedule_dict(schedule)

    return (ExchangeStatus.SUCCESS, None)

def create_direct_exchange_participants(student_schedules, exchanges, inserted_exchanges, exchange_db_model, auth_user):
    if exchange_overlap(student_schedules, auth_user):
        return (ExchangeStatus.CLASSES_OVERLAP, None)

    for curr_exchange in exchanges:
        other_student = curr_exchange["other_student"]

        course_unit = course_unit_by_id(curr_exchange["course_unit_id"])

        if exchange_overlap(student_schedules, other_student):
            return (ExchangeStatus.CLASSES_OVERLAP, None)
    
        inserted_exchanges.append(DirectExchangeParticipants(
            participant=curr_exchange["other_student"],
            old_class=curr_exchange["old_class"], 
            new_class=curr_exchange["new_class"],
            course_unit=course_unit.acronym,
            course_unit_id=curr_exchange["course_unit_id"],
            direct_exchange=exchange_db_model,
            accepted=False
        ))

        inserted_exchanges.append(DirectExchangeParticipants(
            participant=auth_user,
            old_class=curr_exchange["new_class"], # This is not a typo, the old class of the authenticted student is the new class of the other student
            new_class=curr_exchange["old_class"],
            course_unit=course_unit.acronym,
            course_unit_id=curr_exchange["course_unit_id"],
            direct_exchange=exchange_db_model,
            accepted=False
        ))

    return (ExchangeStatus.SUCCESS, None)


def build_student_schedule_dict(schedule: list):
    return {
        (class_schedule["turma_sigla"], class_schedule["ucurr_sigla"]): class_schedule for class_schedule in schedule if class_schedule["tipo"] == "TP"
    }

def check_class_schedule_overlap(day_1: int, start_1: int, end_1: int, day_2: int, start_2: int, end_2: int) -> bool:
    if day_1 != day_2:
        return False

    if (start_2 >= start_1 and start_2 <= end_1) or (start_1 >= start_2 and start_1 <= end_2):
        return True

    return False


def exchange_overlap(student_schedules, username) -> bool:
    for (key, class_schedule) in student_schedules[username].items():
        for (other_key, other_class_schedule) in student_schedules[username].items():
            print(f"({key}, {other_key})")
            if key == other_key:
                continue

            (class_schedule_day, class_schedule_start, class_schedule_end) = (class_schedule["dia"], class_schedule["hora_inicio"], class_schedule["aula_duracao"] + class_schedule["hora_inicio"])
            (overlap_param_day, overlap_param_start, overlap_param_end) = (other_class_schedule["dia"], other_class_schedule["hora_inicio"], other_class_schedule["aula_duracao"] + other_class_schedule["hora_inicio"])

            if check_class_schedule_overlap(class_schedule_day, class_schedule_start, class_schedule_end, overlap_param_day, overlap_param_start, overlap_param_end):
                return True

    return False

"""
    Returns name of course unit given its id
"""
def course_unit_name(course_unit_id):
    course_unit = CourseUnit.objects.get(sigarra_id=course_unit_id)
    return course_unit.name

"""
    Returns name of course unit given its acronym
"""
def course_unit_by_id(id):
    course_units = CourseUnit.objects.filter(sigarra_id=id)
    return course_units.first()

def curr_semester_weeks():
    currdate = date.today()
    year = str(currdate.year)
    primeiro_semestre = currdate.month >= 10 and currdate.month <= 12
    if primeiro_semestre: 
        semana_ini = "1001"
        semana_fim = "1201"
    else:
        semana_ini = "0101"
        semana_fim = "0601"
    return (year+semana_ini, year+semana_fim)

def incorrect_class_error() -> str:
    return "students-with-incorrect-classes"    

def append_tts_info_to_sigarra_schedule(schedule):
    course_unit = CourseUnit.objects.filter(sigarra_id=schedule['ocorrencia_id'])[0]
            
    schedule['url'] = course_unit.url
    # The sigarra api does not return the course with the full name, just the acronym
    schedule['ucurr_nome'] = course_unit_name(schedule['ocorrencia_id'])

def convert_sigarra_schedule(schedule_data):
    new_schedule_data = []
        
    for schedule in schedule_data:
        course_unit = CourseUnit.objects.filter(sigarra_id=schedule['ocorrencia_id'])[0]
        professors = []
        for docente in schedule['docentes']:
            professor = Professor.objects.filter(sigarra_id=docente['doc_codigo'])
            if(len(professor) < 1):
                continue
            professors.append({"name": docente['doc_nome'], "acronym": professor[0].professor_acronym})

        new_schedule = {
            'acronym': schedule['ucurr_sigla'],
            'name': course_unit.name,
            'class': schedule['turma_sigla'],
            'code': schedule['ocorrencia_id'],
            'type': schedule['tipo'],
            'duration': schedule['aula_duracao'],
            'room': schedule['sala_sigla'],
            'start': str(schedule['hora_inicio'] / 3600),
            'day': schedule['dia'] - 2,
            'professors': professors
        }

        new_schedule_data.append(new_schedule)

    return new_schedule_data

def update_schedule_accepted_exchanges(student, schedule, cookies):
    direct_exchange_ids = DirectExchangeParticipants.objects.filter(
        participant=student, direct_exchange__accepted=True
    ).values_list('direct_exchange', flat=True)
    direct_exchanges = DirectExchange.objects.filter(id__in=direct_exchange_ids).order_by('date')

    for exchange in direct_exchanges:
        participants = DirectExchangeParticipants.objects.filter(direct_exchange=exchange, participant=student).order_by('date')
        (status, trailing) = update_schedule(schedule, participants, cookies) 
        if status == ExchangeStatus.FETCH_SCHEDULE_ERROR:
            return (ExchangeStatus.FETCH_SCHEDULE_ERROR, trailing)

    return (ExchangeStatus.SUCCESS, None)

def update_schedule(student_schedule, exchanges, cookies):
    (semana_ini, semana_fim) = curr_semester_weeks();

    for exchange in exchanges:
        for i, schedule in enumerate(student_schedule):
            if schedule["ucurr_sigla"] == exchange.course_unit:
                ocorr_id = schedule["ocorrencia_id"]
                class_type = schedule["tipo"]

                unit_schedules = requests.get(get_unit_schedule_url(
                    ocorr_id,
                    semana_ini,
                    semana_fim
                ), cookies=cookies)

                if unit_schedules.status_code != 200:
                    return (ExchangeStatus.FETCH_SCHEDULE_ERROR, unit_schedules.status_code)

                for unit_schedule in unit_schedules.json()["horario"]:
                    for turma in unit_schedule["turmas"]:
                        if turma["turma_sigla"] == exchange.new_class and unit_schedule["tipo"] == class_type:
                            student_schedule[i] = unit_schedule

    return (ExchangeStatus.SUCCESS, None)

"""
Util function to get the schedule of a class from sigarra
"""
def get_class_from_sigarra(course_unit_id, class_name, cookies):
    (semana_ini, semana_fim) = curr_semester_weeks();

    print("course unit id: ", course_unit_id)

    response = requests.get(get_unit_schedule_url(
            course_unit_id, 
            semana_ini, 
            semana_fim
        ), cookies=cookies)

    print("response is: ", response)

    if(response.status_code != 200):
        return None

    schedule = json.loads(response.content)
    classes = schedule["horario"]
    class_schedule = list(filter(lambda c: c["turma_sigla"] == class_name, classes))
    theoretical_schedule = list(filter(lambda c: c["tipo"] == "T" and any(schedule["turma_sigla"] == class_name for schedule in c["turmas"]), classes))
        
    return (class_schedule, theoretical_schedule)
