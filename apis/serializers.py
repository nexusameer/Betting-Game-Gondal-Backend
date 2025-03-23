
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Deposit, Withdrawal, Bonus, DepositAccounts, Config
from .utils import calculate_balance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'user', 'email', 'phone_no', 'date_joined', 'level_1', 'level_2', 'level_3', 'gameId', 'balance','bank_account','bank_name', 'owner_name', 'image','crypto_address', 'network' ]

    def get_balance(self, profile):
        user_id = self.context['request'].user.id
        return calculate_balance(user_id)

class DepositSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Deposit
        fields = ['id', 'user', 'date', 'amount', 'source', 'confirmed', 'deposit_account', 'deposit_currency', 'crypto_amount','deposit_currency']

class WithdrawalSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Withdrawal
        fields = ['id', 'user', 'amount', 'fee', 'date', 'confirmed','withdrawal_currency']

class BonusSerializer(serializers.ModelSerializer):
    giver = UserSerializer()
    receiver = UserSerializer()

    class Meta:
        model = Bonus
        fields = ['id', 'amount', 'giver', 'receiver', 'date']


class DepositAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositAccounts
        fields = '__all__'

class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Config
        fields = '__all__'
        

class AccountSerallizer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['bank_account','bank_name', 'owner_name',"crypto_address", "network" ]