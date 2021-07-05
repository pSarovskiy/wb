from django.urls import path
from .views import List, Detail, Delete, product_add

urlpatterns = [
    path('', List.as_view(), name='product-list'),
    path('add/', product_add, name='product-add'),
    path('delete/<int:pk>/', Delete.as_view(), name='product-delete'),
    path('<int:pk>/', Detail.as_view(), name='product-detail'),
]
