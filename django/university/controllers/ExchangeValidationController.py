from university.controllers.ExchangeController import ExchangeController
from university.controllers.SigarraController import SigarraController

from university.exchange.utils import exchange_overlap, build_student_schedule_dict, ExchangeStatus, exchange_status_message

from university.models import DirectExchangeParticipants, DirectExchange

from django.db import transaction

class ExchangeValidationResponse:
    def __init__(self, status: bool, message: ExchangeStatus):
        self.status = status
        self.message = exchange_status_message(message)

class ExchangeValidationController:
    """
        Imagine the scenario where a person has two active pending exchanges:

        - 1LEIC01 -> 1LEIC06 (AM I) 
        - 1LEIC01 -> 1LEIC09 (AM I)

        If the user accepts the first exchange and the exchange is accepted, the other exchange will be invalidated and users should be warned about that.


        All of the exchanges that include classes that were changed by the accepted exchange need to be revalidated or even canceled.
    """
    def cancel_conflicting_exchanges(self, accepted_exchange_id: int):
        if(DirectExchange.objects.filter(id=accepted_exchange_id).first().canceled):
            return 

        conflicting_exchanges = []

        with transaction.atomic():
            accepted_exchange_participants = DirectExchangeParticipants.objects.filter(direct_exchange__id=accepted_exchange_id)
            for participant in accepted_exchange_participants:
                # 1. Are there any exchanges that include classes that a participant changed from?
                conflicting = DirectExchangeParticipants.objects.exclude(direct_exchange__id=accepted_exchange_id).filter(
                    participant_nmec=participant.participant_nmec, 
                    class_participant_goes_from=participant.class_participant_goes_from,
                    direct_exchange__accepted=True
                )
                conflicting_exchanges.extend(list(map(lambda conflicting_exchange: conflicting_exchange.direct_exchange, conflicting)))
                
            # 2. Revalidate all of the other exchanges who include classes from the participant but not classes
            # that are the "class_participant_goes_from" of the exchange
            for participant in accepted_exchange_participants:
                exchanges = DirectExchange.objects.exclude(id=accepted_exchange_id).filter(
                    directexchangeparticipants__participant_nmec=participant.participant_nmec
                )
                exchanges = [exchange for exchange in exchanges if exchange not in conflicting_exchanges]

                for exchange in exchanges:
                    if not self.validate_direct_exchange(exchange.id).status:
                        conflicting_exchanges.append(exchange)

            # 3. Cancel all the conflicting exchanges
            for conflicting_exchange in conflicting_exchanges:
                self.cancel_exchange(conflicting_exchange)

    def cancel_exchange(self, exchange):
        exchange.canceled = True
        exchange.save()

    """
        This class will contain methods to validate the direct exchanges that are already inside
        of the database.

        The validation inside the views of the marketplace exchange and direct exchange have
        a different logic of working because they cannot use what is inside of the database and
        will validate the request format.
    """
    def validate_direct_exchange(self, exchange_id: int) -> ExchangeValidationResponse:
        exchange_participants = DirectExchangeParticipants.objects.filter(direct_exchange__id=exchange_id).all()

        # 1. Build new schedule of each student
        schedule = {}
        for participant in exchange_participants:
            if participant.participant_nmec not in schedule.keys():
                schedule[participant.participant_nmec] = build_student_schedule_dict(SigarraController().get_student_schedule(int(participant.participant_nmec)).data)

            # Get new schedule from accepted changes
            ExchangeController.update_schedule_accepted_exchanges(participant.participant_nmec, list(schedule[participant.participant_nmec].values()))

        # 2. Check if users are inside classes they will exchange from with
        for username in schedule.keys():
            participant_entries = list(exchange_participants.filter(participant_nmec=username))

            for entry in participant_entries:
                if (entry.class_participant_goes_from, int(entry.course_unit_id)) not in list(schedule[username].keys()):
                    return ExchangeValidationResponse(False, ExchangeStatus.STUDENTS_NOT_ENROLLED)

                # 3. Alter the schedule of the users according to the exchange metadata 
                class_schedule = SigarraController().get_class_schedule(int(entry.course_unit_id), entry.class_participant_goes_to).data[0][0] # For other courses we will need to have pratical class as a list in the dictionary

                schedule[username][(entry.class_participant_goes_to, int(entry.course_unit_id))] = class_schedule
                del schedule[username][(entry.class_participant_goes_from, int(entry.course_unit_id))]

        # 4. Verify if the exchanges will have overlaps after building the new schedules
        for username in schedule.keys():
            if ExchangeController.exchange_overlap(schedule, username):
                return ExchangeValidationResponse(False, ExchangeStatus.CLASSES_OVERLAP)

        return ExchangeValidationResponse(True, ExchangeStatus.SUCCESS)