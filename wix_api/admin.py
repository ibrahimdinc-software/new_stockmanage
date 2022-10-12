from django.contrib import admin
from wix_api.models import WixAuthTokensModel, WixProductModel, WixProductUpdateModel

# Register your models here.


class WixProductUpdateModelTabularInline (admin.TabularInline):
    model = WixProductUpdateModel
    extra = 0

@admin.register(WixAuthTokensModel)
class WixAuthTokensModelAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'time',]


@admin.register(WixProductModel)
class WixProductModelAdmin(admin.ModelAdmin):
    inlines = [WixProductUpdateModelTabularInline,]


