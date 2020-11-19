from django.contrib import admin

from .models import ProductModel, BaseProductModel, MedProductModel

from hepsiburada_api.admin import HepsiMedProductModelTabularInline
from trendyol_api.admin import TrendMedProductModelTabularInline

# Register your models here.


class MedProductModelTabularInline(admin.TabularInline):
    model = MedProductModel
    extra = 0

class ProductModelAdmin(admin.ModelAdmin):
    inlines = [
        MedProductModelTabularInline, 
        HepsiMedProductModelTabularInline,
        TrendMedProductModelTabularInline
    ]
    class Meta:
        model = ProductModel
    """#!
    def save_formset(self, request, form, formset, change):
        print(dir(formset.data))
        print(formset.form)
        piece = formset.forms[0].instance.base_product.piece / formset.forms[0].instance.piece
        for i in formset.forms:
            if piece > i.instance.base_product.piece / i.instance.piece:
                piece = i.instance.base_product.piece / i.instance.piece
        form.instance.piece = piece
        form.instance.save()
        super(ProductModelAdmin, self).save_formset(request, form, formset, change)
    """
    def save_model(self, request, obj, form, change):
        print(form)
        super().save_model(request, obj, form, change)

admin.site.register(ProductModel, ProductModelAdmin)
admin.site.register(BaseProductModel)
#!admin.site.register(MedProductModel)

