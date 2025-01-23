from rest_framework import serializers

class ClassSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=31)
    last_updated = serializers.DateTimeField()