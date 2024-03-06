from university.models import CourseUnit

def get_student_schedule_url(username, semana_ini, semana_fim):
    return f"https://sigarra.up.pt/feup/pt/mob_hor_geral.estudante?pv_codigo={username}&pv_semana_ini={semana_ini}&pv_semana_fim={semana_fim}" 

def build_student_schedule_dict(schedule: list):
    return {
        (class_schedule["turma_sigla"], class_schedule["ucurr_sigla"]): class_schedule for class_schedule in schedule if class_schedule["tipo"] == "TP"
    }

def check_class_schedule_overlap(start_1: int, end_1: int, start_2: int, end_2: int) -> bool:
    if (start_2 >= start_1 and start_2 <= end_1) or (start_1 >= start_2 and start_1 <= end_2):
        return True

    return False


def exchange_overlap(student_schedules, student, class_to_insert) -> bool:
    for class_schedule in student_schedules[student]:
        if class_schedule["ucurr_sigla"] != class_to_insert["uccur_sigla"]:
            (class_schedule_start, class_schedule_end) = (class_schedule["hora_inicio"], class_schedule["aula_duracao"] + class_schedule["hora_inicio"])
            (overlap_param_start, overlap_param_end) = (class_to_insert["hora_inicio"], class_to_insert["aula_duracao"] + class_to_insert["hora_inicio"])

            if check_class_schedule_overlap(class_schedule_start, class_schedule_end, overlap_param_start, overlap_param_end):
                return True

    return False

"""
    Returns name of course unit
"""
def course_unit_name(course_unit_id):
    course_unit = CourseUnit.objects.get(sigarra_id=course_unit_id)
    return course_unit.name
