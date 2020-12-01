from django.shortcuts import render
from django.views.generic import ListView

from .main_module import ProductModule

# Create your views here.

def index(request):


    context = {
        'unassigned': len(ProductModule().getUnassigned()),
        'unassignedHB': len(ProductModule().getUnassignedHB()),
        'unassignedTR': len(ProductModule().getUnassignedTR()),
    }
    print()
    return render(request, "main/index.html", context=context)




class UnassignedProductListView(ListView):
    template_name = "main/unassignedProductList.html"

    def get_queryset(self):
        return ProductModule().getUnassigned()

class UnassignedProductHBListView(ListView):
    template_name = "main/unassignedProductListHB.html"

    def get_queryset(self):
        return ProductModule().getUnassignedHB()

class UnassignedProductTRListView(ListView):
    template_name = "main/unassignedProductListHB.html"
    ordering = "name"
    def get_queryset(self):
        return ProductModule().getUnassignedTR()

