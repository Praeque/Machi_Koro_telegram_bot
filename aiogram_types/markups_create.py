from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data import ActionDB


class MarkupMaker:

    def __init__(self, db: ActionDB, human_unicode, bot_unicode):

        self.DB = db

        self.human_unicode = human_unicode
        self.bot_unicode = bot_unicode
        self.emoji = {'bread': '\U0001F35E', 'cow_face': '\U0001F42E', 'airplane': '\U00002708',
                      'sheaf_of_rice': '\U0001F33E', 'hot_beverage': '\U00002615', 'blue': '\U000026CF',
                      'green': '\U0001F3ED', 'red': '\U0001F37D	', 'pink': '\U0001F3E2', 'attraction': '\U000026E9',
                      'convenience_store': '\U0001F3EA', 'evergreen_tree': '\U0001F332', 'station': '\U0001F689',
                      'kaaba': '\U0001F54B', 'ferris_wheel': '\U0001F3A1', 'Tokyo_tower': '\U0001F5FC',
                      'mountain': '\U000026F0', 'red_apple': '\U0001F34E', 'cheese_wedge': '\U0001F9C0',
                      'chair': '\U0001FA91', 'carrot': '\U0001F955', 'steaming_bowl': '\U0001F35C',
                      'stadium': '\U0001F3DF', 'television': '\U0001F4FA', 'office_building': '\U0001F3E2',
                      'briefcase': '\U0001F4BC', 'gear': '\U00002699', 'herb': '\U0001F33F', 'anchor': '\U00002693',
                      'tulip': '\U0001F337', 'canned_food': '\U0001F96B', 'pizza': '\U0001F355',
                      'hot_dog': '\U0001F32D', 'sushi': '\U0001F363', 'sailboat': '\U000026F5',
                      'passenger_ship': '\U0001F6F3', 'heavy_dollar_sign': '\U0001F4B2', 'printer': '\U0001F5A8',
                      'satellite_antenna': '\U0001F4E1', 'bouquet': '\U0001F490', 'package': '\U0001F4E6'

         }

    @staticmethod
    def start_lobby():
        markup = InlineKeyboardMarkup(row_width=1)
        join_button = InlineKeyboardButton('Присоединиться к игре \U00002B05', callback_data=f'get_place_lobby')
        markup.add(InlineKeyboardButton('Наблюдать 👀', callback_data=f'audience'))
        start_game_button = InlineKeyboardButton('Минимум 2 игрока для старта \U0001F6AB', callback_data=' ')
        markup.add(join_button, start_game_button)
        return markup

    def lobby_with_people(self, game_id):
        all_players = self.DB.select_all_players(game_id)
        markup = InlineKeyboardMarkup(row_width=1)
        buttons = []
        for player in all_players:
            smile_view = self.human_unicode
            if player.bot:
                smile_view = self.bot_unicode
            view = f'{smile_view}  {player.player_name}'
            buttons.append(InlineKeyboardButton(view, callback_data=f'place,{player.player_id}'))
        all_audiences = self.DB.select_all_audiences(game_id)
        for user in all_audiences:
            buttons.append(InlineKeyboardButton(f'{user.user_name}   👁', callback_data=f'audiencer,{user.user_id}'))
        markup.add(*buttons)
        count_player = self.DB.get_count_player(game_id)
        if count_player < 5:
            markup.add(InlineKeyboardButton('Присоединиться к игре \U00002B05', callback_data='get_place_lobby'))
            markup.add(InlineKeyboardButton(f'Добавить ИИ \U00002795 {self.bot_unicode}', callback_data=f'add_bot'))
        if len(all_audiences) < 3:
            markup.add(InlineKeyboardButton('Наблюдать 👀', callback_data=f'audience'))
        if len(all_players) > 1:
            markup.add(InlineKeyboardButton('Начать игру (Классика) 🏁', callback_data=f'start_game,basic'))
            markup.add(InlineKeyboardButton('Начать игру (Дополнение) 🏁', callback_data=f'start_game,additions'))
        else:
            markup.add(InlineKeyboardButton('Нужно минимум 2 игрока \U0001F6AB', callback_data=' '))
            markup.add(InlineKeyboardButton('Нужно минимум 2 игрока \U0001F6AB', callback_data=' '))
        return markup

    def create_roll_markup(self, game_id):
        markup = InlineKeyboardMarkup(row_width=2)
        one_button = InlineKeyboardButton('Бросить кубик  🎲', callback_data=f'roll,1,0,{game_id}')
        if self.DB.is_train_station(game_id):
            two_button = InlineKeyboardButton('Бросить два  🎲 🎲', callback_data=f'roll,2,0,{game_id}')
        else:
            two_button = InlineKeyboardButton('\U0001F512', callback_data=' ')
        markup.add(one_button, two_button)
        return markup

    def create_reroll_or_continue_markup(self, game_id, numbers):
        markup = InlineKeyboardMarkup(row_width=2)
        one_button = InlineKeyboardButton('   🔄    🎲', callback_data=f'roll,1,1,{game_id}')
        if self.DB.is_train_station(game_id):
            two_button = InlineKeyboardButton('   🔄    🎲 🎲', callback_data=f'roll,2,1,{game_id}')
        else:
            two_button = InlineKeyboardButton('\U0001F512', callback_data=' ')
            # U0001F512
        numbers_str = '   '.join([str(number) for number in numbers])
        number_data = '.'.join([str(number) for number in numbers])
        count = len(numbers)
        view = f'Продолжить {"🎲 " * count}  {numbers_str}'
        data = f'continue_numbers,{number_data},{game_id}'
        continue_button = InlineKeyboardButton(view, callback_data=data)
        markup.add(one_button, two_button, continue_button)
        return markup

    @staticmethod
    def create_port_markup(game_id, number):
        markup = InlineKeyboardMarkup(row_width=1)
        button_1 = InlineKeyboardButton(f'  {number}  🎲🎲', callback_data=f'port,{number},0,{game_id}')
        button_2 = InlineKeyboardButton(f'  {number}  🎲🎲  +  2 ⚓️', callback_data=f'port,{number},1,{game_id}')
        markup.add(button_1, button_2)
        return markup

    def create_card_buttons(self, type_of_cards: list, color: str, game_id, player_id):
        number = 1
        if color == 'attraction':
            number = 0
        buttons = [
            InlineKeyboardButton(f'{self.emoji[color]} \U00002754', callback_data=f'type_card_info,{color},{game_id}')]
        is_empty_button = False
        empty_button = InlineKeyboardButton(' ', callback_data=f'pass_turn,{game_id}')
        for card in type_of_cards:
            if (color == 'attraction' or color == 'pink') and self.DB.is_card_in_city(game_id, player_id, card.name):
                continue
            if len(buttons) % 5 == 0:
                buttons.append(empty_button)
            callback_data = f'card_info,{card.name},{game_id}'
            view = f'{str(card.number_str) * number}{self.emoji[card.emoji_view]}'
            buttons.append(InlineKeyboardButton(view, callback_data=callback_data))
        empty_buttons = [empty_button for i in range(len(buttons) % 5, 5) if len(buttons) % 5 != 0]
        if empty_button:
            is_empty_button = True
        buttons.extend(empty_buttons)
        return buttons, is_empty_button

    @staticmethod
    def pass_turn(game_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('❗️ Пропустить ход и ничего не строить ❗️',
                                        callback_data=f'complete_pass_turn,{game_id}'))
        return markup

    def create_build_markup(self, game_id, player_id):
        sorted_cards, session = self.DB.get_table_card(game_id)
        markup = InlineKeyboardMarkup(row_width=5)
        is_pass_button = []
        for color, type_card in sorted_cards.items():
            if type_card:
                type_card.sort(key=lambda obj: obj.number)
                buttons, is_empty = self.create_card_buttons(type_card, color, game_id, player_id)
                markup.add(*buttons)
                is_pass_button.append(is_empty)
        for empty in is_pass_button:
            if empty:
                break
        else:
            markup.add(InlineKeyboardButton(' ', callback_data=f'pass_turn,{game_id}'))
        session.close()
        return markup

    def create_card_info_markup(self, card_name, game_id, player_id):
        markup = InlineKeyboardMarkup()
        money_player = self.DB.money(game_id, player_id)
        cost_card = self.DB.get_cost_card(card_name)
        if money_player >= cost_card:
            callback_data = f'build,{card_name},{cost_card},{game_id}'
            button = InlineKeyboardButton(f'Построить \U0001F528  (ход будет завершен)', callback_data=callback_data)
        else:
            button = InlineKeyboardButton(f'Нехватает денег на постройку \U0001F6D1', callback_data=' ')
        markup.add(button)
        return markup

    def create_tv_station_markup(self, game_id, player_id):
        cities, session = self.DB.get_all_cities(game_id)
        buttons = []
        for city in cities:
            if city.player_id == player_id or city.money == 0:
                continue
            victim_id = city.player_id
            if city.bot:
                emoji_view = self.bot_unicode
            else:
                emoji_view = self.human_unicode
            view = f'{emoji_view}  {city.player_name}  💰 {city.money}'
            callback_data = f'tv_station,{victim_id},{game_id}'
            buttons.append(InlineKeyboardButton(view, callback_data=callback_data))
        session.close()
        if buttons:
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(*buttons)
            return markup

    @staticmethod
    def create_trawler_markup(game_id):
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton('  🎲 🎲  🛳', callback_data=f'trawler,{game_id}'))
        return markup

    def create_markup_office_self(self, game_id, player_id):
        cards, session = self.DB.get_player_cards(game_id, player_id)
        cards_list = [card for card in cards]
        cards_list.sort(key=lambda obj: (obj.number, obj.number_str))
        markup = InlineKeyboardMarkup(row_width=4)
        buttons = []
        for card in cards_list:
            if card.sign == 'special' or not card.original:
                continue
            emoji_view = self.emoji[card.emoji_view]
            view = f'{card.number_str}{emoji_view}'
            name_gift_card = card.name_card
            data = f'office_self,{name_gift_card},{game_id}'
            buttons.append(InlineKeyboardButton(view, callback_data=data))
        session.close()
        empty_button = InlineKeyboardButton(' ', callback_data=' ')
        empty_buttons = [empty_button for i in range(4 - (len(buttons) % 4)) if len(buttons) % 4 != 0]
        markup.add(*buttons, *empty_buttons)
        return markup

    def create_buttons_office_other(self, game_id, name_gift_card, victim_player, cards):
        cards.sort(key=lambda obj: (obj.number, obj.number_str))
        buttons = []
        for card in cards:
            if card.sign == 'special' or not card.original:
                continue
            emoji_view = self.emoji[card.emoji_view]
            view = f'{card.number_str}{emoji_view}'
            name_taken_card = card.name_card
            data = f'office_other,{name_gift_card},{name_taken_card},{victim_player},{game_id}'
            buttons.append(InlineKeyboardButton(view, callback_data=data))
        empty_button = InlineKeyboardButton(' ', callback_data=' ')
        empty_buttons = [empty_button for i in range(4 - (len(buttons) % 4)) if len(buttons) % 4 != 0]
        buttons.extend(empty_buttons)
        return buttons

    def create_markup_office_other(self, name_gift_card, game_id, player_id):
        markup = InlineKeyboardMarkup(row_width=4)
        cards, session = self.DB.get_players_cards(game_id)
        sorted_cards = {}
        for card in cards:
            if card.player_id == player_id or card.sign == 'special' or not card.original:
                continue
            if card.player_id not in sorted_cards:
                sorted_cards[card.player_id] = [card]
            else:
                sorted_cards[card.player_id].append(card)
        for victim_player, cards in sorted_cards.items():
            name_victim = self.DB.get_name(game_id, victim_player)
            victim_money = self.DB.money(game_id, victim_player)
            if self.DB.is_bot(game_id, victim_player):
                emoji_view = self.bot_unicode
            else:
                emoji_view = self.human_unicode
            markup.add(InlineKeyboardButton(f'{emoji_view}  {name_victim}  \U0001F4B0 {victim_money}', callback_data=' '))
            buttons = MarkupMaker.create_buttons_office_other(game_id, name_gift_card, victim_player, cards)
            markup.add(*buttons)
        session.close()
        return markup


class Permission:
    permissions_block = types.ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_change_info=False,
        can_invite_users=True,
        can_pin_messages=False
    )


if __name__ == '__main__':

    ...
