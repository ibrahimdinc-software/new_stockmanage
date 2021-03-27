from django.db import models
from django.utils.html import format_html, format_html_join

from marketplace.models import MarketProductModel, MarketOrderModel, MarketOrderDetailModel

# Create your models here.

TREND_ORDER_STATUS = (
    ('Awaiting', 'Ödeme Onayı Bekleniyor'),
    ('Created', 'Gönderime Hazır'),
    ('Picking', 'Paket Hazırlanıyor'),
    ('Invoiced', 'Fatura Kesildi'),
    ('Shipped', 'Taşıma Durumunda'),
    ('AtCollectionPoint', 'PUDO Noktasında'),
    ('Cancelled', 'İptal Edildi'),
    ('UnPacked', 'Paketi Bölünmüş'),
    ('Delivered', 'Teslim Edildi'),
    ('UnDelivered', 'Müşteriye Ulaştırılmadı'),
    ('UnDeliveredAndReturned', 'Ulaştırılamadı ve Geri Döndü'),
)

TRANSACTION_TYPE = (
    ('a', 'a'),
)

class  TrendProductModel(MarketProductModel):
    listPrice = models.FloatField(verbose_name="Piyasa Satış Fiyatı")
    productLink = models.CharField(verbose_name="Link", max_length=255)

    def productLinkF(self):
        return format_html(
            '<a href="{0}" target="_blank">{1}</a>',
            self.productLink,
            "Ürün Linki",
        )

    def countOfRelated(self):
        return len(self.marketmedproductmodel_set.all())

    def related(self):
        return format_html_join(
            "\n",
            '<a href="/admin/storage/productmodel/{0}/change/" target="_blank">{1}</a>',
            ((tpm.product.id, tpm.product.name) for tpm in self.trendmedproductmodel_set.all())
        )

class TrendOrderModel(MarketOrderModel):
    orderStatus = models.CharField(verbose_name="Siparişin Durumu", max_length=255, choices=TREND_ORDER_STATUS, blank=True, null=True)

class TrendOrderDetailModel(MarketOrderDetailModel):
    pass