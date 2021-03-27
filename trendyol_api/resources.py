from import_export import resources
from .models import TrendOrderModel

class TrendOrderModelResource(resources.ModelResource):
    class Meta:
        model=TrendOrderModel