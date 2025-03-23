
"""
import json
import random
from collections import defaultdict

def calculate_lowest_group_bet_total(bet_data, currency_rates):
    # Define the roulette layout and groups
    rows = {
        "Row-1": [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34],
        "Row-2": [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
        "Row-3": [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]
    }
    dozens = {
        "1-12": list(range(1, 13)),
        "13-24": list(range(13, 25)),
        "25-36": list(range(25, 37))
    }
    halves = {
        "1-18": list(range(1, 19)),
        "19-36": list(range(19, 37))
    }
    colors = {
        "red": [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36],
        "black": [i for i in range(1, 37) if i not in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]]
    }
    parities = {
        "even": [i for i in range(1, 37) if i % 2 == 0],
        "odd": [i for i in range(1, 37) if i % 2 != 0]
    }
    numbers = list(range(1, 37))
    all_groups = {**rows, **dozens, **halves, **colors, **parities}
    
    # Parse JSON data
    bets = json.loads(bet_data)['data']
    
    # Initialize a dictionary to store total bets per group
    all_numbers_and_their_amounts = defaultdict(float)

    
    # Aggregate bets into groups, converting all to USD based on provided rates
    for bet in bets:
        amount = bet['amount']
        currency = bet['currency']
        rate = currency_rates.get(currency, 1.0)
        amount_usd = amount * rate
        number = bet['number']
        
        # Find the group that the number belongs to
        for group_name, group_numbers in all_groups.items():
            if number == group_name:
                if number == "red" or number == "black" or number == "even" or number == "odd" or number == "1-18" or number == "19-36":
                    for num in group_numbers:
                        all_numbers_and_their_amounts[num] += amount_usd * 2
                elif number == "Row-1" or number == "Row-2" or number == "Row-3" or number == "1-12" or number == "13-24" or number == "25-36":
                    for num in group_numbers:
                        all_numbers_and_their_amounts[num] += amount_usd * 3
            else:
                if number.isdigit():
                    if int(number) in numbers:
                        all_numbers_and_their_amounts[int(number)] += amount_usd * 36
        
    # add remaining numbers to the dictionary
    for num in numbers:
        if num not in all_numbers_and_their_amounts:
            all_numbers_and_their_amounts[num] = 0.0

    print(all_numbers_and_their_amounts)
    # find the min value key
    min_value = min(all_numbers_and_their_amounts.values())
    min_keys = [k for k, v in all_numbers_and_their_amounts.items() if v == min_value]
    print(min_keys)


    # If there are multiple numbers with the same lowest total, randomly select one

        
        

    
    


# Example JSON input, adjusted with proper quotes and commas
bet_data = """""""
{
    "message": "bet",
    "data": [
    {"amount": 2, "number": "red", "betColor": "green", "currency": "USDT", "user": "home313"}
    ]
}
""""""

# Define currency rates relative to USD
currency_rates = {
    "PKR": 0.0045,  # Example rate for Pakistani Rupee
    "USDT": 1.0,    # Tether, usually pegged to the US Dollar
    "TRX": 0.07     # Example rate for TRON
}

print(calculate_lowest_group_bet_total(bet_data, currency_rates))

"""
import json
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from bettingGame import models



try:
                            
    def fetch_votes():
        try:
            votes_data = models.Voting.objects.get(session=session)
            return json.loads(votes_data.text)
        except models.Voting.DoesNotExist:
            return []
            
    get_votes = sync_to_async(fetch_votes, thread_sensitive=True)

    alluserVoteswining = []

    votes = await get_votes()

    if len(votes) > 0:

        for vote in votes['data']:
            if vote['number'] == win_num:
                await alluserVoteswining.append(vote['user'])
                votingwinigUser.append({ 'user': vote['user'], 'number': win_num})
            elif vote['number'] == 'red' and win_num in GameConsumer.colors['red']:
                await alluserVoteswining.append(vote['user'])
                votingwinigUser.append({ 'user': vote['user'], 'number': 'red' })
            elif vote['number'] == 'black' and win_num not in GameConsumer.colors['red']:
                await alluserVoteswining.append(vote['user']) 
                votingwinigUser.append({ 'user': vote['user'], 'number': 'black' })
            elif vote['number'] == 'even' and win_num in GameConsumer.parities['even']:
                await alluserVoteswining.append(vote['user'])
                votingwinigUser.append({ 'user': vote['user'], 'number': 'even' })
            elif vote['number'] == 'odd' and win_num not in GameConsumer.parities['even']:
                await alluserVoteswining.append(vote['user'])
                votingwinigUser.append({ 'user': vote['user'], 'number': 'odd' })

        try:
            find_percentage = sync_to_async(totalbetslost.objects.get, thread_sensitive=True)
            percentage = await find_percentage(session=session)
            per = percentage.percent20ofthetotalinpkramount()

            for username in alluserVoteswining:
                get_user = sync_to_async(User.objects.get, thread_sensitive=True)
                user = await get_user(username=username)

                single_user_per = per / len(alluserVoteswining)
                send_amount = sync_to_async(GameConsumer.add_amountAfterVotewin, thread_sensitive=True)
                await send_amount(user, single_user_per)
        except Exception as e:
            print(e, "Error in finding percentage")

except Exception as e:
    print(e, "Error in voting")