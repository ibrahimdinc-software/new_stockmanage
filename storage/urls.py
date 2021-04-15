from django.urls import path
from django.views.generic.list import BaseListView
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('baseProducts/', views.BaseProductListView.as_view(), name="baseProductsListView"),
    #path('api/baseProducts/', views.BaseProductList.as_view()),
    #path('api/baseProducts/<int:pk>/', views.BaseProductDetail.as_view()),
]

#urlpatterns = format_suffix_patterns(urlpatterns)
