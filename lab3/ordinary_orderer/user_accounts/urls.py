from django.urls import path
from . import views


app_name = 'user_accounts'
urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.account_login, name='login'),
    path('<str:username>/logout/', views.account_logout, name='logout'),
    path('<str:username>/', views.info, name='info'),
    path('<str:username>/update/', views.update, name='update'),
    path('<str:username>/delete/', views.delete, name='delete'),
]
