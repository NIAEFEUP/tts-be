from rest_framework import serializers

class MarketplaceExchangeClassSerializer(serializers.Serializer):
    course_unit_name = serializers.CharField(max_length=200)
    course_unit_acronym = serializers.CharField(max_length=256)
    course_unit_id = serializers.CharField(max_length=256)
    class_issuer_goes_from = serializers.CharField(max_length=16)
    class_issuer_goes_to = serializers.CharField(max_length=16)
