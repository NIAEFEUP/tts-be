from rest_framework import serializers

from university.serializers.CourseSerializer import CourseSerializer

class StudentCourseMetadataSerializer(serializers.Serializer):
    nmec = serializers.CharField(max_length=255)
    fest_id = serializers.IntegerField()
    course = serializers.SerializerMethodField()

    def get_course(self, obj):
        return CourseSerializer(obj.course).data