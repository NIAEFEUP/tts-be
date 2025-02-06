import base64
import json

from django.core.paginator import Paginator
from university.controllers.ClassController import ClassController
from university.controllers.SigarraController import SigarraController
from university.exchange.utils import ExchangeStatus, check_class_mandatory, check_class_schedule_overlap, course_unit_by_id
from university.models import DirectExchange, DirectExchangeParticipants, ExchangeExpirations, MarketplaceExchange
from django.utils import timezone
from enum import Enum

from university.models import UserCourseUnits

from university.serializers.DirectExchangeParticipantsSerializer import DirectExchangeParticipantsSerializer
from university.serializers.MarketplaceExchangeClassSerializer import MarketplaceExchangeClassSerializer

class ExchangeType(Enum):
    MARKETPLACE_EXCHANGE = 1
    DIRECT_EXCHANGE = 2

    def toString(self):
        return "marketplaceexchange" if self == ExchangeType.MARKETPLACE_EXCHANGE else "directexchange"

class DirectExchangePendingMotive(Enum):
    USER_DID_NOT_ACCEPT = 1
    OTHERS_DID_NOT_ACCEPT = 2
    NOT_PENDING = 3
    
    @staticmethod
    def get_pending_motive(curr_user_nmec: str, direct_exchange: DirectExchange):
        participants = list(DirectExchangeParticipants.objects.filter(
            participant_nmec=curr_user_nmec, direct_exchange=direct_exchange).all()
        )

        # The participants list includes the options in the exchange of the current user
        for participant in participants:
            if not participant.accepted:
                return DirectExchangePendingMotive.USER_DID_NOT_ACCEPT

        if not direct_exchange.accepted:
            return DirectExchangePendingMotive.OTHERS_DID_NOT_ACCEPT

        return DirectExchangePendingMotive.NOT_PENDING 
    
    @staticmethod
    def get_value(pending_motive):
        return pending_motive.value


