import requests
import json

from datetime import date
from tts_be.settings import CONFIG

class SigarraResponse:
    def __init__(self, data, status_code):
        self.data = data
        self.status_code = status_code
    
class SigarraController:
    def __init__(self):
        self.username = CONFIG["SIGARRA_USERNAME"]
        self.password = CONFIG["SIGARRA_PASSWORD"]
        self.cookies = None

        self.login()

    def semester_weeks(self):
        currdate = date.today()
        year = str(currdate.year)
        first_semester = currdate.month >= 9 and currdate.month <= 12
        if first_semester: 
            semana_ini = "1001"
            semana_fim = "1201"
        else:
            semana_ini = "0101"
            semana_fim = "0601"
        
        return (year + semana_ini, year + semana_fim)
    
    def student_schedule_url(self, nmec, semana_ini, semana_fim) -> str:
        return f"https://sigarra.up.pt/feup/pt/mob_hor_geral.estudante?pv_codigo={nmec}&pv_semana_ini={semana_ini}&pv_semana_fim={semana_fim}" 

    def course_unit_schedule_url(self, ocorrencia_id, semana_ini, semana_fim):
        return f"https://sigarra.up.pt/feup/pt/mob_hor_geral.ucurr?pv_ocorrencia_id={ocorrencia_id}&pv_semana_ini={semana_ini}&pv_semana_fim={semana_fim}"


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

        return SigarraResponse(response.json()['horario'], response.status_code)
    
    def get_course_unit_classes(self, course_unit_id: int) -> SigarraResponse:
        url = f"https://sigarra.up.pt/feup/pt/mob_ucurr_geral.uc_inscritos?pv_ocorrencia_id={course_unit_id}"
        response = requests.get(url, cookies=self.cookies)

        if response.status_code != 200:
            return SigarraResponse(None, response.status_code)

        return SigarraResponse(response.json(), 200)

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
        class_schedule = list(filter(lambda c: c["turma_sigla"] == class_name, classes))
        theoretical_schedule = list(filter(lambda c: c["tipo"] == "T" and any(schedule["turma_sigla"] == class_name for schedule in c["turmas"]), classes))
        
        return SigarraResponse((class_schedule, theoretical_schedule), 200)
 

