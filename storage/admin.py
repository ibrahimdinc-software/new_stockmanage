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
    class Meta:
        model = ProductModel
    

    def save_model(self, request, obj, form, change):
        print(form)
        super().save_model(request, obj, form, change)


@admin.register(BaseProductModel)
class BaseProductModelAdmin(admin.ModelAdmin):
    
    change_list_template = "storage/admin/get_products.html"
    list_display=["name","barcode","piece"]
    ordering = ["name"]

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
                p.save()
        return HttpResponseRedirect("../")

#!admin.site.register(MedProductModel)

