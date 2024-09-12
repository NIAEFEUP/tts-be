import requests

from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from django.db.models import Prefetch

from university.models import Class

class ExchangeCardMetadataView(APIView):
    def get(self, request, course_unit_id):
        """
            Returns the classes and students of a course unit
        """
        try:
            url = f"https://sigarra.up.pt/feup/pt/mob_ucurr_geral.uc_inscritos?pv_ocorrencia_id={course_unit_id}"
            response = requests.get(url, cookies=request.COOKIES)

            if (response.status_code != 200):
                return HttpResponse(status=response.status_code)

            students = response.json()
            new_response = JsonResponse({
                "classes": list(Class.objects.filter(course_unit_id=course_unit_id).all().values()),
                "students": students
            }, safe=False)

            new_response.status_code = response.status_code

            return new_response

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": e}, safe=False)
