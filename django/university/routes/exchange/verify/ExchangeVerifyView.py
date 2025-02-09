import json
import jwt
import time

from django.core.cache import cache

from django.db import transaction

from django.http import HttpResponse, JsonResponse
from django.views import View
from tts_be.settings import JWT_KEY, VERIFY_EXCHANGE_TOKEN_EXPIRATION_SECONDS

from university.controllers.StudentController import StudentController
from university.controllers.ExchangeValidationController import ExchangeValidationController
from university.models import DirectExchange, DirectExchangeParticipants

class ExchangeVerifyView(View):
    def post(self, request, token):
        try:
            exchange_info = jwt.decode(token, JWT_KEY, algorithms=["HS256"])

            direct_exchange = DirectExchange.objects.get(id=exchange_info["exchange_id"])

            if(
                len(DirectExchangeParticipants.objects.filter(direct_exchange=direct_exchange, participant_nmec=request.user.username, accepted=True)) ==
                len(DirectExchangeParticipants.objects.filter(direct_exchange=direct_exchange, participant_nmec=request.user.username))
            ):
                return JsonResponse({"verified": True}, safe=False)

            if not ExchangeValidationController().validate_direct_exchange(exchange_info["exchange_id"]).status:
                ExchangeValidationController().cancel_exchange(direct_exchange)
                return JsonResponse({"verified": False}, safe=False, status=403)
        
            token_seconds_elapsed = time.time() - exchange_info["exp"]
            if token_seconds_elapsed > VERIFY_EXCHANGE_TOKEN_EXPIRATION_SECONDS:
                return JsonResponse({"verified": False}, safe=False, status=400)

            with transaction.atomic():
                participant = DirectExchangeParticipants.objects.filter(participant_nmec=request.user.username)
                participant.update(accepted=True)

                all_participants = DirectExchangeParticipants.objects.filter(direct_exchange__id=exchange_info["exchange_id"])
            
                accepted_participants = 0
                for participant in all_participants:
                    accepted_participants += participant.accepted

                if accepted_participants == len(all_participants):
                    direct_exchange.accepted = True
                    direct_exchange.save()

                    # Change user schedule
                    for participant in all_participants:
                        StudentController.populate_user_course_unit_data(int(participant.participant_nmec), erase_previous=True)

                    if direct_exchange.marketplace_exchange:
                        direct_exchange.marketplace_exchange.delete() 

                    ExchangeValidationController().cancel_conflicting_exchanges(int(exchange_info["exchange_id"]))

                if cache.get(token) is not None:
                    return JsonResponse({"verified": False}, safe=False, status=403)
            
                # Blacklist token since this token is usable only once
                cache.set(
                    key=token,
                    value=token,
                    timeout=VERIFY_EXCHANGE_TOKEN_EXPIRATION_SECONDS - token_seconds_elapsed
                )

                return JsonResponse({"verified": True}, safe=False)

        except Exception as e:
            print("Error: ", e)
            return HttpResponse(status=500)