from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
import random
from . import models
from apis.models import betWinner, betLoser, VoteCoin, voteWinner, totalbetslost, winigbets
from django.contrib.auth.models import User
from apis.utils import calculate_balance, calculate_vote_balance
from collections import defaultdict
from django.utils import timezone

class GameConsumer(AsyncWebsocketConsumer):

    session_number = 0
    count = 20
    phase = 'betting'
    send_state = False
    bets = []
    votes = []
    wining_number = random.choice(list(range(1, 37)))
    numbers = list(range(1, 37))
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
    all_groups = {**rows, **dozens, **halves, **colors, **parities}
    lowestAmountNumber = 0
    
    async def connect(self):
        # get the user which is connected
        await self.accept()
        await self.channel_layer.group_add("my_group", self.channel_name)
        await self.send(json.dumps({'message': self.phase, 'time': self.count}))
        # send all periouvvs bets
        bets = await sync_to_async(models.Allbets.objects.all, thread_sensitive=True)()
        all_wining_number = await sync_to_async(list, thread_sensitive=True)(bets)
        number = []
        for bet in all_wining_number:
            number.append(bet.wining_num)
        await self.send(json.dumps({'message': 'previous_bets', 'data': number}))

    async def disconnect(self, close_code):
        # Optional: Handle any cleanup here
        print(f"Disconnected with close code {close_code}")
        # If using channel groups, you might want to remove the user from the group
        await self.channel_layer.group_discard("my_group", self.channel_name)

    async def receive(self, text_data=None):
        # Handle when a message is received from the WebSocket
        text_data_json = json.loads(text_data)
        if text_data_json['message'] == 'user':
            get_user = sync_to_async(User.objects.get, thread_sensitive=True)
            user = await get_user(username=text_data_json['data'])
            user_id = user.id
            get_balanceCalulate = sync_to_async(calculate_balance, thread_sensitive=True)
            balance = await get_balanceCalulate(user_id)
            pkrBalance = balance['PKR']['balance']
            usdBalance = balance['USDT']['balance']
            trxBalance = balance['TRX']['balance']
            func = sync_to_async(calculate_vote_balance, thread_sensitive=True)
            total_votes = await func(user_id)

            try:
                user_exists = sync_to_async(models.UserWallet.objects.filter(user=user).exists, thread_sensitive=True)
                updateWallet = sync_to_async(models.UserWallet.objects.get, thread_sensitive=True)
                wallet = await updateWallet(user=user)
                wallet.pkramount = pkrBalance
                wallet.trxamount = trxBalance
                wallet.usdtamount = usdBalance
                await sync_to_async(wallet.save, thread_sensitive=True)()
                
            except Exception as e:
                addintoWallet = sync_to_async(models.UserWallet.objects.create, thread_sensitive=True)
                await addintoWallet(user=user, pkramount=pkrBalance, trxamount=trxBalance, usdtamount=usdBalance)
                

            await self.send(json.dumps({'message': 'balance', 'data': {'pkr': pkrBalance, 'usdt': usdBalance, 'trx': trxBalance, 'vcoin': float(total_votes)}}))

            get_bets = sync_to_async(models.UserSessionBet.objects.all, thread_sensitive=True)

            user_bets = await get_bets()

            bets = await sync_to_async(list)(user_bets)

            user_bets_data = []
            for bet in bets:
                cleaned_string = bet.text.replace('\\"', '"')
                obj = json.loads(cleaned_string)
                for data in obj['data']:
                    if data['user'] == text_data_json['data']:
                        user_bets_data.append(obj['data'])

            await self.send(json.dumps({'message': 'userprevious_bets', 'data': user_bets_data}))

            get_voting = sync_to_async(models.Voting.objects.all, thread_sensitive=True)
            user_voting = await get_voting()

            votes = await sync_to_async(list)(user_voting)

            user_voting_data = []
            for vote in votes:
                cleaned_string = vote.text.replace('\\"', '"')
                obj = json.loads(cleaned_string)
                for data in obj['data']:
                    if data['user'] == text_data_json['data']:
                        user_voting_data.append(obj['data'])
                        
            await self.send(json.dumps({'message': 'userprevious_votes', 'data': user_voting_data}))

        if text_data_json['message'] == 'bet':
            # Handle the bet message
            if self.phase == 'voting':
                self.votes = text_data_json['data']

                # check if the session voting is already present
                check_session = sync_to_async(models.Session.objects.latest, thread_sensitive=True)
                    # get the last bet and update this
                session = await check_session('id')
                try:
                    if session.session_number != self.session_number:
                        create_session = sync_to_async(models.Session.objects.create, thread_sensitive=True)
                        await create_session(session_number=self.session_number)

                        check_session = sync_to_async(models.Session.objects.latest, thread_sensitive=True)
                        last_session = await check_session('id')

                        create_voting = sync_to_async(models.Voting.objects.create, thread_sensitive=True)
                        await create_voting(session=last_session, text=text_data)
                    else:
                        # Get voting for the current session
                        get_voting = sync_to_async(models.Voting.objects.latest, thread_sensitive=True)
                        voting = await get_voting('id')
                        # Update the voting for the current session
                        voting.text = text_data
                        # Save the updated voting
                        update_voting = sync_to_async(voting.save, thread_sensitive=True)
                        await update_voting()
                except Exception as e:
                    print(e)

            else:
                self.bets = text_data_json['data']
                # check if the session is already present
                check_session = sync_to_async(models.Session.objects.latest, thread_sensitive=True)
                session = await check_session('id')
                # if the session is not present then create the session
                try:
                    if session.session_number != self.session_number:
                        create_session = sync_to_async(models.Session.objects.create, thread_sensitive=True)
                        await create_session(session_number=self.session_number)

                        check_session = sync_to_async(models.Session.objects.latest, thread_sensitive=True)
                        last_session = await check_session('id')

                        create_bet = sync_to_async(models.UserSessionBet.objects.create, thread_sensitive=True)
                        await create_bet(session=last_session, text=text_data)
                    else:
                        # Get the last bet for the current session
                        get_bet = sync_to_async(models.UserSessionBet.objects.latest, thread_sensitive=True)
                        bet = await get_bet('id')
                        # Update the bet for the current session
                        bet.text = text_data
                        # Save the updated bet
                        update_bet = sync_to_async(bet.save, thread_sensitive=True)
                        await update_bet()
                except Exception as e:
                    print(e)
            

    # Handler for sending messages received from the group
    async def game_message(self, event):
        message = event['message']
        await self.send(text_data=message)
    
    async def send_state(self):
        # Helper method to send the state to the individual client
        await self.send(json.dumps({
            'message': self.phase,
            'count': self.count
        }))

    async def win_num():
        self = GameConsumer
        # Currency rates
        currency_rates = {
            "PKR": 0.0045,
            "USDT": 1.0,
            "TRX": 0.07
        }

        session_obj = sync_to_async(models.Session.objects.latest, thread_sensitive=True)
        session = await session_obj('id')
        
        if session.session_number == self.session_number:
            
            # Check for a confirmed custom winning number
            try:
                def fetch_custom_winning_number():
                    current_time = timezone.now()  # Ensure you are using the correct method to get the current time
                    return list(models.AddCustomWinningNumber.objects.filter(
                        start_datetime__lte=current_time,
                        end_datetime__gte=current_time,
                        confirmed=True
                    ))

                # Wrap the synchronous function for asynchronous execution
                custom_win_num_query = sync_to_async(fetch_custom_winning_number, thread_sensitive=True)

                # Execute the query asynchronously
                custom_winning_number = await custom_win_num_query()


                if custom_winning_number:
                    self.wining_number = custom_winning_number.wining_num
                    # Set the confirmed to False after use
                    update_confirmed = sync_to_async(custom_winning_number.save, thread_sensitive=True)
                    custom_winning_number.confirmed = False
                    await update_confirmed()
                    return self.wining_number

                    # If no custom number, proceed with existing logic
                def fetch_bets():
                    try:
                        bets_data = models.UserSessionBet.objects.get(session=session)
                        return json.loads(bets_data.text)
                    except models.UserSessionBet.DoesNotExist:
                        return []
                    
                get_bets = sync_to_async(fetch_bets, thread_sensitive=True)

                # Execute the function asynchronously
                betsData = await get_bets()
                
                bets = betsData['data']
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
                    for group_name, group_numbers in self.all_groups.items():
                        if number == group_name:
                            if number == "red" or number == "black" or number == "even" or number == "odd" or number == "1-18" or number == "19-36":
                                for num in group_numbers:
                                    all_numbers_and_their_amounts[num] += amount_usd * 2
                            elif number == "Row-1" or number == "Row-2" or number == "Row-3" or number == "1-12" or number == "13-24" or number == "25-36":
                                for num in group_numbers:
                                    all_numbers_and_their_amounts[num] += amount_usd * 3
                        else:
                            if number.isdigit():
                                if int(number) in self.numbers:
                                    all_numbers_and_their_amounts[int(number)] += amount_usd * 36

                # add remaining numbers to the dictionary
                for num in self.numbers:
                    if num not in all_numbers_and_their_amounts:
                        all_numbers_and_their_amounts[num] = 0.0

                # find the min value key
                min_value = min(all_numbers_and_their_amounts.values())
                min_keys = [k for k, v in all_numbers_and_their_amounts.items() if v == min_value]
                return random.choice(min_keys)
            
            except Exception as e:
                print(e, "Error in win_num")
                self.wining_number = random.choice(self.numbers)
                return random.choice(self.numbers)
            
        else:
            # Select a random number if session doesn't match
            self.wining_number = random.choice(self.numbers)
            return random.choice(self.numbers)
    
    async def add_profit(percent, bet):

        get_user = sync_to_async(User.objects.get, thread_sensitive=True)
        user = await get_user(username=bet['user'])

        create_win = sync_to_async(betWinner.objects.create, thread_sensitive=True)
        await create_win(user=user, amount=bet['amount'] * percent, currency=bet['currency'])

        create_winig = sync_to_async(winigbets.objects.create, thread_sensitive=True)
        await create_winig(user=user, amount=bet['amount'], currency=bet['currency'])

    async def add_amountAfterVotewin(user, amount):

        get_latest = sync_to_async(betLoser.objects.latest, thread_sensitive=True)
        latest = await get_latest('id', user=user)

        if latest.currency == 'PKR':
            create_vote_win = sync_to_async(voteWinner.objects.create, thread_sensitive=True)
            await create_vote_win(user=user, amount=amount, currency=latest.currency)
        elif latest.currency == 'USDT':
            create_vote_win = sync_to_async(voteWinner.objects.create, thread_sensitive=True)
            await create_vote_win(user=user, amount=amount, currency=latest.currency)
        elif latest.currency == 'TRX':
            create_vote_win = sync_to_async(voteWinner.objects.create, thread_sensitive=True)
            await create_vote_win(user=user, amount=amount, currency=latest.currency)




    @staticmethod
    async def session_management():
        while True:
            if GameConsumer.count == 0:
                channel_layer = get_channel_layer()
                if GameConsumer.phase == 'betting':
                    GameConsumer.phase = 'voting'
                    GameConsumer.count = 20
                    await channel_layer.group_send(
                            "my_group",
                            {
                                "type": "game.message",
                                "message": json.dumps({'message': GameConsumer.phase, 'time': GameConsumer.count}),
                            }
                        )
                    
                elif GameConsumer.phase == 'voting':
                    GameConsumer.phase = 'result'
                    GameConsumer.count = 20
                    win_num = await GameConsumer.win_num()
                    addwin = sync_to_async(models.Allbets.objects.create, thread_sensitive=True)
                    await addwin(wining_num=win_num)
                    votingwinigUser = []
                    # create a random numver between a range of 0 to 36 not including win_num
                    secondHighest = random.choice([i for i in range(0, 37) if i != win_num])
                    ThirdHighest = random.choice([i for i in range(0, 37) if i != win_num and i != secondHighest])
                    total_votes = {
                        win_num : random.randint(10000, 50000),
                        secondHighest: random.randint(5000, 10000),
                        ThirdHighest: random.randint(1000, 5000),
                    }
                    bettingwinigUser = []
                    session_obj = sync_to_async(models.Session.objects.latest, thread_sensitive=True)
                    session = await session_obj('id')
                    if session.session_number == GameConsumer.session_number:
                        
                        try:  
                            def fetch_bets():
                                try:
                                    bets_data = models.UserSessionBet.objects.get(session=session)
                                    return json.loads(bets_data.text)
                                except models.UserSessionBet.DoesNotExist:
                                    return []
                                
                            get_bets = sync_to_async(fetch_bets, thread_sensitive=True)

                            # Execute the function asynchronously
                            bets = await get_bets()
                            totalloseamountofbet = {
                                'PKR': 0,
                                'USDT': 0,
                                'TRX': 0
                            }
                            if len(bets) > 0:
                                for bet in bets['data']:
                                    if bet['number'] == win_num:
                                        await GameConsumer.add_profit(30, bet)
                                        bettingwinigUser.append({ 'user': bet['user'], 'number': win_num, "profit": bet['amount'] * 30, "currency" : bet['currency']})
                                    elif bet['number'] == 'red' and win_num in GameConsumer.colors['red']:
                                        await GameConsumer.add_profit(2, bet)
                                        bettingwinigUser.append({ 'user': bet['user'], 'number': 'red', "profit": bet['amount'] * 2, "currency" : bet['currency'] })
                                    elif bet['number'] == 'black' and win_num not in GameConsumer.colors['red']:
                                        await GameConsumer.add_profit(2, bet)
                                        bettingwinigUser.append({ 'user': bet['user'], 'number': 'black', "profit": bet['amount'] * 2, "currency" : bet['currency'] })
                                    elif bet['number'] == 'even' and win_num in GameConsumer.parities['even']:
                                        await GameConsumer.add_profit(2, bet)
                                        bettingwinigUser.append({ 'user': bet['user'], 'number': 'even', "profit": bet['amount'] * 2, "currency" : bet['currency'] })
                                    elif bet['number'] == 'odd' and win_num not in GameConsumer.parities['even']:
                                        await GameConsumer.add_profit(2, bet)
                                        bettingwinigUser.append({ 'user': bet['user'], 'number': 'odd', "profit": bet['amount'] * 2, "currency" : bet['currency'] })
                                    elif bet['number'] == '1-12' and win_num in GameConsumer.dozens['1-12']:
                                        await GameConsumer.add_profit(3, bet)
                                        bettingwinigUser.append({ 'user': bet['user'], 'number': '1-12', "profit": bet['amount'] * 3, "currency" : bet['currency'] })
                                    elif bet['number'] == '13-24' and win_num in GameConsumer.dozens['13-24']:
                                        await GameConsumer.add_profit(3, bet)
                                        bettingwinigUser.append({ 'user': bet['user'], 'number': '13-24', "profit": bet['amount'] * 3, "currency" : bet['currency'] })
                                    elif bet['number'] == '25-36' and win_num in GameConsumer.dozens['25-36']:
                                        await GameConsumer.add_profit(3, bet)
                                        bettingwinigUser.append({ 'user': bet['user'], 'number': '25-36', "profit": bet['amount'] * 3, "currency" : bet['currency'] })
                                    elif bet['number'] == '1-18' and win_num in GameConsumer.halves['1-18']:
                                        await GameConsumer.add_profit(2, bet)
                                        bettingwinigUser.append({ 'user': bet['user'], 'number': '1to18', "profit": bet['amount'] * 2, "currency" : bet['currency'] })
                                    elif bet['number'] == '19-36' and win_num in GameConsumer.halves['19-36']:
                                        await GameConsumer.add_profit(2, bet)
                                        bettingwinigUser.append({ 'user': bet['user'], 'number': '19-36', "profit": bet['amount'] * 2, "currency" : bet['currency'] })
                                    elif bet['number'] == 'Row-1' and win_num in GameConsumer.rows['Row-1']:
                                        await GameConsumer.add_profit(3, bet)
                                        bettingwinigUser.append({ 'user': bet['user'], 'number': 'Row-1', "profit": bet['amount'] * 3, "currency" : bet['currency'] })
                                    elif bet['number'] == 'Row-2' and win_num in GameConsumer.rows['Row-2']:
                                        await GameConsumer.add_profit(3, bet)
                                        bettingwinigUser.append({ 'user': bet['user'], 'number': 'Row-2', "profit": bet['amount'] * 3, "currency" : bet['currency'] })
                                    elif bet['number'] == 'Row-3' and win_num in GameConsumer.rows['Row-3']:
                                        await GameConsumer.add_profit(3, bet)
                                        bettingwinigUser.append({ 'user': bet['user'], 'number': 'Row-3', "profit": bet['amount'] * 3, "currency" : bet['currency'] })
                                    else:
                                        get_user = sync_to_async(User.objects.get, thread_sensitive=True)
                                        user = await get_user(username=bet['user'])
                                        create_lose = sync_to_async(betLoser.objects.create, thread_sensitive=True)
                                        await create_lose(user=user, amount=bet['amount'], currency=bet['currency'])

                                        # 1. if user lose 100pkr bet he/she will win free 1 coin and can vote from that
                                        # 2.if user lose 1 usdt bet he/she will win free 2.8 coin and can vote from that
                                        # 3. if user lose 1 trx bet he/she will win free 0.4 coin and can vote from that
                                        if bet['currency'] == 'PKR':
                                            totalloseamountofbet['PKR'] += bet['amount']
                                            # if amount is multiple of 100 and amount add to their multiple of 100
                                            if int(bet['amount']) % 100 == 0:
                                                amount = int(bet['amount']) / 100
                                                create_vote = sync_to_async(VoteCoin.objects.create, thread_sensitive=True)
                                                await create_vote(user=user, amount=amount, price_paid=0, price_currency='PKR', confirmed=True)
                                        elif bet['currency'] == 'USDT':
                                            totalloseamountofbet['USDT'] += bet['amount']
                                            amount = 2.8 * int(bet['amount'])
                                            create_vote = sync_to_async(VoteCoin.objects.create, thread_sensitive=True)
                                            await create_vote(user=user, amount=amount, price_paid=0, price_currency='USDT', confirmed=True)
                                        elif bet['currency'] == 'TRX':
                                            totalloseamountofbet['TRX'] += bet['amount']
                                            amount = 0.4 * int(bet['amount'])
                                            create_vote = sync_to_async(VoteCoin.objects.create, thread_sensitive=True)
                                            await create_vote(user=user, amount=amount, price_paid=0, price_currency='TRX', confirmed=True)

                                create_bet_lost_amount = sync_to_async(totalbetslost.objects.create, thread_sensitive=True)
                                await create_bet_lost_amount(pkramount=totalloseamountofbet['PKR'], usdtamount=totalloseamountofbet['USDT'], trxamount=totalloseamountofbet['TRX'], session=session.session_number)

                        except Exception as e:
                            print(e, "Error in betting")

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
                                        alluserVoteswining.append(vote['user'])
                                        votingwinigUser.append({ 'user': vote['user'], 'number': win_num})
                                    elif vote['number'] == 'red' and win_num in GameConsumer.colors['red']:
                                        alluserVoteswining.append(vote['user'])
                                        votingwinigUser.append({ 'user': vote['user'], 'number': 'red' })
                                    elif vote['number'] == 'black' and win_num not in GameConsumer.colors['red']:
                                        alluserVoteswining.append(vote['user']) 
                                        votingwinigUser.append({ 'user': vote['user'], 'number': 'black' })
                                    elif vote['number'] == 'even' and win_num in GameConsumer.parities['even']:
                                        alluserVoteswining.append(vote['user'])
                                        votingwinigUser.append({ 'user': vote['user'], 'number': 'even' })
                                    elif vote['number'] == 'odd' and win_num not in GameConsumer.parities['even']:
                                        alluserVoteswining.append(vote['user'])
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
                        

                    await channel_layer.group_send(
                        "my_group",
                        {
                            "type": "game.message",
                            "message": json.dumps({'message': GameConsumer.phase, 
                                                'time': GameConsumer.count, 
                                                'winning_number': win_num,
                                                    'betting_winners': bettingwinigUser,
                                                    'voting_winners': votingwinigUser,
                                                    'total_votes': total_votes
                                                }),
                        },
                    )

                elif GameConsumer.phase == 'result':
                    GameConsumer.session_number += 1
                    GameConsumer.phase = 'betting'
                    GameConsumer.count = 20
                    bets = await sync_to_async(models.Allbets.objects.all, thread_sensitive=True)()
                    all_wining_number = await sync_to_async(list, thread_sensitive=True)(bets)
                    number = []
                    for bet in all_wining_number:
                        number.append(bet.wining_num)
                    await channel_layer.group_send(
                        "my_group",
                        {
                            "type": "game.message",
                            "message": json.dumps({'message': GameConsumer.phase, 'time': GameConsumer.count}),
                        }
                    )
                    
                    await channel_layer.group_send(
                        "my_group",
                        {
                            "type": "game.message",
                            "message": json.dumps({'message': 'previous_bets', 'data': number}),
                        }
                    )             

            await asyncio.sleep(1)
            GameConsumer.count -= 1
                
