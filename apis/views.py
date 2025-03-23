# finance/views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import Profile, VoteCoin, Config
from .serializers import ProfileSerializer, ConfigSerializer,AccountSerallizer
from .utils import calculate_balance
from rest_framework.decorators import api_view


@api_view(["GET", "POST"])
def user_profile(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    if request.method == "GET":
        serializer = ProfileSerializer(profile, context={"request": request})
        votes_sum = VoteCoin.get_votes_sum(user.id)
        config= Config.objects.all()[0]
        config=ConfigSerializer(config)
        return Response({"profile": serializer.data, "config":config.data, "votes" :votes_sum })
    else:
        if profile.bank_account is None:
            bank_account = request.data.get("bank_account")
            bank_name = request.data.get("bank_name")
            owner_name = request.data.get("owner_name")
            profile.bank_account = bank_account
            profile.bank_name = bank_name
            profile.owner_name = owner_name
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def Swap(request):
    user = request.user
    amount = request.data.get("amount")
    currency = request.data.get("currency")
    if currency == 'USDT':
        conversion_rate =  Config.objects.all()[0].conversion_usdt
    elif currency == 'TRX':
        conversion_rate =  Config.objects.all()[0].conversion_usdt
    else:
        conversion_rate =  Config.objects.all()[0].conversion_pkr

    price_paid = float(amount) / conversion_rate
    price_paid = round(price_paid, 2)  # Round to two decimal places

    balance = calculate_balance(user.id)

    if balance[currency]['balance'] >= price_paid:
        Vote = VoteCoin.objects.create(
            user=user, amount=amount, price_paid=price_paid, confirmed=True, price_currency=currency
        )
        return Response(
            {"message": "Swap request successful"}, status=status.HTTP_200_OK
        )
    else:
        return Response(
            {"message": "Not enough balance"}, status=status.HTTP_400_BAD_REQUEST
        )

@api_view(["GET"])
def balance(request):
    user = request.user
    balance = calculate_balance(user.id)
    config =  Config.objects.all()[0]
    serlizer = ConfigSerializer(config)
    profile = Profile.objects.get(user=user)
    prserilizer = AccountSerallizer(profile)
    return Response(
        {"balance": balance['PKR'],"balance_trx": balance['TRX'],"balance_usdt": balance['USDT'], "config": serlizer.data, "accounts": prserilizer.data}
    )


@api_view(["GET"])
def configvalues(request):
    config =  Config.objects.all()[0]
    serlizer = ConfigSerializer(config)
    return Response(serlizer.data)


@api_view(["POST"])
def GetAccount(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    serilizer = AccountSerallizer(profile, data=request.data, partial=True)
    if serilizer.is_valid():
        serilizer.save()
    return Response("Success")


@api_view(["GET"])
def get_team_members(request):
    try:
        current_user_profile = Profile.objects.get(user=request.user)
        levels = ['level_1', 'level_2', 'level_3']
        response_data = {}
        profile=Profile.objects.all()
        for level in levels:
            level_members = profile.filter(**{level: current_user_profile.user})
            level_serializer = ProfileSerializer(level_members, many=True, context={'request': request})
            response_data[level] = level_serializer.data

        return Response(response_data, status=status.HTTP_200_OK)

    except Profile.DoesNotExist:
        return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)