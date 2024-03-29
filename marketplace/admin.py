from django.contrib.admin.decorators import register
from django.urls import path
from django.contrib import admin
from django.http import HttpResponseRedirect

from rangefilter.filter import DateTimeRangeFilter
from import_export.admin import ImportExportActionModelAdmin
import requests

from .resources import MarketOrderModelResource
from .models import MarketBuyBoxTraceModel, MarketMedProductModel, MarketOrderPredCostModel, MarketProductBuyBoxListModel, MarketProductCommissionModel, MarketUpdateQueueModel, MarketProductModel, MarketOrderModel, MarketOrderDetailModel, UserMarketPlaceModel, UserMarketShipmentRuleModel
from .module import ProductModule, OrderModule, ProfitModule
# Register your models here.


class UserMarketShipmentRuleModelTabularInline(admin.TabularInline):
    model = UserMarketShipmentRuleModel
    extra = 0


@admin.register(UserMarketPlaceModel)
class UserMarketPlaceModelAdmin(admin.ModelAdmin):
    inlines = [UserMarketShipmentRuleModelTabularInline]



class MarketProductBuyBoxListModelTabularInline (admin.TabularInline):
    model = MarketProductBuyBoxListModel
    extra = 0
    ordering = ('rank',)


class MarketMedProductModelTabularInline(admin.TabularInline):
    model = MarketMedProductModel
    extra = 0
    autocomplete_fields = ["mpm"]


class MarketBuyBoxTraceModelTabularInline(admin.TabularInline):
    model = MarketBuyBoxTraceModel
    extra = 0


class MarketProductCommissionModelTabularInline(admin.TabularInline):
    model = MarketProductCommissionModel
    extra = 0


@admin.register(MarketProductModel)
class MarketProductModelAdmin(admin.ModelAdmin):
    ordering = ("-buyBoxRank",)

    change_list_template = ["trendyol_api/admin/get_products.html"]
    change_form_template = "trendyol_api/admin/updateProduct.html"

    search_fields = ["marketplaceSku", "sellerSku", ]
    actions = ['send_list', 'getBuyBoxes']

    list_filter = ["onSale", "userMarket"]
    list_display = ['sellerSku', 'salePrice', 'availableStock',
                    'onSale', 'buyBoxRank', "lastControlDate"]

    inlines = [
        MarketBuyBoxTraceModelTabularInline,
        MarketMedProductModelTabularInline,
        MarketProductBuyBoxListModelTabularInline,
        MarketProductCommissionModelTabularInline
    ]

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
            self.message_user(request, "Ürünler geldi...")
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
                self.message_user(request, "Buybox getirildi.")
            return HttpResponseRedirect(".")
        if "getBuyBoxTest" in request.POST:
            message = ProductModule().cronBuyBoxTest(obj)
            if message:
                self.message_user(request, message)
            else:
                self.message_user(request, "Buybox getirildi.")
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

        self.message_user(request, "Ürünler pazar yerlerine gönderildi.")
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


@admin.register(MarketBuyBoxTraceModel)
class MarketBuyBoxTraceModelAdmin(admin.ModelAdmin):
    list_display = ["marketProduct", "minPrice", "maxPrice", "priceStep"]

    objId = None

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.objId = obj.marketProduct.id
        return super().get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'marketProduct':
            distinct = MarketBuyBoxTraceModel.objects.exclude(
                marketProduct=self.objId).values_list('marketProduct_id').distinct()
            kwargs["queryset"] = MarketProductModel.objects.filter(
                onSale=True).exclude(id__in=distinct)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class MarketOrderDetailModelTabularInline(admin.TabularInline):
    model = MarketOrderDetailModel
    extra = 0


class MarketOrderPredCostModelTabularInline(admin.TabularInline):
    model = MarketOrderPredCostModel
    extra = 1

    objId = None


    def get_formset(self, request, obj=None, **kwargs):
        if obj:
            self.objId = obj.id
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'modm':
            kwargs["queryset"] = MarketOrderDetailModel.objects.filter(mom=self.objId)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(MarketOrderModel)
class MarketOrderModelAdmin(ImportExportActionModelAdmin):
    inlines = [MarketOrderDetailModelTabularInline, MarketOrderPredCostModelTabularInline]

    change_list_template = "market/admin/get_order.html"
    change_form_template = "trendyol_api/admin/cancelOrder.html"
    
    list_display = ["__str__", "userMarket", "customerModel",
                    "totalPrice", "orderDate", "getDetailCount", "orderStatus"]
    list_filter = [
        "userMarket",
        ("orderDate", DateTimeRangeFilter),
        ("deliveryDate", DateTimeRangeFilter),
        "orderStatus"]

    readonly_fields = ["getProfit"]

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
        self.message_user(request, "Siparişler getirildi...")
        return HttpResponseRedirect("../")

    def getOldOrders(self, request):
        OrderModule().getOldOrders(request.POST.get("date"))
        self.message_user(request, "Siparişler getirildi...")
        return HttpResponseRedirect("../")

    def getdeliverdorders(self, request):
        OrderModule().getDeliveredOrders()
        self.message_user(request, "Siparişler getirildi...")
        return HttpResponseRedirect("../")

    def response_change(self, request, obj):
        if "cancelOrder" in request.POST:

            obj.canceledOrder()
            self.message_user(request, "İptal Edildi")

            return HttpResponseRedirect(".")

        if "calcProfit" in request.POST:
            ProfitModule().calcProfit(obj)
            self.message_user(request, "Kâr Hesaplandı")
            return HttpResponseRedirect(".")

        return super().response_change(request, obj)
