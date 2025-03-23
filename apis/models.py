# finance/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_no = models.CharField(max_length=15)
    date_joined = models.DateTimeField(auto_now_add=True)
    level_1 = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='level_1', null=True, blank=True)
    level_2 = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='level_2', null=True, blank=True)
    level_3 = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='level_3', null=True, blank=True)
    bank_account=models.CharField(max_length=255, blank=True, null=True)
    bank_name=models.CharField(max_length=255,blank=True, null=True)
    owner_name=models.CharField(max_length=255,blank=True, null=True)
    gameId = models.CharField(max_length=255, unique=True)
    crypto_address = models.CharField(max_length=255, blank=True, null=True)
    network=models.CharField(max_length=255, blank=True, null=True)
    image=models.ImageField(upload_to='profile_images', null=True, blank=True)

    def __str__(self):
        return f"Profile for {self.user.username if self.user else 'No User'}"

class DepositAccounts(models.Model):
    account_name = models.CharField(max_length=255)
    account_limit = models.FloatField(default=0)
    account_number = models.CharField(max_length=255, unique=True)
    date = models.DateTimeField(default=timezone.now)
    account_company = models.CharField(max_length=255)
    
    
class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deposit_account = models.ForeignKey(DepositAccounts, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    source = models.CharField(max_length=255)
    confirmed = models.BooleanField(default=False)
    deposit_currency = models.CharField(max_length=255, default="PKR")
    crypto_amount = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    deposit_reciept=models.ImageField(upload_to='deposit_reciepts', null=True, blank=True)
    def __str__(self):
        return f"{self.user.username} - {self.amount} on {self.date}"
    
class betWinner(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=255, default="PKR")
    date = models.DateTimeField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    def __str__(self):
        return f"{self.user.username} - {self.amount} on {self.date}"
    
    def sumofallamounts(self, user_id, currency):
        return self.objects.filter(user_id=user_id, currency=currency).aggregate(Sum('amount'))['amount__sum'] or 0
    
class winigbets(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=255, default="PKR")
    date = models.DateTimeField(default=timezone.now)
    time = models.TimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.amount} on {self.date}"


    
class betLoser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=255, default="PKR")
    date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"{self.user.username} - {self.amount} on {self.date}"
    
class totalbetslost(models.Model):
    session = models.CharField(max_length=255)
    usdtamount = models.DecimalField(max_digits=10, decimal_places=2)
    pkramount = models.DecimalField(max_digits=10, decimal_places=2)
    trxamount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.session}"
    
    def calculate_totalinUsdt(self):
        return self.usdtamount + self.pkramount * 0.0045 + self.trxamount * 0.07
    
    def calculate_totalinPkr(self):
        return self.pkramount + self.usdtamount * 260 + self.trxamount * 40
    
    def calculate_totalinTrx(self):
        return self.trxamount + self.usdtamount * 14 + self.pkramount * 0.025
    
    def percent20ofthetotalinpkramount(self):
        return self.calculate_totalinPkr() * 0.2

      
class bets(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"{self.user.username} - {self.amount} on {self.date}"
    
class voteWinner(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=255, default="PKR")
    date = models.DateTimeField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    def __str__(self):
        return f"{self.user.username} - {self.amount} on {self.date}"


class Withdrawal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee = models.DecimalField(max_digits=6, decimal_places=2)
    account_type = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)
    confirmed = models.BooleanField(default=False)
    withdrawal_currency = models.CharField(max_length=255, default="PKR")
    def __str__(self):
        return f"{self.account_type} - {self.amount} on {self.date}"


class Bonus(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    giver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bonus_giver')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bonus_receiver')
    date = models.DateTimeField(default=timezone.now)
    bonus_currency=models.CharField(max_length=255, default="PKR")

    def __str__(self):
        return f"{self.amount} bonus from {self.giver.username} to {self.receiver.username} on {self.date}"


class VoteCoin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    confirmed = models.BooleanField(default=False)
    price_paid=models.DecimalField(max_digits=20, decimal_places=5)
    price_currency=models.CharField(max_length=255, default='PKR')
    def __str__(self):
        return f"{self.user.username} - {self.amount} on {self.date}"
    @classmethod
    def get_votes_sum(cls, user_id):
        return cls.objects.filter(user_id=user_id).aggregate(Sum('amount'))['amount__sum'] or 0

    @classmethod
    def get_pkr_sum(cls, user_id, currency):
        return cls.objects.filter(user_id=user_id, price_currency=currency).aggregate(Sum('price_paid'))['price_paid__sum'] or 0


class Config(models.Model):
    fee=models.FloatField(default=5.3)
    conversion_pkr=models.FloatField(default=1)
    conversion_trx=models.FloatField(default=0.26)
    conversion_usdt=models.FloatField(default=279)
    minimu_deposit=models.FloatField(default=200)
    max_deposit=models.FloatField(default=1000000)
    minimum_withdrawal=models.FloatField(default=200)
    maximum_withdrawal=models.FloatField(default=1000000)
    minimum_withdrawal_trx=models.FloatField(default=10)
    maximum_withdrawal_trx=models.FloatField(default=1000000)
    minimum_withdrawal_usdt=models.FloatField(default=2)
    maximum_withdrawal_usdt=models.FloatField(default=1000000)
    crypto_fee=models.FloatField(default=5)
    normal_fee=models.FloatField(default=0)
    def __str__(self):
        return f"App Configurations"
    

class CryptoAccounts(models.Model):
    account_name = models.CharField(max_length=255)
    account_limit = models.FloatField(default=0)
    account_address = models.CharField(max_length=255, unique=True)
    date = models.DateTimeField(default=timezone.now)
    account_network = models.CharField(max_length=255)
