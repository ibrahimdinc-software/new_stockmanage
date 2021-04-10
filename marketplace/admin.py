from django.urls import path
from django.contrib import admin
from django.http import HttpResponseRedirect

from rangefilter.filter import DateTimeRangeFilter
from import_export.admin import ImportExportActionModelAdmin
import requests

from .resources import MarketOrderModelResource
from .models import MarketMedProductModel, MarketProductBuyBoxListModel, MarketUpdateQueueModel, MarketProductModel, MarketOrderModel, MarketOrderDetailModel
from .module import ProductModule, OrderModule
# Register your models here.


class MarketProductBuyBoxListModelTabularInline (admin.TabularInline):
    model = MarketProductBuyBoxListModel
    extra = 0
    ordering = ('rank',)


class MarketMedProductModelTabularInline(admin.TabularInline):
    model = MarketMedProductModel
    extra = 0
    autocomplete_fields = ["mpm"]


@admin.register(MarketProductModel)
class MarketProductModelAdmin(admin.ModelAdmin):
    change_list_template = ["trendyol_api/admin/get_products.html"]
    change_form_template = "trendyol_api/admin/updateProduct.html"

    search_fields = ["marketplaceSku", "sellerSku", ]
    actions = ['send_list', 'getBuyBoxes']

    list_filter = ["onSale", "marketType"]
    list_display = ['sellerSku', 'salePrice', 'availableStock',
                    'onSale', 'buyBoxRank']

    inlines = [MarketMedProductModelTabularInline,
               MarketProductBuyBoxListModelTabularInline, ]

    readonly_fields = ["productLinkF"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('getlist/', self.get_list),
        ]
        return my_urls + urls

    def get_list(self, request):

        result = ProductModule().getProducts()
        if result:
            self.message_user(request, result)
        else:
            self.message_user(request, "Ürünler geldii hanıım...")
        return HttpResponseRedirect("../")

    def send_list(self, request, queryset):

        ProductModule().updateQueue(queryset)

        self.message_user(request, "Bekleme listesine eklendi.")

    def getBuyBoxes(self, request, queryset):
        message = ProductModule().buyboxList(queryset)
        self.message_user(request, message)

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
                self.message_user(request, "Geldi mi bak")
            return HttpResponseRedirect(".")

        return super().response_change(request, obj)

    send_list.short_description = "Seçili ürünleri trendyola gönder."
    getBuyBoxes.short_description = "Seçili ürünlerin BuyBoxını getir."


@admin.register(MarketUpdateQueueModel)
class MarketUpdateQueueModelAdmin(admin.ModelAdmin):
    list_display = ["date", "mpm", "isUpdated"]
    list_filter = ["isUpdated", ]
    change_list_template = "market/admin/updateQueue.html"

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


@admin.register(MarketMedProductModel)
class MarketMedProductModelAdmin(admin.ModelAdmin):
    list_display = ['product', 'mpm', 'isSalable', ]
    actions = ["outOfStock"]

    def outOfStock(self, request, queryset):
        for q in queryset:
            q.isSalable = False
            q.mpm.removeFromSale()
            q.save()
        self.message_user(request, "Stoklar sıfırlandı.")

    outOfStock.short_description = "Seçili ürünlerin satışını kapat."


class MarketOrderDetailModelTabularInline(admin.TabularInline):
    model = MarketOrderDetailModel
    extra = 0


@admin.register(MarketOrderModel)
class MarketOrderModelAdmin(ImportExportActionModelAdmin):
    inlines = [MarketOrderDetailModelTabularInline]

    change_list_template = "market/admin/get_order.html"
    change_form_template = "trendyol_api/admin/cancelOrder.html"

    list_display = ["__str__", "marketType", "customerName",
                    "totalPrice", "orderDate", "getDetailCount", "orderStatus"]
    list_filter = [
        "marketType",
        ("orderDate", DateTimeRangeFilter),
        ("deliveryDate", DateTimeRangeFilter),
        "orderStatus"]

    resource_class = MarketOrderModelResource

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('getorders/', self.getOrder),
            path('getoldorders/', self.getOldOrders),
            path('getdeliverdorders/', self.getdeliverdorders),
        ]
        return my_urls + urls

    def getOrder(self, request):
        OrderModule().getOrders()
        self.message_user(request, "Siparişler gelmiştir ha...")
        return HttpResponseRedirect("../")

    def getOldOrders(self, request):
        OrderModule().getOldOrders(request.POST.get("date"))
        self.message_user(request, "Siparişler gelmiştir ha...")
        return HttpResponseRedirect("../")

    def getdeliverdorders(self, request):
        OrderModule().getDeliveredOrders()
        self.message_user(request, "Siparişler gelmiştir ha...")
        return HttpResponseRedirect("../")

    def response_change(self, request, obj):
        if "cancelOrder" in request.POST:

            obj.canceledOrder()
            self.message_user(request, "İptal Edildi")

            return HttpResponseRedirect(".")
        return super().response_change(request, obj)
