from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.views import View

from university.controllers.AdminExchangeStateChangeController import AdminExchangeStateChangeController
from university.models import Class

from exchange.models import DirectExchange, DirectExchangeParticipants, ExchangeUrgentRequests, CourseUnitEnrollments, UserCourseUnits, ExchangeUrgentRequestOptions


class TargetClassNotFound(Exception):
    """Raised when the class a student should be moved to does not exist in the DB."""

    def __init__(self, course_unit_id, class_name):
        super().__init__(f"Class {class_name!r} not found for course unit {course_unit_id}")
        self.course_unit_id = course_unit_id
        self.class_name = class_name


class AdminExchangeRequestAcceptView(View):
    def put(self, request, request_type, id):
        # All-or-nothing: the request may only be marked as "treated"/accepted if the
        # students' classes were actually updated too.
        try:
            with transaction.atomic():
                AdminExchangeStateChangeController().update_state_to(request_type, id, "treated")

                if request_type == "direct_exchange":
                    self.accept_direct_exchange(id)
                elif request_type == "urgent_exchange":
                    self.accept_urgent_exchange(id)
                elif request_type == "enrollment":
                    CourseUnitEnrollments.objects.filter(id=id).update(accepted=True)
        except ExchangeUrgentRequests.DoesNotExist:
            return JsonResponse({"error": "request-not-found"}, status=404)
        except TargetClassNotFound as e:
            return JsonResponse({
                "error": "class-not-found",
                "course_unit_id": str(e.course_unit_id),
                "class_name": e.class_name,
            }, status=400)

        return HttpResponse(status=200)

    def accept_direct_exchange(self, id):
        DirectExchange.objects.filter(id=id).update(accepted=True, canceled=False)

        direct_exchange_participants = DirectExchangeParticipants.objects.filter(direct_exchange_id=id)
        for participant in direct_exchange_participants:
            class_ = Class.objects.filter(name=participant.class_participant_goes_to, course_unit__id=participant.course_unit_id).first()
            if class_ is None:
                raise TargetClassNotFound(participant.course_unit_id, participant.class_participant_goes_to)

            UserCourseUnits.objects.filter(user_nmec=participant.participant_nmec, course_unit__id=participant.course_unit_id).update(class_field=class_)

    def accept_urgent_exchange(self, id):
        exchange_urgent_request = ExchangeUrgentRequests.objects.get(id=id)
        exchange_urgent_request.accepted = True
        exchange_urgent_request.save(update_fields=["accepted"])

        exchange_urgent_request_options = ExchangeUrgentRequestOptions.objects.filter(exchange_urgent_request__id=id)
        for option in exchange_urgent_request_options:
            # Resolve the class the same way ExchangeUrgentRequestOptionsSerializer does when
            # showing the request to the admin (composed names like "1LEIC01+1LEIC02" map to
            # "1LEIC01"), so the admin accepts exactly what they were shown.
            class_ = Class.from_course_unit(option.course_unit_id, option.class_issuer_goes_to)
            if class_ is None:
                raise TargetClassNotFound(option.course_unit_id, option.class_issuer_goes_to)

            UserCourseUnits.objects.filter(user_nmec=exchange_urgent_request.issuer_nmec, course_unit__id=option.course_unit_id).update(class_field=class_)
