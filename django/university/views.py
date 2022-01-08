from django.http.response import HttpResponse
from university.models import Faculty
from university.models import Course
from django.http import JsonResponse
from django.core import serializers
from rest_framework.decorators import api_view
import json
# Create your views here. 

@api_view(['GET'])
def faculty(request): 
    json_data = serializers.serialize('json', Faculty.objects.all())
    return HttpResponse(json_data, content_type="application/json")

@api_view(['GET'])
def course(request):
    json_data = serializers.serialize('json', Course.objects.all())
    return HttpResponse(json_data, content_type="application/json")
