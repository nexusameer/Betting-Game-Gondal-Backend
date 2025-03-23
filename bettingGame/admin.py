from django.contrib import admin

# Register your models here.

from .models import Message, Allbets, Session, UserSessionBet, Voting, UserWallet, AddCustomWinningNumber

admin.site.register(Message)
admin.site.register(Allbets)
admin.site.register(Session)
admin.site.register(UserSessionBet)
admin.site.register(Voting)
admin.site.register(UserWallet)
admin.site.register(AddCustomWinningNumber)
