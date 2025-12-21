class ScheduleController:
    def __init__(self):
        self.weekday_to_day = {
            "Segunda-feira": 0,
            "Terça-feira": 1,
            "Quarta-feira": 2,
            "Quinta-feira": 3,
            "Sexta-feira": 4,
            "Sábado": 5,
            "Domingo": 6
        }

    def from_sigarra_day(self, day: int):
        return day - 1

    def day_from_sigarra_week_day(self, day: str):
        return self.weekday_to_day[day]

    def calendarios_api(self, faculty: str, course_unit_id: int, year: int, semester: int):
        return f"https://sigarra.up.pt/calendarios-api/api/v1/events/{faculty}/uc/{course_unit_id}/?academic_year={year}&period={semester}"
