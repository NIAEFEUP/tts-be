from rest_framework import serializers
from django.db import models

class ClassSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=31)
    last_updated = serializers.DateTimeField()