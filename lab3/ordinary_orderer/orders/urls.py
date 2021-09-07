from django.urls import path
from . import views


app_name = 'orders'
urlpatterns = [
    path('', views.show, name='show'),
    path('create/', views.create, name='create'),
    path('<uuid:order_uuid>/', views.detail, name='detail'),
    path('<uuid:order_uuid>/update/', views.update, name='update'),
    path('<uuid:order_uuid>/delete/', views.delete, name='delete'),
    path('<uuid:order_uuid>/accept/', views.accept, name='accept'),
    path('<uuid:order_uuid>/call_done/', views.call_done, name='call_done'),
    path('<uuid:order_uuid>/set_done/', views.set_done, name='set_done')
]
