import base64
import json
from rest_framework.views import APIView
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Prefetch

from university.controllers.ClassController import ClassController
from university.controllers.ExchangeController import ExchangeController
from university.controllers.SigarraController import SigarraController
from university.exchange.utils import ExchangeStatus, build_marketplace_submission_schedule, build_student_schedule_dict, convert_sigarra_schedule, curr_semester_weeks, exchange_overlap, get_student_schedule_url, incorrect_class_error, update_schedule_accepted_exchanges
from university.models import CourseUnit, DirectExchangeParticipants, MarketplaceExchange, MarketplaceExchangeClass
from university.routes.student.schedule.StudentScheduleView import StudentScheduleView
from university.serializers.MarketplaceExchangeClassSerializer import MarketplaceExchangeClassSerializer

class MarketplaceExchangeView(APIView):
    def build_pagination_payload(self, request, exchanges):
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
                "type": "marketplaceexchange",
                "issuer_name": exchange.issuer_name,
                "issuer_nmec": exchange.issuer_nmec,
                "options": [
                    MarketplaceExchangeClassSerializer(exchange_class).data for exchange_class in exchange.options
                ],
                "classes": list(self.getExchangeOptionClasses(exchange.options)),
                "date":  exchange.date,
                "accepted": exchange.accepted
            } for exchange in page_obj]
        }


    def filterMineExchanges(self, request, course_unit_name_filter, classes_filter):
        marketplace_exchanges = list(MarketplaceExchange.objects.prefetch_related(
                Prefetch(
                    'marketplaceexchangeclass_set',
                    queryset=MarketplaceExchangeClass.objects.all(),
                    to_attr='options'
                )
            ).filter(issuer_nmec=request.user.username).all())

        if course_unit_name_filter:
            marketplace_exchanges = list(filter(
                lambda x: self.courseUnitNameFilterInExchangeOptions(x.options, course_unit_name_filter),
                marketplace_exchanges
            ))

        return self.build_pagination_payload(request, marketplace_exchanges)

    def filterAllExchanges(self, request, course_unit_name_filter, classes_filter):
        print("classes filter: ", classes_filter)
        marketplace_exchanges = list(MarketplaceExchange.objects
                .exclude(issuer_nmec=request.user.username).all())

        marketplace_exchanges = self.advanced_classes_filter(marketplace_exchanges, classes_filter)
        
        if course_unit_name_filter:
            marketplace_exchanges = list(filter(
                lambda x: self.courseUnitNameFilterInExchangeOptions(x.options, course_unit_name_filter),
                marketplace_exchanges
            ))

        return self.build_pagination_payload(request, marketplace_exchanges)

    def advanced_classes_filter(self, marketplace_exchanges, classes_filter):
        filtered_marketplace_exchanges = []
        for exchange in marketplace_exchanges:
            exchange_tainted = False
            for option in exchange.options:
                if option.course_unit_acronym in classes_filter.keys():
                    correct_class_included = option.class_issuer_goes_from in classes_filter[option.course_unit_acronym]
                    exchange_tainted = not correct_class_included

            if not exchange_tainted:
                filtered_marketplace_exchanges.append(exchange)

        return filtered_marketplace_exchanges

    def courseUnitNameFilterInExchangeOptions(self, options, courseUnitNameFilter):
        matches = []
        for courseUnitId in courseUnitNameFilter:
            for option in options:
                if courseUnitId == option.course_unit_id:
                    matches.append(1)

        return len(matches) == len(courseUnitNameFilter)
   

    """
        Returns all the current marketplace exchange requests paginated
    """
    def get(self, request):
        courseUnitNameFilter = request.query_params.get('courseUnitNameFilter', None)
        classesFilter = self.parseClassesFilter(request.query_params.get('classesFilter', None))
    
        return JsonResponse(self.filterAllExchanges(request, courseUnitNameFilter.split(',') if courseUnitNameFilter else None, classesFilter), safe=False)

    def parseClassesFilter(self, classesFilter: str) -> dict:
        if not classesFilter:
            return {}

        b64_decoded = base64.b64decode(classesFilter)
        string = b64_decoded.decode('utf-8')
        return dict(json.loads(string))

    def post(self, request):
        return self.submit_marketplace_exchange_request(request)

    def getExchangeOptionClasses(self, options):
        classes = sum(list(map(lambda option: ClassController.get_classes(option.course_unit_id), options)), [])
        return filter(lambda currentClass: any(currentClass["name"] == option.class_issuer_goes_from for option in options), classes)

    def submit_marketplace_exchange_request(self, request):
        exchanges = request.POST.getlist('exchangeChoices[]')
        exchanges = list(map(lambda exchange : json.loads(exchange), exchanges))

        print("Marketplace exchange: ", exchanges)
        curr_student = request.user.username
        sigarra_res = SigarraController().get_student_schedule(curr_student)
        
        if(sigarra_res.status_code != 200):
            return HttpResponse(status=sigarra_res.status_code)
    
        student_schedules = {}
        student_schedules[curr_student] = build_student_schedule_dict(sigarra_res.data)
    
        student_schedule = list(student_schedules[curr_student].values())
        update_schedule_accepted_exchanges(curr_student, student_schedule)
        student_schedules[curr_student] = build_student_schedule_dict(student_schedule)

        (status, new_marketplace_schedule) = build_marketplace_submission_schedule(student_schedules, exchanges, curr_student)
        print("Student schedules: ", student_schedules[curr_student])
        if status == ExchangeStatus.STUDENTS_NOT_ENROLLED:
            return JsonResponse({"error": incorrect_class_error()}, status=400, safe=False)

        if exchange_overlap(student_schedules, curr_student):
            return JsonResponse({"error": "classes-overlap"}, status=400, safe=False)

        self.insert_marketplace_exchange(exchanges, request.user)
    
        return JsonResponse({"success": True}, safe=False)

    def insert_marketplace_exchange(self, exchanges, user):
        issuer_name = f"{user.first_name} {user.last_name.split(' ')[-1]}"
        marketplace_exchange = MarketplaceExchange.objects.create(
            id=MarketplaceExchange.objects.latest("id").id + 1,
            issuer_name=issuer_name,
            issuer_nmec=user.username, 
            accepted=False
        )
        for exchange in exchanges:
            course_unit_id = int(exchange["courseUnitId"])
            course_unit = CourseUnit.objects.get(pk=course_unit_id)
            MarketplaceExchangeClass.objects.create(
                id=MarketplaceExchangeClass.objects.latest("id").id + 1,
                marketplace_exchange=marketplace_exchange,
                course_unit_acronym=course_unit.acronym,
                course_unit_id=course_unit_id,
                course_unit_name=course_unit.name,
                class_issuer_goes_from=exchange["classNameRequesterGoesFrom"],
                class_issuer_goes_to=exchange["classNameRequesterGoesTo"]
            ) 
