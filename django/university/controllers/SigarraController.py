import base64
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

import requests

from university.controllers.ScheduleController import ScheduleController
from university.utils import sigarra_mock

from datetime import date
from tts_be.settings import CONFIG

class SigarraResponse:
    def __init__(self, data, status_code):
        self.data = data
        self.status_code = status_code

class SigarraController:
    """
        This class will contain methods to manipulate student data that is inside sigarra.
    """

    def __init__(self, login = True):
        self.username = CONFIG["SIGARRA_USERNAME"]
        self.password = CONFIG["SIGARRA_PASSWORD"]
        self.cookies = None
        self.mock = CONFIG["MOCK_SIGARRA"] if "MOCK_SIGARRA" in CONFIG else 0

        if login and not self.mock:
            self.login()

    def make_get_request(self, url):
        print(f"made GET request to {url}")
        if self.mock:
            return sigarra_mock.get(url)
        return requests.get(url, cookies=self.cookies)
        
    def make_post_request(self, url, data = None):
        print(f"made POST request to {url}")
        if self.mock:
            return sigarra_mock.post(url, data)
        return requests.post(url, data)

    def get_student_photo_url(self, nmec) -> str:
        return f"https://sigarra.up.pt/feup/pt/fotografias_service.foto?pct_cod={nmec}"

    def semester_weeks(self):
        currdate = date.today()
        year = str(currdate.year) if not CONFIG["EXCHANGE_YEAR"] else CONFIG["EXCHANGE_YEAR"] 
        first_semester = int(CONFIG["EXCHANGE_SEMESTER"]) == 1 if CONFIG["EXCHANGE_SEMESTER"] else currdate.month >= 10 or currdate.month <= 1
        if first_semester:
            if currdate.month == 1:
                year = str(int(year) - 1)

            semana_ini = year + "1001"
            semana_fim = f"{int(year) + 1}0131"
        else:
            semana_ini = year + "0210"
            semana_fim = year + "0601"

        return (semana_ini, semana_fim)

    def student_profile_url(self, nmec):
        return f"https://sigarra.up.pt/feup/pt/mob_fest_geral.perfil?pv_codigo={nmec}"

    def student_schedule_url(self, nmec, semana_ini, semana_fim) -> str:
        return f"https://sigarra.up.pt/feup/pt/mob_hor_geral.estudante?pv_codigo={nmec}&pv_semana_ini={semana_ini}&pv_semana_fim={semana_fim}"

    def course_unit_schedule_url(self, ocorrencia_id, semana_ini, semana_fim, faculty: str = "feup"):
        return f"https://sigarra.up.pt/{faculty}/pt/mob_hor_geral.ucurr?pv_ocorrencia_id={ocorrencia_id}&pv_semana_ini={semana_ini}&pv_semana_fim={semana_fim}"

    def retrieve_student_photo(self, nmec):
        response = self.make_get_request(self.get_student_photo_url(nmec))

        if response.status_code != 200:
            return SigarraResponse(None, response.status_code)
        print(response.content)

        return SigarraResponse(response.content, 200)

    def get_student_profile(self, nmec):
        response = self.make_get_request(self.student_profile_url(nmec))

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

    def login(self):
        try:
            response = self.make_post_request("https://sigarra.up.pt/feup/pt/vld_validacao.validacao", data={
                "p_user": self.username,
                "p_pass": self.password
            })

            self.cookies = response.cookies
        except requests.exceptions.RequestException as e:
            print("Error: ", e)

    def get_student_schedule(self, nmec: int) -> SigarraResponse:
        (semana_ini, semana_fim) = self.semester_weeks()
        print(f"url is {self.student_schedule_url(nmec,semana_ini,semana_fim)}")
        response = self.make_get_request(self.student_schedule_url(
            nmec,
            semana_ini,
            semana_fim
        ))

        if(response.status_code != 200):
            return SigarraResponse(None, response.status_code)

        return SigarraResponse(response.json()['horario'], response.status_code)

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
        response = self.make_get_request(url)

        if response.status_code != 200:
            return SigarraResponse(None, response.status_code)

        return SigarraResponse(response.json(), 200)

    def get_course_schedule(self, course_unit_id: int, new_schedule_api: bool = False, faculty: str = "feup") -> SigarraResponse:
        (semana_ini, semana_fim) = self.semester_weeks()
        schedule_controller = ScheduleController()

        response = self.make_get_request(self.course_unit_schedule_url(
            course_unit_id,
            semana_ini,
            semana_fim,
            faculty
        ) if not new_schedule_api else ScheduleController().calendarios_api(
            faculty,
            course_unit_id,
            schedule_controller.get_academic_year(),
            schedule_controller.get_period()
        ))

        if(response.status_code != 200):
            return SigarraResponse(None, response.status_code)

        return SigarraResponse(response.json()['horario' if not new_schedule_api else 'data'], response.status_code)

    """
        Returns a tuple with (pratical class, theoretical class)
    """
    def get_class_schedule(self, course_unit_id: int, class_name: str) -> SigarraResponse:
        (semana_ini, semana_fim) = self.semester_weeks()

        response = self.make_get_request(self.course_unit_schedule_url(
            course_unit_id,
            semana_ini,
            semana_fim
        ))

        if(response.status_code != 200):
            return SigarraResponse(None, response.status_code)

        classes = json.loads(response.content)["horario"]
        class_schedule = list(filter(lambda c: any(schedule["turma_sigla"] == class_name for schedule in c["turmas"]), classes))
        theoretical_schedule = list(filter(lambda c: c["tipo"] == "T" and any(schedule["turma_sigla"] == class_name for schedule in c["turmas"]), classes))

        return SigarraResponse((class_schedule, theoretical_schedule), 200)


