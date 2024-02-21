from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pages/', views.page_list, name='page_list'),
    path('pages/create/', views.page_create, name='page_create'),
    path('pages/<int:pk>/', views.page_detail, name='page_detail'),
    path('page/<int:pk>/edit/', views.page_update, name='page_update'),
    path('page/<int:pk>/delete/', views.page_delete, name='page_delete'),
    path('pages/<int:pk>/published/', views.page_published, name='page_published'),  
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('category/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),  
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('category/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('category/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
]

