from errorLogger.models import ErrorLoggingModel
from django.contrib import admin

# Register your models here.


@admin.register(ErrorLoggingModel)
class ErrorLoggingModelAdmin(admin.ModelAdmin):
    pass
