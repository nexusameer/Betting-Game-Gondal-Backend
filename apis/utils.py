from django.db.models import Sum
from .models import Deposit, Withdrawal, Bonus, Profile, VoteCoin, betWinner, betLoser, winigbets
from django.db.models import Sum
from bettingGame.models import UserSessionBet, Voting
import json

def calculate_commission(user_id):
    level_one_profiles = Profile.objects.filter(level_1=user_id)
    total_commission = 0.0
    
    for profile in level_one_profiles:
        first_deposit = Deposit.objects.filter(user=profile.user, confirmed=True).order_by('date').first()
        if first_deposit:
            total_commission += float(first_deposit.amount )* 0.05  # 5% commission
    
    return total_commission


def calculate_balance(user_id):
    # Get the user's profile
    user_profile = Profile.objects.get(user_id=user_id)

    # Initialize dictionaries to store balances for each currency
    balance_components = {
        'PKR': {'total_deposit': 0, 'total_withdrawal': 0, 'total_fee': 0, 'net_withdrawal': 0, 'total_receiver_bonus': 0, 'balance': 0, },
        'TRX': {'total_deposit': 0, 'total_withdrawal': 0, 'total_fee': 0, 'net_withdrawal': 0, 'total_receiver_bonus': 0, 'balance': 0},
        'USDT': {'total_deposit': 0, 'total_withdrawal': 0, 'total_fee': 0, 'net_withdrawal': 0, 'total_receiver_bonus': 0, 'balance': 0},
    }

    # Iterate over each currency and calculate balances
    for currency in balance_components.keys():
        # Calculate the total deposit amount for the user in the current currency
        deposits=Deposit.objects.filter(user=user_profile.user, confirmed=True, deposit_currency=currency)
        total_deposit = deposits.aggregate(Sum('amount'))['amount__sum'] or 0.0
        first_deposit=deposits.first()
        deposit_comission=0.0
        if first_deposit:
            deposit_comission=float(first_deposit.amount)*0.05
        balance_components[currency]['total_deposit'] = total_deposit

        # Calculate the total withdrawal amount for the user in the current currency (considering fees)
        total_withdrawal = Withdrawal.objects.filter(user=user_profile.user, confirmed=True, withdrawal_currency=currency).aggregate(Sum('amount'))['amount__sum'] or 0
        total_fee = Withdrawal.objects.filter(user=user_profile.user, confirmed=True, withdrawal_currency=currency).aggregate(Sum('fee'))['fee__sum'] or 0.0
        net_withdrawal = float(total_withdrawal) + float(total_fee)
        balance_components[currency]['total_withdrawal'] = total_withdrawal
        balance_components[currency]['total_fee'] = total_fee
        balance_components[currency]['net_withdrawal'] = net_withdrawal
        
        # get user name
        get_user = Profile.objects.get(user_id=user_id)
        username = get_user.user.username
        # get all bets of the user
        get_bets = UserSessionBet.objects.all()
        user_bets_data = []
        for bet in get_bets:
            cleaned_string = bet.text.replace('\\"', '"')
            obj = json.loads(cleaned_string)
            for data in obj['data']:
                if data['user'] == username:
                    user_bets_data.append(obj['data'])
        
        # # Initialize a total amount variable
        # total_amount_all_bet = 0
        # # Loop through the list of lists and sum amounts for the currency "USDT"
        # for sublist in user_bets_data:
        #     for item in sublist:
        #         if item['currency'] == currency:  # Check if the currency is USDT
        #             total_amount_all_bet += float(item['amount'])  # Add the amount to the total


        # get all winigbet of the user
        getbetWinneramount = betWinner.objects.filter(user=user_profile.user, currency=currency).aggregate(Sum('amount'))['amount__sum'] or 0.0
        getbetlooseramount = betLoser.objects.filter(user=user_profile.user, currency=currency).aggregate(Sum('amount'))['amount__sum'] or 0.0
        gettotalwinbet = winigbets.objects.filter(user=user_profile.user, currency=currency).aggregate(Sum('amount'))['amount__sum'] or 0.0
        # Calculate the total received bonus amount for the user in the current currency
        total_receiver_bonus = Bonus.objects.filter(receiver=user_profile.user, bonus_currency=currency).aggregate(Sum('amount'))['amount__sum'] or 0.0
        balance_components[currency]['total_receiver_bonus'] = total_receiver_bonus

        amount = float(getbetWinneramount) - float(getbetlooseramount) - float(gettotalwinbet)

        # Calculate the balance for the current currency
        balance = float(total_deposit) +  float(total_receiver_bonus) + float(amount) - float(net_withdrawal)
        total_commission=calculate_commission(user_id)
        balance_components[currency]['balance'] = float(balance) + float(deposit_comission) + float(total_commission)

    return balance_components

def calculate_vote_balance(user_id):
    total_votes = VoteCoin.get_votes_sum(user_id)

    get_user = Profile.objects.get(user_id=user_id)
    username = get_user.user.username

    # get all votes of the user
    get_votes = Voting.objects.all()
    user_votes_data = []
    for vote in get_votes:
        cleaned_string = vote.text.replace('\\"', '"')
        obj = json.loads(cleaned_string)
        for data in obj['data']:
            if data['user'] == username:
                user_votes_data.append(obj['data'])

    current_vote_balance = total_votes - len(user_votes_data)

    return current_vote_balance



