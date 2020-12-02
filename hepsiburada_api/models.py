from django.db import models

# Create your models here.


class HepsiProductModel(models.Model):
    HepsiburadaSku = models.CharField(verbose_name="Hepsiburada SKU", max_length=100,unique=True)
    MerchantSku = models.CharField(verbose_name="Satıcı SKU", max_length=100)
    ProductName = models.CharField(verbose_name="Ürün Adı", max_length=200, blank=True, null=True)
    Price = models.FloatField(verbose_name="Ürün Fiyatı")
    AvailableStock = models.IntegerField(verbose_name="Mevcut Stok")
    DispatchTime = models.IntegerField(verbose_name="Kargoya Verilme Süresi")
    CargoCompany1 = models.CharField(verbose_name="Kargo Firması 1", max_length=200, blank=True, null=True)
    CargoCompany2 = models.CharField(verbose_name="Kargo Firması 2", max_length=200, blank=True, null=True)
    CargoCompany3 = models.CharField(verbose_name="Kargo Firması 3", max_length=200, blank=True, null=True)
    is_salable = models.BooleanField(verbose_name="Satılabilir mi?")

    def __str__(self):
        return self.MerchantSku + " / " + self.HepsiburadaSku

    def updateStock(self):
        from .hb_module import ProductModule
        ProductModule().updateQueue(self)
    
    def get_price(self):
        return str(self.Price).replace('.',',')



class HepsiMedProductModel(models.Model):
    product = models.ForeignKey("storage.ProductModel", verbose_name="Bağlı Ürün", on_delete=models.CASCADE)
    hpm = models.ForeignKey(HepsiProductModel, verbose_name="Hepsiburada Ürünü", on_delete=models.CASCADE)
    
class HepsiUpdateQueueModel(models.Model):
    hpm = models.ForeignKey(HepsiProductModel, verbose_name="Hepsiburada Ürünü", on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name="Oluşturma Tarihi", auto_now_add=True)

class HepsiProductBuyBoxListModel(models.Model):
    hpm = models.ForeignKey(HepsiProductModel, on_delete=models.CASCADE)
    rank = models.IntegerField(verbose_name="Sıralama")
    merchantName = models.CharField(verbose_name="Satıcı Adı", max_length=255)
    price = models.FloatField(verbose_name="Satıcının Fiyatı")
    dispatchTime = models.IntegerField("Kargoya Verme Süresi") 

    def __str__(self):
        return str(self.rank)
    

class UpdateStatusModel(models.Model):
    control_id = models.CharField(verbose_name="Kontrol ID", max_length=200)
    date = models.DateTimeField(verbose_name="Tarih",auto_created=True, auto_now_add=True)

    def control(self):
        from .hb_module import ProductModule

        message = ProductModule().updateControl(self.control_id)

        return message




class HepsiOrderModel(models.Model):
    hepsiId = models.CharField(verbose_name="Hepsiburada Sipariş ID", max_length=200)
    customerName = models.CharField(verbose_name="Müşteri Adı", max_length=200)
    orderNumber = models.CharField(verbose_name="Hepsiburada Sipariş No", max_length=100)
    orderDate = models.DateTimeField(verbose_name="Sipariş Tarihi")
    totalPrice = models.FloatField(verbose_name="Toplam Tutar")

    def __str__(self):
        return str(self.orderNumber)
    def getDetailCount(self):
        return self.hepsiorderdetailmodel_set.all().count()
    
    def canceledOrder(self):
        hodms = self.hepsiorderdetailmodel_set.all()
        if hodms:
            for hodm in hodms:
                hodm.increaseStock()
        

class HepsiOrderDetailModel(models.Model):
    hom = models.ForeignKey(HepsiOrderModel, verbose_name="Hepsiburada Sipariş Modeli", on_delete=models.CASCADE)
    hpm = models.ForeignKey(HepsiProductModel, verbose_name="Hepsiburada Ürün Modeli", on_delete=models.CASCADE)
    totalPrice = models.FloatField(verbose_name="Toplam Tutar")
    quantity = models.IntegerField(verbose_name="Adet")

    def dropStock(self):
        from .hb_module import ProductModule
        ProductModule().dropStock(self.hpm, self.quantity)

    def increaseStock(self):
        from .hb_module import ProductModule
        ProductModule().increaseStock(self.hpm, self.quantity)
















