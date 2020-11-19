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
    
    def get_price(self):
        return str(self.Price).replace('.',',')

    def save(self, *args, **kwargs):
        if self.pk:
            from .hb_module import ListingModule
            ListingModule().sendProducts(self)
        super(HepsiProductModel, self).save(*args, **kwargs) # Call the real save() method


class HepsiMedProductModel(models.Model):
    product = models.ForeignKey("storage.ProductModel", verbose_name="Bağlı Ürün", on_delete=models.CASCADE)
    hpm = models.ForeignKey(HepsiProductModel, verbose_name="Hepsiburada Ürünü", on_delete=models.CASCADE)
    


class UpdateStatusModel(models.Model):
    control_id = models.CharField(verbose_name="Kontrol ID", max_length=200)
    date = models.DateTimeField(verbose_name="Tarih",auto_created=True, auto_now_add=True)

    def control(self):
        from .hb_module import ListingModule

        message = ListingModule().listingUpdateControl(self.control_id)

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


class HepsiOrderDetailModel(models.Model):
    hom = models.ForeignKey(HepsiOrderModel, verbose_name="Hepsiburada Sipariş Modeli", on_delete=models.CASCADE)
    hpm = models.ForeignKey(HepsiProductModel, verbose_name="Hepsiburada Ürün Modeli", on_delete=models.CASCADE)
    totalPrice = models.FloatField(verbose_name="Toplam Tutar")
    quantity = models.IntegerField(verbose_name="Adet")


    def save(self, *args, **kwargs):
        from .hb_module import ListingModule
        ListingModule().dropStock(self.hpm, self.quantity)
        super(HepsiOrderDetailModel, self).save(*args, **kwargs) # Call the real save() method
