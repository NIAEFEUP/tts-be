from django.forms.models import model_to_dict
from rest_framework import serializers

from university.models import CourseUnitEnrollmentOptions, CourseUnit
from university.controllers.ClassController import ClassController
from university.controllers.SigarraController import SigarraController
from university.exchange.utils import convert_sigarra_schedule

class CourseUnitEnrollmentsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_nmec = serializers.CharField(max_length=32)
    accepted = serializers.BooleanField()
    options = serializers.SerializerMethodField()
    schedule = serializers.SerializerMethodField()

    def get_schedule(self, obj):
        return convert_sigarra_schedule(SigarraController().get_student_schedule(obj.user_nmec).data)

    def get_options(self, obj):
        options = CourseUnitEnrollmentOptions.objects.filter(course_unit_enrollment__id=obj.id)
        return list(map(lambda option: CourseUnitEnrollmentOptionsSerializer(option).data, options))

class CourseUnitEnrollmentOptionsSerializer(serializers.Serializer):
    course_unit = serializers.SerializerMethodField()
    class_user_goes_to = serializers.SerializerMethodField()

    def get_course_unit(self, obj):
        course_unit_id = obj.course_unit.id

        try:
            return model_to_dict(CourseUnit.objects.get(pk=course_unit_id))
        except:
            return None

    def get_class_user_goes_to(self, obj):
        class_issuer_id = obj.class_field.name
        classes = ClassController.get_classes(obj.course_unit.id)
        filtered_classes = list(filter(lambda x: x['name'] == class_issuer_id, classes))

        try:
            return filtered_classes[0]
        except: 
            return None