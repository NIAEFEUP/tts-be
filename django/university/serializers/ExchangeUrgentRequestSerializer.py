from django.forms.models import model_to_dict
from rest_framework import serializers

from university.models import CourseUnit, ExchangeUrgentRequestOptions

class ExchangeUrgentRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_nmec = serializers.CharField(max_length=32)
    message = serializers.CharField(max_length=2048)
    accepted = serializers.BooleanField()
    options = serializers.SerializerMethodField()

    def get_options(self, obj):
        options = ExchangeUrgentRequestOptions.objects.filter(exchange_urgent_request__id=obj.id)
        return list(map(lambda option: ExchangeUrgentRequestOptionsSerializer(option).data, options))

class ExchangeUrgentRequestOptionsSerializer(serializers.Serializer):
    course_unit = serializers.SerializerMethodField()
    class_user_goes_from = serializers.CharField(max_length=16)
    class_user_goes_to = serializers.CharField(max_length=16)

    def get_course_unit(self, obj):
        course_unit_id = obj.course_unit_id

        try:
            return model_to_dict(CourseUnit.objects.get(pk=course_unit_id))
        except:
            return None
