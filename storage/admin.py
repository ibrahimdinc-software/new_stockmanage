import pandas as pd
import math

from django.contrib import admin

from django.http import HttpResponseRedirect
from django.urls import path

from .models import ProductModel, BaseProductModel, MedProductModel

from hepsiburada_api.admin import HepsiMedProductModelTabularInline
from trendyol_api.admin import TrendMedProductModelTabularInline

# Register your models here.


class MedProductModelTabularInline(admin.TabularInline):
    model = MedProductModel
    extra = 0
    autocomplete_fields = ["base_product"]

@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    inlines = [
        MedProductModelTabularInline, 
        HepsiMedProductModelTabularInline,
        TrendMedProductModelTabularInline
    ]

    list_display=["name", "sku", "piece"]
    change_form_template = "storage/admin/productPage.html"
    #search_fields = ["hepsimedproductmodel.__str__","trendmedproductmodel.__str__"]

    def response_change(self, request, obj):
        if "setStock" in request.POST:
            obj.setStock()
            self.message_user(request, "Stok belirlendi.")

            return HttpResponseRedirect(".")
        elif "updateToMarkets" in request.POST:
            obj.setMedProductStocks()
            
            return HttpResponseRedirect(".")

        return super().response_change(request, obj)

@admin.register(BaseProductModel)
class BaseProductModelAdmin(admin.ModelAdmin):
    
    change_list_template = "storage/admin/get_products.html"
    change_form_template = "storage/admin/baseProduct.html"
    list_display=["name","barcode","piece"]
    ordering = ["name"]
    actions = ['set_stock']

    search_fields = ["name","barcode",]


    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('getProducts/', self.getProductsFromExcel),
        ]
        return my_urls + urls

    def getProductsFromExcel(self, request):
        excel = pd.read_excel(request.FILES.get("excel"))
        products = BaseProductModel.objects.all()
        for product in excel.iloc:
            barcode = 0 if math.isnan(product.get("Barcode")) else product.get("Barcode")
            p = products.filter(name=product.get("Item"),barcode=barcode)
            print(p)
            if not p:
                p = BaseProductModel(
                    name=product.get("Item"),
                    barcode=barcode,
                    piece=product.get("Quantity")
                )
            else:
                p = p[0]
                p.piece = product.get("Quantity")
            p.save()
        return HttpResponseRedirect("../")

    def response_change(self, request, obj):
        if "setStock" in request.POST:
            obj.setMedProductStock()
            self.message_user(request, "Güncellendi.")

            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    def set_stock(self, request, queryset):
        for obj in queryset:
            obj.setMedProductStock()
        self.message_user(request, "Güncellendi.")
    
    set_stock.short_description = "Bağlı ürünlerin stoklarını güncelle!"

#!admin.site.register(MedProductModel)

