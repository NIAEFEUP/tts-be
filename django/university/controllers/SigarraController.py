import requests
import json

from django.utils import timezone
from datetime import date
from tts_be.settings import CONFIG

from university.models import CourseUnit, Professor

class SigarraResponse:
    def __init__(self, data, status_code):
        self.data = data
        self.status_code = status_code
    
class SigarraController:
    """
        This class will contain methods to manipulate student data that is inside sigarra.
    """

    def __init__(self):
        self.username = CONFIG["SIGARRA_USERNAME"]
        self.password = CONFIG["SIGARRA_PASSWORD"]
        self.cookies = None

        self.login()
    
    def get_student_photo_url(self, nmec) -> str:
        return f"https://sigarra.up.pt/feup/pt/fotografias_service.foto?pct_cod={nmec}"

    def semester_weeks(self):
        currdate = date.today()
        year = str(currdate.year)
        first_semester = currdate.month >= 10 or currdate.month <= 2
        if first_semester: 
            semana_ini = "20241001"
            semana_fim = "20250131"
        else:
            semana_ini = year + "0210"
            semana_fim = year + "0601"
        
        return (semana_ini, semana_fim)

    def student_profile_url(self, nmec):
        return f"https://sigarra.up.pt/feup/pt/mob_fest_geral.perfil?pv_codigo={nmec}"
    
    def student_schedule_url(self, nmec, semana_ini, semana_fim) -> str:
        return f"https://sigarra.up.pt/feup/pt/mob_hor_geral.estudante?pv_codigo={nmec}&pv_semana_ini={semana_ini}&pv_semana_fim={semana_fim}" 

    def course_unit_schedule_url(self, ocorrencia_id, semana_ini, semana_fim):
        return f"https://sigarra.up.pt/feup/pt/mob_hor_geral.ucurr?pv_ocorrencia_id={ocorrencia_id}&pv_semana_ini={semana_ini}&pv_semana_fim={semana_fim}"
    
    def retrieve_student_photo(self, nmec):
        response = requests.get(self.get_student_photo_url(nmec), cookies=self.cookies)

        if response.status_code != 200:
            return SigarraResponse(None, response.status_code)

        return SigarraResponse(response.content, 200)

    def get_student_profile(self, nmec):
        response = requests.get(self.student_profile_url(nmec), cookies=self.cookies)

        if response.status_code != 200:
            return SigarraResponse(None, response.status_code)

        return SigarraResponse(response.content, 200)

    def get_student_festid(self, nmec):
        profile: SigarraResponse = self.get_student_profile(nmec)

        if profile.status_code != 200:
            return None

        try:
            courses = json.loads(profile.data)["cursos"]
        except json.decoder.JSONDecodeError:
            return None

        return list(map(lambda course: {
            "fest_id": course["fest_id"],
            "faculty": course["inst_sigla"].lower(),
            "course_name": course["cur_nome"]
        }, courses))

    def convert_sigarra_schedule(self, schedule_data):
        new_schedule_data = []
            
        for schedule in schedule_data:
            course_unit = CourseUnit.objects.filter(id=schedule['ocorrencia_id'])[0]
            professors = []
            for docente in schedule['docentes']:
                professor = Professor.objects.filter(id=docente['doc_codigo'])
                if(len(professor) < 1):
                    continue
                professors.append({"name": docente['doc_nome'], "acronym": professor[0].professor_acronym})

            new_schedule = {
                'courseInfo': {
                    'id': schedule['ocorrencia_id'],
                    'course_unit_id': schedule['ocorrencia_id'],
                    'acronym': course_unit.acronym,
                    'name': course_unit.name,
                    'url': course_unit.url
                },
                'classInfo': {
                    'id': schedule['ocorrencia_id'],
                    'name': schedule['turma_sigla'],
                    'filteredTeachers': [],
                    'slots': [{
                        'id': schedule['ocorrencia_id'],
                        'lesson_type': schedule["tipo"],
                        'day': schedule['dia'] - 2,
                        'start_time': schedule['hora_inicio'] / 3600,
                        'duration': schedule['aula_duracao'],
                        'location': schedule['sala_sigla'],
                        'professors_link': '',
                        'professors': professors
                    }],
                }
            }

            new_schedule_data.append(new_schedule)

        return new_schedule_data

    def login(self):
        try:
            response = requests.post("https://sigarra.up.pt/feup/pt/mob_val_geral.autentica/", data={
                "pv_login": self.username,  
                "pv_password": self.password
            })

            self.cookies = response.cookies
        except requests.exceptions.RequestException as e:
            print("Error: ", e)

    def get_student_schedule(self, nmec: int) -> SigarraResponse:
        (semana_ini, semana_fim) = self.semester_weeks()

        response = requests.get(self.student_schedule_url(
            nmec,
            semana_ini,
            semana_fim
        ), cookies=self.cookies)

        if(response.status_code != 200):
            return SigarraResponse(None, response.status_code)

        return SigarraResponse(self.convert_sigarra_schedule(response.json()['horario']), response.status_code)

    def get_student_course_units(self, nmec: int) -> SigarraResponse:
        schedule = self.get_student_schedule(nmec)

        if schedule.status_code != 200:
            return SigarraResponse(None, schedule.status_code)
        
        course_units = set()
        for scheduleItem in schedule.data:
            course_units.add(scheduleItem["ocorrencia_id"])

        return SigarraResponse(list(course_units), 200)

    def get_course_unit_classes(self, course_unit_id: int) -> SigarraResponse:
        url = f"https://sigarra.up.pt/feup/pt/mob_ucurr_geral.uc_inscritos?pv_ocorrencia_id={course_unit_id}"
        response = requests.get(url, cookies=self.cookies)

        if response.status_code != 200:
            return SigarraResponse(None, response.status_code)

        return SigarraResponse(response.json(), 200)

    """
        Returns a tuple with (pratical class, theoretical class)
    """
    def get_class_schedule(self, course_unit_id: int, class_name: str) -> SigarraResponse:
        (semana_ini, semana_fim) = self.semester_weeks()

        response = requests.get(self.course_unit_schedule_url(
            course_unit_id, 
            semana_ini, 
            semana_fim
        ), cookies=self.cookies)

        if(response.status_code != 200):
            return SigarraResponse(None, response.status_code)

        classes = json.loads(response.content)["horario"]
        class_schedule = list(filter(lambda c: any(schedule["turma_sigla"] == class_name for schedule in c["turmas"]), classes))
        theoretical_schedule = list(filter(lambda c: c["tipo"] == "T" and any(schedule["turma_sigla"] == class_name for schedule in c["turmas"]), classes))
        
        return SigarraResponse((class_schedule, theoretical_schedule), 200)
 

