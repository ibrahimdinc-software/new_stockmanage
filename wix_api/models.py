from django.db import models
from marketplace.models import MarketOrderDetailModel, MarketProductModel
# Create your models here.


class WixAuthTokensModel(models.Model):
    refreshToken = models.CharField(verbose_name="Refresh Token", max_length=499)
    authToken = models.TextField(verbose_name="Auth Token", max_length=3000)
    time = models.DateTimeField("Token Alma Tarihi", auto_now_add=True)

    def __str__(self):
        return str(self.pk) + ". Wix Auth Token Modeli"

class WixProductModel(MarketProductModel):
    variantId = models.CharField(verbose_name="Varyant ID", max_length=100)


class WixProductUpdateModel(models.Model):
    product = models.ForeignKey(WixProductModel, on_delete=models.CASCADE)
    changeQuantity = models.IntegerField(verbose_name="Değişim Miktarı")
    updated = models.BooleanField(verbose_name="Güncellendi Mi?", default=False)



class WixOrderDetailModel(MarketOrderDetailModel):
    pass
