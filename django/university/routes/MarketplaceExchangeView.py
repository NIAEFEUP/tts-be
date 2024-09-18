import json
from rest_framework.views import APIView
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.db.models import Prefetch

from university.controllers.ClassController import ClassController
from university.exchange.utils import curr_semester_weeks
from university.models import MarketplaceExchange, MarketplaceExchangeClass
from university.serializers.MarketplaceExchangeClassSerializer import MarketplaceExchangeClassSerializer

class MarketplaceExchangeView(APIView):
    def courseUnitNameFilterInExchangeOptions(self, options, courseUnitNameFilter):
        for courseUnitId in courseUnitNameFilter:
            for option in options:
                if courseUnitId == option.course_unit_id:
                    return True

        return False

    """
        Returns all the current marketplace exchange requests paginated
    """
    def get(self, request):
        courseUnitNameFilter = request.query_params.get('courseUnitNameFilter', None)
        requestTypeFilter = request.query_params.get('typeFilter')  
            
        marketplace_exchanges = []
        if requestTypeFilter and requestTypeFilter == 'received':
            pass
        else:
            marketplace_exchanges = list(MarketplaceExchange.objects.prefetch_related(
                Prefetch(
                    'marketplaceexchangeclass_set',
                    queryset=MarketplaceExchangeClass.objects.all(),
                    to_attr='options'
                )
            ).all())

            if requestTypeFilter and requestTypeFilter == 'mine':
                marketplace_exchanges = list(filter(
                    lambda x: x.issuer_nmec == 202108880,
                    marketplace_exchanges
                ))

        if courseUnitNameFilter:
            marketplace_exchanges = list(filter(
                lambda x: self.courseUnitNameFilterInExchangeOptions(x.options, courseUnitNameFilter), 
                marketplace_exchanges
            ))

        page_number = request.GET.get("page")
        paginator = Paginator(marketplace_exchanges, 10)
        page_obj = paginator.get_page(page_number if page_number != None else 1)
        
        payload = {
            "page": {
                "current": page_obj.number,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
            "data": [
                {
                    "id": exchange.id,
                    "issuer_name": exchange.issuer_name,
                    "issuer_nmec": exchange.issuer_nmec,
                    "options": [
                        MarketplaceExchangeClassSerializer(exchange_class).data for exchange_class in exchange.options
                    ],
                    "classes": list(self.getExchangeOptionClasses(exchange.options)),
                    "date":  exchange.date
                } for exchange in page_obj
            ]
        }

        return JsonResponse(payload)

    def post(self, request):
        print("request: ", request)
        
        return HttpResponse()

    def getExchangeOptionClasses(self, options):
        classes = sum(list(map(lambda option: ClassController.get_classes(option.course_unit_id), options)), [])
        return filter(lambda currentClass: any(currentClass["name"] == option.class_issuer_goes_from for option in options), classes)

    def submit_marketplace_exchange_request(request):
        exchanges = request.POST.getlist('exchangeChoices[]')
        exchanges = list(map(lambda exchange : json.loads(exchange), exchanges))

        print("Marketplace exchange: ", exchanges)

        (semana_ini, semana_fim) = curr_semester_weeks()
        curr_student = request.session["username"]

        curr_student_schedule = requests.get(get_student_schedule_url(
            request.session["username"], # type: ignore
            semana_ini,
            semana_fim
        ), cookies=request.COOKIES)

        if(curr_student_schedule.status_code != 200):
            return HttpResponse(status=curr_student_schedule.status_code)
    
        student_schedules = {}
        student_schedules[curr_student] = build_student_schedule_dict(json.loads(curr_student_schedule.content)["horario"])
    
        student_schedule = list(student_schedules[curr_student].values())
        update_schedule_accepted_exchanges(curr_student, student_schedule, request.COOKIES)
        student_schedules[curr_student] = build_student_schedule_dict(student_schedule)

        (status, new_marketplace_schedule) = build_marketplace_submission_schedule(student_schedules, exchanges, request.COOKIES, curr_student)
        print("Student schedules: ", student_schedules[curr_student])
        if status == ExchangeStatus.STUDENTS_NOT_ENROLLED:
            return JsonResponse({"error": incorrect_class_error()}, status=400, safe=False)

        if exchange_overlap(student_schedules, curr_student):
            return JsonResponse({"error": "classes-overlap"}, status=400, safe=False)
    
        # create_marketplace_exchange_on_db(exchanges, curr_student)
    
        return JsonResponse({"success": True}, safe=False)

    def marketplace_exchange(request):
        exchanges = MarketplaceExchange.objects.all()

        exchanges_json = json.loads(serializers.serialize('json', exchanges))

        exchanges_map = dict()
        for exchange in exchanges_json:
            exchange_id = exchange['pk']  
            exchange_fields = exchange['fields']  

            student = get_student_data(exchange_fields["issuer"], request.COOKIES)

            if(student.json()["codigo"] == request.session["username"]):
                continue

            if exchange_id and exchanges_map.get(exchange_id):
                exchanges_map[exchange_id]['class_exchanges'].append(exchange_fields)
            elif exchange_id:
                exchanges_map[exchange_id] = {
                    'id' : exchange_id,
                    'issuer' :  student.json(),
                    'accepted' : exchange_fields.get('accepted'),
                    'date' : exchange_fields.get('date'),
                    'class_exchanges' : []
                }

        for exchange_id, exchange in exchanges_map.items():
            class_exchanges = MarketplaceExchangeClass.objects.filter(marketplace_exchange=exchange_id)
        
            for class_exchange in class_exchanges:
                course_unit = course_unit_by_id(class_exchange.course_unit_id)
                print("current class exchange is: ", class_exchange)
                exchange['class_exchanges'].append({
                    'course_unit' : course_unit.name,
                    'course_unit_id': class_exchange.course_unit_id,
                    'course_unit_acronym': course_unit.acronym,
                    'old_class' : class_exchange.old_class,
                    'new_class' : class_exchange.new_class,
                })

        return JsonResponse(list(exchanges_map.values()), safe=False)