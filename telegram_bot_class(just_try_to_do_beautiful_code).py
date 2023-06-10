from data import ActionDB
from aiogram_types import MarkupMaker, MessageSender
from game_play import CardPlay, BotPlay

import random
from asyncio import sleep
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, executor
import os
from emoji import emojize


class MachiKoroBot:

    human_unicode = '\U0001F64E\U0000200D\U00002642\U0000FE0F'
    human_cldr = ':man_pouting:'
    bot_unicode = '\U0001F916'
    bot_cldr = ':robot:'
    quick_sleep = 0.4

    def __init__(self, bot_token, class_DB: type[ActionDB], class_CardPlay: type[CardPlay],
                 class_Messages: type[MessageSender], class_BotsPlay: type[BotPlay], class_Markups: type[MarkupMaker]):

        self.bot = Bot(bot_token)
        self.dp = Dispatcher(self.bot)
        self.DB = class_DB(self.human_cldr, self.bot_cldr)
        self.roll_play = class_CardPlay(self.DB)
        self.sender = class_Messages(self.bot)
        self.bot_gameplay = class_BotsPlay(self.DB, self.bot, self.quick_sleep, self.sender, self.bot_cldr)
        self.markups = class_Markups(self.DB, self.human_unicode, self.bot_unicode)
        self.registration_callback()
        self.registration_commands()
        # self.set_commands()

    def registration_callback(self):
        registration = self.dp.register_callback_query_handler
        registration(self.callback_join_player, lambda call: call.data == 'get_place_lobby')
        registration(self.callback_join_audience, lambda call: call.data == 'audience')
        registration(self.callback_kick_player, lambda call: call.data.split(',')[0] == 'place')
        registration(self.callback_kick_audience, lambda call: call.data.split(',')[0] == 'audiencer')
        registration(self.callback_add_bot, lambda call: call.data == 'add_bot')
        registration(self.callback_start_game, lambda call: call.data.split(',')[0] == 'start_game')
        registration(self.callback_roll, lambda call: call.data.split(',')[0] == 'roll')
        registration(self.callback_trawler, lambda call: call.data.split(',')[0] == 'trawler')
        registration(self.callback_tv_station, lambda call: call.data.split(',')[0] == 'tv_station')
        registration(self.callback_office_self, lambda call: call.data.split(',')[0] == 'office_self')
        registration(self.callback_office_other, lambda call: call.data.split(',')[0] == 'office_other')
        registration(self.callback_continue_numbers, lambda call: call.data.split(',')[0] == 'continue_numbers')
        registration(self.callback_port, lambda call: call.data.split(',')[0] == 'port')
        registration(self. callback_type_card_info, lambda call: call.data.split(',')[0] == 'type_card_info')
        registration(self.callback_card_info, lambda call: call.data.split(',')[0] == 'card_info')
        registration(self.callback_pass_turn, lambda call: call.data.split(',')[0] == 'pass_turn')
        registration(self.callback_complete_pass_turn, lambda call: call.data.split(',')[0] == 'complete_pass_turn')
        registration(self.callback_build, lambda callback_query: callback_query.data.split(',')[0] == 'build')

    def registration_commands(self):
        self.dp.register_message_handler(self.command_create_lobby, commands=['start_game'])
        self.dp.register_message_handler(self.command_end_session, commands=['end_session'])
        self.dp.register_message_handler(self.command_how_to_play, commands=['how_to_play'])
        self.dp.register_message_handler(self.command_rules, commands=['rules'])

    def start_polling(self):
        executor.start_polling(self.dp, skip_updates=True)

    # async def set_commands(self):
    #
    #     commands_private = [
    #         types.BotCommand(command='/rules', description='Правила игры'),
    #         types.BotCommand(command='/how_to_play', description='Как начать игру')
    #     ]
    #     commands_group = [
    #         types.BotCommand(command='/start_game', description='Создать лобби игры')
    #     ]
    #     await self.bot.set_my_commands(commands_private, scope=types.BotCommandScopeAllPrivateChats())
    #     await self.bot.set_my_commands(commands_group, scope=types.BotCommandScopeAllGroupChats())

    async def command_create_lobby(self, message: types.Message):
        group = message.chat.type == 'supergroup'
        administration = await self.check_admin_status(message.chat.id, message.from_user.id)
        if group:
            if administration:
                if not self.DB.is_session(message.chat.id):
                    text = 'Займите место, нажав "Присоединиться к игре"\nМогут играть от 2 до 5 игроков 👥'
                    markup = self.markups.start_lobby()
                    message_lobby = await message.answer(text, reply_markup=markup)
                    self.DB.create_session(message.chat.id, message_lobby.message_id)
                else:
                    text = '<b>⚠️ У вас не законченная сессия в этом чате ❗️</b>\n<u>Доиграйте</u>, либо' \
                           ' <u>закройте</u> ее принудително:\n<b>"/end_session"</b>'
                    await message.answer(text, parse_mode='html')
            else:
                text = '⚠️ <b>Только администратор чата может создавать игру</b>❗ ️'
                await message.answer(text, parse_mode='html')
        else:
            text = '⚠️ <b>Только в группах можно создавать игры</b>❗ ️'
            await message.answer(text, parse_mode='html')

    async def command_how_to_play(self, message: types.Message):
        if message.chat.type == 'private':
            rules = emojize(self.DB.get_description('how_to_play'))
            await message.answer(rules, parse_mode='html')

    async def command_rules(self, message: types.Message):
        if message.chat.type == 'private':
            rules = emojize(self.DB.get_description('rules'))
            await message.answer(rules, parse_mode='html')

    async def command_end_session(self, message: types.Message):
        administration = await self.check_admin_status(message.chat.id, message.from_user.id)
        if administration:
            messages = self.DB.delete_chat_session(message.chat.id)
            if messages:
                for chat_id, messages_id in messages.items():
                    for message_id in messages_id:
                        await self.sender.delete_message(chat_id, message_id)
                        await sleep(0.5)
                await message.answer('Сессия успешно удалена, можете начинать новую!')
        else:
            text = '⚠️ <b>Только администратор чата может принудительно закончить сессию </b>❗ ️'
            await message.answer(text, parse_mode='html')

    async def callback_join_player(self, call: types.CallbackQuery):
        player_id = call.from_user.id
        player_name = call.from_user.first_name
        game_id = call.message.chat.id

        is_player_in_lobby = self.DB.is_player_in_lobby(game_id, player_id)
        is_player_in_lobby += self.DB.is_audience_in_lobby(game_id, player_id)
        if not is_player_in_lobby:

            count_player = self.DB.get_count_player(call.message.chat.id)
            if count_player < 5:
                self.DB.create_new_city(game_id, player_id, player_name)

                markup = self.markups.lobby_with_people(game_id)
                await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                                         reply_markup=markup)

    async def callback_join_audience(self, call: types.CallbackQuery):
        user_id = call.from_user.id
        user_name = call.from_user.first_name
        game_id = call.message.chat.id

        is_player_in_lobby = self.DB.is_player_in_lobby(game_id, user_id)
        is_player_in_lobby += self.DB.is_audience_in_lobby(game_id, user_id)
        if not is_player_in_lobby:
            if self.DB.create_new_audience(game_id, user_id, user_name):
                markup = self.markups.lobby_with_people(game_id)
                await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                                         reply_markup=markup)

    async def callback_kick_player(self, call: types.CallbackQuery):
        administration = await self.check_admin_status(call.message.chat.id, call.from_user.id)
        if administration:
            game_id = call.message.chat.id
            player_id = int(call.data.split(',')[1])  # 'place,{player.player_id}'
            self.DB.kick_player_lobby(game_id, player_id)

            markup = self.markups.lobby_with_people(game_id)
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)

    async def callback_kick_audience(self, call: types.CallbackQuery):
        administration = await self.check_admin_status(call.message.chat.id, call.from_user.id)
        if administration:
            game_id = call.message.chat.id
            user_id = int(call.data.split(',')[1])  # 'place,{player.player_id}'
            self.DB.kick_audience_lobby(game_id, user_id)

            markup = self.markups.lobby_with_people(game_id)
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)

    async def callback_add_bot(self, call: types.CallbackQuery):
        administration = await self.check_admin_status(call.message.chat.id, call.from_user.id)
        if administration:
            game_id = call.message.chat.id

            count_player = self.DB.get_count_player(call.message.chat.id)
            if count_player < 5:
                self.DB.create_bot_city(game_id)

                markup = self.markups.lobby_with_people(game_id)
                await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                                         reply_markup=markup)

    async def callback_start_game(self, call: types.CallbackQuery):
        administration = await self.check_admin_status(call.message.chat.id, call.from_user.id)
        if administration:
            game_id = call.message.chat.id
            if self.DB.check_and_lock(game_id):
                type_game = call.data.split(',')[1]

                self.DB.start_game(game_id, type_game)
                text = 'Интерфейс игры у каждого в личном чате, с ботом.\nПриятной вам игры.'
                await self.bot.edit_message_text(text, call.message.chat.id, call.message.message_id)
                await self.send_game_messages(game_id)
                self.DB.unlock_game(game_id)

    async def send_game_messages(self, game_id):
        messages = {}
        first_player_id, first_player_name, first_player_bot, all_players_id = self.DB.get_players_id_for_start(game_id)
        all_players_id.extend(self.DB.get_all_audiencers(game_id))
        cities_info = emojize(self.DB.get_cities_info(game_id))
        slime_view = self.human_unicode
        if first_player_bot:
            slime_view = self.bot_unicode
        for player_id in all_players_id:
            if player_id in [1, 2, 3, 4, 5]:
                continue
            history = await self.sender.send_message(player_id, '...')  # '1️⃣♻️'
            cities = await self.sender.send_message(player_id, cities_info)
            if player_id == first_player_id:
                markup = self.markups.create_roll_markup(game_id)
                view = ' <b>  Ваш ход   </b> 🎲 '  # f' <b>  Ваш ход   </b> 🎲 '
                action_1 = await self.sender.send_message(player_id, view, markup)
            else:
                view = f'Ходит {slime_view}<b>{first_player_name}</b>'  # f'Ходит  {slime_view}  <b>{first_player_name}</b>  👣'
                action_1 = await self.sender.send_message(player_id, view)
            action_2 = await self.sender.send_message(player_id, '...')
            messages[player_id] = {'history': history.message_id, 'cities': cities.message_id,
                                   'action_1': action_1.message_id, 'action_2': action_2.message_id}
        self.DB.save_id_messages(game_id, messages)
        if first_player_bot:
            await self.play_bot(game_id, first_player_id, first_player_name)

    async def callback_roll(self, call: types.CallbackQuery):
        # parse_data
        # 'roll,{number_of_dice},{reroll},{game_id}'
        number_of_dice, reroll, game_id = [int(variable) for variable in call.data.split(',')[1:]]

        player_id = call.from_user.id
        self.DB.lock_game(game_id)

        number, numbers = await self.roll_dice(call.from_user.first_name, game_id, reroll, number_of_dice)

        is_radio_tower = self.DB.is_radio_tower(game_id, player_id)
        if is_radio_tower and not reroll:
            await self.make_rerollin_view(call, game_id, numbers)
        else:
            await self.refresh_history(game_id)
            await sleep(1)
            await self.duple_check(game_id, numbers, player_id)
            is_port = self.DB.is_card_in_city(game_id, player_id, 'port')
            if is_port and number > 9:
                await self.make_port_view(call, game_id, number)
            else:
                await self.play_number(call, player_id, game_id, number)
        self.DB.unlock_game(game_id)

    async def duple_check(self, game_id, numbers, player_id):
        if len(numbers) == 2:
            if numbers[0] == numbers[1]:
                self.DB.duple_rolled(game_id, player_id)

    async def roll_dice(self, name, game_id, reroll, number_of_dice):
        numbers = [random.randint(1, 6) for i in range(number_of_dice)]
        number = sum(numbers)
        await self.save_rolling(name, game_id, numbers, reroll, number_of_dice)
        return number, numbers

    async def save_rolling(self, name, game_id, numbers, reroll, number_of_dice):
        numbers_str = '  '.join([str(number) for number in numbers])
        if reroll:
            turn_story = f'\n      :counterclockwise_arrows_button:   {":game_die:" * number_of_dice}' \
                         f'   {numbers_str}'
        else:
            turn_story = f'\n{self.human_cldr} {name}   {":game_die:" * number_of_dice}   {numbers_str}'
        self.DB.put_new_story(turn_story, game_id)

    async def make_rerollin_view(self, call, game_id, numbers):
        await sleep(self.quick_sleep)
        await self.refresh_history(game_id)
        markup = self.markups.create_reroll_or_continue_markup(game_id, numbers)
        await self.sender.edit_markup(call, markup=markup)

    async def make_port_view(self, call, game_id, number):
        await sleep(self.quick_sleep)
        await self.refresh_history(game_id)
        markup = self.markups.create_port_markup(game_id, number)
        await self.sender.edit_markup(call, markup=markup)

    async def play_number(self, call, player_id, game_id, number, continue_number=False, port=False):
        is_change_money = self.roll_play.all_cards_play(game_id, player_id, number)
        is_change_money += self.DB.town_hall(game_id, player_id)
        if is_change_money or not continue_number or port:
            await self.refresh_history(game_id)
        if is_change_money:
            await self.refresh_cities_property(game_id)
        if number == 6:
            if self.DB.is_tv_station(game_id, player_id) and self.DB.is_money_other_player(game_id, player_id):
                return await self.play_tv_station(call, game_id, player_id)
            if self.DB.is_office(game_id, player_id):
                return await self.play_office(call, game_id, player_id)
        elif number > 11 and self.DB.is_trawler(game_id):
            return await self.play_trawler(call, game_id)
        await self.create_build_view(call, game_id, player_id)

    async def refresh_history(self, game_id):
        await sleep(self.quick_sleep)
        history = emojize(self.DB.get_history(game_id))
        messages_id = self.DB.get_messages_history(game_id)
        for player_id, mess_id in messages_id.items():
            await self.sender.edit_message(history, player_id, mess_id)

    async def refresh_cities_property(self, game_id):
        await sleep(self.quick_sleep)
        cities_info = emojize(self.DB.get_cities_info(game_id))
        messages_id = self.DB.get_messages_cities(game_id)
        for player_id, mess_id in messages_id.items():
            await self.sender.edit_message(cities_info, player_id, mess_id)

    async def create_build_view(self, call, game_id, player_id):
        await sleep(self.quick_sleep)
        markup = self.markups.create_build_markup(game_id, player_id)
        text = f'    Выберете, что хотите построить в своем городе   🏗 '
        await self.sender.edit_message_this_chat(text, call, markup=markup)

    async def play_tv_station(self, call, game_id, player_id):
        await sleep(self.quick_sleep)
        markup = self.markups.create_tv_station_markup(game_id, player_id)
        text = f'<b>{call.from_user.first_name}</b>  Выбирает у кого забрать деньги...'
        await self.sender.edit_message_this_chat(text, call, markup=markup)

    async def play_trawler(self, call, game_id):
        await sleep(self.quick_sleep)
        markup = self.markups.create_trawler_markup(game_id)
        text = 'Киньте кубики еще раз, для срабатывания Траулера 🛳'
        await self.sender.edit_message_this_chat(text, call, markup=markup)

    async def callback_trawler(self, call: types.CallbackQuery):
        game_id = int(call.data.split(',')[1])
        player_id = call.from_user.id
        self.DB.lock_game(game_id)
        self.roll_play.play_trawler(game_id)
        await self.refresh_history(game_id)
        await self.refresh_cities_property(game_id)
        await self.create_build_view(call, game_id, player_id)
        self.DB.unlock_game(game_id)

    async def callback_tv_station(self, call: types.CallbackQuery):
        # f'tv_station,{victim_id},{game_id}'
        game_id = int(call.data.split(',')[2])
        player_id = call.from_user.id
        victim_id = int(call.data.split(',')[1])
        self.DB.lock_game(game_id)
        self.roll_play.play_tv_station(game_id, player_id, victim_id)
        await self.refresh_history(game_id)
        await self.refresh_cities_property(game_id)
        if self.DB.is_office(game_id, player_id):
            await self.play_office(call, game_id, player_id)
        else:
            await self.create_build_view(call, game_id, player_id)
        self.DB.unlock_game(game_id)

    async def play_office(self, call, game_id, player_id):
        await sleep(self.quick_sleep)
        markup = self.markups.create_markup_office_self(game_id, player_id)
        text = f'<b>{call.from_user.first_name} \U000026A0  ' \
               f'Выберите какое предприятие вы хотите <u>отдать</u> \U000027A1</b>'
        await self.sender.edit_message_this_chat(text, call, markup=markup)

    async def callback_office_self(self, call: types.CallbackQuery):
        # 'office_self,{name_gift_card},{game_id}'
        game_id = int(call.data.split(',')[2])
        player_id = call.from_user.id
        name_gift_card = call.data.split(',')[1]
        markup = self.markups.create_markup_office_other(name_gift_card, game_id, player_id)
        text = f'<b>{call.from_user.first_name}  Выберите какое предприятие вы хотите <u>забрать</u> \U0001F90C</b>'
        await sleep(self.quick_sleep)
        await self.sender.edit_message_this_chat(text, call, markup=markup)
        self.DB.unlock_game(game_id)

    async def callback_office_other(self, call: types.CallbackQuery):
        #  'office_other,{name_gift_card},{name_taken_card},{victim_player},{game_id}'
        name_gift_card, name_taken_card, victim_player, game_id = call.data.split(',')[1:]
        game_id, victim_player = int(game_id), int(victim_player)
        player_id = call.from_user.id
        self.DB.lock_game(game_id)
        self.DB.swap_cards(name_gift_card, name_taken_card, player_id, victim_player, game_id)
        await self.refresh_history(game_id)
        await self.refresh_cities_property(game_id)
        await self.create_build_view(call, game_id, player_id)
        self.DB.unlock_game(game_id)

    async def callback_continue_numbers(self, call: types.CallbackQuery):
        # 'continue_numbers,{number_data},{game_id}'
        game_id = int(call.data.split(',')[2])
        player_id = call.from_user.id
        self.DB.lock_game(game_id)
        number_data_str = call.data.split(',')[1]
        numbers = [int(number) for number in number_data_str.split('.')]
        number = sum(numbers)
        await self.duple_check(game_id, numbers, player_id)
        is_port = self.DB.is_card_in_city(game_id, player_id, 'port')
        if is_port and number > 9:
            await self.make_port_view(call, game_id, number)
        else:
            await self.play_number(call, player_id, game_id, number, continue_number=True)
        self.DB.unlock_game(game_id)

    async def callback_port(self, call: types.CallbackQuery):
        # 'port,{number},{is_used_port},{game_id}'
        number, is_used_port, game_id = [int(var) for var in call.data.split(',')[1:]]
        player_id = call.from_user.id
        self.DB.lock_game(game_id)
        if is_used_port:
            new_number = number + 2
            new_story = f'\n      :anchor: :game_die::game_die:  {number} :right_arrow: {new_number}'
            self.DB.put_new_story(new_story, game_id)
            await self.play_number(call, player_id, game_id, new_number, port=is_used_port)
        else:
            await self.play_number(call, player_id, game_id, number)
        self.DB.unlock_game(game_id)

    async def callback_type_card_info(self, call: types.CallbackQuery):
        # 'type_card_info,{color},{game_id}'
        # game_id = int(call.data.split(',')[2])
        # player_id = call.from_user.id
        card_type = call.data.split(',')[1]
        description = emojize(self.DB.get_description(card_type))
        await self.sender.edit_message_try(description, call, 1)

    async def callback_card_info(self, call: types.CallbackQuery):
        # 'card_info,{card.name},{game_id}'
        game_id = int(call.data.split(',')[2])
        player_id = call.from_user.id
        card_name = call.data.split(',')[1]
        markup = self.markups.create_card_info_markup(card_name, game_id, player_id)
        description = emojize(self.DB.get_card_description(card_name, game_id))
        await self.sender.edit_message_try(description, call, 1, markup=markup)

    async def callback_pass_turn(self, call: types.CallbackQuery):
        # 'pass_turn,{game_id}'
        game_id = int(call.data.split(',')[1])
        # player_id = call.from_user.id
        markup = self.markups.pass_turn(game_id)
        await self.sender.edit_message_try('<b>Дать рабочим выходной</b> \U000026A0', call, 1, markup)

    async def callback_complete_pass_turn(self, call: types.CallbackQuery):
        # 'complete_pass_turn,{game_id}'
        game_id = int(call.data.split(',')[1])
        player_id = call.from_user.id
        self.DB.lock_game(game_id)
        new_story = f'\n       :building_construction:      :prohibited:'
        is_airport = self.DB.is_card_in_city(game_id, player_id, 'airport')
        if is_airport:
            self.DB.pull_money_changes(game_id, {player_id: 10})
            new_story += f'\n    -  {call.from_user.first_name}   + 10  :dollar_banknote:'
        self.DB.put_new_story(new_story, game_id)
        await self.refresh_history(game_id)
        if is_airport:
            await self.refresh_cities_property(game_id)
        await self.make_next_turn(call, player_id, game_id, win=False)
        self.DB.unlock_game(game_id)

    async def callback_build(self, call: types.CallbackQuery):
        # f'build,{card_name},{cost_card},{game_id}'
        game_id = int(call.data.split(',')[3])
        player_id = call.from_user.id
        self.DB.lock_game(game_id)
        card_name, cost_card = call.data.split(',')[1], int(call.data.split(',')[2])
        win = self.DB.add_card_to_player(game_id, card_name, player_id)
        self.DB.pull_money_changes(game_id, {player_id: - cost_card})
        build_history = f'\n       :building_construction:      :{self.DB.get_card_emoji(card_name)}:'
        self.DB.put_new_story(build_history, game_id)
        await self.refresh_history(game_id)
        await self.refresh_cities_property(game_id)
        await self.make_next_turn(call, player_id, game_id, win=win)
        self.DB.unlock_game(game_id)

    async def make_next_turn(self, call: types.CallbackQuery, player_id, game_id, win):
        if win:
            await self.refresh_history(game_id)
            await self.refresh_cities_property(game_id)
            await self.finish_game(call, game_id)
        else:
            next_player_id, next_player_name, need_refresh = self.DB.get_number_next_player(game_id, player_id)
            if need_refresh:
                await self.refresh_history(game_id)
            if self.DB.is_bot(game_id, next_player_id):
                await self.sender.edit_message_this_chat('...', call)
                await self.play_bot(game_id, next_player_id, next_player_name)
            else:
                await self.edit_roll_messages_next_player(game_id, next_player_id, next_player_name)
                await self.sender.edit_message_this_chat('...', call)

    async def edit_roll_messages_next_player(self, game_id, next_player_id, next_player_name):
        markup = self.markups.create_roll_markup(game_id)
        messages_id = self.DB.get_messages_action_1(game_id)
        for player_id, mess_id in messages_id.items():
            if player_id == next_player_id:
                text = f' <b>  Ваш ход   </b> 🎲 '
                await self.sender.edit_message(text, player_id, mess_id, markup)
            else:
                text = f'Ходит  {self.human_unicode}  <b>{next_player_name}</b>  👣'
                await self.sender.edit_message(text, player_id, mess_id)

    async def play_bot(self, game_id, bot_id, bot_name):
        win = False
        try:
            await self.send_message_bot_play(game_id, bot_name)
            await sleep(1.5)
            number = await self.bot_gameplay.bot_roll(game_id, bot_id, bot_name)
            is_change_money = self.roll_play.all_cards_play(game_id, bot_id, number)
            is_change_money += self.DB.town_hall(game_id, bot_id)
            await self.refresh_history(game_id)
            if number > 11 and self.DB.is_trawler(game_id):
                self.roll_play.play_trawler(game_id)
            if is_change_money:
                await self.refresh_cities_property(game_id)
            await sleep(2.5)
            built, win = await self.bot_gameplay.bot_build(game_id, bot_id, bot_name)
            await self.refresh_history(game_id)
            if built:
                await self.refresh_cities_property(game_id)
        except Exception as error:
            print(error)
        await self.make_next_bot(bot_id, game_id, win, bot_name)

    async def send_message_bot_play(self, game_id, bot_name):
        messages_id = self.DB.get_messages_action_1(game_id)
        for player_id, mess_id in messages_id.items():
            text = f'Ходит  {self.bot_unicode}  <b>{bot_name}</b>  👣'
            await self.sender.edit_message(text, player_id, mess_id)

    async def make_next_bot(self, bot_id, game_id, win, bot_name):
        if win:
            await self.finish_game_bot(game_id, bot_id, bot_name)
        else:
            next_player_id, next_player_name, need_refresh = self.DB.get_number_next_player(game_id, bot_id)
            if need_refresh:
                await self.refresh_history(game_id)
            if self.DB.is_bot(game_id, next_player_id):
                await self.play_bot(game_id, next_player_id, next_player_name)
            else:
                await self.edit_roll_messages_next_player(game_id, next_player_id, next_player_name)

    async def finish_game_bot(self, game_id, bot_id, bot_name):
        messages_id = self.DB.get_actions_messages(game_id)
        for player_id, mess_id in messages_id['action_1'].items():
            text = f'{self.bot_unicode} {bot_name} вытащил город со дна, и теперь даже Зеленский приезжает, чтоб ' \
                   f'посмотреть на его достопримечательности.\n{self.bot_unicode} {bot_name} побеждает! 🦾'
            await self.sender.edit_message(text, player_id, mess_id)
        for player_id, mess_id in messages_id['action_2'].items():
            await self.sender.edit_message('🏁', player_id, mess_id)
        moves, laps, chat_message_id = self.DB.get_game_last_info(game_id)
        view = f'🏁 Победил  {self.bot_unicode}  <b>{bot_name}</b>  🦾!' \
               f'\n {moves} / {laps} (ходов / кругов - было сделано)'
        await self.sender.edit_message(view, game_id, chat_message_id)
        self.DB.delete_chat_session(game_id)

    async def finish_game(self, call, game_id):
        messages_id = self.DB.get_actions_messages(game_id)
        for player_id, mess_id in messages_id['action_1'].items():
            if player_id == call.from_user.id:
                text = f'Вы вытащил город со дна, и теперь даже Зеленский приезжает,' \
                       f' чтоб посмотреть на его достопримечательности.\n' \
                       f'🥇 Вы побеждаете! 🏆'
            else:
                text = f'{self.human_unicode} {call.from_user.first_name} вытащил город со дна, и теперь даже ' \
                       f'Зеленский приезжает, чтоб посмотреть на его достопримечательности.\n' \
                       f'🥇{self.human_unicode} {call.from_user.first_name} побеждает! 🏆'
            await self.sender.edit_message(text, player_id, mess_id)
        for player_id, mess_id in messages_id['action_2'].items():
            if player_id == call.from_user.id:
                await self.sender.edit_message('🎉', player_id, mess_id)
            else:
                await self.sender.edit_message('🏁', player_id, mess_id)
        moves, laps, chat_message_id = self.DB.get_game_last_info(game_id)
        name_winner = self.DB.get_name(game_id, player_id)
        text = f'🏁 Победил  {self.human_unicode}  <b>{name_winner}</b>  💪!' \
               f'\n {moves} / {laps} (ходов / кругов - было сделано)'
        await self.sender.edit_message(text, game_id, chat_message_id)

        self.DB.delete_chat_session(game_id)

    async def check_admin_status(self, chat_id, user_id):
        # Получение информации о пользователе в чате
        chat_member = await self.bot.get_chat_member(chat_id, user_id)
        print(chat_member.status)
        # Проверка статуса пользователя (является ли администратором)
        if chat_member.status in [types.ChatMemberStatus.CREATOR, types.ChatMemberStatus.ADMINISTRATOR]:
            return True
        else:
            return False


if __name__ == '__main__':

    load_dotenv()
    BOT = MachiKoroBot(
        bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
        class_DB=ActionDB,
        class_CardPlay=CardPlay,
        class_Messages=MessageSender,
        class_BotsPlay=BotPlay,
        class_Markups=MarkupMaker
    )
    BOT.start_polling()
