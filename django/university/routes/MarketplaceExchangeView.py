from functools import reduce
import json
import requests
from rest_framework.views import APIView
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Prefetch

from university.controllers.ClassController import ClassController
from university.controllers.SigarraController import SigarraController
from university.exchange.utils import ExchangeStatus, build_marketplace_submission_schedule, build_student_schedule_dict, convert_sigarra_schedule, curr_semester_weeks, exchange_overlap, get_student_schedule_url, incorrect_class_error, update_schedule_accepted_exchanges
from university.models import CourseUnit, DirectExchangeParticipants, MarketplaceExchange, MarketplaceExchangeClass
from university.routes.student.schedule.StudentScheduleView import StudentScheduleView
from university.serializers.MarketplaceExchangeClassSerializer import MarketplaceExchangeClassSerializer

class MarketplaceExchangeView(APIView):
    def __init__(self):
        self.filterAction = {
            "mine": self.filterMineExchanges,
            "all": self.filterAllExchanges
        }

    
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


    def filterMineExchanges(self, request, course_unit_name_filter):
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

    def filterAllExchanges(self, request, course_unit_name_filter):
        courseUnitClasses = StudentScheduleView.retrieveCourseUnitClasses(SigarraController(), request.user.username)
        marketplace_exchanges = list(MarketplaceExchange.objects
                .exclude(issuer_nmec=request.user.username).prefetch_related(
                Prefetch(
                    'marketplaceexchangeclass_set',
                    queryset=MarketplaceExchangeClass.objects.filter(
                        reduce(lambda x, y: x | y, [
                            Q(class_issuer_goes_to=k) & Q(course_unit_acronym=v)
                            for k, v in courseUnitClasses.items()
                        ])
                    ),
                    to_attr='options'
                )
            ).all())

        marketplace_exchanges = list(filter(lambda x: len(x.options) > 0, marketplace_exchanges))
        
        if course_unit_name_filter:
            marketplace_exchanges = list(filter(
                lambda x: self.courseUnitNameFilterInExchangeOptions(x.options, course_unit_name_filter),
                marketplace_exchanges
            ))

        return self.build_pagination_payload(request, marketplace_exchanges)
   
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
        requestTypeFilter = request.query_params.get('typeFilter')  

        return JsonResponse(self.filterAction[requestTypeFilter](request, courseUnitNameFilter.split(',') if courseUnitNameFilter else None), safe=False)
        
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
            issuer_name=issuer_name,
            issuer_nmec=user.username, 
            accepted=False
        )
        for exchange in exchanges:
            course_unit_id = int(exchange["courseUnitId"])
            course_unit = CourseUnit.objects.get(pk=course_unit_id)
            MarketplaceExchangeClass.objects.create(
                marketplace_exchange=marketplace_exchange,
                course_unit_acronym=course_unit.acronym,
                course_unit_id=course_unit_id,
                course_unit_name=course_unit.name,
                class_issuer_goes_from=exchange["classNameRequesterGoesFrom"],
                class_issuer_goes_to=exchange["classNameRequesterGoesTo"]
            ) 
