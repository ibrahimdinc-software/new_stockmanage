
from django.views.generic import UpdateView, CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

from rest_framework import generics

from .forms import BaseProductModelForm
from .models import BaseProductModel, ProductModel
from .serializers import BaseProductModelSerializer, ProductModelSeriailzer

# Create your views here.


class BaseProductList(generics.ListAPIView):
    queryset = BaseProductModel.objects.all()
    serializer_class = BaseProductModelSerializer


class ProductList(generics.ListAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductModelSeriailzer


class BaseProductCreateView(CreateView, SuccessMessageMixin):
    template_name = "storage/baseProductCreateView.html"
    model = BaseProductModel
    form_class = BaseProductModelForm


class BaseProductUpdateView(UpdateView, SuccessMessageMixin):
    template_name = "storage/baseProductCreateView.html"
    model = BaseProductModel
    form_class = BaseProductModelForm


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
