from django.db import models

# Create your models here.

ORDER_STATUS = (
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


class TrendProductModel(models.Model):
    name = models.CharField(verbose_name="Ürün Adı", max_length=500)
    sku = models.CharField(verbose_name="SKU", max_length=100)
    barcode = models.CharField(verbose_name="Barkod", max_length=100)
    listPrice = models.FloatField(verbose_name="Piyasa Satış Fiyatı")
    salePrice = models.FloatField(verbose_name="Satış Fiyatı")
    piece = models.IntegerField(verbose_name="Adet")
    onSale = models.BooleanField(verbose_name="Satışta Mı?")
    buyBoxRank = models.IntegerField(
        verbose_name="Buybox Sıralaması", blank=True, null=True)

    def __str__(self):
        return self.name

    def removeFromSale(self):
        self.onSale = False
        self.piece = 0
        self.save()
        self.updateStock()

    def updateStock(self):
        from .tr_module import ProductModule
        ProductModule().updateQueue(self)


class TrendMedProductModel(models.Model):
    product = models.ForeignKey(
        'storage.ProductModel', verbose_name="Bağlı Ürün", on_delete=models.CASCADE)
    tpm = models.ForeignKey(
        TrendProductModel, verbose_name="Trendyol Ürünü", on_delete=models.CASCADE)
    isSalable = models.BooleanField(verbose_name="Satılabilir mi?")


class TrendUpdateQueueModel(models.Model):
    tpm = models.ForeignKey(
        TrendProductModel, verbose_name="Trendyol Ürünü", on_delete=models.CASCADE)
    date = models.DateTimeField(
        verbose_name="Oluşturma Tarihi", auto_now_add=True)


class TrendProductBuyBoxListModel(models.Model):
    tpm = models.ForeignKey(TrendProductModel, on_delete=models.CASCADE)
    rank = models.IntegerField(verbose_name="Sıralama")
    merchantName = models.CharField(verbose_name="Satıcı Adı", max_length=255)
    price = models.FloatField(verbose_name="Satıcının Fiyatı")
    dispatchTime = models.IntegerField("Kargoya Verme Süresi")

    def __str__(self):
        return str(self.rank)


class TrendOrderModel(models.Model):
    customerName = models.CharField(verbose_name="Müşteri Adı", max_length=100)
    orderNumber = models.CharField(
        verbose_name="Sipariş Numarası", max_length=100)
    orderDate = models.DateTimeField(verbose_name="Sipariş Tarihi")
    totalPrice = models.FloatField(verbose_name="Toplam Tutar")
    orderStatus = models.CharField(
        verbose_name="Siparişin Durumu", max_length=255, choices=ORDER_STATUS, blank=True, null=True)

    def __str__(self):
        return self.orderNumber

    def getDetailCount(self):
        return self.trendorderdetailmodel_set.all().count()

    def canceledOrder(self):
        todms = self.trendorderdetailmodel_set.all()
        if todms:
            for todm in todms:
                todm.increaseStock()


class TrendOrderDetailModel(models.Model):
    tom = models.ForeignKey(TrendOrderModel, verbose_name="Trendyol Sipariş Modeli", on_delete=models.CASCADE)
    tpm = models.ForeignKey( TrendProductModel, verbose_name="Trendyol Ürünü", on_delete=models.CASCADE)
    totalPrice = models.FloatField(verbose_name="Tutar")
    quantity = models.IntegerField(verbose_name="Adet")


    def dropStock(self):
        from .tr_module import ProductModule
        ProductModule().dropStock(self.tpm, self.quantity)

    def increaseStock(self):
        from .tr_module import ProductModule
        ProductModule().increaseStock(self.tpm, self.quantity)


class TrendOrderCostModel(models.Model):
    tom = models.ForeignKey(TrendOrderModel, on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Maliyet Adı", max_length=255)
    price = models.FloatField(verbose_name="Tutar")
