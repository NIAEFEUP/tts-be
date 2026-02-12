import requests
import json

from university.controllers.ScheduleController import ScheduleController

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

        if login:
            self.login()

    def get_student_photo_url(self, nmec) -> str:
        return f"https://sigarra.up.pt/feup/pt/fotografias_service.foto?pct_cod={nmec}"

    def semester_weeks(self):
        currdate = date.today()
        year = str(currdate.year)
        first_semester = int(CONFIG["EXCHANGE_SEMESTER"]) == 1 if CONFIG["EXCHANGE_SEMESTER"] else currdate.month >= 10 or currdate.month <= 1
        if first_semester:
            if currdate.month <= 2:
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

    def login(self):
        try:
            response = requests.post("https://sigarra.up.pt/feup/pt/vld_validacao.validacao", data={
                "p_user": self.username,
                "p_pass": self.password
            })

            self.cookies = response.cookies
        except requests.exceptions.RequestException as e:
            print("Error: ", e)

    def get_student_schedule(self, nmec: int) -> SigarraResponse:
        (semana_ini, semana_fim) = self.semester_weeks()
       
        big_map = {'2LEIC01': ['202403501', '202306547', '202406588', '202404631', '202404403', '202404733', '202406915', '202304958', '202406698', '202404270', '202407213', '202405575', '202403883', '202209797', '202403344', '202403747', '202404872', '202409115', '202404211', '202406149', '202405590', '202406919', '202404218', '202404436'], '2LEIC02': ['202405569', '202405143', '202404117', '202403705', '202407377', '202405159', '202406972', '202006525', '202405577', '202405528', '202403505', '202404828', '202406974', '202404670', '202405336', '202406706', '202403644'], '2LEIC03': ['202405858', '202404687', '202405390', '202407080', '202404038', '202404406', '202407152', '202403874', '202407099', '202406360', '202403346', '202406040', '202403355', '202404098', '202400103', '202407736', '202404987', '202406334', '202403845', '202403626', '202407238', '202306955', '202403468', '202407243'], '2LEIC04': ['202405385', '202403577', '202407661', '202405066', '202000137', '202403634', '202403438', '202406155', '202404233', '202404396', '202409216', '202405044', '202407709', '202404122', '202406278', '202406702', '202405055', '202404971', '202403324', '202403784', '202403853', '202404394', '202405067'], '2LEIC05': ['202405681', '202404312', '202409403', '202406798', '202407548', '202406938', '202308554', '202310411', '202404550', '202409108', '202407257', '202404986', '202406543', '202405428', '202404941', '202407005', '202403604'], '2LEIC07': ['202300449', '202008423', '202307104', '202304549', '202309694', '202306967', '202210143', '202405892', '202307295', '202304565', '202304496', '202304298', '202305717', '202306719', '202204857', '202307229', '202208340', '202304412', '202306727', '202309532', '202304126', '202405335', '202304762', '202305823'], '2LEIC09': ['202407009', '202405613', '202406324', '202406332', '202404947', '202403406', '202405017', '202406511', '202406502', '202407250', '202404789', '202406584', '202403429', '202405618', '202405319', '202307837', '202404802', '202404805', '202405637', '202403480', '202403362', '202403435'], '2LEIC10': ['202304970', '202404977', '202403962', '202409357', '202404158', '202405068', '202305998', '202406765', '202405164', '202406001', '202407255', '202407047', '202403383', '202405578', '202405579', '202403752', '202406035', '202404966', '202109258', '202405295'], '2LEIC12': ['202405418', '202403939', '202404210', '202404630', '202407472', '202404189', '202306056', '202406448', '202404022', '202404899', '202404656', '202407098', '202404812', '202404170', '202403610', '202406359', '202405711', '202404078', '202404194', '202405484', '202300428', '202406079', '202404099', '202403623', '202403624', '202405057'], '2LEIC13': ['202403579', '202407409', '202407068', '202406986', '202405079', '202407071', '202404033', '202407338', '202404073', '202405890', '202306967', '202407486', '202407040', '202403340', '202404376', '202405961', '202404498', '202405967', '202407231', '202406902', '202404878', '202404455', '202406903', '202412740'], '2LEIC14': ['202406140', '202403904', '201406150', '202406592', '202405947', '202407434', '202404485', '202406609', '202407610', '202406771', '202404904', '202404967', '202404127', '202404130', '202403993', '202404912', '202406654', '202404344', '202405342', '202405343'], '2LEIC16': ['202209729', '202004551', '202000137', '202307628', '202306484', '201806326', '201604138', '202306919', '202309927', '202305080', '202304718', '202306582', '202304607', '202307047', '202409110', '202310202', '202109258', '202008864', '202305878', '202206640', '202307438', '202306438', '202304459']}
        bad_clases = ['2LEIC02', '2LEIC05', '2LEIC06', '2LEIC11', '2LEIC10', '2LEIC14', '2LEIC15', '2LEIC09','2LEIC07','2LEIC16']
        
        mapping = {'2LEIC02':'{"dia":3,"hora_inicio":37800,"ucurr_sigla":"CP","ocorrencia_id":564271,"tipo":"TP","aula_id":11000726,"aula_duracao":2,"sala_sigla":"B318","salas":[{"espaco_id":73150,"espaco_nome":"B318"}],"doc_sigla":"FMSTT","docentes":[{"doc_codigo":"449830","doc_nome":"Fernanda Maria dos Santos Teixeira Torres"}],"turma_sigla":"2LEIC02","turmas":[{"turma_id":215543,"turma_sigla":"2LEIC02"}],"periodo":3}',
                   '2LEIC05':'{"dia":3,"hora_inicio":37800,"ucurr_sigla":"CP","ocorrencia_id":564271,"tipo":"TP","aula_id":11000757,"aula_duracao":2,"sala_sigla":"B223","salas":[{"espaco_id":73172,"espaco_nome":"B223"}],"doc_sigla":"MFST","docentes":[{"doc_codigo":"322605","doc_nome":"Manuel Firmino da Silva Torres"}],"turma_sigla":"2LEIC05","turmas":[{"turma_id":215546,"turma_sigla":"2LEIC05"}],"periodo":3}',
                   '2LEIC10':'{"dia":5,"hora_inicio":37800,"ucurr_sigla":"CP","ocorrencia_id":564271,"tipo":"TP","aula_id":12000757,"aula_duracao":2,"sala_sigla":"B217","salas":[{"espaco_id":73173,"espaco_nome":"B217"}],"doc_sigla":"FMSTT","docentes":[{"doc_codigo":"449830","doc_nome":"Fernanda Maria dos Santos Teixeira Torres"}],"turma_sigla":"2LEIC10","turmas":[{"turma_id":215551,"turma_sigla":"2LEIC10"}],"periodo":3}',
                   '2LEIC14':'{"dia":5,"hora_inicio":37800,"ucurr_sigla":"CP","ocorrencia_id":564271,"tipo":"TP","aula_id":11000779,"aula_duracao":2,"sala_sigla":"B318","salas":[{"espaco_id":73150,"espaco_nome":"B318"}],"doc_sigla":"MFST","docentes":[{"doc_codigo":"322605","doc_nome":"Manuel Firmino da Silva Torres"}],"turma_sigla":"2LEIC14","turmas":[{"turma_id":215555,"turma_sigla":"2LEIC14"}],"periodo":3}',
                   '2LEIC09': '{"dia":5,"hora_inicio":37800,"ucurr_sigla":"CP","ocorrencia_id":564271,"tipo":"TP","aula_id":13000757,"aula_duracao":2,"sala_sigla":"B217","salas":[{"espaco_id":73173,"espaco_nome":"B217"}],"doc_sigla":"FMSTT","docentes":[{"doc_codigo":"449830","doc_nome":"Fernanda Maria dos Santos Teixeira Torres"}],"turma_sigla":"2LEIC09","turmas":[{"turma_id":215550,"turma_sigla":"2LEIC09"}],"periodo":3}',
                   '2LEIC07': '{"dia":4,"hora_inicio":50400,"ucurr_sigla":"CP","ocorrencia_id":564271,"tipo":"TP","aula_id":14000757,"aula_duracao":2,"sala_sigla":"B217","salas":[{"espaco_id":73173,"espaco_nome":"B217"}],"doc_sigla":"FMSTT","docentes":[{"doc_codigo":"449830","doc_nome":"Fernanda Maria dos Santos Teixeira Torres"}],"turma_sigla":"2LEIC07","turmas":[{"turma_id":215548,"turma_sigla":"2LEIC07"}],"periodo":3}',
                   '2LEIC16': '{"dia":4,"hora_inicio":50400,"ucurr_sigla":"CP","ocorrencia_id":564271,"tipo":"TP","aula_id":15000757,"aula_duracao":2,"sala_sigla":"B229","salas":[{"espaco_id":73356,"espaco_nome":"B229"}],"doc_sigla":"MFST","docentes":[{"doc_codigo":"322605","doc_nome":"Manuel Firmino da Silva Torres"}],"turma_sigla":"2LEIC16","turmas":[{"turma_id":215557,"turma_sigla":"2LEIC16"}],"periodo":3}'}   
        
        nmec_str = str(nmec)

        student_class = next(
            (class_name for class_name, students in big_map.items() if nmec_str in students),
            None
        )
         
        bad_student = student_class in bad_clases
        
        response = requests.get(self.student_schedule_url(
            nmec,
            semana_ini,
            semana_fim
        ), cookies=self.cookies)
        
        data = response.json()
        
        if bad_student and student_class in mapping:
            injected_class = json.loads(mapping[student_class])
            data["horario"].append(injected_class)

    
        if(response.status_code != 200):
            return SigarraResponse(None, response.status_code)
        

        return SigarraResponse(data["horario"], response.status_code)

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

    def get_course_schedule(self, course_unit_id: int, new_schedule_api: bool = False, faculty: str = "feup") -> SigarraResponse:
        (semana_ini, semana_fim) = self.semester_weeks()
        schedule_controller = ScheduleController()

        response = requests.get(self.course_unit_schedule_url(
            course_unit_id,
            semana_ini,
            semana_fim,
            faculty
        ) if not new_schedule_api else ScheduleController().calendarios_api(
            faculty,
            course_unit_id,
            schedule_controller.get_academic_year(),
            schedule_controller.get_period()
        ), cookies=self.cookies)

        if(response.status_code != 200):
            return SigarraResponse(None, response.status_code)

        return SigarraResponse(response.json()['horario' if not new_schedule_api else 'data'], response.status_code)

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



