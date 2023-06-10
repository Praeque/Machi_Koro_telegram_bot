import asyncio

from data import ActionDB
from aiogram_types import MarkupMaker, MessageSender
from game_play import CardPlay, BotPlay

import random
from asyncio import sleep
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, executor
import os
import emoji


quick_sleep = 0.4

human_unicode = '\U0001F64E\U0000200D\U00002642\U0000FE0F'
human_cldr = ':man_pouting:'
bot_unicode = '\U0001F916'             # '\U0001F464'
bot_cldr = ':robot:'         # ':bust_in_silhouette:'

load_dotenv()
bot = Bot(os.getenv('TELEGRAM_BOT_TOKEN'))
dp = Dispatcher(bot)
DB = ActionDB(human_cldr, bot_cldr)
roll_play = CardPlay(DB)
sender = MessageSender(bot)
bot_gameplay = BotPlay(DB, bot, quick_sleep, sender, bot_cldr)
markups = MarkupMaker(DB, human_unicode, bot_unicode)


@dp.message_handler(commands=['rules'])
async def command_rules(message: types.Message):
    if message.chat.type == 'private':
        rules = emoji.emojize(DB.get_description('rules'))
        await message.answer(rules, parse_mode='html')


@dp.message_handler(commands=['how_to_play'])
async def command_how_to_play(message: types.Message):
    if message.chat.type == 'private':
        rules = emoji.emojize(DB.get_description('how_to_play'))
        await message.answer(rules, parse_mode='html')



@dp.message_handler(commands=['start_game'])
async def set_up(message: types.Message):
    group = message.chat.type == 'supergroup'
    administration = await check_admin_status(message.chat.id, message.from_user.id)
    if group:
        if administration:
            if not DB.is_session(message.chat.id):
                text = 'Займите место, нажав "Присоединиться к игре"\nМогут играть от 2 до 5 игроков 👥'
                markup = markups.start_lobby()
                message_lobby = await bot.send_message(message.chat.id, text, reply_markup=markup)
                DB.create_session(message.chat.id, message_lobby.message_id)
            else:
                view = '<b>⚠️ У вас не законченная сессия в этом чате ❗️</b>\n<u>Доиграйте</u>, либо <u>закройте</u> ' \
                       'ее принудително:\n<b>"/end_session"</b>'
                await bot.send_message(message.chat.id, view, parse_mode='html')
        else:
            view = '⚠️ <b>Только администратор чата может создавать игру</b>❗ ️'
            await bot.send_message(message.chat.id, view, parse_mode='html')
    else:
        view = '⚠️ <b>Только в группах можно создавать игры</b>❗ ️'
        await bot.send_message(message.chat.id, view, parse_mode='html')


@dp.message_handler(commands=['end_session'])
async def end_session(message: types.Message):
    administration = await check_admin_status(message.chat.id, message.from_user.id)
    if administration:
        messages = DB.delete_chat_session(message.chat.id)
        if messages:
            for chat_id, messages_id in messages.items():
                for message_id in messages_id:
                    await sender.delete_message(chat_id, message_id)
                    await sleep(0.5)
            await message.answer('Сессия успешно удалена, можете начинать новую!')
    else:
        view = '⚠️ <b>Только администратор чата может принудительно закончить сессию </b>❗ ️'
        await bot.send_message(message.chat.id, view, parse_mode='html')


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'get_place_lobby')
async def lobby_callback(call: types.CallbackQuery):
    player_id = call.from_user.id
    player_name = call.from_user.first_name
    game_id = call.message.chat.id

    is_player_in_lobby = DB.is_player_in_lobby(game_id, player_id) + DB.is_audience_in_lobby(game_id, player_id)
    if not is_player_in_lobby:

        count_player = DB.get_count_player(call.message.chat.id)
        if count_player < 5:

            DB.create_new_city(game_id, player_id, player_name)

            markup = markups.lobby_with_people(game_id)
            await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'audience')
async def audience(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_name = call.from_user.first_name
    game_id = call.message.chat.id

    is_player_in_lobby = DB.is_player_in_lobby(game_id, user_id) + DB.is_audience_in_lobby(game_id, user_id)
    if not is_player_in_lobby:
        if DB.create_new_audience(game_id, user_id, user_name):
            markup = markups.lobby_with_people(game_id)
            await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)


