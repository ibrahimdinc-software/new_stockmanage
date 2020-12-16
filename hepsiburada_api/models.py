from django.db import models

# Create your models here.


TRANSACTION_TYPE = [
    ('Payment', 'Sipariş Tutarı'),
    ('CommissionSettlement', 'Komisyon mahsuplaşma tutarı (Komisyon-Kampanya)'),
    ('ShipmentCostSharingIncome', 'Kargo Katkı Payı Gideri'),
    ('Return', 'İade Tutarı'),
    ('CommissionInvoiceRefund', 'Komisyon Fatura İadesi'),
    ('ProcessingFeeIncome', 'İşlem Ücret Gideri'),
    ('CommissionReturnPriceDifference', 'Komisyon İade Tutarı'),
    ('Commission', 'Komisyon Tutarı'),
    ('CustomerSatisfaction', 'Hediye Çeki Tutarı'),
    ('RevenueIncome', 'Ciro Gideri'),
    ('RevenueExpense', 'Ciro Geliri'),
    ('StudioIncome', 'Stüdyo Gideri'),
    ('ShipmentCostSharingExpense', 'Kargo Katkı Payı Geliri'),
    ('MarketingIncome', 'Pazarlama Gideri'),
    ('MarketingExpense', 'Pazarlama Geliri'),
    ('PriceDifferenceIncome', 'Fiyat Farkı Gideri'),
    ('PriceDifferenceExpense', 'Fiyat Farkı Geliri'),
    ('LateInterestIncome', 'Vade Farkı Gideri'),
    ('CampaignDiscount', 'Kampanya İndirimleri Tutarı'),
    ('CargoCompensationIncome', 'Kargo Tazmin Gideri'),
    ('CargoCompensationExpense', 'Kargo Tazmin Geliri'),
    ('CargoCompensationSellerSatisfactionRevenue', 'Kargo Tazmin Satıcı Memnuniyet Geliri'),
    ('RefusedInvoiceIncome', 'Red Edilen Fatura Gideri'),
    ('RefusedInvoiceExpense', 'Red Edilen Fatura Geliri'),
    ('GiftChequeRefund', 'Hediye Çeki İadesi'),
    ('CargoCostRefund', 'Kargo İade'),
    ('LineitemTransferExpense', 'Sipariş Kaydırma Geliri'),
    ('LineItemTransferIncome', 'Sipariş Kaydırma Gideri'),
    ('RoadAssistanceExpense', 'Yol Yardım Geliri'),
    ('RoadAssistanceIncome', 'Yol Yardım Gideri'),
    ('ProcessingFeeRefund', 'İşlem Ücret Gelir İadesi'),
    ('SponsorshipFee', 'Sponsorluk Bedeli'),
    ('CampaignDiscountRefund', 'Kampanya İndirimleri İadesi'),
]

