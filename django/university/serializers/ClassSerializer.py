from rest_framework import serializers
from django.db import models

class ClassSerializer(serializers.Serializer):
    name = models.CharField(max_length=255)