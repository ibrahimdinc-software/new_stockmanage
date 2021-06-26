
from django.views.generic import ListView, UpdateView, CreateView
from django.contrib.messages.views import SuccessMessageMixin

from rest_framework import generics

from .forms import BaseProductModelForm
from .models import BaseProductModel
from .serializers import BaseProductModelSerializer

# Create your views here.


class BaseProductListView(ListView):
    template_name = "storage/baseProductListView.html"
    model = BaseProductModel


class BaseProductCreateView(CreateView, SuccessMessageMixin):
    template_name = "storage/baseProductCreateView.html"
    model = BaseProductModel
    form_class = BaseProductModelForm

    success_message = 'Temel ürün başarıyla eklendi!'


class BaseProductUpdateView(UpdateView):
    template_name = "storage/baseProductUpdateView.html"
    







"""
class BaseProductList(generics.ListCreateAPIView):
    queryset = BaseProductModel.objects.all()
    serializer_class = BaseProductModelSerializer


class BaseProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = BaseProductModel.objects.all()
    serializer_class = BaseProductModelSerializer

    def options(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

"""
