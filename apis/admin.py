# finance/admin.py
from django.contrib import admin
from .models import Profile, Deposit, Withdrawal, Bonus, DepositAccounts, Config, VoteCoin, CryptoAccounts, voteWinner, betWinner, betLoser, totalbetslost

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'phone_no', 'date_joined', 'level_1', 'level_2', 'level_3', 'gameId']
    search_fields = ['user__username', 'email', 'phone_no', 'gameId']
    list_filter = ['date_joined']

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'amount', 'source', 'confirmed']
    search_fields = ['user__username', 'source']
    list_filter = ['date', 'confirmed']

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = [ 'user', 'amount', 'fee',  'date', 'confirmed']
    search_fields = [ 'user__username',]
    list_filter = ['date', 'confirmed','user']

@admin.register(Bonus)
class BonusAdmin(admin.ModelAdmin):
    list_display = ['amount', 'giver', 'receiver', 'date']
    search_fields = ['giver__username', 'receiver__username']
    list_filter = ['date']

@admin.register(DepositAccounts)
class DepositAccountsAdmin(admin.ModelAdmin):
    list_display = ['account_name', 'account_number', 'account_company', 'date']
    search_fields = ['account_name', 'account_number']
    list_filter = ['date','account_limit']
    
@admin.register(CryptoAccounts)
class CryptoAccountsAdmin(admin.ModelAdmin):
    list_display = ['account_name', 'account_address', 'account_network', 'date']
    search_fields = ['account_name', 'account_address']
    list_filter = ['date','account_limit']
#
admin.site.register(Config)
admin.site.register(VoteCoin)
admin.site.register(voteWinner)
admin.site.register(betWinner)
admin.site.register(betLoser)
admin.site.register(totalbetslost)

