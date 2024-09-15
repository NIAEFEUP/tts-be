from django.forms.models import model_to_dict
from rest_framework import serializers

from university.models import CourseUnit

class MarketplaceExchangeClassSerializer(serializers.Serializer):
    course_info = serializers.SerializerMethodField()
    class_issuer_goes_from = serializers.CharField(max_length=16)
    class_issuer_goes_to = serializers.CharField(max_length=16)

    def get_course_info(self, obj):
        course_unit_id = obj.course_unit_id

        try:
            return model_to_dict(CourseUnit.objects.get(pk=course_unit_id))
        except:
            return None