@dp.callback_query_handler(lambda callback_query: callback_query.data.split(',')[0] == 'place')
async def place_kick(call: types.CallbackQuery):
    administration = await check_admin_status(call.message.chat.id, call.from_user.id)
    if administration:
        game_id = call.message.chat.id
        player_id = int(call.data.split(',')[1])   # 'place,{player.player_id}'
        DB.kick_player_lobby(game_id, player_id)

        markup = markups.lobby_with_people(game_id)
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)


@dp.callback_query_handler(lambda callback_query: callback_query.data.split(',')[0] == 'audiencer')
async def audience_kick(call: types.CallbackQuery):
    administration = await check_admin_status(call.message.chat.id, call.from_user.id)
    if administration:
        game_id = call.message.chat.id
        user_id = int(call.data.split(',')[1])  # 'place,{player.player_id}'
        DB.kick_audience_lobby(game_id, user_id)

        markup = markups.lobby_with_people(game_id)
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'add_bot')
async def start_game(call: types.CallbackQuery):
    administration = await check_admin_status(call.message.chat.id, call.from_user.id)
    if administration:
        game_id = call.message.chat.id

        count_player = DB.get_count_player(call.message.chat.id)
        if count_player < 5:
            DB.create_bot_city(game_id)

            markup = markups.lobby_with_people(game_id)
            await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)


@dp.callback_query_handler(lambda callback_query: callback_query.data.split(',')[0] == 'start_game')
async def start_game(call: types.CallbackQuery):
    administration = await check_admin_status(call.message.chat.id, call.from_user.id)
    if administration:
        game_id = call.message.chat.id
        if DB.check_and_lock(game_id):
            type_game = call.data.split(',')[1]

            DB.start_game(game_id, type_game)
            text = 'Интерфейс игры у каждого в личном чате, с ботом.\nПриятной вам игры.'
            await bot.edit_message_text(text, call.message.chat.id, call.message.message_id)
            await send_game_messages(game_id)

            DB.unlock_game(game_id)


async def send_game_messages(game_id):
    messages = {}
    first_player_id, first_player_name, first_player_bot, all_players_id = DB.get_players_id_for_start(game_id)
    all_players_id.extend(DB.get_all_audiencers(game_id))
    cities_info = emoji.emojize(DB.get_cities_info(game_id))
    slime_view = human_unicode
    if first_player_bot:
        slime_view = bot_unicode
    for player_id in all_players_id:
        if player_id in [1, 2, 3, 4, 5]:
            continue
        history = await sender.send_message(player_id, '...')
        cities = await sender.send_message(player_id, cities_info)
        if player_id == first_player_id:
            markup = markups.create_roll_markup(game_id)
            view = ' <b>  Ваш ход   </b>'
            action_1 = await sender.send_message(player_id, view, markup)
        else:
            view = f'Ходит {slime_view}<b>{first_player_name}</b>'
            action_1 = await sender.send_message(player_id, view)
        action_2 = await sender.send_message(player_id, '...')
        messages[player_id] = {'history': history.message_id, 'cities': cities.message_id,
                               'action_1': action_1.message_id, 'action_2': action_2.message_id}
    DB.save_id_messages(game_id, messages)
    if first_player_bot:
        await play_bot(game_id, first_player_id, first_player_name)


@dp.callback_query_handler(lambda callback_query: callback_query.data.split(',')[0] == 'roll')
async def roll(call: types.CallbackQuery):
    # parse_data
    # 'roll,{number_of_dice},{reroll},{game_id}'
    number_of_dice, reroll, game_id = [int(variable) for variable in call.data.split(',')[1:]]

    player_id = call.from_user.id
    DB.lock_game(game_id)

    number, numbers = await roll_dice(call.from_user.first_name, game_id, reroll, number_of_dice)

    is_radio_tower = DB.is_radio_tower(game_id, player_id)
    if is_radio_tower and not reroll:
        await make_rerollin_view(call, game_id, numbers)
    else:
        await duple_check(game_id, numbers, player_id)
        is_port = DB.is_card_in_city(game_id, player_id, 'port')
        if is_port and number > 9:
            await make_port_view(call, game_id, number)
        else:
            await play_number(call, player_id, game_id, number)
    DB.unlock_game(game_id)


async def duple_check(game_id, numbers, player_id):
    if len(numbers) == 2:
        if numbers[0] == numbers[1]:
            DB.duple_rolled(game_id, player_id)


