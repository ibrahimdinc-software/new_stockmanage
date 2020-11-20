from django.contrib import admin

from django.http import HttpResponseRedirect
from django.urls import path

from .models import TrendProductModel, TrendMedProductModel, TrendOrderModel, TrendOrderDetailModel, TrendUpdateQueueModel

from .tr_module import ProductModule, OrderModule
# Register your models here.

class TrendMedProductModelTabularInline(admin.TabularInline):
    model = TrendMedProductModel
    extra = 0
    autocomplete_fields = ["tpm"]

@admin.register(TrendProductModel)
class TrendProductModelAdmin(admin.ModelAdmin):
    change_list_template = ["trendyol_api/admin/get_products.html"]
    
    search_fields = ["sku","barcode","name"]
    actions = ['send_list']
    list_display = ['__str__', 'sku', 'barcode', 'salePrice', 'piece', 'onSale']


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
        
        self.message_user(request, "Listeye Aldım la")

    send_list.short_description = "Seçili ürünleri trendyola gönder."


@admin.register(TrendUpdateQueueModel)
class HTrendUpdateQueueModelAdmin(admin.ModelAdmin):
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
    change_list_template = "trendyol_api/admin/get_trorder.html"
    list_display = ["__str__", "customerName","totalPrice", "orderDate", "getDetailCount"]
    inlines = [TrendOrderDetailModelTabularInline]

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








