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

COST_TYPES = (
    ('Shipment', 'Kargo'),
    ('Comission', 'Komisyon'),
    ('PurchasePrice', 'Alım Fiyatı'),
    ('Extra', 'Ekstra'),
)

MARKET_TYPE = (
    ('hepsiburada','Hepsiburada'),
    ('trendyol','Trendyol'),
    ('n11','N11'),
)


class UserMarketPlaceModel(models.Model):
    user = models.ForeignKey("auth.user", on_delete=models.CASCADE)
    marketType = models.CharField(verbose_name="Market Tipi", max_length=255, choices=MARKET_TYPE)
    supplierId = models.CharField(verbose_name="Trendyol Satıcı ID / Hepsiburada Merchant ID", max_length=255, unique=True, blank=True, null=True)
    apiKey = models.CharField(verbose_name="Trendyol / N11 Satıcı ApiKey", max_length=255, blank=True, null=True)
    apiSecret = models.CharField(verbose_name="Trendyol / N11 Satıcı ApiSecret", max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.get_marketType_display())
    

class UserMarketShipmentRuleModel(models.Model):
    userMarket = models.ForeignKey(UserMarketPlaceModel, on_delete=models.CASCADE)
    minPrice = models.FloatField(verbose_name="Min Fiyat")
    maxPrice = models.FloatField(verbose_name="Max Fiyat")
    cost = models.FloatField(verbose_name="Kargo Tutarı")



class MarketProductModel(models.Model):
    userMarket = models.ForeignKey(UserMarketPlaceModel, verbose_name="Pazar Yeri", on_delete=models.CASCADE, blank=True, null=True)
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
        return str(self.userMarket) + " / " + self.sellerSku

    def save(self, *args, **kwargs):
        if int(self.availableStock) > 0:
           self.onSale = True
        else:
            self.onSale=False
        super(MarketProductModel, self).save(*args, **kwargs) # Call the real save() method

    def setUserMarket(self, mType):
        userMarket = UserMarketPlaceModel.objects.get(marketType=mType)
        self.userMarket = userMarket
        self.save()

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
    oldPrice = models.FloatField(verbose_name="Satıcının Önceki Fiyatı")
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
    userMarket = models.ForeignKey(UserMarketPlaceModel, verbose_name="Pazar Yeri", on_delete=models.CASCADE, blank=True, null=True)
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

    def setUserMarket(self, mType):
        userMarket = UserMarketPlaceModel.objects.get(marketType=mType)
        self.userMarket = userMarket
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

    def __str__(self):
        return str(self.mom)+"/"+str(self.mpm)

    def dropStock(self):
        from .module import ProductModule
        ProductModule().dropStock(self.mpm, self.quantity)

    def increaseStock(self):
        from .module import ProductModule
        ProductModule().increaseStock(self.mpm, self.quantity)


class MarketOrderPredCostModel(models.Model):
    mom = models.ForeignKey(MarketOrderModel, verbose_name="Sipariş Modeli", on_delete=models.CASCADE)
    modm = models.ForeignKey(MarketOrderDetailModel, verbose_name="Sipariş Detay Modeli", on_delete=models.CASCADE, blank=True, null=True)
    costType = models.CharField(verbose_name="Gider Türü", max_length=255, choices=COST_TYPES)
    costAmount = models.FloatField(verbose_name="Tutar")