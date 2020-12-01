from django.contrib import admin
from rangefilter.filter import DateTimeRangeFilter

from django.http import HttpResponseRedirect
from django.urls import path

from .models import HepsiProductModel, UpdateStatusModel, HepsiOrderModel, HepsiOrderDetailModel, HepsiMedProductModel, HepsiUpdateQueueModel

from .hb_module import ProductModule, OrderModule

# Register your models here.


class HepsiMedProductModelTabularInline(admin.TabularInline):
    model = HepsiMedProductModel
    extra = 0
    autocomplete_fields = ["hpm"]

@admin.register(HepsiProductModel)
class HepsiProductModelAdmin(admin.ModelAdmin):
    
    search_fields = ["HepsiburadaSku","MerchantSku",]

    change_list_template = "hepsiburada_api/admin/get_productlist.html"
    list_display = ['MerchantSku','HepsiburadaSku',  'is_salable',]
    actions = ['send_list']


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

    def response_change(self, request, obj):
        if "update" in request.POST:
            obj.save()
            obj.updateStock()
            self.message_user(request, "Bekleme listesine alındı en geç 5 dk içinde güncellenecek.\n Elle güncelleyebilirsiniz.")

            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    send_list.short_description = "Seçili ürünleri hepsiburadaya gönder."

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


@admin.register(HepsiOrderModel)
class HepsiOrderModelAdmin(admin.ModelAdmin):
    change_list_template = "hepsiburada_api/admin/get_hborder.html"
    change_form_template = "hepsiburada_api/admin/cancelOrder.html"
    inlines = [HepsiOrderDetailModelTabularInline]

    list_display = ["__str__", "customerName", "totalPrice", "orderDate", "getDetailCount"]
    list_filter = [("orderDate",DateTimeRangeFilter)]

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

    def response_change(self, request, obj):
        if "cancelOrder" in request.POST:

            obj.canceledOrder()
            self.message_user(request, "İptal Edildi")

            return HttpResponseRedirect(".")
        return super().response_change(request, obj)
    


#class HepsiOrderCancelModel(models.Mode)