from django.db import models
from django.utils.html import format_html
from django.utils import timezone
from .manager import MarketOrderModelManager

# Create your models here.

ORDER_STATUS = (
    ('Awaiting', 'Ödeme Onayı Bekleniyor'),
    ('ReadyToShip', 'Gönderime Hazır'), #Open
    ('Picking', 'Paket Hazırlanıyor'), #Packaged
    ('Invoiced', 'Fatura Kesildi'),
    ('Shipped', 'Taşıma Durumunda'), #InTransit
    ('AtCollectionPoint', 'PUDO Noktasında'),
    ('Cancelled', 'İptal Edildi'), #Refunded
    ('UnPacked', 'Paketi Bölünmüş'),
    ('Delivered', 'Teslim Edildi'),
    ('UnDelivered', 'Müşteriye Ulaştırılmadı'),
    ('UnDeliveredAndReturned', 'Ulaştırılamadı ve Geri Döndü'),
)

MARKET_TYPE = (
    ('hepsiburada','Hepsiburada'),
    ('trendyol','Trendyol'),
)


class MarketProductModel(models.Model):
    marketType = models.CharField(verbose_name="Pazar yeri", choices=MARKET_TYPE, max_length=255, blank=True, null=True)
    productName = models.CharField(verbose_name="Ürün Adı", max_length=200, blank=True, null=True)
    marketplaceSku = models.CharField(verbose_name="Pazaryeri SKU", max_length=100)
    sellerSku = models.CharField(verbose_name="Satıcı SKU", max_length=100)
    salePrice = models.FloatField(verbose_name="Satış Fiyatı")
    onSale = models.BooleanField(verbose_name="Satılabilir mi?")
    availableStock = models.IntegerField(verbose_name="Mevcut Stok")
    lastControlDate = models.DateTimeField(verbose_name="Son BuyBox Kontrol Tarihi", default=timezone.now)
    buyBoxRank = models.IntegerField(verbose_name="Buybox Sıralaması", blank=True, null=True)
    productLink = models.CharField(verbose_name="Link", max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.sellerSku

    def updateStock(self):
        from .module import ProductModule
        ProductModule().updateQueue(self)

    def removeFromSale(self):
        self.onSale = False
        self.availableStock = 0
        self.save()
        self.updateStock()

    def productLinkF(self):
        return format_html(
            '<a href="{0}" target="_blank">{1}</a>',
            self.productLink,
            "Ürün Linki",
        )
    
  
    
class MarketMedProductModel(models.Model):
    product = models.ForeignKey("storage.ProductModel", verbose_name="Bağlı Ürün", on_delete=models.CASCADE)
    mpm = models.ForeignKey(MarketProductModel, verbose_name="Pazaryeri Ürünü", on_delete=models.CASCADE)
    isSalable = models.BooleanField(verbose_name="Satılabilir mi?")

    
class MarketUpdateQueueModel(models.Model):
    mpm = models.ForeignKey(MarketProductModel, verbose_name="Pazaryeri Ürünü", on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name="Oluşturma Tarihi", auto_now_add=True)
    isUpdated = models.BooleanField(verbose_name="Güncellendi mi?", default=False)

class MarketProductBuyBoxListModel(models.Model):
    mpm = models.ForeignKey(MarketProductModel, verbose_name="Pazaryeri Ürünü", on_delete=models.CASCADE)
    rank = models.IntegerField(verbose_name="Sıralama")
    merchantName = models.CharField(verbose_name="Satıcı Adı", max_length=255)
    price = models.FloatField(verbose_name="Satıcının Fiyatı")
    dispatchTime = models.IntegerField("Kargoya Verme Süresi", blank=True, null=True) 
    uncomp = models.BooleanField(verbose_name="Rekabet edilemez?", default=False)

    def __str__(self):
        return str(self.rank) + self.merchantName

class MarketBuyBoxTraceModel(models.Model):
    marketProduct = models.ForeignKey(MarketProductModel, on_delete=models.CASCADE)
    minPrice = models.FloatField(verbose_name="Alt Fiyat")
    maxPrice = models.FloatField(verbose_name="Üst Fiyat")
    priceStep = models.FloatField(verbose_name="Değişim Miktarı")
    isActive = models.BooleanField(verbose_name="Aktif mi?", default=True)


    def __str__(self):
        return str(self.marketProduct)
    
    def price(self):
        return self.marketProduct.salePrice
    


class MarketOrderModel(models.Model):
    marketType = models.CharField(verbose_name="Pazar yeri", choices=MARKET_TYPE, max_length=255, blank=True, null=True)
    customerModel = models.ForeignKey("billing.CustomerModel", blank=True, null=True, on_delete=models.CASCADE)
    orderNumber = models.CharField(verbose_name="Sipariş No", max_length=100)
    packageNumber = models.CharField(verbose_name="Paket Numarası",max_length=100, blank=True, null=True)
    orderDate = models.DateTimeField(verbose_name="Sipariş Tarihi")
    deliveryDate = models.DateTimeField(verbose_name="Teslim Tarihi", blank=True, null=True)
    totalPrice = models.FloatField(verbose_name="Toplam Tutar", blank=True, null=True)
    priceToBilling = models.FloatField(verbose_name="Faturalandırılacak Tutar", blank=True, null=True)
    orderStatus = models.CharField(verbose_name="Siparişin Durumu", max_length=255, choices=ORDER_STATUS, blank=True, null=True)

    objects = MarketOrderModelManager()

    def __str__(self):
        return str(self.orderNumber)

    def getDetailCount(self):
        return self.marketorderdetailmodel_set.all().count()

    def setCustomer(self, customer, customerData):
        if type(customerData) == dict:  
            customer.taxId = customerData.get("taxId")
            customer.mail = customerData.get("mail")
            customer.phone = customerData.get("phone")
            customer.province = customerData.get("city")
            customer.district = customerData.get("district")
            customer.address = customerData.get("fullAddress")
            customer.save()
        
        self.customerModel = customer
        self.save()

    def canceledOrder(self):
        self.orderStatus = "Cancelled"
        self.save()
        modms = self.marketorderdetailmodel_set.all()
        if modms:
            for modm in modms:
                modm.increaseStock()
        

class MarketOrderDetailModel(models.Model):
    mom = models.ForeignKey(MarketOrderModel, verbose_name="Sipariş Modeli", on_delete=models.CASCADE)
    mpm = models.ForeignKey(MarketProductModel, verbose_name="Market Ürünü", on_delete=models.CASCADE)
    totalPrice = models.FloatField(verbose_name="Tutar", blank=True, null=True)
    quantity = models.IntegerField(verbose_name="Adet")

    def dropStock(self):
        from .module import ProductModule
        ProductModule().dropStock(self.mpm, self.quantity)

    def increaseStock(self):
        from .module import ProductModule
        ProductModule().increaseStock(self.mpm, self.quantity)