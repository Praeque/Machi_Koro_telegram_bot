import random
from asyncio import sleep
from aiogram import Bot
from data import ActionDB
from emoji import emojize


class BotPlay:

    def __init__(self, db: ActionDB, bot: Bot, quick_sleep, sender, bot_cldr):
        self.DB = db
        self.bot = bot
        self.quick_sleep = quick_sleep
        self.sender = sender
        self.bot_cldr = bot_cldr
        self.strategy_build = {
            'basic': {2: self.basic_build_2, 3: self.basic_build_3, 4: self.basic_build_3, 5: self.basic_build_3},
            'additions': {2: self.add_build_4, 3: self.add_build_4, 4: self.add_build_4, 5: self.add_build_4}}

        self.strategy_roll = {
            'basic': {2: self.basic_roll_2, 3: self.basic_roll_3, 4: self.basic_roll_3, 5: self.basic_roll_3},
            'additions': {2: self.add_roll_4, 3: self.add_roll_4, 4: self.add_roll_4, 5: self.add_roll_4}}

        self.good_strategy_add_4_current_lap = {
            0: self.add_build_4_lap_0, 1: self.add_build_4_lap_1, 2: self.add_build_4_lap_2, 3: self.add_build_4_lap_3,
            4: self.add_build_4_lap_4, 5: self.add_build_4_lap_5, 6: self.add_build_4_lap_6, 7: self.add_build_4_lap_7,
            8: self.add_build_4_lap_8, 9: self.add_build_4_lap_9, 10: self.add_build_4_lap_10,
            11: self.add_build_4_lap_11, 12: self.add_build_4_lap_12}

    async def refresh_history(self, game_id):
        await sleep(self.quick_sleep)
        history = emojize(self.DB.get_history(game_id))
        messages_id = self.DB.get_messages_history(game_id)
        for player_id, mess_id in messages_id.items():
            await self.sender.edit_message(history, player_id, mess_id)

    async def basic_roll_2(self, game_id, bot_id, bot_name):
        number = random.randint(1, 6)
        turn_story = f'\n{self.bot_cldr} {bot_name}   {":game_die:" * 1}   {number}'
        if self.DB.is_radio_tower(game_id, bot_id):
            needed_number = [2, 4]
            money = self.DB.money(game_id, bot_id)
            if money == 0 or self.DB.not_much_cafe(game_id, bot_id):
                needed_number.append(3)
            if number not in needed_number:
                await self.refresh_history(game_id)
                await sleep(2.5)
                number = random.randint(1, 6)
                turn_story += f'\n      :counterclockwise_arrows_button:   {":game_die:" * 1}   {number}'
        self.DB.put_new_story(turn_story, game_id)
        await self.refresh_history(game_id)
        await sleep(1)
        return number

    async def basic_roll_3(self, game_id, bot_id, bot_name):
        number = random.randint(1, 6)
        turn_story = f'\n{self.bot_cldr} {bot_name}   {":game_die:" * 1}   {number}'
        if self.DB.is_radio_tower(game_id, bot_id):
            needed_number = self.DB.get_needed_numbers(game_id, bot_id)
            money = self.DB.money(game_id, bot_id)
            if 3 in needed_number:
                if money and not self.DB.not_much_cafe(game_id, bot_id):
                    needed_number.remove(3)
            if number not in needed_number:
                await self.refresh_history(game_id)
                await sleep(2.5)
                number = random.randint(1, 6)
                turn_story += f'\n      :counterclockwise_arrows_button:   {":game_die:" * 1}   {number}'
        self.DB.put_new_story(turn_story, game_id)
        await self.refresh_history(game_id)
        await sleep(1)
        return number

    async def add_roll_4(self, game_id, bot_id, bot_name):
        if self.DB.is_train_station(game_id):
            number_1 = random.randint(1, 6)
            number_2 = random.randint(1, 6)
            number = number_2 + number_1
            turn_story = f'\n{self.bot_cldr} {bot_name}   :game_die::game_die:   {number_1}  {number_2}'
            self.DB.put_new_story(turn_story, game_id)
            if self.DB.is_radio_tower(game_id, bot_id):
                needed_number = self.DB.get_needed_numbers_add(game_id, bot_id)
                duple = self.DB.is_card_in_city(game_id, bot_id, 'amusement park') and (number_1 == number_2)
                print(number_1, number_2)
                print(needed_number, '.   is duple - >', duple)
                if (number not in needed_number) and (not duple):
                    print('rerroll')
                    await sleep(2.5)
                    await self.refresh_history(game_id)
                    number_1 = random.randint(1, 6)
                    number_2 = random.randint(1, 6)
                    number = number_2 + number_1
                    turn_story = f'\n      :counterclockwise_arrows_button:   :game_die::game_die:' \
                                 f'   {number_1}  {number_2}'
                    self.DB.put_new_story(turn_story, game_id)
            if number_1 == number_2:
                self.DB.duple_rolled(game_id, bot_id)
            is_port = self.DB.is_card_in_city(game_id, bot_id, 'port')
            number_for_port = self.DB.check_number_for_port(game_id, bot_id)
            if is_port and (number in number_for_port):
                await sleep(2.5)
                await self.refresh_history(game_id)
                new_number = number + 2
                new_story = f'\n      :anchor: :game_die::game_die:  {number} :right_arrow: {new_number}'
                self.DB.put_new_story(new_story, game_id)
                number = new_number
            await self.refresh_history(game_id)
            await sleep(1)
        else:
            number = random.randint(1, 6)
            turn_story = f'\n{self.bot_cldr} {bot_name}   :game_die:   {number}'
            self.DB.put_new_story(turn_story, game_id)
            await self.refresh_history(game_id)
            await sleep(1)
        return number

    async def basic_build_2(self, game_id, bot_id):
        money = self.DB.money(game_id, bot_id)
        if money:
            all_card = self.DB.get_all_card_from_table(game_id)
            bot_card = self.DB.get_player_card(game_id, bot_id)

            if money > 9 and not ('shopping mall' in bot_card): return 'shopping mall'
            if 'radio tower' in bot_card:
                if money > 3 and not ('train station' in bot_card): return 'train station'
                if money > 15 and not('amusement park' in bot_card): return 'amusement park'
            else:
                if money > 21: return 'radio tower'
            if money > 2 and ('store' in all_card): return 'store'
            if 'bakery' in all_card: return 'bakery'
            if money > 1 and ('cafe' in all_card): return 'cafe'
            if 'farm' in all_card: return 'farm'
            if 'wheat field' in all_card: return 'wheat field'

    async def basic_build_3(self, game_id, bot_id):
        money = self.DB.money(game_id, bot_id)
        if money:
            all_cards = self.DB.get_all_card_from_table(game_id)
            bot_cards = self.DB.get_player_card(game_id, bot_id)
            shopping_card = 0
            for card, quantity in bot_cards.items():
                if card in ['bakery', 'store', 'cafe']:
                    shopping_card += quantity
            if shopping_card > 4:
                if money > 9 and not ('shopping mall' in bot_cards): return 'shopping mall'
            if 'bakery' in bot_cards:
                if bot_cards['bakery'] > 2:
                    if money > 9 and not ('shopping mall' in bot_cards): return 'shopping mall'
            if 'radio tower' in bot_cards:
                if money > 9 and not ('shopping mall' in bot_cards): return 'shopping mall'
                if money > 3 and not ('train station' in bot_cards): return 'train station'
                if money > 15 and not('amusement park' in bot_cards): return 'amusement park'
            else:
                if money > 21: return 'radio tower'
            if 'farm' in all_cards: return 'farm'
            if 'wheat field' in all_cards: return 'wheat field'
            if money > 1 and ('cafe' in all_cards): return 'cafe'
            if money > 2 and ('store' in all_cards): return 'store'
            if 'bakery' in all_cards: return 'bakery'

    async def add_build_4(self, game_id, bot_id):
        money = self.DB.money(game_id, bot_id)
        all_cards = self.DB.get_all_card_from_table(game_id)
        bot_cards = self.DB.get_player_card(game_id, bot_id)
        game_laps, game_moves = self.DB.get_laps_and_moves(game_id)
        if 'train station' in bot_cards:
            if not ('radio tower' in bot_cards) and (money > 21): return 'radio tower'
            if 'radio tower' in bot_cards:
                if not ('amusement park' in bot_cards) and (money > 15): return 'amusement park'
                if not ('airport' in bot_cards) and (money > 29): return 'airport'
            if 'airport' in bot_cards:
                if not ('shopping mall' in bot_cards) and (money > 9): return 'shopping mall'
                if not ('port' in bot_cards) and (money > 1): return 'port'
                return None
        if game_laps < 13:
            return await self.good_strategy_add_4_current_lap[game_laps](money, all_cards, bot_cards)
        return await self.add_build_4_lap_13_plus(money, all_cards, bot_cards)

    @staticmethod
    async def add_build_4_lap_13_plus(money, all_cards, bot_cards):
        if 'cafe' in bot_cards:
            if ('food storage' in bot_cards) and not ('train station' in bot_cards) and (
                    money > 3): return 'train station'
            if (money > 3) and not ('tax office' in bot_cards): return 'tax office'
            if (money > 1) and ('food storage' in all_cards): return 'food storage'
            if (money > 2) and ('restaurant' in all_cards) and ((bot_cards.get(
                    'restaurant', 0) <= bot_cards.get('pizzeria', 0) and (bot_cards.get(
                    'restaurant', 0) <= bot_cards.get('diner', 0)))): return 'restaurant'
            if ('pizzeria' in all_cards) and (
                    bot_cards.get('pizzeria', 0) <= bot_cards.get('diner', 0)): return 'pizzeria'
            if 'diner' in all_cards: return 'diner'
        mech = bot_cards.get('forest', 0) + bot_cards.get('mine', 0)
        if mech:
            if ('furniture factory' in bot_cards) and (money > 3) and not (
                    'train station' in bot_cards): return 'train station'
            if (money > 3) and not ('tax office' in bot_cards): return 'tax office'
            if (money > 2) and ('furniture factory' in all_cards) and (
                    (bot_cards.get('furniture factory', 0) < mech - 4) or (
                    not ('forest' in all_cards) and (money < 6))): return 'furniture factory'
            if (money > 5) and ('mine' in all_cards) and ((mech > 4) or not ('forest' in all_cards)): return 'mine'
            if (money > 2) and ('forest' in all_cards): return 'forest'
        if bot_cards.get('farm', 0) >= 3:
            if (money > 3) and ('cheese factory' in bot_cards) and not (
                    'train station' in bot_cards): return 'train station'
            if (money > 3) and not ('tax office' in bot_cards) and (
                    (bot_cards.get('cheese factory', 0) > 1) or (money < 5)): return 'tax office'
            if (money > 4) and not ('publisher' in bot_cards) and (bot_cards.get(
                    'cheese factory', 0) > 3): return 'publisher'
            if (money > 4) and ('cheese factory' in all_cards): return 'cheese factory'
        fruit = bot_cards.get('flower garden', 0) + bot_cards['wheat field'] + bot_cards.get('apple orchard', 0)
        if fruit > 4:
            if (bot_cards.get('produce market', 0) > 1) and (money > 3) and not (
                    'train station' in bot_cards): return 'train station'
            if not ('port' in bot_cards) and (money > 1): return 'port'
            if ('produce market' in all_cards) and (money > 1) and (
                    bot_cards.get('produce market', 0) < fruit - 4): return 'produce market'
            if (money > 2) and ('apple orchard' in all_cards): return 'apple orchard'
            if (money > 1) and ('flower garden' in all_cards): return 'flower garden'
            if bot_cards.get('flower garden', 0) > 2: return 'flower shop'
        if (money > 3) and not ('train station' in bot_cards):return 'train station'
        if (money > 3) and not ('tax office' in bot_cards): return 'tax office'
        if 'port' in bot_cards:
            if (money > 4) and ('trawler' in all_cards): return 'trawler'
            if (money > 1) and ('fishing launch' in all_cards): return 'fishing launch'
        else:
            if money > 1: return 'port'

    @staticmethod
    async def add_build_4_lap_12(money, all_cards, bot_cards):
        if 'cafe' in bot_cards:
            if ('food storage' in bot_cards) and not ('train station' in bot_cards) and (
                    money > 3): return 'train station'
            if (money > 2) and ('restaurant' in all_cards) and ((bot_cards.get(
                    'restaurant', 0) <= bot_cards.get('pizzeria', 0) and (bot_cards.get(
                'restaurant', 0) <= bot_cards.get('diner', 0)))): return 'restaurant'
            if (money > 1) and ('food storage' in all_cards): return 'food storage'
            if ('pizzeria' in all_cards) and (
                    bot_cards.get('pizzeria', 0) <= bot_cards.get('diner', 0)): return 'pizzeria'
            if 'diner' in all_cards: return 'diner'
        mech = bot_cards.get('forest', 0) + bot_cards.get('mine', 0)
        if mech:
            if ('furniture factory' in bot_cards) and (money > 3) and not (
                    'train station' in bot_cards): return 'train station'
            if (money > 3) and not ('tax office' in bot_cards): return 'tax office'
            if (money > 2) and ('furniture factory' in all_cards) and (
                    (bot_cards.get('furniture factory', 0) < mech - 4) or (
                    not ('forest' in all_cards) and (money < 6))): return 'furniture factory'
            if (money > 5) and ('mine' in all_cards) and ((mech > 4) or not ('forest' in all_cards)): return 'mine'
            if (money > 2) and ('forest' in all_cards): return 'forest'
        if bot_cards.get('farm', 0) >= 3:
            if (money > 3) and ('cheese factory' in bot_cards) and not (
                    'train station' in bot_cards): return 'train station'
            if (money > 3) and not ('tax office' in bot_cards): return 'tax office'
            if (money > 4) and not ('publisher' in bot_cards): return 'publisher'
            if (money > 4) and ('cheese factory' in all_cards): return 'cheese factory'
        fruit = bot_cards.get('flower garden', 0) + bot_cards['wheat field'] + bot_cards.get('apple orchard', 0)
        if fruit > 4:
            if (bot_cards.get('produce market', 0) > 1) and (money > 3) and not (
                    'train station' in bot_cards): return 'train station'
            if not ('port' in bot_cards) and ('train station' in bot_cards) and (money > 1): return 'port'
            if (money > 3) and not ('tax office' in bot_cards) and (
                    (bot_cards.get('cheese factory', 0) > 1) or (money < 5)): return 'tax office'
            if ('produce market' in all_cards) and (money > 1) and (
                    bot_cards.get('produce market', 0) < fruit - 4): return 'produce market'
            if (money > 2) and ('apple orchard' in all_cards): return 'apple orchard'
            if (money > 1) and ('flower garden' in all_cards): return 'flower garden'
            if bot_cards.get('flower garden', 0) > 2: return 'flower shop'
        if (money > 3) and not ('train station' in bot_cards):return 'train station'
        if (money > 3) and not ('tax office' in bot_cards): return 'tax office'
        if 'port' in bot_cards:
            if (money > 4) and ('trawler' in all_cards): return 'trawler'
            if (money > 1) and ('fishing launch' in all_cards): return 'fishing launch'
        else:
            if money > 1: return 'port'

    @staticmethod
    async def add_build_4_lap_11(money, all_cards, bot_cards):
        if 'cafe' in bot_cards:
            if ('food storage' in bot_cards) and not ('train station' in bot_cards) and (
                    money > 3): return 'train station'
            if (money > 2) and ('restaurant' in all_cards) and ((bot_cards.get(
                    'restaurant', 0) <= bot_cards.get('pizzeria', 0) and (bot_cards.get(
                'restaurant', 0) <= bot_cards.get('diner', 0)))): return 'restaurant'
            if (money > 1) and ('food storage' in all_cards): return 'food storage'
            if ('pizzeria' in all_cards) and (
                    bot_cards.get('pizzeria', 0) <= bot_cards.get('diner', 0)): return 'pizzeria'
            if 'diner' in all_cards: return 'diner'
        mech = bot_cards.get('forest', 0) + bot_cards.get('mine', 0)
        if mech:
            if ('furniture factory' in bot_cards) and (money > 3) and not (
                    'train station' in bot_cards): return 'train station'
            if (money > 3) and not ('tax office' in bot_cards): return 'tax office'
            if (money > 2) and ('furniture factory' in all_cards) and (
                    (bot_cards.get('furniture factory', 0) < mech - 4) or (
                    not ('forest' in all_cards) and (money < 6))): return 'furniture factory'
            if (money > 5) and ('mine' in all_cards) and ((mech > 4) or not ('forest' in all_cards)): return 'mine'
            if (money > 2) and ('forest' in all_cards): return 'forest'
        if bot_cards.get('farm', 0) >= 3:
            if (money > 3) and ('cheese factory' in bot_cards) and not (
                    'train station' in bot_cards): return 'train station'
            if (money > 3) and not ('tax office' in bot_cards) and (
                    (bot_cards.get('cheese factory', 0) > 1) or (money < 5)): return 'tax office'
            if (money > 4) and not ('publisher' in bot_cards) and (bot_cards.get(
                    'cheese factory', 0) > 2): return 'publisher'
            if (money > 4) and ('cheese factory' in all_cards): return 'cheese factory'
        fruit = bot_cards.get('flower garden', 0) + bot_cards['wheat field'] + bot_cards.get('apple orchard', 0)
        if fruit > 4:
            if (bot_cards.get('produce market', 0) > 1) and (money > 3) and not (
                    'train station' in bot_cards): return 'train station'
            if not ('port' in bot_cards) and ('train station' in bot_cards) and (money > 1): return 'port'
            if ('produce market' in all_cards) and (money > 1) and (
                    bot_cards.get('produce market', 0) < fruit - 4): return 'produce market'
            if (money > 2) and ('apple orchard' in all_cards): return 'apple orchard'
            if (money > 1) and ('flower garden' in all_cards): return 'flower garden'
            if bot_cards.get('flower garden', 0) > 2: return 'flower shop'
        if (money > 3) and not ('train station' in bot_cards):return 'train station'
        if (money > 3) and not ('tax office' in bot_cards): return 'tax office'
        if 'port' in bot_cards:
            if (money > 4) and ('trawler' in all_cards): return 'trawler'
            if (money > 1) and ('fishing launch' in all_cards): return 'fishing launch'
        else:
            if money > 1: return 'port'

    @staticmethod
    async def add_build_4_lap_10(money, all_cards, bot_cards):
        if 'cafe' in bot_cards:
            if bot_cards['cafe'] == 2 and not ('port' in bot_cards) and (money > 1): return 'port'
            if 'food storage' in bot_cards and (money > 3): return 'train station'
            if (money > 1) and ('food storage' in all_cards): return 'food storage'
            if ('pizzeria' in all_cards) and (
                    bot_cards.get('pizzeria', 0) <= bot_cards.get('diner', 0)): return 'pizzeria'
            if 'diner' in all_cards: return 'diner'
        mech = bot_cards.get('forest', 0) + bot_cards.get('mine', 0)
        if mech:
            if ('furniture factory' in bot_cards) and (money > 3) and not (
                    'train station' in bot_cards): return 'train station'
            if (money > 2) and ('furniture factory' in all_cards) and (
                    (bot_cards.get('furniture factory', 0) < mech - 4) or (
                    not ('forest' in all_cards) and (money < 6))): return 'furniture factory'
            if (money > 5) and ('mine' in all_cards) and ((mech > 4) or not ('forest' in all_cards)): return 'mine'
            if (money > 2) and ('forest' in all_cards): return 'forest'
        if bot_cards.get('farm', 0) >= 3:
            if (money > 3) and ('cheese factory' in bot_cards) and not (
                    'train station' in bot_cards): return 'train station'
            if (money > 3) and not ('tax office' in bot_cards) and (
                    (bot_cards.get('cheese factory', 0) > 1) or (money < 5)): return 'tax office'
            if (money > 4) and ('cheese factory' in all_cards): return 'cheese factory'
        fruit = bot_cards.get('flower garden', 0) + bot_cards['wheat field'] + bot_cards.get('apple orchard', 0)
        if fruit > 4:
            if (bot_cards.get('produce market', 0) > 1) and (money > 3) and not (
                    'train station' in bot_cards): return 'train station'
            if not ('port' in bot_cards) and ('train station' in bot_cards) and (money > 1): return 'port'
            if ('produce market' in all_cards) and (money > 1) and (
                bot_cards.get('produce market', 0) < fruit - 4): return 'produce market'
            if (money > 2) and ('apple orchard' in all_cards) : return 'apple orchard'
            if (money > 1) and ('flower garden' in all_cards): return 'flower garden'
            if bot_cards.get('flower garden', 0) > 2: return 'flower shop'
        if (money > 3) and not ('train station' in bot_cards):return 'train station'
        if (money > 3) and not ('tax office' in bot_cards): return 'tax office'
        if 'port' in bot_cards:
            if (money > 4) and ('trawler' in all_cards): return 'trawler'
            if (money > 1) and ('fishing launch' in all_cards): return 'fishing launch'
        else:
            if money > 1: return 'port'

    @staticmethod
    async def add_build_4_lap_9(money, all_cards, bot_cards):
        if 'cafe' in bot_cards:
            if (money) > 1 and ('food storage' in all_cards): return 'food storage'
            if ('pizzeria' in all_cards) and (
                    bot_cards.get('pizzeria', 0) <= bot_cards.get('diner', 0)): return 'pizzeria'
            if 'diner' in all_cards: return 'diner'
        mech = bot_cards.get('forest', 0) + bot_cards.get('mine', 0)
        if mech:
            if ('furniture factory' in bot_cards) and (money > 3) and not (
                    'train station' in bot_cards): return 'train station'
            if (money > 2) and ('furniture factory' in all_cards) and (
                    (bot_cards.get('furniture factory', 0) < mech - 4) or (
                    not ('forest' in all_cards) and (money < 6))): return 'furniture factory'
            if (money > 5) and ('mine' in all_cards) and ((mech > 4) or not ('forest' in all_cards)): return 'mine'
            if (money > 2) and ('forest' in all_cards): return 'forest'
        if bot_cards.get('farm', 0) >= 3:
            if (money > 3) and ('cheese factory' in bot_cards) and not (
                    'train station' in bot_cards): return 'train station'
            if (money > 3) and not ('tax office' in bot_cards) and (
                    (bot_cards.get('cheese factory', 0) > 1) or (money < 5)): return 'tax office'
            if (money > 4) and ('cheese factory' in all_cards): return 'cheese factory'
        fruit = bot_cards.get('flower garden', 0) + bot_cards['wheat field'] + bot_cards.get('apple orchard', 0)
        if fruit > 4:
            if (bot_cards.get('produce market', 0) > 1) and (money > 3) and not (
                    'train station' in bot_cards): return 'train station'
            if not ('port' in bot_cards) and ('train station' in bot_cards) and (money > 1): return 'port'
            if ('produce market' in all_cards) and (money > 1) and (
                    bot_cards.get('produce market', 0) < fruit - 4): return 'produce market'
            if (money > 2) and ('apple orchard' in all_cards): return 'apple orchard'
            if (money > 1) and ('flower garden' in all_cards): return 'flower garden'
            if bot_cards.get('flower garden', 0) > 2: return 'flower shop'
        if (money > 3) and not ('train station' in bot_cards):return 'train station'
        if (money > 3) and not ('tax office' in bot_cards): return 'tax office'
        if 'port' in bot_cards:
            if (money > 4) and ('trawler' in all_cards): return 'trawler'
            if (money > 1) and ('fishing launch' in all_cards): return 'fishing launch'
        else:
            if money > 1: return 'port'

    @staticmethod
    async def add_build_4_lap_8(money, all_cards, bot_cards):
        if 'cafe' in bot_cards:
            if (money > 9) and not ('shopping mall' in bot_cards): return 'shopping mall'
            if 'port' in bot_cards:
                if (money > 1) and ('sushi bar' in all_cards) and not ('sushi bar' in bot_cards): return 'sushi bar'
            if bot_cards['cafe'] == 2 and not ('port' in bot_cards) and (money > 1): return 'port'
            if (money > 1) and ('cafe' in all_cards) and (bot_cards['cafe'] < 3): return 'cafe'
            if (money > 2) and ('restaurant' in all_cards) and ((bot_cards.get(
                    'restaurant', 0) <= bot_cards.get('pizzeria', 0) and (bot_cards.get(
                'restaurant', 0) <= bot_cards.get('diner', 0)))): return 'restaurant'
            if ('pizzeria' in all_cards) and (
                    bot_cards.get('pizzeria', 0) <= bot_cards.get('diner', 0)): return 'pizzeria'
            if 'diner' in all_cards: return 'diner'
        mech = bot_cards.get('forest', 0) + bot_cards.get('mine', 0)
        if mech:
            if ('furniture factory' in bot_cards) and (money > 3) and not (
                    'train station' in bot_cards): return 'train station'
            if (money > 2) and ('furniture factory' in all_cards) and (
                    (bot_cards.get('furniture factory', 0) < mech - 4) or (
                    not ('forest' in all_cards) and (money < 6))): return 'furniture factory'
            if (money > 5) and ('mine' in all_cards) and ((mech > 4) or not ('forest' in all_cards)): return 'mine'
            if (money > 2) and ('forest' in all_cards): return 'forest'
        if bot_cards.get('farm', 0) >= 3:
            if (money > 3) and ('cheese factory' in bot_cards) and not (
                    'train station' in bot_cards): return 'train station'
            if (money > 4) and ('cheese factory' in all_cards): return 'cheese factory'
        fruit = bot_cards.get('flower garden', 0) + bot_cards['wheat field'] + bot_cards.get('apple orchard', 0)
        if fruit > 4:
            if (bot_cards.get('produce market', 0) > 1) and (money > 3) and not (
                    'train station' in bot_cards): return 'train station'
            if ('produce market' in all_cards) and (money > 1) and (
                    bot_cards.get('produce market', 0) < fruit - 4): return 'produce market'
            if (money > 2) and ('apple orchard' in all_cards): return 'apple orchard'
            if (money > 1) and ('flower garden' in all_cards): return 'flower garden'
            if bot_cards.get('flower garden', 0) > 2: return 'flower shop'
        if (money > 3) and not ('train station' in bot_cards):return 'train station'
        if (money > 3) and not ('tax office' in bot_cards): return 'tax office'
        if 'port' in bot_cards:
            if (money > 4) and ('trawler' in all_cards): return 'trawler'
            if (money > 1) and ('fishing launch' in all_cards): return 'fishing launch'
        else:
            if money > 1: return 'port'

    @staticmethod
    async def add_build_4_lap_7(money, all_cards, bot_cards):
        if 'cafe' in bot_cards:
            if (money > 9) and not ('shopping mall' in bot_cards): return 'shopping mall'
            if 'port' in bot_cards:
                if (money > 1) and ('sushi bar' in all_cards) and not ('sushi bar' in bot_cards): return 'sushi bar'
            if bot_cards['cafe'] == 2 and not ('port' in bot_cards) and (money > 1): return 'port'
            if (money > 1) and ('cafe' in all_cards) and (bot_cards['cafe'] < 3): return 'cafe'
            if (money > 2) and ('restaurant' in all_cards) and ((bot_cards.get(
                    'restaurant', 0) <= bot_cards.get('pizzeria', 0) and (bot_cards.get(
                'restaurant', 0) <= bot_cards.get('diner', 0)))): return 'restaurant'
            if ('pizzeria' in all_cards) and (
                    bot_cards.get('pizzeria', 0) <= bot_cards.get('diner', 0)): return 'pizzeria'
            if 'diner' in all_cards: return 'diner'
        mech = bot_cards.get('forest', 0) + bot_cards.get('mine', 0)
        if mech:
            if ('furniture factory' in bot_cards) and (money > 3): return 'train station'
            if (money > 2) and ('furniture factory' in all_cards) and (
                    (bot_cards.get('furniture factory', 0) < mech - 4) or (
                    not ('forest' in all_cards) and (money < 6))): return 'furniture factory'
            if (money > 5) and ('mine' in all_cards) and ((mech > 4) or not ('forest' in all_cards)): return 'mine'
            if (money > 2) and ('forest' in all_cards): return 'forest'
        if bot_cards.get('farm', 0) >= 3:
            if (money > 3) and ('cheese factory' in bot_cards) and not (
                    'train station' in bot_cards): return 'train station'
            if (money > 4) and ('cheese factory' in all_cards): return 'cheese factory'
        fruit = bot_cards.get('flower garden', 0) + bot_cards['wheat field'] + bot_cards.get('apple orchard', 0)
        if fruit > 4:
            if (bot_cards.get('produce market', 0) > 1) and (money > 3) and not (
                    'train station' in bot_cards): return 'train station'
            if ('produce market' in all_cards) and (money > 1) and (
                    bot_cards.get('produce market', 0) < fruit - 4): return 'produce market'
            if (money > 2) and ('apple orchard' in all_cards): return 'apple orchard'
            if (money > 1) and ('flower garden' in all_cards): return 'flower garden'
            if bot_cards.get('flower garden', 0) > 2: return 'flower shop'
        if (money > 3) and not ('train station' in bot_cards):return 'train station'
        if (money > 3) and not ('tax office' in bot_cards): return 'tax office'
        if 'port' in bot_cards:
            if (money > 4) and ('trawler' in all_cards): return 'trawler'
            if (money > 1) and ('fishing launch' in all_cards): return 'fishing launch'
        else:
            if money > 1: return 'port'

    @staticmethod
    async def add_build_4_lap_6(money, all_cards, bot_cards):
        if 'cafe' in bot_cards:
            if (money > 9) and not ('shopping mall' in bot_cards): return 'shopping mall'
            if 'port' in bot_cards:
                if (money > 1) and ('sushi bar' in all_cards) and not ('sushi bar' in bot_cards): return 'sushi bar'
            if bot_cards['cafe'] == 2 and not ('port' in bot_cards) and (money > 1): return 'port'
            if (money > 1) and ('cafe' in all_cards) and (bot_cards['cafe'] < 3): return 'cafe'
            if (money > 2) and ('restaurant' in all_cards) and ((bot_cards.get(
                    'restaurant', 0) <= bot_cards.get('pizzeria', 0) and (bot_cards.get(
                    'restaurant', 0) <= bot_cards.get('diner', 0)))): return 'restaurant'
            if ('pizzeria' in all_cards) and (
                    bot_cards.get('pizzeria', 0) <= bot_cards.get('diner', 0)): return 'pizzeria'
            if 'diner' in all_cards: return 'diner'
        mech = bot_cards.get('forest', 0) + bot_cards.get('mine', 0)
        if mech:
            if (money > 2) and ('furniture factory' in all_cards) and (
               (bot_cards.get('furniture factory', 0) < mech - 4) or (
                not ('forest' in all_cards) and (money < 6))): return 'furniture factory'
            if (money > 5) and ('mine' in all_cards) and ((mech > 4) or not ('forest' in all_cards)): return 'mine'
            if (money > 2) and ('forest' in all_cards): return 'forest'
        if bot_cards.get('farm', 0) >= 3:
            if 'farm' in all_cards: return 'farm'
            if (money > 3) and ('cheese factory' in bot_cards) and not (
                    'train station' in bot_cards): return 'train station'
            if (money > 4) and ('cheese factory' in all_cards): return 'cheese factory'
        fruit = bot_cards.get('flower garden', 0) + bot_cards['wheat field']
        if fruit > 3:
            if (bot_cards.get('produce market', 0) > 1) and (money > 3) and not (
                    'train station' in bot_cards): return 'train station'
            if (money > 1) and ('flower garden' in all_cards): return 'flower garden'
            if ('produce market' in all_cards) and (money > 1): return 'produce market'
            if bot_cards.get('flower garden', 0) > 2: return 'flower shop'
            if 'wheat field' in all_cards: return 'wheat field'
            if 'farm' in all_cards: return 'farm'
            if (money > 2) and ('apple orchard' in all_cards): return 'apple orchard'
        if (money > 3) and not ('train station' in bot_cards):return 'train station'
        if (money > 3) and not ('tax office' in bot_cards): return 'tax office'
        if 'port' in bot_cards:
            if (money > 4) and ('trawler' in all_cards): return 'trawler'
            if (money > 1) and ('fishing launch' in all_cards): return 'fishing launch'
        else:
            if money > 1: return 'port'

    @staticmethod
    async def add_build_4_lap_5(money, all_cards, bot_cards):
        if 'cafe' in bot_cards:
            if money > 9: return 'shopping mall'
            if 'port' in bot_cards:
                if (money > 1) and ('sushi bar' in all_cards) and not ('sushi bar' in bot_cards): return 'sushi bar'
            if bot_cards['cafe'] == 2 and not ('port' in bot_cards) and (money > 1): return 'port'
            if (money > 1) and ('cafe' in all_cards) and (bot_cards['cafe'] < 3): return 'cafe'
            if ('diner' in all_cards) and (bot_cards.get('pizzeria', 0) > bot_cards.get('diner', 0)): return 'diner'
            if 'pizzeria' in all_cards: return 'pizzeria'
        if 'forest' in bot_cards:
            if (money > 2) and ('forest' in all_cards): return 'forest'
            if (money > 5) and ('mine' in all_cards): return 'mine'
            if (money > 2) and ('furniture factory' in all_cards): return 'furniture factory'
            if all_cards.get('farm', 0): return 'farm'
            if 'wheat field' in all_cards: return 'wheat field'
        if bot_cards.get('farm', 0) >= 3:
            if 'farm' in all_cards: return 'farm'
            if (money > 3) and ('cheese factory' in bot_cards) and not(
                    'train station' in bot_cards): return 'train station'
            if (money > 4) and ('cheese factory' in all_cards): return 'cheese factory'
            if 'wheat field' in all_cards: return 'wheat field'
            if 'bakery' in all_cards: return 'bakery'
        fruit = bot_cards.get('flower garden', 0) + bot_cards['wheat field']
        if fruit > 3:
            if (money > 1) and ('flower garden' in all_cards): return 'flower garden'
            if ('produce market' in all_cards) and (money > 1): return 'produce market'
            if bot_cards.get('flower garden', 0) > 2: return 'flower shop'
            if 'wheat field' in all_cards: return 'wheat field'
            if 'farm' in all_cards: return 'farm'
            if (money > 2) and ('apple orchard' in all_cards): return 'apple orchard'
            if ('produce market' in all_cards) and (money > 1): return'produce market'
        if 'port' in bot_cards:
            if (money > 4) and ('trawler' in all_cards): return 'trawler'
            if (money > 1) and ('fishing launch' in all_cards): return 'fishing launch'
        else:
            if money > 1: return 'port'

    @staticmethod
    async def add_build_4_lap_4(money, all_cards, bot_cards):
        if 'cafe' in bot_cards:
            if 'port' in bot_cards:
                if (money > 1) and ('sushi bar' in all_cards) and not ('sushi bar' in bot_cards): return 'sushi bar'
            if bot_cards['cafe'] == 2 and not ('port' in bot_cards) and (money > 1): return 'port'
            if (money > 1) and ('cafe' in all_cards) and (bot_cards['cafe'] < 3): return 'cafe'
            if ('diner' in all_cards) and (bot_cards.get('pizzeria', 0) > bot_cards.get('diner', 0)): return 'diner'
            if 'pizzeria' in all_cards: return 'pizzeria'
        if 'forest' in bot_cards:
            if (money > 2) and ('forest' in all_cards): return 'forest'
            if all_cards.get('farm', 0): return 'farm'
            if 'wheat field' in all_cards: return 'wheat field'
        if bot_cards.get('farm', 0) >= 3:
            if 'farm' in all_cards: return 'farm'
            if (money > 3) and ('cheese factory' in bot_cards): return 'train station'
            if (money > 4) and ('cheese factory' in all_cards): return 'cheese factory'
            if 'wheat field' in all_cards: return 'wheat field'
            if 'bakery' in all_cards: return 'bakery'
        fruit = bot_cards.get('flower garden', 0) + bot_cards['wheat field']
        if fruit >= 3:
            if (money > 1) and ('flower garden' in all_cards): return 'flower garden'
            if 'wheat field' in all_cards: return 'wheat field'
            if ('produce market' in all_cards) and (money > 1): return'produce market'
            if 'farm' in all_cards: return 'farm'
        if 'port' in bot_cards:
            if (money > 4) and ('trawler' in all_cards): return 'trawler'
            if (money > 1) and ('fishing launch' in all_cards): return 'fishing launch'
        else:
            if money > 1: return 'port'

    @staticmethod
    async def add_build_4_lap_3(money, all_cards, bot_cards):
        if 'cafe' in bot_cards:
            if 'port' in bot_cards:
                if (money > 1) and ('sushi bar' in all_cards): return 'sushi bar'
            if bot_cards['cafe'] == 2 and not ('port' in bot_cards) and (money > 1): return 'port'
            if (money > 1) and ('cafe' in all_cards): return 'cafe'
            if 'pizzeria' in all_cards: return 'pizzeria'
            if 'diner' in all_cards: return 'diner'
        if 'forest' in bot_cards:
            if (money > 2) and ('forest' in all_cards): return 'forest'
            if all_cards.get('farm', 0) > 2: return 'farm'
            if 'wheat field' in all_cards: return 'wheat field'
        if bot_cards.get('farm', 0) == 3:
            if 'farm' in all_cards: return 'farm'
            if money > 5: return 'stadium'
            if (money > 4) and ('cheese factory' in all_cards): return 'cheese factory'
            if 'wheat field' in all_cards: return 'wheat field'
            if 'bakery' in all_cards: return 'bakery'
        fruit = bot_cards.get('flower garden', 0) + bot_cards['wheat field']
        if (fruit == 4) or ((fruit >= 2) and ('farm' in bot_cards)):
            if (money > 1) and ('flower garden' in all_cards): return 'flower garden'
            if 'wheat field' in all_cards: return 'wheat field'
            if ('produce market' in all_cards) and (money > 1): return 'produce market'
            if 'farm' in all_cards: return 'farm'
        if ('store' in all_cards) and (money > 1): return 'store'
        if 'bakery' in all_cards: return 'bakery'

    @staticmethod
    async def add_build_4_lap_2(money, all_cards, bot_cards):
        if 'cafe' in bot_cards:
            if bot_cards['cafe'] == 2:
                if money > 1: return 'port'
            if (money > 1) and ('cafe' in all_cards): return 'cafe'
            if 'pizzeria' in all_cards: return 'pizzeria'
            if 'diner' in all_cards: return 'diner'
        if 'forest' in bot_cards:
            if (money > 2) and ('forest' in all_cards): return 'forest'
            if all_cards.get('farm', 0) > 3: return 'farm'
            if 'wheat field' in all_cards: return 'wheat field'
        fruit = bot_cards.get('flower garden', 0) + bot_cards['wheat field']
        if (fruit == 3) or ((fruit == 2) and ('farm' in bot_cards)):
            if (money > 1) and ('flower garden' in all_cards): return 'flower garden'
            if 'wheat field' in all_cards: return 'wheat field'
            if 'farm' in all_cards: return 'farm'
            if ('produce market' in all_cards) and (money > 1): return 'produce market'
        if bot_cards.get('farm', 0) == 2:
            if all_cards.get('farm', 0) > 1: return 'farm'
            if (all_cards.get('forest', 0) > 3) and (money > 2): 'forest'
            if (all_cards.get('cafe', 0) > 2) and (money > 1): 'cafe'
            if (money > 1) and ('flower garden' in all_cards): 'flower garden'
        if 'wheat field' in all_cards: return 'wheat field'
        if ('store' in all_cards) and (money > 1): return 'store'
        if 'bakery' in all_cards: return 'bakery'

    @staticmethod
    async def add_build_4_lap_1(money, all_cards, bot_cards):
        if 'cafe' in bot_cards:
            if (money > 1) and ('cafe' in all_cards): return 'cafe'
            if all_cards.get('farm', 0): return 'farm'
            if 'wheat field' in all_cards: return 'wheat field'
        if 'forest' in bot_cards:
            if (money > 2) and ('forest' in all_cards): return 'forest'
            if all_cards.get('farm', 0) > 4: return 'farm'
            if 'wheat field' in all_cards: return 'wheat field'
        if ('flower garden' in bot_cards) or bot_cards['wheat field'] == 2:
            if ((all_cards.get('flower garden', 0) + all_cards.get('wheat field', 0)) < 9) and (
                    all_cards.get('forest', 0) == 6) and (money > 2): return 'forest'
            if (money > 1) and ('flower garden' in all_cards): return 'flower garden'
            if 'wheat field' in all_cards: return 'wheat field'
            if 'farm' in all_cards: return 'farm'
        if 'farm' in bot_cards:
            if all_cards.get('farm', 0) > 3: return 'farm'
            if (all_cards.get('forest', 0) > 4) and (money > 2): return 'forest'
            if (all_cards.get('cafe', 0) > 4) and (money > 1): return 'cafe'
            if (money > 1) and ('flower garden' in all_cards): 'flower garden'
        if 'wheat field' in all_cards: return 'wheat field'
        if ('store' in all_cards) and (money > 1): return 'store'
        if 'bakery' in all_cards: return 'bakery'



    @staticmethod
    async def add_build_4_lap_0(money, all_cards, bot_cards):
        if (money > 2) and (all_cards['forest'] == 6): return 'forest'
        if (money > 1) and (all_cards['cafe'] == 6): return 'cafe'
        if (money > 1) and (all_cards['flower garden'] >= all_cards['farm']): return 'flower garden'
        if (all_cards['farm'] >= all_cards['wheat field']) and all_cards['farm'] > 4: return 'farm'
        return 'wheat field'

    async def bot_roll(self, game_id, bot_id, bot_name):
        type_game, number_players = self.DB.type_game(game_id)
        number = await self.strategy_roll[type_game][number_players](game_id, bot_id, bot_name)
        return number

    async def bot_build(self, game_id, bot_id, bot_name):
        type_game, number_players = self.DB.type_game(game_id)
        card_name = await self.strategy_build[type_game][number_players](game_id, bot_id)

        if card_name:
            cots_card, view_card = self.DB.card_info_for_bot_build(card_name)
            win = self.DB.add_card_to_player(game_id, card_name, bot_id)
            self.DB.pull_money_changes(game_id, {bot_id: -cots_card})
            build_history = f'\n       :building_construction:      :{view_card}:'
            self.DB.put_new_story(build_history, game_id)
            return True, win
        else:
            is_airport = self.DB.is_card_in_city(game_id, bot_id, 'airport')
            new_story = f'\n       :building_construction:      :prohibited:'
            if is_airport:
                self.DB.pull_money_changes(game_id, {bot_id: 10})
                new_story += f'\n    -  {bot_name}   + 10  :dollar_banknote:'
            self.DB.put_new_story(new_story, game_id)
            return False, False
