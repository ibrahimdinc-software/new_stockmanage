from django.db import models

from hepsiburada_api.hb_module import ProductModule

# Create your models here.



class ProductModel(models.Model):
    name = models.CharField(verbose_name="Ürün Adı", max_length=100)
    sku = models.CharField(verbose_name="Stok Kodu", max_length=100, unique=True)
    piece = models.IntegerField(verbose_name="Bağlı Üründen Kaç Tane Var?", blank=True, null=True)
    
    def __str__(self):
        return self.name
    

    def setMedProductStocks(self):
        hmpm = self.hepsimedproductmodel_set.all()
        tmpm = self.trendmedproductmodel_set.all()
        for m in hmpm:
            m.hpm.AvailableStock = self.piece
            m.hpm.save()
            m.hpm.updateStock()
        del hmpm
        for m in tmpm:
            m.tpm.piece = self.piece
            m.tpm.save()
            m.tpm.updateStock()
        del tmpm

    def stockMethod(self):
        meds = self.medproductmodel_set.all()
        print(meds)
        if meds:
            piece = meds[0].base_product.piece / meds[0].piece
            print(piece)
            for m in meds:
                if piece > m.base_product.piece / m.piece:
                    print(piece)                
                    piece = m.base_product.piece / m.piece
            return piece

    def setStock(self):        
        self.piece = self.stockMethod()
        self.save()

class BaseProductModel(models.Model):
    name = models.CharField("Temel Ürün Adı", max_length=100)
    barcode = models.BigIntegerField(verbose_name="Barkod", blank=True, null=True)
    piece = models.IntegerField(verbose_name="Adet")
    cost = models.FloatField(verbose_name="Maliyet")
    nexdPiece = models.IntegerField(verbose_name="Son Kullanma Tarihi Yakın Adet")
    def __str__(self):
        return self.name

    def getCost(self):
        cdm = self.costdetailmodel_set.all()
        if cdm:
            nearExpDate = cdm[0].expDate
            for c in cdm:
                if nearExpDate > c.expDate:
                    nearExpDate = c.expDate
            self.cost = nearExpDate.cost
            self.nexdPiece = nearExpDate.piece
            self.save()

    def setMedProductStock(self):
        meds = self.medproductmodel_set.all()
        
        for m in meds:
            m.product.setStock()
            m.product.setMedProductStocks()

    def dropStock(self, quantity):
        self.piece -= quantity
        self.save()
        self.setMedProductStock()
    
    def increaseStock(self, quantity):
        self.piece += quantity
        self.save()
        self.setMedProductStock()

class CostDetailModel(models.Model):
    baseProduct = models.ForeignKey(BaseProductModel, verbose_name="Ürün", on_delete=models.CASCADE)
    expDate = models.DateTimeField(verbose_name="SKT")
    piece = models.IntegerField(verbose_name="Adet")
    amount = models.FloatField(verbose_name="Tutar")


class MedProductModel(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    base_product = models.ForeignKey(BaseProductModel, on_delete=models.CASCADE)
    piece = models.IntegerField(verbose_name="Bağlı Üründe Kaç Tane")

    