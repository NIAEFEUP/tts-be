from rest_framework import serializers
from django.db import models

class StudentCourseMetadataSerializer(serializers.Serializer):
    nmec = serializers.CharField(max_length=255)
    fest_id = serializers.IntegerField()