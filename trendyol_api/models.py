from django.db import models


# Create your models here.




class TrendProductModel(models.Model):
    name = models.CharField(verbose_name="Ürün Adı", max_length=500)
    sku = models.CharField(verbose_name="SKU", max_length=100)
    barcode = models.CharField(verbose_name="Barkod", max_length=100)
    listPrice = models.FloatField(verbose_name="Piyasa Satış Fiyatı")
    salePrice = models.FloatField(verbose_name="Satış Fiyatı")
    piece = models.IntegerField(verbose_name="Adet")
    onSale = models.BooleanField(verbose_name="Satışta Mı?")

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        from .tr_module import ProductModule
        ProductModule().updateProducts([self])
        super(TrendProductModel, self).save(*args, **kwargs) # Call the real save() method
    

class TrendMedProductModel(models.Model):
    product = models.ForeignKey('storage.ProductModel', verbose_name="Bağlı Ürün", on_delete=models.CASCADE)
    tpm = models.ForeignKey(TrendProductModel, verbose_name="Trendyol Ürünü", on_delete=models.CASCADE)


class TrendOrderModel(models.Model):
    customerName = models.CharField(verbose_name="Müşteri Adı", max_length=100)
    orderNumber = models.CharField(verbose_name="Sipariş Numarası", max_length=100)
    orderDate = models.DateTimeField(verbose_name="Sipariş Tarihi")
    totalPrice = models.FloatField(verbose_name="Toplam Tutar")

    def __str__(self):
        return self.orderNumber
    
    def getDetailCount(self):
        return self.trendorderdetailmodel_set.all().count()


class TrendOrderDetailModel(models.Model):
    tom = models.ForeignKey(TrendOrderModel, verbose_name="Trendyol Sipariş Modeli", on_delete=models.CASCADE)
    tpm = models.ForeignKey(TrendProductModel, verbose_name="Trendyol Ürünü", on_delete=models.CASCADE)
    totalPrice = models.FloatField(verbose_name="Tutar")
    quantity = models.IntegerField(verbose_name="Adet")

    def save(self, *args, **kwargs):
        from .tr_module import ProductModule
        ProductModule().dropStock(self.tpm, self.quantity)
        super(TrendOrderDetailModel, self).save(*args, **kwargs) # Call the real save() method

    def delete(self, *args, **kwargs):
        from .tr_module import ProductModule
        ProductModule().increaseStock(self.tpm, self.quantity)
        super(TrendOrderDetailModel, self).delete(*args, **kwargs)
