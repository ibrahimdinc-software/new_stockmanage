from datetime import date
from django.contrib import admin
from rangefilter.filter import DateTimeRangeFilter

from django.http import HttpResponseRedirect
from django.urls import path

from .models import TrendProductModel, TrendMedProductModel, TrendOrderModel, TrendOrderDetailModel, TrendUpdateQueueModel, TrendProductBuyBoxListModel

from .tr_module import ProductModule, OrderModule
# Register your models here.


class TrendMedProductModelTabularInline(admin.TabularInline):
    model = TrendMedProductModel
    extra = 0
    autocomplete_fields = ["tpm"]

class TrendProductBuyBoxListModelTabularInline(admin.TabularInline):
    model = TrendProductBuyBoxListModel
    extra = 0
    ordering = ('rank',)

@admin.register(TrendProductModel)
class TrendProductModelAdmin(admin.ModelAdmin):
    change_list_template = ["trendyol_api/admin/get_products.html"]
    change_form_template = "trendyol_api/admin/updateProduct.html"
    
    search_fields = ["sku","barcode","name"]
    actions = ['send_list', 'getBuyBoxes']

    list_filter = ["onSale",]
    list_display = ['name', 'salePrice', 'piece', 'onSale', 'buyBoxRank', "countOfRelated"]
    
    readonly_fields = ["productLinkF"]

    inlines = [TrendMedProductModelTabularInline, TrendProductBuyBoxListModelTabularInline,]

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
        ProductModule().buyboxList(queryset)
        

    def response_change(self, request, obj):
        if "update" in request.POST:
            obj.save()
            obj.updateStock()
            self.message_user(request, "Bekleme listesine alındı en geç 5 dk içinde güncellenecek.\n Elle güncelleyebilirsiniz.")
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


@admin.register(TrendUpdateQueueModel)
class TrendUpdateQueueModelAdmin(admin.ModelAdmin):
    list_display = ["tpm", "date"]
    change_list_template = "trendyol_api/admin/trUpdateQueue.html"

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



class TrendOrderDetailModelTabularInline(admin.TabularInline):
    model = TrendOrderDetailModel
    extra = 0


@admin.register(TrendOrderModel)
class TrendOrderModelAdmin(admin.ModelAdmin):
    inlines = [TrendOrderDetailModelTabularInline]
    
    change_list_template = "trendyol_api/admin/get_trorder.html"
    change_form_template = "trendyol_api/admin/cancelOrder.html"
    
    list_display = ["__str__", "customerName","totalPrice", "orderDate", "getDetailCount"]
    list_filter = [("orderDate",DateTimeRangeFilter)]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('gettrorders/', self.get_tr_order),
        ]
        return my_urls + urls

    def get_tr_order(self, request):
        
        OrderModule().getOrders()
        print("WORK")
        self.message_user(request, "Siparişler gelmiştir ha...")
        return HttpResponseRedirect("../")

    def response_change(self, request, obj):
        if "cancelOrder" in request.POST:

            obj.canceledOrder()
            self.message_user(request, "İptal Edildi")

            return HttpResponseRedirect(".")
        return super().response_change(request, obj)







