from django.shortcuts import render

from .main_module import ProductModule

# Create your views here.

def index(request):


    context = {
        'unassigned': len(ProductModule().getUnassigned()),
        'test':ProductModule().getUnassigned()
    }
    print()
    return render(request, "main/index.html", context=context)