from rest_framework import serializers
from .models import BaseProductModel, ProductModel


class BaseProductModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseProductModel
        fields = "__all__"

class ProductModelSeriailzer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = "__all__"