async def roll_dice(name, game_id, reroll, number_of_dice):
    numbers = [random.randint(1, 6) for i in range(number_of_dice)]
    number = sum(numbers)
    await save_rolling(name, game_id, numbers, reroll, number_of_dice)
    await refresh_history(game_id)
    await sleep(1)
    return number, numbers


async def save_rolling(name, game_id, numbers, reroll, number_of_dice):
    numbers_str = '  '.join([str(number) for number in numbers])
    if reroll:
        turn_story = f'\n      :counterclockwise_arrows_button:   {":game_die:" * number_of_dice}' \
                     f'   {numbers_str}'
    else:
        turn_story = f'\n{human_cldr} {name}   {":game_die:" * number_of_dice}   {numbers_str}'
    DB.put_new_story(turn_story, game_id)


async def make_rerollin_view(call, game_id, numbers):
    await sleep(quick_sleep)
    markup = markups.create_reroll_or_continue_markup(game_id, numbers)
    await sender.edit_markup(call, markup=markup)


async def make_port_view(call, game_id, number):
    await sleep(quick_sleep)
    markup = markups.create_port_markup(game_id, number)
    await sender.edit_markup(call, markup=markup)


async def play_number(call, player_id, game_id, number, continue_number=False, port=False):
    is_change_money = roll_play.all_cards_play(game_id, player_id, number) + DB.town_hall(game_id, player_id)
    if is_change_money:
        await refresh_history(game_id)
        await refresh_cities_property(game_id)
    if number == 6:
        if DB.is_tv_station(game_id, player_id) and DB.is_money_other_player(game_id, player_id):
            return await play_tv_station(call, game_id, player_id)
        if DB.is_office(game_id, player_id):
            return await play_office(call, game_id, player_id)
    elif number > 11 and DB.is_trawler(game_id):
        return await play_trawler(call, game_id)
    await create_build_view(call, game_id, player_id)


async def refresh_history(game_id):
    await sleep(quick_sleep)
    history = emoji.emojize(DB.get_history(game_id))
    messages_id = DB.get_messages_history(game_id)
    for player_id, mess_id in messages_id.items():
        await sender.edit_message(history, player_id, mess_id)


async def refresh_cities_property(game_id):
    await sleep(quick_sleep)
    cities_info = emoji.emojize(DB.get_cities_info(game_id))
    messages_id = DB.get_messages_cities(game_id)
    for player_id, mess_id in messages_id.items():
        await sender.edit_message(cities_info, player_id, mess_id)


async def create_build_view(call, game_id, player_id):
    await sleep(quick_sleep)
    markup = markups.create_build_markup(game_id, player_id)
    view = f'    Выберете, что хотите построить в своем городе   🏗 '
    await sender.edit_message_this_chat(view, call, markup=markup)


async def play_tv_station(call, game_id, player_id):
    await sleep(quick_sleep)
    markup = markups.create_tv_station_markup(game_id, player_id)
    view = f'<b>{call.from_user.first_name}</b>  Выбирает у кого забрать деньги...'
    await sender.edit_message_this_chat(view, call, markup=markup)


async def play_trawler(call, game_id):
    await sleep(quick_sleep)
    markup = markups.create_trawler_markup(game_id)
    view = 'Киньте кубики еще раз, для срабатывания Траулера 🛳'
    await sender.edit_message_this_chat(view, call, markup=markup)


@dp.callback_query_handler(lambda callback_query: callback_query.data.split(',')[0] == 'trawler')
async def trawler(call: types.CallbackQuery):
    game_id = int(call.data.split(',')[1])
    player_id = call.from_user.id
    DB.lock_game(game_id)
    roll_play.play_trawler(game_id)
    await refresh_history(game_id)
    await refresh_cities_property(game_id)
    await create_build_view(call, game_id, player_id)
    DB.unlock_game(game_id)


@dp.callback_query_handler(lambda callback_query: callback_query.data.split(',')[0] == 'tv_station')
async def tv_station(call: types.CallbackQuery):
    # f'tv_station,{victim_id},{game_id}'
    game_id = int(call.data.split(',')[2])
    player_id = call.from_user.id
    victim_id = int(call.data.split(',')[1])
    DB.lock_game(game_id)
    roll_play.play_tv_station(game_id, player_id, victim_id)
    await refresh_history(game_id)
    await refresh_cities_property(game_id)
    if DB.is_office(game_id, player_id):
        await play_office(call, game_id, player_id)
    else:
        await create_build_view(call, game_id, player_id)

    DB.unlock_game(game_id)


