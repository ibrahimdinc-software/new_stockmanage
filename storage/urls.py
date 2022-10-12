from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('baseProducts/edit/<int:pk>', views.BaseProductUpdateView.as_view(), name="baseProductsUpdateView"),
    path('baseProducts/add/', views.BaseProductCreateView.as_view(), name="baseProductsCreateView"),
    path('api/baseProducts/', views.BaseProductList.as_view()),
    path('api/product/', views.ProductList.as_view()),
    
    #path('api/baseProducts/<int:pk>/', views.BaseProductDetail.as_view()),
]

#urlpatterns = format_suffix_patterns(urlpatterns)
