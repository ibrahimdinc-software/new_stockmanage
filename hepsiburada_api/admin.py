from django.contrib import admin
from rangefilter.filter import DateTimeRangeFilter

from django.http import HttpResponseRedirect
from django.urls import path

from .models import HepsiProductModel, UpdateStatusModel, HepsiOrderModel, HepsiOrderDetailModel, HepsiMedProductModel, HepsiUpdateQueueModel, HepsiProductBuyBoxListModel, HepsiPaymentModel, HepsiBillModel

from .hb_module import ProductModule, OrderModule, AccountingModule

# Register your models here.


class HepsiMedProductModelTabularInline(admin.TabularInline):
    model = HepsiMedProductModel
    extra = 0
    autocomplete_fields = ["hpm"]

class HepsiProductBuyBoxListModelTabularInline (admin.TabularInline):
    model = HepsiProductBuyBoxListModel
    extra = 0
    ordering = ('rank',)

@admin.register(HepsiProductModel)
class HepsiProductModelAdmin(admin.ModelAdmin):
    change_list_template = "hepsiburada_api/admin/get_productlist.html"
    change_form_template = "hepsiburada_api/admin/updateProduct.html"

    search_fields = ["HepsiburadaSku","MerchantSku",]
    list_display = ['MerchantSku','HepsiburadaSku',  'is_salable',]

    inlines = [HepsiProductBuyBoxListModelTabularInline]

    actions = ['send_list', 'getBuyBoxes']

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('getlist/', self.get_list),
        ]
        return my_urls + urls

    def get_list(self, request):
        
        ProductModule().getProducts()
        
        self.message_user(request, "Ürünler geldii hanıım...")
        return HttpResponseRedirect("../")

    def send_list(self, request, queryset):

        ProductModule().updateQueue(queryset)

        self.message_user(request, "Bekleme listesine eklendi.")

    def getBuyBoxes(self, request, queryset):
        import time
        for q in queryset:
            ProductModule().buyboxList(q)
            time.sleep(.100)
        self.message_user(request, "Hadi H.O.")

    def response_change(self, request, obj):
        if "update" in request.POST:
            obj.save()
            obj.updateStock()
            self.message_user(request, "Bekleme listesine alındı en geç 5 dk içinde güncellenecek.\n Elle güncelleyebilirsiniz.")
            return HttpResponseRedirect(".")
        if "getBuyBox" in request.POST:
            message = ProductModule().buyboxList(obj)
            if message:
                self.message_user(request, message)
            else:
                self.message_user(request, "Geldi mi bi bak bakalım.")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    send_list.short_description = "Seçili ürünleri hepsiburadaya gönder."
    getBuyBoxes.short_description = "Seçili ürünlerin BuyBoxını getir."

@admin.register(UpdateStatusModel)
class UpdateStatusModelAdmin(admin.ModelAdmin):

    change_form_template = "hepsiburada_api/admin/list_update_control.html"
    list_display = ['control_id', 'date',]
    readonly_fields = ['date']

    def response_change(self, request, obj):
        if "_control" in request.POST:

            message = obj.control()


            self.message_user(request, message)

            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

@admin.register(HepsiUpdateQueueModel)
class HepsiUpdateQueueModelAdmin(admin.ModelAdmin):
    list_display = ["hpm", "date"]
    change_list_template = "hepsiburada_api/admin/hbUpdateQueue.html"

    readonly_fields = ["date"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('updateQueue/', self.updateQueue),
        ]
        return my_urls + urls

    def updateQueue(self, request):
        
        ProductModule().updateProducts()
        
        self.message_user(request, "Ürünler gitti loo...")
        return HttpResponseRedirect("../")


class HepsiOrderDetailModelTabularInline(admin.TabularInline):
    model = HepsiOrderDetailModel
    extra = 0


class HepsiBillModelTabularInline(admin.TabularInline):
    model = HepsiBillModel
    extra = 0


@admin.register(HepsiOrderModel)
class HepsiOrderModelAdmin(admin.ModelAdmin):
    inlines = [HepsiOrderDetailModelTabularInline, HepsiBillModelTabularInline]

    change_list_template = "hepsiburada_api/admin/get_hborder.html"
    change_form_template = "hepsiburada_api/admin/cancelOrder.html"
    
    search_fields = ["orderNumber","customerName","packageNumber",]

    list_display = ["__str__", "customerName", "totalPrice", "orderDate", "status", "getDetailCount",]
    list_filter = [("orderDate",DateTimeRangeFilter), "status"]

    ordering = ["-orderDate"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('gethborders/', self.get_hb_order),
            path('getoldorders/', self.getOldOrders),
            path('getPackageDetails/', self.getPackageDetails),
        ]
        return my_urls + urls

    def getOldOrders(self, request):
        OrderModule().getOldOrders(request.FILES.get("excel"))
        self.message_user(request, "Siparişler gelmiştir ha...")
        return HttpResponseRedirect("../")

    def get_hb_order(self, request):
    
        OrderModule().getOrders()
        
        self.message_user(request, "Siparişler gelmiştir ha...")
        return HttpResponseRedirect("../")

    def getPackageDetails(self, request):
        OrderModule().getPackageDetails()
        self.message_user(request, "Paket detaylarını getirelim")
        return HttpResponseRedirect("../")


    def response_change(self, request, obj):
        if "cancelOrder" in request.POST:

            obj.canceledOrder()
            self.message_user(request, "İptal Edildi")

            return HttpResponseRedirect(".")
        return super().response_change(request, obj)


@admin.register(HepsiPaymentModel)
class HepsiPaymentModelAdmin(admin.ModelAdmin):
    inlines = [HepsiBillModelTabularInline]

    list_display = ["__str__", "totalPayment"]
    ordering = ["-date"]

    change_form_template = "hepsiburada_api/admin/HepsiPaymentModelAdmin.html"


    def response_change(self, request, obj):
        if "getBills" in request.POST:
            AccountingModule().getBills(obj)
            self.message_user(request, "Faturalar geldi.")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

@admin.register(HepsiBillModel)
class HepsiBillModelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "paymentDate", "invoiceDate", "hom", "totalAmount"]
    list_filter = [("invoiceDate",DateTimeRangeFilter), "transactionType", "hpm"]
    ordering = ["paymentDate"]
#class HepsiOrderCancelModel(models.Mode)