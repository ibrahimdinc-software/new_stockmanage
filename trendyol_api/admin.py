from datetime import date
from django.contrib import admin
from rangefilter.filter import DateTimeRangeFilter

from django.http import HttpResponseRedirect
from django.urls import path

from import_export.admin import ImportExportModelAdmin
from .resources import TrendOrderModelResource

from .models import TrendProductModel, TrendOrderModel, TrendOrderDetailModel

from .tr_module import TrendProductModule, TrendOrderModule

from marketplace.module import ProductModule
from marketplace.admin import MarketProductBuyBoxListModelTabularInline, MarketMedProductModelTabularInline, MarketOrderDetailModelTabularInline
# Register your models here.



@admin.register(TrendProductModel)
class TrendProductModelAdmin(admin.ModelAdmin):
    change_list_template = ["trendyol_api/admin/get_products.html"]
    change_form_template = "trendyol_api/admin/updateProduct.html"

    search_fields = ["sellerSku", "marketplaceSku", "productName"]
    actions = ['send_list', 'getBuyBoxes']

    list_filter = ["onSale", ]
    list_display = ['productName', 'salePrice', 'availableStock',
                    'onSale', 'buyBoxRank', "countOfRelated"]

    readonly_fields = ["productLinkF", "related"]

    inlines = [MarketMedProductModelTabularInline,
               MarketProductBuyBoxListModelTabularInline, ]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('getlist/', self.get_list),
        ]
        return my_urls + urls

    def get_list(self, request):

        result = TrendProductModule().getTrendProducts()
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



@admin.register(TrendOrderModel)
class TrendOrderModelAdmin(ImportExportModelAdmin):
    inlines = [MarketOrderDetailModelTabularInline]

    change_list_template = "trendyol_api/admin/get_trorder.html"
    change_form_template = "trendyol_api/admin/cancelOrder.html"

    list_display = ["__str__", "customerModel",
                    "totalPrice", "orderDate", "getDetailCount"]
    list_filter = [("orderDate", DateTimeRangeFilter)]

    resource_class = TrendOrderModelResource

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('gettrorders/', self.get_tr_order),
        ]
        return my_urls + urls

    def get_tr_order(self, request):

        TrendOrderModule().getTrendOrders()
        self.message_user(request, "Siparişler gelmiştir ha...")
        return HttpResponseRedirect("../")

    def response_change(self, request, obj):
        if "cancelOrder" in request.POST:

            obj.canceledOrder()
            self.message_user(request, "İptal Edildi")

            return HttpResponseRedirect(".")
        return super().response_change(request, obj)
