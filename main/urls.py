
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('unassigned/', views.UnassignedProductListView.as_view()),
    path('unassignedHB/', views.UnassignedProductHBListView.as_view()),
    path('losedBuyboxHB/', views.LosedBuyboxHBListView.as_view()),
    path('unassignedTR/', views.UnassignedProductTRListView.as_view()),
    path('losedBuyboxTR/', views.LosedBuyboxTRListView.as_view()),
]
