# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Withdrawal
from .serializers import WithdrawalSerializer
from .models import Config, Withdrawal, betWinner


@api_view(["POST"])
@transaction.atomic
def create_withdrawal(request):
   
    user = request.user
    print(request.data)
   
    withdrawal_amount = float(request.data.get("amount", 0))
    account_type = request.data.get("account_type", "")
    currency = request.data.get("currency", "")
    config = Config.objects.all()[0]
    balance=0
    try:
        balance = betWinner.sumofallamounts(user.id, currency)
        print(balance)
    except Exception as e:
        print(e)
        return Response({"error": "Invalid currency"}, status=status.HTTP_400_BAD_REQUEST)
    pending_withdraw=Withdrawal.objects.filter(user=user, confirmed=False).exists()
    # Validate withdrawal amount
    if float(withdrawal_amount) <= 0.0 or float(withdrawal_amount) < float(config.minimum_withdrawal) or pending_withdraw:
        return Response({"error": "Invalid withdrawal amount You may have a pending withdrawal"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Determine fee based on account type
    fee_percentage = config.crypto_fee if account_type == 'crypto' else config.normal_fee
    fee = withdrawal_amount * fee_percentage / 100
 
    # Validate and check balance
    if withdrawal_amount + fee > balance:
        return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create withdrawal object
    withdrawal = Withdrawal.objects.create(
        user=user,
        amount=withdrawal_amount,
        fee=fee,
        account_type=account_type,
        confirmed=False,
        withdrawal_currency=currency,
    )
    
    serializer = WithdrawalSerializer(withdrawal)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def get_withdrawal_history(request):
    user = request.user
    withdrawal_history = Withdrawal.objects.filter(user=user).order_by("-date")
    serializer = WithdrawalSerializer(withdrawal_history, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
