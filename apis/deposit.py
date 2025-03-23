# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, F
from .models import Deposit, DepositAccounts
from .serializers import DepositSerializer, DepositAccountSerializer


@api_view(["POST"])
def create_deposit(request):
    account_number = request.data.get("account_number", None)
    deposits=Deposit.objects.all()
    last_deposit = deposits.filter(user=request.user, confirmed=False).exists()
    if last_deposit:
        return Response(
            {"error": "You have a pending deposit request"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    # if last_deposit.exists() and account_number and last_deposit.confirmed:
    try:
        deposit_account = DepositAccounts.objects.get(account_number=account_number)
    except DepositAccounts.DoesNotExist:
        return Response(
            {"error": "Deposit account not found"}, status=status.HTTP_404_NOT_FOUND
        )

    current_deposit_sum = (
        deposits.filter(
            deposit_account=deposit_account, deposit_currency="PKR"
        ).aggregate(Sum("amount"))["amount__sum"]
        or 0
    )

    if (
        deposit_account.account_limit
        and float(current_deposit_sum) + float(request.data["amount"])
        <= deposit_account.account_limit
    ):
        deposit_data = {
            "user": request.user,
            "deposit_account": deposit_account,
            "amount": request.data["amount"],
            "source": request.data["source"],
            "confirmed": False,
            "deposit_currency": request.data.get("deposit_currency"),
        }

        # Check if 'deposit_reciept' is included in the request
        deposit_reciept = request.data.get("deposit_reciept")
        # print(depo)
        deposit_data["deposit_reciept"] = deposit_reciept

        deposit = Deposit.objects.create(**deposit_data)

        return Response(DepositSerializer(deposit).data, status=status.HTTP_201_CREATED)

    return Response(
        {"message": "Invalid request You may have a pending request"},
        status=status.HTTP_400_BAD_REQUEST,
    )


from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Value
from django.db.models.functions import Coalesce


@api_view(["GET"])
def get_available_accounts(request, new_amount):
    # Ensure new_amount is a valid numeric value
    try:
        new_amount = float(new_amount)
    except ValueError:
        return Response(
            {"error": "Invalid new amount"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Calculate the total sum of deposits for each account and the remaining limit
    available_accounts = DepositAccounts.objects.annotate(
        deposited_sum=Coalesce(
            Sum("deposit__amount"), Value(0, output_field=DecimalField())
        ),
        remaining_limit=ExpressionWrapper(
            F("account_limit")
            - Coalesce(Sum("deposit__amount"), Value(0, output_field=DecimalField())),
            output_field=DecimalField(),
        ),
    ).filter(remaining_limit__gte=new_amount)

    if available_accounts.exists():
        account = available_accounts.first()
        serializer = DepositAccountSerializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(
            {"error": "No available accounts or not enough remaining limit"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
def get_deposit_history(request):
    deposit_history = Deposit.objects.filter(user=request.user).order_by("-date")
    serializer = DepositSerializer(deposit_history, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
