from django.db import models
from marketplace.models import MarketProductModel, MarketOrderModel, MarketOrderDetailModel
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


class HepsiProductModel(MarketProductModel):
    DispatchTime = models.IntegerField(verbose_name="Kargoya Verilme Süresi")
    CargoCompany1 = models.CharField(verbose_name="Kargo Firması 1", max_length=200, blank=True, null=True)
    CargoCompany2 = models.CharField(verbose_name="Kargo Firması 2", max_length=200, blank=True, null=True)
    CargoCompany3 = models.CharField(verbose_name="Kargo Firması 3", max_length=200, blank=True, null=True)

    def get_price(self):
        return str(self.salePrice).replace('.',',')

class HepsiOrderModel(MarketOrderModel):

    def getTotalPrice(self):
        hodm = HepsiOrderDetailModel.objects.filter(mom=self)
        price = 0
        for i in hodm:
            price += i.totalPrice
        return price

    def setTotalPrice(self):
        self.totalPrice = self.getTotalPrice()
        self.save()

    def getPriceToBilling(self):
        hodm = HepsiOrderDetailModel.objects.filter(mom=self)
        price = 0
        for i in hodm:
            price += i.priceToBilling
        return price

    def setPriceToBilling(self):
        self.priceToBilling = self.getPriceToBilling()
        self.save()

class HepsiOrderDetailModel(MarketOrderDetailModel):
    totalHbDiscount = models.FloatField(verbose_name="Toplam HB İndirimi")
    priceToBilling = models.FloatField(verbose_name="Faturalandırılacak Tutar")
   
    comission = models.FloatField(verbose_name="Komisyon Tutarı(KDV Dahil)", blank=True, null=True)
    recoupByHB = models.FloatField(verbose_name="HB'nin Karşıladığı Kampanya Tutarı", blank=True, null=True)
    billToHb = models.FloatField(verbose_name="HB'ye Faturalandırılacak", blank=True, null=True)

    def __str__(self):
        return str(self.mom) + " " + self.mpm.sellerSku
    

    def getTotalPrice(self):
        return self.totalHbDiscount + self.priceToBilling

    def setTotalPrice(self):
        self.totalPrice = self.getTotalPrice()
        self.save()

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

class UpdateStatusModel(models.Model):
    control_id = models.CharField(verbose_name="Kontrol ID", max_length=200)
    date = models.DateTimeField(verbose_name="Tarih",auto_created=True, auto_now_add=True)

    def control(self):
        from .hb_module import HepsiProductModule

        message = HepsiProductModule().updateControl(self.control_id)

        return message
