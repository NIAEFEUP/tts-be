import base64
import json

from django.core.paginator import Paginator
from university.controllers.ClassController import ClassController
from university.exchange.utils import ExchangeStatus, check_class_schedule_overlap, course_unit_by_id
from university.models import DirectExchangeParticipants, ExchangeExpirations
from django.utils import timezone

from university.serializers.MarketplaceExchangeClassSerializer import MarketplaceExchangeClassSerializer


class ExchangeController:
    @staticmethod
    def eligible_course_units(sigarra_controller, nmec):
        course_units = sigarra_controller.get_student_course_units(nmec).data

        exchange_expirations = ExchangeExpirations.objects.filter(
            course_unit_id__in=course_units, 
            active_date__lte=timezone.now(),
            end_date__gte=timezone.now(),
        ).values_list("course_unit_id", flat=True)
    
        return list(exchange_expirations)

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
    def build_pagination_payload(request, exchanges):
        page_number = request.GET.get("page")
        paginator = Paginator(exchanges, 10)
        page_obj = paginator.get_page(page_number if page_number != None else 1)

        return {
            "page": {
                "current": page_obj.number,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
            "data": [{
                "id": exchange.id,
                "issuer_name": exchange.issuer_name,
                "issuer_nmec": exchange.issuer_nmec,
                "options": [
                    MarketplaceExchangeClassSerializer(exchange_class).data for exchange_class in exchange.options
                ],
                "classes": list(ExchangeController.getExchangeOptionClasses(exchange.options)),
                "date":  exchange.date,
                "accepted": exchange.accepted
            } for exchange in page_obj]
        }
  
    @staticmethod
    def create_direct_exchange_participants(student_schedules, exchanges, inserted_exchanges, exchange_db_model, auth_user):
        if ExchangeController.exchange_overlap(student_schedules, auth_user):
            return (ExchangeStatus.CLASSES_OVERLAP, None)

        for curr_exchange in exchanges:
            other_student = curr_exchange["other_student"]

            course_unit = course_unit_by_id(curr_exchange["course_unit_id"])

            if ExchangeController.exchange_overlap(student_schedules, other_student):
                return (ExchangeStatus.CLASSES_OVERLAP, None)
        
            inserted_exchanges.append(DirectExchangeParticipants(
                participant_name=curr_exchange["other_student"],
                participant_nmec=curr_exchange["other_student"],
                old_class=curr_exchange["old_class"], 
                new_class=curr_exchange["new_class"],
                course_unit=course_unit.acronym,
                course_unit_id=curr_exchange["course_unit_id"],
                direct_exchange=exchange_db_model,
                accepted=False
            ))

            inserted_exchanges.append(DirectExchangeParticipants(
                participant_name=auth_user,
                participant_nmec=auth_user,
                old_class=curr_exchange["new_class"], # This is not a typo, the old class of the authenticted student is the new class of the other student
                new_class=curr_exchange["old_class"],
                course_unit=course_unit.acronym,
                course_unit_id=curr_exchange["course_unit_id"],
                direct_exchange=exchange_db_model,
                accepted=False
            ))

        return (ExchangeStatus.SUCCESS, None)

    @staticmethod
    def exchange_overlap(student_schedules, username) -> bool:
        for (key, class_schedule) in student_schedules[username].items():
            for (other_key, other_class_schedule) in student_schedules[username].items():
                print(f"({key}, {other_key})")
                if key == other_key:
                    continue

                (class_schedule_day, class_schedule_start, class_schedule_end) = (class_schedule["dia"], class_schedule["hora_inicio"], class_schedule["aula_duracao"] + class_schedule["hora_inicio"])
                (overlap_param_day, overlap_param_start, overlap_param_end) = (other_class_schedule["dia"], other_class_schedule["hora_inicio"], other_class_schedule["aula_duracao"] + other_class_schedule["hora_inicio"])

                if check_class_schedule_overlap(class_schedule_day, class_schedule_start, class_schedule_end, overlap_param_day, overlap_param_start, overlap_param_end):
                    return True

        return False




