from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pages/', views.page_list, name='page_list'),
    path('pages/<int:pk>/', views.page_detail, name='page_detail'),
    path('pages/<int:pk>/published/', views.page_published, name='page_published'),    
]