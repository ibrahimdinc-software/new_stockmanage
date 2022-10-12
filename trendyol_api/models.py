from django.db import models
from django.utils.html import format_html, format_html_join

from marketplace.models import MarketProductModel, MarketOrderModel, MarketOrderDetailModel

# Create your models here.



TRANSACTION_TYPE = (
    ('a', 'a'),
)

class  TrendProductModel(MarketProductModel):
    listPrice = models.FloatField(verbose_name="Piyasa Satış Fiyatı")


    def countOfRelated(self):
        return len(self.marketmedproductmodel_set.all())

    def related(self):
        return format_html_join(
            "\n",
            '<a href="/admin/storage/productmodel/{0}/change/" target="_blank">{1}</a>',
            ((tpm.product.id, tpm.product.name) for tpm in self.trendmedproductmodel_set.all())
        )

class TrendOrderModel(MarketOrderModel):
    pass

class TrendOrderDetailModel(MarketOrderDetailModel):
    pass