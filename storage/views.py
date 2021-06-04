from typing import List
from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import BaseProductModel
from .serializers import BaseProductModelSerializer
from rest_framework import generics

# Create your views here.


class BaseProductListView(ListView):
    template_name = "storage/baseProductListView.html"
    model = BaseProductModel

class BaseProductDetailView(DetailView):
    template_name = "storage/baseProductDetailView.html"
    model = BaseProductModel






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