class ExchangeController:
    @staticmethod
    def eligible_course_units(nmec):
        course_units = UserCourseUnits.objects.filter(user_nmec=nmec).values_list("course_unit_id", flat=True)

        exchange_expirations = ExchangeExpirations.objects.filter(
            course_unit_id__in=course_units, 
            active_date__lte=timezone.now(),
            end_date__gte=timezone.now(),
        ).values_list("course_unit_id", flat=True)

        return list(exchange_expirations)

    @staticmethod
    def getExchangeType(exchange) -> ExchangeType:
        if type(exchange) == MarketplaceExchange:
            return ExchangeType.MARKETPLACE_EXCHANGE
        
        return ExchangeType.DIRECT_EXCHANGE

    @staticmethod
    def getOptionsDependinOnExchangeType(exchange):
        if type(exchange) == MarketplaceExchange:
            return [MarketplaceExchangeClassSerializer(exchange_class).data for exchange_class in exchange.options]
        elif type(exchange) == DirectExchange:
            return [DirectExchangeParticipantsSerializer(participant).data for participant in exchange.options]

    @staticmethod
    def getExchangeOptionClasses(options):
        classes = sum(list(map(lambda option: ClassController.get_classes(option.course_unit_id), options)), [])
        return filter(lambda currentClass: any(currentClass["name"] == option.class_issuer_goes_from for option in options), classes)

    @staticmethod
    def courseUnitNameFilterInExchangeOptions(options, courseUnitNameFilter):
        matches = []
        for courseUnitId in courseUnitNameFilter:
            for option in options:
                if courseUnitId == option.course_unit_id:
                    matches.append(1)

        return len(matches) == len(courseUnitNameFilter)

    @staticmethod
    def parseClassesFilter(classesFilter: str) -> dict:
        if not classesFilter:
            return {}

        b64_decoded = base64.b64decode(classesFilter)
        string = b64_decoded.decode('utf-8')
        return dict(json.loads(string))

    @staticmethod
    def getStudentClass(student_schedules, username, courseUnitId):
        schedule = student_schedules[username]
        for key in schedule.keys():
            if key[1] == courseUnitId:
                return key[0]

        return None

    @staticmethod
    def create_direct_exchange_participants(student_schedules, exchanges, inserted_exchanges, exchange_db_model, auth_user):
        for curr_exchange in exchanges:
            other_student = curr_exchange["other_student"]["mecNumber"]
            course_unit = course_unit_by_id(curr_exchange["courseUnitId"])

            inserted_exchanges.append(DirectExchangeParticipants(
                participant_name=curr_exchange["other_student"]["name"],
                participant_nmec=curr_exchange["other_student"]["mecNumber"],
                class_participant_goes_from=ExchangeController.getStudentClass(student_schedules, other_student, curr_exchange["courseUnitId"]),
                class_participant_goes_to=curr_exchange["classNameRequesterGoesFrom"],
                course_unit=course_unit.acronym,
                course_unit_id=curr_exchange["courseUnitId"],
                direct_exchange=exchange_db_model,
                accepted=False,
                date=timezone.now()
            ))

            inserted_exchanges.append(DirectExchangeParticipants(
                participant_name=auth_user,
                participant_nmec=auth_user,
                class_participant_goes_from=curr_exchange["classNameRequesterGoesFrom"], # This is not a typo, the old class of the authenticted student is the new class of the other student
                class_participant_goes_to=curr_exchange["classNameRequesterGoesTo"],
                course_unit=course_unit.acronym,
                course_unit_id=curr_exchange["courseUnitId"],
                direct_exchange=exchange_db_model,
                accepted=False,
                date=timezone.now()
            ))

        return (ExchangeStatus.SUCCESS, None)

    """
        Checks if schedule for a user with a given username has overlpas
    """
    @staticmethod
    def exchange_overlap(student_schedules, username, from_local_db: bool = False) -> bool:

        for (key, class_schedule) in student_schedules[username].items():
            for (other_key, other_class_schedule) in student_schedules[username].items():
                if key == other_key:
                    continue

                print("CLASS SCHEDULE: ", class_schedule)
                print("OTHER CLASS SCHEDULE: ", other_class_schedule)

                class_slot = class_schedule["classInfo"]["slots"][0]
                other_class_slot = other_class_schedule["classInfo"]["slots"][0]

                (class_schedule_day, class_schedule_start, class_schedule_end, class_schedule_type) = (class_slot["day"], class_slot["start_time"], class_slot["duration"] + class_slot["start_time"], class_slot['lesson_type'])
                (overlap_param_day, overlap_param_start, overlap_param_end, overlap_param_type) = (other_class_slot["day"], other_class_slot["start_time"], other_class_slot["duration"] + other_class_slot["start_time"], other_class_slot['lesson_type'])

                if (check_class_mandatory(class_schedule_type) and check_class_mandatory(overlap_param_type)
                    and check_class_schedule_overlap(class_schedule_day, class_schedule_start, class_schedule_end, overlap_param_day, overlap_param_start, overlap_param_end)):
                    return True

        return False

    @staticmethod
    def update_schedule_accepted_exchanges(student, schedule, from_local_db: bool = False):
        accepted_options = DirectExchangeParticipants.objects.filter(participant_nmec=student, accepted=True, direct_exchange__canceled=False, direct_exchange__accepted=True)
        (status, trailing) = ExchangeController.update_schedule(schedule, accepted_options, from_local_db) 
        if status == ExchangeStatus.FETCH_SCHEDULE_ERROR:
            return (ExchangeStatus.FETCH_SCHEDULE_ERROR, trailing)

        return (ExchangeStatus.SUCCESS, None)

    def update_schedule(student_schedule, exchanges, from_local_db: bool = False):
        print("UPDATING SCHEDULE: ", student_schedule)
        return (ExchangeStatus.SUCCESS, None)

        # if from_local_db:
        #     return (ExchangeStatus.SUCCESS, None)
        # else:
        #     for exchange in exchanges:
        #         for i, schedule in enumerate(student_schedule):
        #             ocurr_id = int(schedule["ocorrencia_id"])

        #             if ocurr_id == int(exchange.course_unit_id):
        #                 class_type = schedule["tipo"]

        #                 res = SigarraController().get_class_schedule(int(exchange.course_unit_id), exchange.class_participant_goes_to)
        #                 if res.status_code != 200: 
        #                     return (ExchangeStatus.FETCH_SCHEDULE_ERROR, None)

        #                 (tp_schedule, t_schedule) = res.data
        #                 tp_schedule.extend(t_schedule)
        #                 new_schedules = tp_schedule

        #                 for new_schedule in new_schedules:
        #                     for turma in new_schedule["turmas"]:
        #                         if turma["turma_sigla"] == exchange.class_participant_goes_to and new_schedule["tipo"] == class_type:
        #                             student_schedule[i] = new_schedule
            
        #     return (ExchangeStatus.SUCCESS, None)