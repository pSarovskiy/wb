from django.urls import path

from .views import *

urlpatterns = [
    path('list/', ProductList.as_view()),
    path('data/', product_info),
    path('add/', product_add),
    path('delete/<int:pk>/', product_delete),
    path('views/<int:pk>/', product_views),
]
