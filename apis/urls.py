
from django.urls import path
from .deposit import create_deposit, get_available_accounts, get_deposit_history
from .views import user_profile, balance, configvalues,GetAccount,get_team_members, Swap

from .withdraw import create_withdrawal, get_withdrawal_history
urlpatterns = [
    path('create-deposit/', create_deposit, name='create-deposit'),
    path('available-accounts/<str:new_amount>/', get_available_accounts, name='available-accounts'),
    path('deposit-history/', get_deposit_history, name='deposit-history'),
    path('profile/', user_profile, name='user_profile'),
    path('balance/', balance,name="balance" ),
    path('config/', configvalues,name="config" ),
    # withdraw urls
    path('create-withdrawal/', create_withdrawal, name="withdraw"),
    path('withdrawal-history/', get_withdrawal_history, name="withdrawal-history"),
    # account urls
    path('account/', GetAccount, name="account"),
    path('get_team_members/', get_team_members, name="get_team_members"),
    path('swap/', Swap, name="Swap"),
    
]



