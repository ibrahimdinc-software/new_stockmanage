from django.db import models

from marketplace.models import MarketProductModel

# Create your models here.


class CicekProductModel(MarketProductModel):
    listPrice = models.FloatField(verbose_name="Liste Fiyatı")








