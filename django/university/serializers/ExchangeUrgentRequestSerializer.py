from django.forms.models import model_to_dict
from rest_framework import serializers

from university.models import CourseUnit

class ExchangeUrgentRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_nmec = serializers.CharField(max_length=32)
    course_unit = serializers.SerializerMethodField()
    class_user_goes_from = serializers.CharField(max_length=16)
    class_user_goes_to = serializers.CharField(max_length=16)
    message = serializers.CharField(max_length=2048)
    accepted = serializers.BooleanField()
    
    def get_course_unit(self, obj):
        course_unit_id = obj.course_unit_id

        try:
            return model_to_dict(CourseUnit.objects.get(pk=course_unit_id))
        except:
            return None
