from django.urls import path
from . import views


urlpatterns = [
    path('accounts/', views.AccountListAPIView.as_view(), name='index'),
    path('accounts/register/', views.RegisterAPIView.as_view()),
    path('accounts/login/', views.obtain_auth_token),
    path('accounts/<str:username>/',
         views.DisplayUpdateDeleteAccountAPIView.as_view()),
    path('profile/', views.get_current_account_detail),

    path('orders/', views.ListCreateOrderAPIView.as_view()),
    path('orders/<uuid:id>/', views.DisplayUpdateDeleteOrderAPIView.as_view()),
    path('orders/<uuid:id>/perform_action/', views.make_order_action),

    path('wallets/', views.ListDisplayWalletAPIView.as_view()),
    path('wallets/admin/', views.AdminListDisplayWalletAPIView.as_view()),
    path('wallets/admin/create/', views.AdminCreateWalletAPIView.as_view()),
    path('wallets/admin/<str:walletname>/',
         views.AdminUpdateDeleteWalletAPIView.as_view()),
    path('wallets/add/', views.add_wallet),
    path('wallets/<str:walletname>/remove/', views.remove_wallet),
]
