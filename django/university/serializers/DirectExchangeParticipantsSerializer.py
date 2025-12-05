from django.forms.models import model_to_dict
from rest_framework import serializers

from university.models import CourseUnit
from exchange.models import DirectExchangeParticipants
from university.controllers.ClassController import ClassController

from university.controllers.SigarraController import SigarraController
from university.exchange.utils import convert_sigarra_schedule

class DirectExchangeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    issuer_name = serializers.CharField(max_length=32)
    issuer_nmec = serializers.CharField(max_length=32)
    accepted = serializers.BooleanField()
    admin_state = serializers.CharField(max_length=32)
    date = serializers.DateTimeField()    
    last_validated = serializers.DateTimeField(allow_null=True)
    options = serializers.SerializerMethodField()

    def get_options(self, obj):
        participants = DirectExchangeParticipants.objects.filter(direct_exchange__id=obj.id)

        return list(map(lambda participant: DirectExchangeParticipantsSerializer(participant).data, participants))

class DirectExchangeParticipantsSerializer(serializers.Serializer):
    course_info = serializers.SerializerMethodField()
    participant_name = serializers.CharField(max_length=32)
    participant_nmec = serializers.CharField(max_length=32)
    class_participant_goes_from = serializers.SerializerMethodField()
    class_participant_goes_to = serializers.SerializerMethodField()
    course_unit = serializers.CharField(max_length=64)
    course_unit_id = serializers.CharField(max_length=16)
    accepted = serializers.BooleanField()
    date = serializers.DateTimeField()

    def get_course_info(self, obj):
        course_unit_id = obj.course_unit_id

        try:
            return model_to_dict(CourseUnit.objects.get(pk=course_unit_id))
        except:
            return None


    def get_class_participant_goes_from(self, obj):
        class_issuer_id = obj.class_participant_goes_from
        classes = ClassController.get_classes(obj.course_unit_id, fetch_professors=False)
        filtered_classes = list(filter(lambda x: x['name'] == class_issuer_id, classes))

        try:
            return filtered_classes[0]
        except:
            return None

    def get_class_participant_goes_to(self, obj):
        class_issuer_id = obj.class_participant_goes_to
        classes = ClassController.get_classes(obj.course_unit_id, fetch_professors=False)
        filtered_classes = list(filter(lambda x: x['name'] == class_issuer_id, classes))

        try:
            return filtered_classes[0]
        except:
            return None
