from django.urls import path
from . import views

urlpatterns = [
    path('customers/create/', views.create_customer),
    path('customers/', views.list_customers),
    path('accounts/create/', views.create_account),
    path('accounts/<str:account_number>/', views.get_account_by_number),
    path('accounts/update/<str:account_number>/', views.update_account),
    path('deposit/', views.deposit),
    path('withdraw/', views.withdraw),
    path('transfer/', views.transfer, name='transfer'),
    path('transactions/<str:account_number>/', views.transaction_history),
    path('accounts/delete/<str:account_number>/', views.delete_account),
    path('accounts/', views.get_all_accounts, name='get_all_accounts'),
    path('api/accounts/<str:account_number>/', views.get_account_by_number, name='get_account_by_number'),
  
]
