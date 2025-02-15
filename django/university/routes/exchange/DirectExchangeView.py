import json
import base64
import jwt
import datetime
import hashlib
import os

from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.template.loader import render_to_string
from tts_be.settings import JWT_KEY, VERIFY_EXCHANGE_TOKEN_EXPIRATION_SECONDS, DOMAIN

from university.controllers.CourseUnitController import CourseUnitController
from university.controllers.AdminRequestFiltersController import AdminRequestFiltersController
from university.controllers.ExchangeController import ExchangeController
from university.controllers.SigarraController import SigarraController
from university.models import DirectExchange, DirectExchangeParticipants, DirectExchangeParticipants, ExchangeAdmin, MarketplaceExchange, MarketplaceExchangeClass
from university.serializers.DirectExchangeParticipantsSerializer import DirectExchangeSerializer
from university.controllers.ExchangeValidationController import ExchangeValidationController
from university.controllers.StudentController import StudentController
from university.exchange.utils import ExchangeStatus, build_new_schedules, build_student_schedule_dict, build_student_schedule_dicts, incorrect_class_error 

class DirectExchangeView(View):
    def __init__(self):
        self.filter_actions = {
            "activeCourse": self.filter_active_course,
            "activeCurricularYear": self.filter_active_curricular_year,
            "activeStates": self.filter_active_state
        }

    def filter_active_course(self, exchanges, major_id):
        return list(
            filter(
                lambda exchange: len(list(
                    filter(
                        lambda course_unit: int(CourseUnitController.course_unit_major(course_unit.get("course_info").get("id"))) == int(major_id), exchange.get("options"))
                    )) > 0,
                exchanges
            )
        )

    def filter_active_curricular_year(self, exchanges, curricular_year):
        return list(
            filter(
                lambda exchange: len(list(
                    filter(
                        lambda course_unit: int(CourseUnitController.course_unit_curricular_year(course_unit.get("course_info").get("id"))) == int(curricular_year), exchange.get("options"))
                    )) > 0,
                exchanges
            )
        )

    def filter_active_state(self, exchanges, state):
        states = state.split(",")
        return list(
            filter(
                lambda exchange: exchange.admin_state in states,
                exchanges
            )
        )

    """
        Returns every direct exchange
    """
    def get(self, request):
        # 1. Validate if admin
        is_admin = ExchangeAdmin.objects.filter(username=request.user.username).exists()
        if not(is_admin):
            return HttpResponse(status=403) 

        direct_exchanges = DirectExchange.objects.filter(accepted=True).order_by('date')

        for filter in AdminRequestFiltersController.filter_values():
            if request.GET.get(filter):
                direct_exchanges = self.filter_actions[filter](direct_exchanges, request.GET.get(filter))

        paginator = Paginator(direct_exchanges, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number if page_number != None else 1)
        direct_exchanges = [x for x in page_obj]

        direct_exchanges = DirectExchangeSerializer(direct_exchanges, many=True).data
        
        return JsonResponse({
            "exchanges": direct_exchanges,
            "total_pages": paginator.num_pages
        }
        , safe=False)

    def post(self, request):
        student_schedules = {}
        
        sigarra_res = SigarraController().get_student_schedule(request.user.username)
        
        if (sigarra_res.status_code != 200):
            return HttpResponse(status=sigarra_res.status_code)

        username = request.user.username
        schedule_data = sigarra_res.data
        
        student_schedules[username] = build_student_schedule_dict(schedule_data)

        exchange_choices = request.POST.getlist('exchangeChoices[]')
        exchanges = list(map(lambda exchange : json.loads(exchange), exchange_choices))

        marketplace_id = exchanges[0].get("marketplace_id", None)

        # Add the other students schedule to the dictionary
        (status, trailing) = build_student_schedule_dicts(student_schedules, exchanges)
        if status == ExchangeStatus.FETCH_SCHEDULE_ERROR:
            return HttpResponse(status=trailing)
        # Update student schedule with exchange updates that are not in sigarra currently
        for student in student_schedules.keys():
            student_schedule = list(student_schedules[student].values())
            ExchangeController.update_schedule_accepted_exchanges(student, student_schedule)
            student_schedules[student] = build_student_schedule_dict(student_schedule)

        # Restricts repeated exchange requests
        exchange_data_str = json.dumps(exchanges, sort_keys=True)
        exchange_hash = hashlib.sha256(exchange_data_str.encode('utf-8')).hexdigest()

        # if DirectExchange.objects.filter(hash=exchange_hash).exists():
        #     return JsonResponse({"error": "duplicate-request"}, status=400, safe=False)

        with transaction.atomic():
            exchange_model = DirectExchange(
                accepted=False, 
                issuer_name=f"{request.user.first_name} {request.user.last_name}", 
                issuer_nmec=request.user.username,
                date=timezone.now(),
                admin_state="untreated",
                canceled=False,
                hash=exchange_hash,
                marketplace_exchange=None if not marketplace_id else MarketplaceExchange.objects.get(id=marketplace_id)
            )

            inserted_exchanges = []
            ExchangeController.create_direct_exchange_participants(
                student_schedules, exchanges, inserted_exchanges, exchange_model, request.user
            )

            # Change the schedules to the final result of the exchange so it is easier to detect overlaps
            (status, trailing) = build_new_schedules(
                student_schedules, exchanges, request.user.username)
            
            if status == ExchangeStatus.STUDENTS_NOT_ENROLLED:
                return JsonResponse({"error": incorrect_class_error()}, status=400, safe=False)

            for username in student_schedules.keys():
                if ExchangeController.exchange_overlap(student_schedules, username):
                    return JsonResponse({"error": "classes-overlap"}, status=400, safe=False)

            exchange_model.save()
        
            tokens_to_generate = {}
            for inserted_exchange in inserted_exchanges:
                inserted_exchange.save()
    
        for inserted_exchange in inserted_exchanges:
            participant = inserted_exchange.participant_nmec
      
            # A participant may appear multiple times since there is one line in the table for each course unit inside of the exhange
            if participant not in tokens_to_generate.keys():
                token = jwt.encode({"username": participant, "exchange_id": exchange_model.id, "exp": (datetime.datetime.now() + datetime.timedelta(seconds=VERIFY_EXCHANGE_TOKEN_EXPIRATION_SECONDS)).timestamp()}, JWT_KEY, algorithm="HS256")
                tokens_to_generate[participant] = token
        participants = set([(inserted_exchange.participant_nmec, inserted_exchange.participant_name) for inserted_exchange in inserted_exchanges ])

        for (participant_num,participant_name) in participants:
            
            filtered_exchanges = [inserted_exchange for inserted_exchange in inserted_exchanges if inserted_exchange.participant_nmec == participant_num]

            base64_token = base64.b64encode(tokens_to_generate[participant_num].encode('utf-8')).decode('utf-8')
            html_message = render_to_string('confirm_exchange.html', {'confirm_link': f"{DOMAIN}/exchange/verify/{base64_token}", 'exchanges': filtered_exchanges})
            try:
                send_mail(
                    'Confirmação de troca',
                    strip_tags(html_message),
                    os.getenv('SENDER_EMAIL_ADDRESS'),
                    [f'up{participant_num}@up.pt']
                )
            except Exception as e:
                print("Error: ", e)
        
        return JsonResponse({"success": True}, safe=False)

    def put(self, request, id):
        # Validate if exchange is still valid
        if not ExchangeValidationController().validate_direct_exchange(id).status:
            ExchangeValidationController().cancel_exchange(DirectExchange.objects.get(id=id))
            return JsonResponse({"error": ExchangeValidationController().validate_direct_exchange(id).message}, status=400, safe=False)

        exchange = DirectExchange.objects.get(id=id)

        try: 
            with transaction.atomic():
                # Update exchange accepted states
                participants = DirectExchangeParticipants.objects.filter(direct_exchange=exchange)
                for participant in participants:
                    if participant.participant_nmec == request.user.username:
                        participant.accepted = True
                        participant.save()

                if all(participant.accepted for participant in participants):
                    exchange.accepted = True
                    exchange.save()

                    for participant in participants:
                        StudentController.populate_user_course_unit_data(int(participant.participant_nmec), erase_previous=True)

                    if exchange.marketplace_exchange:
                        marketplace_exchange = exchange.marketplace_exchange
                        exchange.marketplace_exchange = None
                        exchange.save()
                        marketplace_exchange.delete()

                    ExchangeValidationController().cancel_conflicting_exchanges(int(exchange.id))

                return JsonResponse({"success": True}, safe=False)
        except Exception as e:
            print("ERROR: ", e)
            return JsonResponse({"success": False}, status=400, safe=False)
