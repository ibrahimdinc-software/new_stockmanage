from django.contrib import admin
from rangefilter.filter import DateTimeRangeFilter

from django.http import HttpResponseRedirect
from django.urls import path

from .models import HepsiProductModel, UpdateStatusModel, HepsiOrderModel, HepsiOrderDetailModel, HepsiPaymentModel, HepsiBillModel

from .hb_module import HepsiProductModule, HepsiOrderModule, AccountingModule

from marketplace.module import ProductModule
from marketplace.admin import MarketProductBuyBoxListModelTabularInline, MarketMedProductModelTabularInline


# Register your models here.

@admin.register(HepsiProductModel)
class HepsiProductModelAdmin(admin.ModelAdmin):
    change_list_template = "hepsiburada_api/admin/get_productlist.html"
    change_form_template = "hepsiburada_api/admin/updateProduct.html"

    search_fields = ["marketplaceSku", "sellerSku", ]
    list_display = ['sellerSku', 'salePrice',
                    'availableStock', 'buyBoxRank', 'onSale', ]

    list_filter = ['onSale', ]

    inlines = [MarketMedProductModelTabularInline,
               MarketProductBuyBoxListModelTabularInline]

    actions = ['send_list', 'getBuyBoxes']

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('getlist/', self.get_list),
        ]
        return my_urls + urls

    def get_list(self, request):

        HepsiProductModule().getHepsiProducts()

        self.message_user(request, "Ürünler geldi...")
        return HttpResponseRedirect("../")

    def send_list(self, request, queryset):

        ProductModule().updateQueue(queryset)

        self.message_user(request, "Bekleme listesine eklendi.")

    def getBuyBoxes(self, request, queryset):
        ProductModule().buyboxList(queryset)
        self.message_user(request, "Buybox listesi getirildi")

    def response_change(self, request, obj):
        if "update" in request.POST:
            obj.save()
            obj.updateStock()
            self.message_user(
                request, "Bekleme listesine alındı en geç 5 dk içinde güncellenecek.\n Elle güncelleyebilirsiniz.")
            return HttpResponseRedirect(".")
        if "getBuyBox" in request.POST:
            message = ProductModule().buyboxList([obj])
            if message:
                self.message_user(request, message)
            else:
                self.message_user(request, "Buybox listesi getirildi.")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    send_list.short_description = "Seçili ürünleri hepsiburadaya gönder."
    getBuyBoxes.short_description = "Seçili ürünlerin BuyBoxını getir."


@admin.register(UpdateStatusModel)
class UpdateStatusModelAdmin(admin.ModelAdmin):

    change_form_template = "hepsiburada_api/admin/list_update_control.html"
    list_display = ['control_id', 'date', ]
    readonly_fields = ['date']

    def response_change(self, request, obj):
        if "_control" in request.POST:

            message = obj.control()

            self.message_user(request, message)

            return HttpResponseRedirect(".")
        return super().response_change(request, obj)


class HepsiOrderDetailModelTabularInline(admin.TabularInline):
    model = HepsiOrderDetailModel
    extra = 0


class HepsiBillModelTabularInline(admin.TabularInline):
    model = HepsiBillModel
    extra = 0
    raw_id_fields = ["hom", "hodm", "hpm"]


@admin.register(HepsiOrderModel)
class HepsiOrderModelAdmin(admin.ModelAdmin):
    inlines = [HepsiOrderDetailModelTabularInline, HepsiBillModelTabularInline]

    change_list_template = "hepsiburada_api/admin/get_hborder.html"
    change_form_template = "hepsiburada_api/admin/cancelOrder.html"

    search_fields = ["orderNumber", "customerModel", "packageNumber", ]

    list_display = ["__str__", "customerModel", "totalPrice",
                    "orderDate", "getDetailCount", ]
    list_filter = [("orderDate", DateTimeRangeFilter), ]

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
        HepsiOrderModule().getHepsiOldOrders(request.FILES.get("excel"))
        self.message_user(request, "Siparişler getirildi...")
        return HttpResponseRedirect("../")

    def get_hb_order(self, request):

        HepsiOrderModule().getHepsiOrders()

        self.message_user(request, "Siparişler getirildi...")
        return HttpResponseRedirect("../")

    def getPackageDetails(self, request):
        HepsiOrderModule().setPackageDetails()
        self.message_user(request, "Paket detayları getirildi.")
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
    list_display = ["__str__", "getOrderDate",
                    "paymentDate", "invoiceDate", "hom", "totalAmount"]
    list_filter = [("invoiceDate", DateTimeRangeFilter),
                   "transactionType", "hpm"]
    ordering = ["paymentDate"]

    autocomplete_fields = ["hom", ]
