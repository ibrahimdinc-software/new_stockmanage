from django.contrib import admin

from django.http import HttpResponseRedirect
from django.urls import path

from .models import HepsiProductModel, UpdateStatusModel, HepsiOrderModel, HepsiOrderDetailModel, HepsiMedProductModel

from .hb_module import ListingModule, OrderModule

# Register your models here.


class HepsiMedProductModelTabularInline(admin.TabularInline):
    model = HepsiMedProductModel
    extra = 0
    autocomplete_fields = ["hpm"]

@admin.register(HepsiProductModel)
class HepsiProductModelAdmin(admin.ModelAdmin):
    
    search_fields = ["HepsiburadaSku","MerchantSku",]

    change_list_template = "entities/get_productlist.html"
    list_display = ['MerchantSku','HepsiburadaSku',  'is_salable',]
    actions = ['send_list','delete_all']


    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('getlist/', self.get_list),
        ]
        return my_urls + urls

    def get_list(self, request):
        
        ListingModule().createProducts()
        
        self.message_user(request, "Ürünler geldii hanıım...")
        return HttpResponseRedirect("../")

    def send_list(self, request, queryset):

        ListingModule().sendProducts(queryset)

        self.message_user(request, "Emmioğluu senin ürünler hepsiburadaya vardı.")

    def delete_all(self, request, queryset):
        ListingModule().deleteAll(queryset)

        self.message_user(request, "Silindi.")

    delete_all.short_description = "Seçili ürünleri hepsiburadadan sil!"
    send_list.short_description = "Seçili ürünleri hepsiburadaya gönder."

@admin.register(UpdateStatusModel)
class UpdateStatusModelAdmin(admin.ModelAdmin):

    change_form_template = "entities/list_update_control.html"
    list_display = ['control_id', 'date',]
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


@admin.register(HepsiOrderModel)
class HepsiOrderModelAdmin(admin.ModelAdmin):
    change_list_template = "entities/get_hborder.html"
    inlines = [HepsiOrderDetailModelTabularInline]

    list_display = ["__str__", "customerName", "totalPrice", "orderDate", "getDetailCount"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('gethborders/', self.get_hb_order),
        ]
        return my_urls + urls

    def get_hb_order(self, request):
    
        OrderModule().getOrders()
        
        self.message_user(request, "Siparişler gelmiştir ha...")
        return HttpResponseRedirect("../")