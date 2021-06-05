from django.contrib import admin
from wix_api.models import WixAuthTokensModel

# Register your models here.


@admin.register(WixAuthTokensModel)
class WixAuthTokensModelAdmin(admin.ModelAdmin):
    pass