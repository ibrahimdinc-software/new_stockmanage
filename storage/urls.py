from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('baseProducts/', views.BaseProductListView.as_view(), name="baseProductsListView"),
    path('baseProducts/detail/<int:pk>', views.BaseProductDetailView.as_view(), name="baseProductsDetailView"),
    #path('api/baseProducts/', views.BaseProductList.as_view()),
    #path('api/baseProducts/<int:pk>/', views.BaseProductDetail.as_view()),
]

#urlpatterns = format_suffix_patterns(urlpatterns)
