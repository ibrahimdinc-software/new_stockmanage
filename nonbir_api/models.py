from django.db import models
from ckeditor.fields import RichTextField

from marketplace.models import MarketOrderModel, MarketProductModel

# Create your models here.

PRODUCT_CONDITION = [
    ('1','Yeni',),
    ('2','2. El',),
]

CURRENCY_TYPE = [
    ('1','TL',),
    ('2','USD',),
    ('3','EUR',),
]

NORDER_STATUS = {
    "1": "New",
    "2": "Approved",
    "3": "Rejected",
    "4": "Shipped",
    "5": "Delivered",
    "6": "Completed",
    "7": "Claimed",
    "8": "LATE_SHIPMENT"
}

class NProductModel(MarketProductModel):

    def getShipmentTemplate():
        from .n_api import ShipmentApi
        shipmentTemplates = ShipmentApi().getShipmentTemplateAPI()

        if type(shipmentTemplates) == list:
            return ((i,i,) for i in shipmentTemplates)
        else:
            return(('ERROR', 'ERROR',),)
    
    displayPrice = models.FloatField(verbose_name="Fatura Fiyatı")
    subtitle = models.CharField(verbose_name="Alt Başlık", max_length=65)
    description = RichTextField(verbose_name="Açıklama", max_length=2500)
    category = models.BigIntegerField(verbose_name="Kategori ID")
    brand = models.CharField(verbose_name="Marka", max_length=255)
    currencyType = models.CharField(verbose_name="Para Birimi", max_length=255, choices=CURRENCY_TYPE)
    productCondition = models.CharField(verbose_name="Ürün Durumu", max_length=255, choices=PRODUCT_CONDITION)
    preparingDay = models.IntegerField(verbose_name="Ürün Hazırlanma Süresi(Gün)")
    shipmentTemplate = models.CharField(verbose_name="Teslimat Şablon Adı", max_length=255, choices=getShipmentTemplate())
    n11CatalogId = models.CharField(verbose_name="N11 Katalog Id", max_length=255, blank=True, null=True)
    
    def __str__(self):
        return str(self.productName)

class NProductImageModel(models.Model):
    nProductModel = models.ForeignKey(NProductModel, on_delete=models.CASCADE)
    imageUrl = models.CharField(verbose_name="Resim Linki", max_length=255, blank=True, null=True)
    image = models.ImageField(verbose_name="Ürün Resmi", blank=True, null=True)
    order = models.IntegerField(verbose_name="Gösterme Sırası")

    def save(self, *args, **kwargs):
       if self.image:
           self.imageUrl = "dev.petifest.com" + self.image.url
       super(NProductImageModel, self).save(*args, **kwargs) # Call the real save() method


class NProductDiscountModel(models.Model):
    npm = models.ForeignKey(NProductModel, verbose_name="N11 Ürünü", on_delete=models.CASCADE)
    type = models.CharField(verbose_name="İndirim Türü", max_length=25)
    value = models.FloatField(verbose_name="İndirim Miktarı")


class NUpdateQueueModel(models.Model):
    npm = models.ForeignKey(NProductModel, verbose_name="N11 Ürünü", on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name="Oluşturma Tarihi", auto_now_add=True)


class NOrderModel(MarketOrderModel):
    pass

