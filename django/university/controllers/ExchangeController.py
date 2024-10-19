from university.models import ExchangeExpirations
from django.utils import timezone


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


