from django.db.models import base
from rest_framework import serializers
from .models import BaseProductModel

"""
class BaseProductModelSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    barcode = serializers.IntegerField()
    piece = serializers.IntegerField()

    def create(self, validated_data):
        return BaseProductModel.objects.create(**validated_data)
"""

class BaseProductModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseProductModel
        fields = "__all__"