async def play_office(call, game_id, player_id):
    await sleep(quick_sleep)
    markup = markups.create_markup_office_self(game_id, player_id)
    view = f'<b>{call.from_user.first_name} \U000026A0  ' \
           f'Выберите какое предприятие вы хотите <u>отдать</u> \U000027A1</b>'
    await sender.edit_message_this_chat(view, call, markup=markup)


@dp.callback_query_handler(lambda callback_query: callback_query.data.split(',')[0] == 'office_self')
async def office_self(call: types.CallbackQuery):
    # f'office_self,{name_gift_card},{game_id}'
    game_id = int(call.data.split(',')[2])
    player_id = call.from_user.id
    name_gift_card = call.data.split(',')[1]
    markup = markups.create_markup_office_other(name_gift_card, game_id, player_id)
    view = f'<b>{call.from_user.first_name}  Выберите какое предприятие вы хотите <u>забрать</u> \U0001F90C</b>'
    await sleep(quick_sleep)
    await sender.edit_message_this_chat(view, call, markup=markup)

    DB.unlock_game(game_id)


@dp.callback_query_handler(lambda callback_query: callback_query.data.split(',')[0] == 'office_other')
async def office_other(call: types.CallbackQuery):
    # f'office_other,{name_gift_card},{name_taken_card},{victim_player},{game_id}'
    name_gift_card, name_taken_card, victim_player, game_id = call.data.split(',')[1:]
    game_id, victim_player = int(game_id), int(victim_player)
    player_id = call.from_user.id
    DB.lock_game(game_id)
    DB.swap_cards(name_gift_card, name_taken_card, player_id, victim_player, game_id)
    await refresh_history(game_id)
    await refresh_cities_property(game_id)
    await create_build_view(call, game_id, player_id)
    DB.unlock_game(game_id)


@dp.callback_query_handler(lambda callback_query: callback_query.data.split(',')[0] == 'continue_numbers')
async def continue_numbers(call: types.CallbackQuery):
    # 'continue_numbers,{number_data},{game_id}'
    game_id = int(call.data.split(',')[2])
    player_id = call.from_user.id
    DB.lock_game(game_id)
    number_data_str = call.data.split(',')[1]
    numbers = [int(number) for number in number_data_str.split('.')]
    number = sum(numbers)
    await duple_check(game_id, numbers, player_id)
    is_port = DB.is_card_in_city(game_id, player_id, 'port')
    if is_port and number > 9:
        await make_port_view(call, game_id, number)
    else:
        await play_number(call, player_id, game_id, number, continue_number=True)
    DB.unlock_game(game_id)


@dp.callback_query_handler(lambda callback_query: callback_query.data.split(',')[0] == 'port')
async def continue_numbers(call: types.CallbackQuery):
    # 'port,{number},{is_used_port},{game_id}'
    number, is_used_port, game_id = [int(var) for var in call.data.split(',')[1:]]
    player_id = call.from_user.id
    DB.lock_game(game_id)
    if is_used_port:
        new_number = number + 2
        new_story = f'\n      :anchor: :game_die::game_die:  {number} :right_arrow: {new_number}'
        DB.put_new_story(new_story, game_id)
        await play_number(call, player_id, game_id, new_number, port=is_used_port)
    else:
        await play_number(call, player_id, game_id, number)
    DB.unlock_game(game_id)


@dp.callback_query_handler(lambda callback_query: callback_query.data.split(',')[0] == 'type_card_info')
async def type_card_info(call: types.CallbackQuery):
    # 'type_card_info,{color},{game_id}'
    # game_id = int(call.data.split(',')[2])
    # player_id = call.from_user.id
    card_type = call.data.split(',')[1]
    description = emoji.emojize(DB.get_description(card_type))
    await sender.edit_message_try(description, call, 1)


@dp.callback_query_handler(lambda callback_query: callback_query.data.split(',')[0] == 'card_info')
async def card_info(call: types.CallbackQuery):
    # 'card_info,{card.name},{game_id}'
    game_id = int(call.data.split(',')[2])
    player_id = call.from_user.id
    card_name = call.data.split(',')[1]
    markup = markups.create_card_info_markup(card_name, game_id, player_id)
    description = emoji.emojize(DB.get_card_description(card_name, game_id))
    await sender.edit_message_try(description, call, 1, markup=markup)


