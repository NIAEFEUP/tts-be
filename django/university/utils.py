from university.models import CourseUnit

def get_student_schedule_url(username, semana_ini, semana_fim):
    return f"https://sigarra.up.pt/feup/pt/mob_hor_geral.estudante?pv_codigo={username}&pv_semana_ini={semana_ini}&pv_semana_fim={semana_fim}" 

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


def exchange_overlap(student_schedules, student) -> bool:
    for (key, class_schedule) in student_schedules[student].items():
        for (other_key, other_class_schedule) in student_schedules[student].items():
            if key == other_key:
                continue

            (class_schedule_day, class_schedule_start, class_schedule_end) = (class_schedule["dia"], class_schedule["hora_inicio"], class_schedule["aula_duracao"] + class_schedule["hora_inicio"])
            (overlap_param_day, overlap_param_start, overlap_param_end) = (other_class_schedule["dia"], other_class_schedule["hora_inicio"], other_class_schedule["aula_duracao"] + other_class_schedule["hora_inicio"])

            if check_class_schedule_overlap(class_schedule_day, class_schedule_start, class_schedule_end, overlap_param_day, overlap_param_start, overlap_param_end):
                print("Key: ", key)
                return True

    return False

"""
    Returns name of course unit
"""
def course_unit_name(course_unit_id):
    course_unit = CourseUnit.objects.get(sigarra_id=course_unit_id)
    return course_unit.name
