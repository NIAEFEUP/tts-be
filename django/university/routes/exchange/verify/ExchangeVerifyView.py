import json
import jwt
import requests
import datetime

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.template.loader import render_to_string
from tts_be.settings import JWT_KEY, VERIFY_EXCHANGE_TOKEN_EXPIRATION_SECONDS, DOMAIN

from university.controllers.StudentController import StudentController
from university.controllers.ExchangeController import ExchangeController
from university.controllers.SigarraController import SigarraController
from university.exchange.utils import ExchangeStatus, build_new_schedules, build_student_schedule_dict, build_student_schedule_dicts, curr_semester_weeks, get_student_schedule_url, incorrect_class_error, update_schedule_accepted_exchanges
from university.models import DirectExchange, MarketplaceExchange, MarketplaceExchangeClass, DirectExchangeParticipants

class ExchangeVerifyView(View):
    def post(self, response):
        try:
            exchange_info = jwt.decode(token, JWT_KEY, algorithms=["HS256"])
        
            token_seconds_elapsed = time.time() - exchange_info["exp"]
            if token_seconds_elapsed > VERIFY_EXCHANGE_TOKEN_EXPIRATION_SECONDS:
                return JsonResponse({"verified": False}, safe=False, status=403)

            participant = DirectExchangeParticipants.objects.filter(participant=request.session["username"])
            participant.update(accepted=True)

            all_participants = DirectExchangeParticipants.objects.filter(direct_exchange_id=exchange_info["exchange_id"])
        
            accepted_participants = 0
            for participant in all_participants:
                accepted_participants += participant.accepted

            if accepted_participants == len(all_participants):
                direct_exchange = DirectExchange.objects.filter(id=int(exchange_info["exchange_id"]))
                direct_exchange.update(accepted=True)

                marketplace_exchange = direct_exchange.first().marketplace_exchange

                if(marketplace_exchange != None):
                    direct_exchange_object = direct_exchange.first()
                    direct_exchange_object.marketplace_exchange = None
                    direct_exchange_object.save()
                    marketplace_exchange.delete()

                for participant in all_participants:
                    StudentController.populate_user_course_unit_data(int(participant.participant_nmec), erase_previous=True)

            if cache.get(token) != None:
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