from django.db import models
from import_export import resources
from .models import MarketOrderModel

class MarketOrderModelResource(resources.ModelResource):
    class Meta:
        model = MarketOrderModel