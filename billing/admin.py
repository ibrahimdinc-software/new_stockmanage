from django.contrib import admin

from .models import CurrentModel
# Register your models here.



@admin.register(CurrentModel)
class CurrentModelAdmin(admin.ModelAdmin):
    pass


