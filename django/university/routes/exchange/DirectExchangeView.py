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


from university.controllers.SigarraController import SigarraController
from university.exchange.utils import ExchangeStatus, build_new_schedules, build_student_schedule_dict, build_student_schedule_dicts, create_direct_exchange_participants, curr_semester_weeks, get_student_schedule_url, incorrect_class_error, update_schedule_accepted_exchanges
from university.models import DirectExchange, MarketplaceExchange, MarketplaceExchangeClass

class DirectExchangeView(View):
    def get(self, request):
        return HttpResponse()

    def post(self, request):
        student_schedules = {}
        
        sigarra_res = SigarraController().get_student_schedule(request.user.username)
        
        if (sigarra_res.status_code != 200):
            return HttpResponse(status=sigarra_res.status_code)

        username = request.user.username
        schedule_data = sigarra_res.data
        
        print("schedule_data: ", schedule_data)
        student_schedules[username] = build_student_schedule_dict(schedule_data)

        exchange_choices = request.POST.getlist('exchangeChoices[]')
        exchanges = list(map(lambda exchange : json.loads(exchange), exchange_choices))

        # Add the other students schedule to the dictionary
        (status, trailing) = build_student_schedule_dicts(student_schedules, exchanges)
        if status == ExchangeStatus.FETCH_SCHEDULE_ERROR:
            return HttpResponse(status=trailing)

        for student in student_schedules.keys():
            student_schedule = list(student_schedules[student].values())
            update_schedule_accepted_exchanges(student, student_schedule)
            student_schedules[student] = build_student_schedule_dict(student_schedule)

        exchange_model = DirectExchange(accepted=False, issuer=request.user.username)

        (status, trailing) = build_new_schedules(
            student_schedules, exchanges, request.user.username)
        
        if status == ExchangeStatus.STUDENTS_NOT_ENROLLED:
            return JsonResponse({"error": incorrect_class_error()}, status=400, safe=False)
    
        inserted_exchanges = []
        (status, trailing) = create_direct_exchange_participants(student_schedules, exchanges, inserted_exchanges, exchange_model, request.user.username)
        
        if status == ExchangeStatus.CLASSES_OVERLAP:    
            return JsonResponse({"error": "classes-overlap"}, status=400, safe=False)

        exchange_model.save()
    
        tokens_to_generate = {}
        for inserted_exchange in inserted_exchanges:
            participant = inserted_exchange.participant;
            if not(participant in tokens_to_generate):
                token = jwt.encode({"username": participant, "exchange_id": exchange_model.id, "exp": (datetime.datetime.now() + datetime.timedelta(seconds=VERIFY_EXCHANGE_TOKEN_EXPIRATION_SECONDS)).timestamp()}, JWT_KEY, algorithm="HS256")
                tokens_to_generate[participant] = token
                html_message = render_to_string('confirm_exchange.html', {'confirm_link': f"{DOMAIN}tts/verify_direct_exchange/{token}"})
                send_mail(
                    'Confirmação de troca',
                    strip_tags(html_message),
                    'tts@exchange.com',
                    [f'up{participant}@up.pt']
                )

            inserted_exchange.save()
    
        return JsonResponse({"success": True}, safe=False)

