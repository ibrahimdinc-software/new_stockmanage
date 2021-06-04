from django.contrib.admin import SimpleListFilter

class OnSaleFilter(SimpleListFilter):
    title = 'onSale'
    parameter_name = 'onSale'

    def lookups(self, request, model_admin):
        return (
            ('true','Satışta',),
            ('false','Satışta değil',),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(availableStock__gte=1)
        if self.value() == 'false':
            return queryset.filter(availableStock__lte=0)
        if self.value() == None:
            return queryset