@dp.callback_query_handler(lambda callback_query: callback_query.data.split(',')[0] == 'pass_turn')
async def pass_turn(call: types.CallbackQuery):
    # 'pass_turn,{game_id}'
    game_id = int(call.data.split(',')[1])
    # player_id = call.from_user.id
    markup = markups.pass_turn(game_id)
    await sender.edit_message_try('<b>Дать рабочим выходной</b> \U000026A0', call, 1, markup)


@dp.callback_query_handler(lambda callback_query: callback_query.data.split(',')[0] == 'complete_pass_turn')
async def complete_pass_turn(call: types.CallbackQuery):
    # 'complete_pass_turn,{game_id}'
    game_id = int(call.data.split(',')[1])
    player_id = call.from_user.id
    DB.lock_game(game_id)
    new_story = f'\n       :building_construction:      :prohibited:'
    is_airport = DB.is_card_in_city(game_id, player_id, 'airport')
    if is_airport:
        DB.pull_money_changes(game_id, {player_id: 10})
        new_story += f'\n    -  {call.from_user.first_name}   + 10  :dollar_banknote:'
    DB.put_new_story(new_story, game_id)
    await refresh_history(game_id)
    if is_airport:
        await refresh_cities_property(game_id)
    await make_next_turn(call, player_id, game_id, win=False)
    DB.unlock_game(game_id)


@dp.callback_query_handler(lambda callback_query: callback_query.data.split(',')[0] == 'build')
async def build(call: types.CallbackQuery):
    # f'build,{card_name},{cost_card},{game_id}'
    game_id = int(call.data.split(',')[3])
    player_id = call.from_user.id
    DB.lock_game(game_id)
    card_name, cost_card = call.data.split(',')[1], int(call.data.split(',')[2])
    win = DB.add_card_to_player(game_id, card_name, player_id)
    DB.pull_money_changes(game_id, {player_id: - cost_card})
    build_history = f'\n       :building_construction:      :{DB.get_card_emoji(card_name)}:'
    DB.put_new_story(build_history, game_id)
    await refresh_history(game_id)
    await refresh_cities_property(game_id)
    await make_next_turn(call, player_id, game_id, win=win)
    DB.unlock_game(game_id)


async def make_next_turn(call: types.CallbackQuery, player_id, game_id, win):
    if win:
        await refresh_history(game_id)
        await refresh_cities_property(game_id)
        await finish_game(call, game_id)
    else:
        next_player_id, next_player_name, need_refresh = DB.get_number_next_player(game_id, player_id)
        if need_refresh:
            await refresh_history(game_id)
        if DB.is_bot(game_id, next_player_id):
            await sender.edit_message_this_chat('...', call)
            await play_bot(game_id, next_player_id, next_player_name)
        else:
            await edit_roll_messages_next_player(game_id, next_player_id, next_player_name)
            await sender.edit_message_this_chat('...', call)


async def edit_roll_messages_next_player(game_id, next_player_id, next_player_name):
    markup = markups.create_roll_markup(game_id)
    messages_id = DB.get_messages_action_1(game_id)
    for player_id, mess_id in messages_id.items():
        if player_id == next_player_id:
            view = f' <b>  Ваш ход   </b> 🎲 '
            await sender.edit_message(view, player_id, mess_id, markup)
        else:
            view = f'Ходит  {human_unicode}  <b>{next_player_name}</b>  👣'
            await sender.edit_message(view, player_id, mess_id)


async def play_bot(game_id, bot_id, bot_name):
    win = False
    try:
        await send_message_bot_play(game_id, bot_name)
        await sleep(1.5)
        number = await bot_gameplay.bot_roll(game_id, bot_id, bot_name)
        is_change_money = roll_play.all_cards_play(game_id, bot_id, number) + DB.town_hall(game_id, bot_id)
        if number > 11 and DB.is_trawler(game_id):
            roll_play.play_trawler(game_id)
        if is_change_money:
            await refresh_history(game_id)
            await refresh_cities_property(game_id)
        await sleep(2.5)
        built, win = await bot_gameplay.bot_build(game_id, bot_id, bot_name)
        await refresh_history(game_id)
        if built:
            await refresh_cities_property(game_id)
    except Exception as error:
        print(error)
        print(f'\033[91m {"___---FAIL---___" * 20}\033[0m')
    await make_next_bot(bot_id, game_id, win, bot_name)


