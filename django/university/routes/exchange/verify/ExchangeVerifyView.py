import json
import jwt
import time

from django.core.cache import cache

from django.db import transaction

from django.http import HttpResponse, JsonResponse
from django.views import View
from tts_be.settings import JWT_KEY, VERIFY_EXCHANGE_TOKEN_EXPIRATION_SECONDS

from university.controllers.StudentController import StudentController
from university.controllers.ExchangeValidationController import ExchangeValidationController, ExchangeValidationMetadata
from university.controllers.StudentScheduleController import StudentScheduleController, StudentScheduleMetadata
from university.controllers.SigarraController import SigarraController

from exchange.models import DirectExchange, DirectExchangeParticipants

class ExchangeVerifyView(View):
    def post(self, request, token):
        try:
            exchange_info = jwt.decode(token, JWT_KEY, algorithms=["HS256"], options={"verify_exp": False})

            direct_exchange = DirectExchange.objects.get(id=exchange_info["exchange_id"])

            if not ExchangeValidationController().validate_direct_exchange(exchange_info["exchange_id"]).status:
                ExchangeValidationController().cancel_exchange(direct_exchange)
                return JsonResponse({"verified": False}, safe=False)

            token_seconds_elapsed = time.time() - exchange_info["exp"]
            if token_seconds_elapsed > VERIFY_EXCHANGE_TOKEN_EXPIRATION_SECONDS:
                return JsonResponse({"verified": False, "expired" : True, "exchange_id": exchange_info["exchange_id"]}, safe=False)

            if(
                len(DirectExchangeParticipants.objects.filter(direct_exchange=direct_exchange, participant_nmec=request.user.username, accepted=True)) ==
                len(DirectExchangeParticipants.objects.filter(direct_exchange=direct_exchange, participant_nmec=request.user.username))
            ):
                return JsonResponse({"verified": True}, safe=False)


            participant = DirectExchangeParticipants.objects.filter(participant_nmec=request.user.username)
            participant.update(accepted=True)

            all_participants = DirectExchangeParticipants.objects.filter(direct_exchange__id=exchange_info["exchange_id"])
            participant_nmecs = {participant.participant_nmec for participant in all_participants}

            all_participants_accepted = all(participant.accepted for participant in all_participants)
            if all_participants_accepted:
                exchange_validation_metadata = ExchangeValidationMetadata()
                student_schedule_metadata = StudentScheduleMetadata()

                # Prefetch important information from SIGARRA
                ExchangeValidationController().fetch_conflicting_exchanges_metadata(int(exchange_info["exchange_id"]), metadata=exchange_validation_metadata)
                for participant in all_participants:
                    StudentScheduleController.fetch_student_schedule_metadata(SigarraController(), student_schedule_metadata, participant.participant_nmec)

            with transaction.atomic():
                if all_participants_accepted:
                    # Ensure fetched participants are consistent with current view
                    new_participants = DirectExchangeParticipants.objects.filter(direct_exchange__id=exchange_info["exchange_id"])
                    new_participant_nmecs = {participant.participant_nmec for participant in new_participants}

                    # If participants differ, invalidate direct exchange acceptance
                    if participant_nmecs != new_participant_nmecs:
                        return JsonResponse({"verified": False}, safe=False, status=409)

                    direct_exchange.accepted = True
                    direct_exchange.save()

                    # Change user schedule
                    for participant in all_participants:
                        StudentController.populate_user_course_unit_data(int(participant.participant_nmec), erase_previous=True, metadata=student_schedule_metadata)

                    if direct_exchange.marketplace_exchange:
                        marketplace_exchange = direct_exchange.marketplace_exchange
                        direct_exchange.marketplace_exchange = None
                        direct_exchange.save()
                        marketplace_exchange.delete()

                    ExchangeValidationController().cancel_conflicting_exchanges_prefetched(int(exchange_info["exchange_id"]), metadata=exchange_validation_metadata)

                if cache.get(token) is not None:
                    return JsonResponse({"verified": False}, safe=False, status=403)

                # Blacklist token since this token is usable only once
                cache.set(
                    key=token,
                    value=token,
                    timeout=VERIFY_EXCHANGE_TOKEN_EXPIRATION_SECONDS - token_seconds_elapsed
                )

                return JsonResponse({"verified": True}, safe=False)

        except jwt.ExpiredSignatureError:
                return JsonResponse({"verified": False, "expired" : True}, safe=False)

        except Exception as e:
            print("Error: ", e)
            return HttpResponse(status=500)
