from django.contrib import admin

from django.http import HttpResponseRedirect
from django.urls import path

from .models import NProductImageModel, NProductModel, NUpdateQueueModel
from .adminFilter import OnSaleFilter
from .n_module import NProductModule

# Register your models here.




class NProductImageModelTabularInline (admin.TabularInline):
    model = NProductImageModel
    extra = 1
    ordering = ('order',)




@admin.register(NProductModel)
class NProductModelAdmin(admin.ModelAdmin):
    class Media:
        js = ('ckeditor.js',)
    change_list_template = ["trendyol_api/admin/get_products.html"]

    search_fields = ["sku", "productName"]
    list_display = ["productName", "salePrice", "availableStock"]

    inlines = [NProductImageModelTabularInline]

    list_filter = [OnSaleFilter]
    
    actions = ['send_list']

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('getlist/', self.get_list),
        ]
        return my_urls + urls

    def get_list(self, request):

            result = NProductModule().getProducts()
            if result:
                self.message_user(request, result)
            else:
                self.message_user(request, "Ürünler geldii hanıım...")
            return HttpResponseRedirect("../")
    
    def send_list(self, request, queryset):
        NProductModule().updateQueue(queryset)
        self.message_user(request, "Bekleme listesine eklendi.")





    send_list.short_description = "Seçili ürünleri N11'e gönder."



@admin.register(NUpdateQueueModel)
class NUpdateQueueModelAdmin(admin.ModelAdmin):
    list_display = ["npm", "date"]
    change_list_template = "nonbir_api/admin/nUpdateQueue.html"

    readonly_fields = ["date"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('updateQueue/', self.updateQueue),
        ]
        return my_urls + urls

    def updateQueue(self, request):
        
        res = NProductModule().updateProducts()
        
        self.message_user(request, res)
        return HttpResponseRedirect("../")