async def send_message_bot_play(game_id, bot_name):
    messages_id = DB.get_messages_action_1(game_id)
    for player_id, mess_id in messages_id.items():
        view = f'Ходит  {bot_unicode}  <b>{bot_name}</b>  👣'
        await sender.edit_message(view, player_id, mess_id)


async def make_next_bot(bot_id, game_id, win, bot_name):
    if win:
        await finish_game_bot(game_id, bot_id, bot_name)
    else:
        next_player_id, next_player_name, need_refresh = DB.get_number_next_player(game_id, bot_id)
        if need_refresh:
            await refresh_history(game_id)
        if DB.is_bot(game_id, next_player_id):
            await play_bot(game_id, next_player_id, next_player_name)
        else:
            await edit_roll_messages_next_player(game_id, next_player_id, next_player_name)


async def finish_game_bot(game_id, bot_id, bot_name):
    messages_id = DB.get_actions_messages(game_id)
    for player_id, mess_id in messages_id['action_1'].items():
        view = f'{bot_unicode} {bot_name} вытащил город со дна, и теперь даже Зеленский приезжает, чтоб посмотреть на его ' \
               f'достопримечательности.\n{bot_unicode} {bot_name} побеждает! 🦾'
        await sender.edit_message(view, player_id, mess_id)
    for player_id, mess_id in messages_id['action_2'].items():
        await sender.edit_message('🏁', player_id, mess_id)
    moves, laps, chat_message_id = DB.get_game_last_info(game_id)
    view = f'🏁 Побеждает  {bot_unicode}  <b>{bot_name}</b>  🦾!' \
           f'\n {moves} / {laps} (ходов / кругов - было сделано)'
    await sender.edit_message(view, game_id, chat_message_id)
    DB.delete_chat_session(game_id)


async def finish_game(call, game_id):
    messages_id = DB.get_actions_messages(game_id)
    for player_id, mess_id in messages_id['action_1'].items():
        if player_id == call.from_user.id:
            view = f'Вы вытащили город со дна, и теперь даже Зеленский приезжает,' \
                   f' чтоб посмотреть на его достопримечательности.\n' \
                   f'🥇 Вы побеждаете! 🏆'
        else:
            view = f'{human_unicode} {call.from_user.first_name} вытащил город со дна, и теперь даже ' \
                   f'Зеленский приезжает, чтоб посмотреть на его достопримечательности.\n' \
                   f'🥇{human_unicode} {call.from_user.first_name} побеждает! 🏆'
        await sender.edit_message(view, player_id, mess_id)
    for player_id, mess_id in messages_id['action_2'].items():
        if player_id == call.from_user.id:
            await sender.edit_message('🎉', player_id, mess_id)
        else:
            await sender.edit_message('🏁', player_id, mess_id)
    moves, laps, chat_message_id = DB.get_game_last_info(game_id)
    name_winner = DB.get_name(game_id, player_id)
    view = f'🏁 Побеждает  {human_unicode}  <b>{name_winner}</b>  💪!' \
           f'\n {moves} / {laps} (ходов / кругов - было сделано)'
    await sender.edit_message(view, game_id, chat_message_id)

    DB.delete_chat_session(game_id)


async def check_admin_status(chat_id, user_id):
    # Получение информации о пользователе в чате
    chat_member = await bot.get_chat_member(chat_id, user_id)
    print(chat_member.status)
    # Проверка статуса пользователя (является ли администратором)
    if chat_member.status in [types.ChatMemberStatus.CREATOR, types.ChatMemberStatus.ADMINISTRATOR]:
        return True
    else:
        return False


async def set_commands():

    commands_private = [
        types.BotCommand(command='/rules', description='Правила игры'),
        types.BotCommand(command='/how_to_play', description='Как начать игру')
    ]
    commands_group = [
        types.BotCommand(command='/start_game', description='Создать лобби игры')
    ]
    await bot.set_my_commands(commands_private, scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands_group, scope=types.BotCommandScopeAllGroupChats())


loop = asyncio.get_event_loop()
loop.run_until_complete(set_commands())

def run_bot():
    executor.start_polling(dp, skip_updates=True)



if __name__ == '__main__':
    run_bot()
