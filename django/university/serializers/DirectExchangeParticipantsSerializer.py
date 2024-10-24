from django.forms.models import model_to_dict
from rest_framework import serializers

from university.models import CourseUnit
from university.controllers.ClassController import ClassController

class DirectExchangeParticipantsSerializer(serializers.Serializer):
    participant_name = serializers.CharField(max_length=32)
    participant_nmec = serializers.CharField(max_length=32)
    old_class = serializers.CharField(max_length=16)
    new_class = serializers.CharField(max_length=16)
    course_unit = serializers.CharField(max_length=64)
    course_unit_id = serializers.CharField(max_length=16)
    accepted = serializers.BooleanField()
    date = serializers.DateTimeField()
