from university.controllers.ExchangeController import ExchangeController
from university.controllers.SigarraController import SigarraController

from university.exchange.utils import exchange_overlap, build_student_schedule_dict, ExchangeStatus, exchange_status_message

from university.models import DirectExchangeParticipants

class ExchangeValidationResponse:
    def __init__(self, status: bool, message: ExchangeStatus):
        self.status = status
        self.message = exchange_status_message(message)

class ExchangeValidationController:
    """
        This class will contain methods to validate the direct exchanges that are already inside
        of the database.

        The validation inside the views of the marketplace exchange and direct exchange have
        a different logic of working because they cannot use what is inside of the database and
        will validate the request format.
    """
    def validate_direct_exchange(self, exchange_id: int) -> ExchangeValidationResponse:
        exchange_participants = list(DirectExchangeParticipants.objects.filter(direct_exchange__id=exchange_id).all())

        # 1. Build new schedule of each student
        schedule = {}
        for participant in exchange_participants:
            if participant.participant_nmec not in schedule.keys():
                schedule[participant.participant_nmec] = build_student_schedule_dict(SigarraController().get_student_schedule(int(participant.participant_nmec)).data)

        # 2. Check if users are inside classes they will exchange from with
        for username in schedule.keys():
            participant_entries = list(DirectExchangeParticipants.objects.filter(participant_nmec=username).all())

            for entry in participant_entries:
                if (entry.class_participant_goes_from, int(entry.course_unit_id)) not in list(schedule[username].keys()):
                    return ExchangeValidationResponse(False, ExchangeStatus.STUDENTS_NOT_ENROLLED)

                # 3. Alter the schedule of the users according to the exchange metadata 
                schedule[username][(entry.class_participant_goes_to, int(entry.course_unit_id))] = SigarraController().get_class_schedule(int(entry.course_unit_id), entry.class_participant_goes_to).data
                del schedule[username][(entry.class_participant_goes_from, int(entry.course_unit_id))]


        # 4. Verify if the exchanges will have overlaps after building the new schedules
        for username in schedule.keys():
            if exchange_overlap(schedule, username):
                return ExchangeValidationResponse(False, ExchangeStatus.CLASSES_OVERLAP)

        return ExchangeValidationResponse(True, ExchangeStatus.SUCCESS)