ORDER_STATUS = [
    ('Delivered', 'Teslim Edildi'),
    ('Undelivered', 'Teslim Edilemedi'),
    ('InTransit', 'Taşıma Durumunda'),
    ('Open', 'Paketlenecek'),
    ('Packaged', 'Paketlendi'),
    ('Unpacked', 'Paket Bozuldu'),
    ('Refunded', 'İade/İptal - Geri Ödeme Yapılmış'),
]


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
    buyBoxRank = models.IntegerField(verbose_name="Buybox Sıralaması", blank=True, null=True)


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
    customerName = models.CharField(verbose_name="Müşteri Adı", max_length=200)
    orderNumber = models.CharField(verbose_name="Hepsiburada Sipariş No", max_length=100)
    orderDate = models.DateTimeField(verbose_name="Sipariş Tarihi")
    totalPrice = models.FloatField(verbose_name="Toplam Tutar", blank=True, null=True)
    priceToBilling = models.FloatField(verbose_name="Faturalandırılacak Tutar", blank=True, null=True)
    packageNumber = models.CharField(verbose_name="Paket Numarası",max_length=100, blank=True, null=True)
    status = models.CharField(verbose_name="Sipariş Durumu", choices=ORDER_STATUS, max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.orderNumber)

    def getTotalPrice(self):
        hodm = self.hepsiorderdetailmodel_set.all()
        price = 0
        for i in hodm:
            price += i.totalPrice
        return price

    def setTotalPrice(self):
        self.totalPrice = self.getTotalPrice()
        self.save()

    def getPriceToBilling(self):
        hodm = self.hepsiorderdetailmodel_set.all()
        price = 0
        for i in hodm:
            price += i.priceToBilling
        return price

    def setPriceToBilling(self):
        self.priceToBilling = self.getPriceToBilling()
        self.save()

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
    totalHbDiscount = models.FloatField(verbose_name="Toplam HB İndirimi")
    priceToBilling = models.FloatField(verbose_name="Faturalandırılacak Tutar")
    totalPrice = models.FloatField(verbose_name="Toplam Tutar", blank=True, null=True)
    quantity = models.IntegerField(verbose_name="Adet")
    
    comissionRate = models.FloatField(verbose_name="Komisyon Oranı", blank=True, null=True)
    comission = models.FloatField(verbose_name="Komisyon Tutarı(KDV Dahil)", blank=True, null=True)
    recoupByHB = models.FloatField(verbose_name="HB'nin Karşıladığı Kampanya Tutarı", blank=True, null=True)
    billToHb = models.FloatField(verbose_name="HB'ye Faturalandırılacak", blank=True, null=True)

    def __str__(self):
        return str(self.hom) + " " + self.hpm.MerchantSku
    

    def getTotalPrice(self):
        return self.totalHbDiscount + self.priceToBilling

    def setTotalPrice(self):
        self.totalPrice = self.getTotalPrice()
        self.save()

    def dropStock(self):
        from .hb_module import ProductModule
        ProductModule().dropStock(self.hpm, self.quantity)

    def increaseStock(self):
        from .hb_module import ProductModule
        ProductModule().increaseStock(self.hpm, self.quantity)


class HepsiPaymentModel(models.Model):
    date = models.DateField(verbose_name="Ödeme Tarihi", auto_now=False, auto_now_add=False)
    incomingAmount = models.FloatField(verbose_name="Gelen Tutar")
    amountToCome = models.FloatField(verbose_name="Gelmesi Gereken Tutar")

    def __str__(self):
        return str(self.date)
    
    def totalPayment(self):
        details = self.hepsibillmodel_set.all()
        price = 0
        for detail in details:
            price += detail.totalAmount
        return price


class HepsiBillModel(models.Model):
    transactionType = models.CharField(verbose_name="İşlem Tipi", max_length=255, choices=TRANSACTION_TYPE)
    hom = models.ForeignKey(HepsiOrderModel, on_delete=models.CASCADE, blank=True, null=True)
    hodm = models.ForeignKey(HepsiOrderDetailModel, on_delete=models.CASCADE, blank=True, null=True)
    hpm = models.ForeignKey(HepsiPaymentModel, on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name="Adet")
    totalAmount = models.FloatField(verbose_name="Toplam Tutar")
    taxAmount = models.FloatField(verbose_name="Vergi Tutarı")
    netAmount = models.FloatField(verbose_name="Net Tutar")
    dueDate = models.DateField(verbose_name="Vade Tarihi", auto_now=False, auto_now_add=False)
    invoiceDate = models.DateField(verbose_name="Fatura Tarihi", auto_now=False, auto_now_add=False)
    paymentDate = models.DateField(verbose_name="Ödeme Tarihi", auto_now=False, auto_now_add=False)
    invoiceNumber = models.CharField(verbose_name="Fatura No", max_length=255)
    invoiceExplanation = models.CharField(verbose_name="Fatura Açıklaması", max_length=255)

    def __str__(self):
        return self.get_transactionType_display()
    
    def getOrderDate(self):
        if self.hom:
            return self.hom.orderDate
        else:
            return "Sipariş Yok"
