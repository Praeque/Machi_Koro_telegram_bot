import random
from data import ActionDB


class CardPlay:

    def __init__(self, db: ActionDB):
        self.DB = db

        self.green_cards = {
            'bakery': self.bakery, 'store': self.store, 'cheese factory': self.cheese_factory,
            'furniture factory': self.furniture_factory, 'produce market': self.produce_market,
            'flower shop': self.flower_shop, 'food storage': self.food_storage,
        }
        self.special_cards = {'stadium': self.play_stadium, 'tax office': self.tax_office, 'publisher': self.publisher}

    def play_red_cards(self, game_id, player_id, number):
        player_money = self.DB.money(game_id, player_id)
        if not player_money:
            return {}
        red_cards, session = self.DB.get_red_cards(game_id, number)
        money_changes = {player_id: 0}
        for card in red_cards:
            if card.player_id == player_id:
                continue
            if card.name_card == 'sushi bar':
                if not self.DB.is_card_in_city(game_id, card.player_id, 'port'):
                    continue
            income = card.income
            if self.DB.is_shopping_mall(game_id, card.player_id):
                income += 1
            income *= card.quantity
            print(self.DB.get_name(game_id, player_id), player_money)
            print(income)
            if player_money < income:
                income = player_money
                print('change', '->', income)
            print(player_money - income, 'after')
            money_changes[card.player_id] = income
            money_changes[player_id] -= income
            player_money -= income
            if player_money == 0:
                break
        session.close()
        self.DB.pull_money_changes(game_id, money_changes)
        del money_changes[player_id]
        return money_changes

    def play_pink_cards(self, game_id, player_id, number):
        pink_cards, session = self.DB.get_pink_card(game_id, number, player_id)
        result = ''
        for card in pink_cards:
            if card.name_card in self.special_cards:
                result += self.special_cards[card.name_card](game_id, player_id)
        session.close()
        return result

    def play_green_cards(self, game_id, player_id, number):
        green_cards, session = self.DB.get_green_cards(game_id, player_id, number)
        money_change = 0
        for card in green_cards:
            money_change += self.green_cards[card.name_card](game_id, player_id, card.quantity)
        session.close()
        return money_change

    def play_blue_cards(self, game_id, number):
        blue_cards, session = self.DB.get_blue_cards(game_id, number)
        money_changes = {}
        for card in blue_cards:
            if card.name_card == 'fishing launch':
                if not self.DB.is_card_in_city(game_id, card.player_id, 'port'):
                    continue
            income = card.income * card.quantity
            money_changes[card.player_id] = income
        session.close()
        self.DB.pull_money_changes(game_id, money_changes)
        return money_changes

    def money_player_to_player(self, game_id, player_id, number):
        red_result = self.play_red_cards(game_id, player_id, number)
        special_result = self.play_pink_cards(game_id, player_id, number)
        result_view = ''
        main_player_name = self.DB.get_name(game_id, player_id)
        for player, money in red_result.items():
            player_name = self.DB.get_name(game_id, player)
            result_view += f'\n    -  {main_player_name}  :dollar_banknote:  {money}   :right_arrow:   {player_name} '
        result_view += special_result

        return result_view

    def money_bank_to_player(self, game_id, player_id, number):
        income_players = self.play_blue_cards(game_id, number)
        income_main_player = self.play_green_cards(game_id, player_id, number)
        if income_main_player != 0:
            if player_id not in income_players:
                income_players[player_id] = income_main_player
            else:
                income_players[player_id] += income_main_player
        str_income = ''
        for player_id, income in income_players.items():
            player_name = self.DB.get_name(game_id, player_id)
            str_income += f'\n    -  {player_name}   + {income}  :dollar_banknote:'
        return str_income

    def all_cards_play(self, game_id, player_id, number):
        result = self.money_player_to_player(game_id, player_id, number)
        result += self.money_bank_to_player(game_id, player_id, number)
        if result != '':
            self.DB.put_new_story(result, game_id)
            return True
        return False

    def bakery(self, game_id, player_id, quantity):
        income = 1
        if self.DB.is_shopping_mall(game_id, player_id):
            income += 1
        income *= quantity
        money_changes = {player_id: income}
        self.DB.pull_money_changes(game_id, money_changes)
        return income

    def store(self, game_id, player_id, quantity):
        income = 3
        if self.DB.is_shopping_mall(game_id, player_id):
            income += 1
        income *= quantity
        money_changes = {player_id: income}
        self.DB.pull_money_changes(game_id, money_changes)
        return income

    def flower_shop(self, game_id, player_id, quantity):
        count_flower = self.DB.count_card_name(game_id, player_id, 'flower garden')
        income = 1
        if self.DB.is_shopping_mall(game_id, player_id):
            income += 1
        income *= quantity * count_flower
        money_changes = {player_id: income}
        self.DB.pull_money_changes(game_id, money_changes)
        return income

    def cheese_factory(self, game_id, player_id, quantity):
        count_farms = self.DB.count_card_sign(game_id, player_id, 'milk')
        income = 3 * count_farms
        income *= quantity
        money_changes = {player_id: income}
        self.DB.pull_money_changes(game_id, money_changes)
        return income

    def furniture_factory(self, game_id, player_id, quantity):
        count_mechanic = self.DB.count_card_sign(game_id, player_id, 'mechanical')
        income = 3 * count_mechanic
        income *= quantity
        money_changes = {player_id: income}
        self.DB.pull_money_changes(game_id, money_changes)
        return income

    def produce_market(self, game_id, player_id, quantity):
        count_fruit = self.DB.count_card_sign(game_id, player_id, 'fruit')
        income = 2 * count_fruit
        income *= quantity
        money_changes = {player_id: income}
        self.DB.pull_money_changes(game_id, money_changes)
        return income

    def food_storage(self, game_id, player_id, quantity):
        count_cook = self.DB.count_card_sign(game_id, player_id, 'cook')
        income = 2 * count_cook
        income *= quantity
        money_changes = {player_id: income}
        self.DB.pull_money_changes(game_id, money_changes)
        return income

    def play_stadium(self, game_id, player_id):
        cities, session = self.DB.get_all_cities(game_id)
        money_changes = {player_id: 0}
        for city in cities:
            if city.player_id == player_id:
                continue
            if city.money >= 2:
                change = 2
            elif city.money == 1:
                change = 1
            else:
                continue
            money_changes[city.player_id] = - change
            money_changes[player_id] += change
        session.close()
        if money_changes[player_id] == 0:
            return ''
        self.DB.pull_money_changes(game_id, money_changes)
        del money_changes[player_id]
        result_view = ''
        main_player_name = self.DB.get_name(game_id, player_id)
        for player, money in money_changes.items():
            player_name = self.DB.get_name(game_id, player)
            result_view += f'\n    -  {main_player_name}   :left_arrow:  {-money}' \
                           f'  :dollar_banknote:   {player_name}'
        return result_view

    def play_tv_station(self, game_id, player_id, victim_id):
        victim_money = self.DB.money(game_id, victim_id)
        if victim_money >= 5:
            steal_money = 5
        else:
            steal_money = victim_money
        money_changes = {player_id: steal_money, victim_id: -steal_money}
        self.DB.pull_money_changes(game_id, money_changes)
        main_player_name = self.DB.get_name(game_id, player_id)
        victim_name = self.DB.get_name(game_id, victim_id)
        result_view = f'\n    -  {main_player_name}   :left_arrow:  {steal_money}' \
                      f'  :dollar_banknote:   {victim_name}'
        self.DB.put_new_story(result_view, game_id)

    def play_trawler(self, game_id):
        number_1 = random.randint(1, 6)
        number_2 = random.randint(1, 6)
        number = number_1 + number_2
        money_changes = {}
        trawlers_cards, session = self.DB.get_trawlers_cards(game_id)
        new_story = f'\n      :passenger_ship:  :game_die::game_die: {number_1}  {number_2}'
        for card in trawlers_cards:
            player_name = self.DB.get_name(game_id, card.player_id)
            income = card.quantity * number
            money_changes[card.player_id] = income
            new_story += f'\n    -  {player_name}   + {income}  :dollar_banknote:'
        self.DB.pull_money_changes(game_id, money_changes)
        self.DB.put_new_story(new_story, game_id)

    def tax_office(self, game_id, player_id):
        cities, session = self.DB.get_all_cities(game_id)
        money_changes = {player_id: 0}
        for city in cities:
            if (city.player_id == player_id) or (city.money < 10):
                continue
            money_changes[city.player_id] = - int(city.money / 2)
            money_changes[player_id] += int(city.money / 2)
        session.close()
        if money_changes[player_id] == 0:
            return ''
        self.DB.pull_money_changes(game_id, money_changes)
        del money_changes[player_id]
        result_view = ''
        main_player_name = self.DB.get_name(game_id, player_id)
        for player, money in money_changes.items():
            player_name = self.DB.get_name(game_id, player)
            result_view += f'\n    -  {main_player_name}   :left_arrow:  {-money}' \
                           f'  :dollar_banknote:   {player_name}'
        return result_view

    def publisher(self, game_id, player_id):
        all_cards, cities, session = self.DB.get_all_card_from_people_and_cities(game_id)
        money_changes = {player_id: 0}
        cities_money = {}
        for city in cities:
            cities_money[city.player_id] = city.money
        for card in all_cards:
            if (card.player_id != player_id) and (card.sign in ['cook', 'shop']) and (
                    card.original and (cities_money[card.player_id] > 0)):
                if card.player_id in money_changes:
                    money_change = money_changes[card.player_id] - card.quantity
                    if (cities_money[card.player_id] + money_change) < 0:
                        money_changes[card.player_id] = -cities_money[card.player_id]
                    else:
                        money_changes[card.player_id] -= card.quantity
                else:
                    if (cities_money[card.player_id] - card.quantity) < 0:
                        money_changes[card.player_id] = -cities_money[card.player_id]
                    else:
                        money_changes[card.player_id] = -card.quantity
        session.close()
        for player, money in money_changes.items():
            if player == player_id:
                continue
            money_changes[player_id] -= money
        if money_changes[player_id] == 0:
            return ''
        self.DB.pull_money_changes(game_id, money_changes)
        del money_changes[player_id]
        result_view = ''
        main_player_name = self.DB.get_name(game_id, player_id)
        for player, money in money_changes.items():
            player_name = self.DB.get_name(game_id, player)
            result_view += f'\n    -  {main_player_name}   :left_arrow:  {-money}' \
                           f'  :dollar_banknote:   {player_name}'
        return result_view


if __name__ == '__main__':
    DB = ActionDB()
    game = CardPlay(DB)
    # game.play_blue_cards(16, 1)
    # res = game.play_green_cards(16, 297126784, 2)
    # a = 16, 297126784, 2
    # b =
