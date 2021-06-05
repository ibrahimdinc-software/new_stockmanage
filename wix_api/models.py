from django.db import models
from marketplace.models import MarketProductModel
# Create your models here.


class WixAuthTokensModel(models.Model):
    refreshToken = models.CharField(verbose_name="Refresh Token", max_length=500)
    authToken = models.CharField(verbose_name="Auth Token", max_length=500)
    time = models.DateTimeField("Token Alma Tarihi", auto_now_add=True)

