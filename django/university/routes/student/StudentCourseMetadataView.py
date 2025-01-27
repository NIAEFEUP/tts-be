from django.http.response import JsonResponse
from rest_framework.views import APIView

from university.models import StudentCourseMetadata, Course, CourseUnit
from university.serializers.StudentCourseMetadataSerializer import StudentCourseMetadataSerializer

class StudentCourseMetadataView(APIView):
    def get(self, request, nmec, course_unit_id):
        course_unit = CourseUnit.objects.get(pk=course_unit_id)

        student_course_metadata = list(StudentCourseMetadata.objects.filter(
            nmec = f"{nmec}",
            course__id = course_unit.course.id
        ).all())


        serialized_student_course_metadata = list(map(lambda metadata: StudentCourseMetadataSerializer(metadata).data, student_course_metadata))

        print("WHAT???", serialized_student_course_metadata)

        return JsonResponse(serialized_student_course_metadata, safe=False)