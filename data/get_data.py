from sqlalchemy import create_engine, select, or_
from sqlalchemy.orm import Session
from .models import Description, Card, TableCard, PlayerCard, City, GameHistory, GameSession, MessagesId, Audience
import random


class ActionDB:

    def __init__(self, human_cldr, bot_cldr):

        self.engine = create_engine('sqlite:///data/data.db')

        self.human_cldr = human_cldr
        self.bot_cldr = bot_cldr

    def select_all_players(self, game_id):
        with Session(self.engine) as session:
            cities = select(City).where(City.game_id == game_id)
            all_players = [player for player in session.scalars(cities)]
        return all_players

    def get_description(self, topic):
        with Session(self.engine) as session:
            descript = select(Description).where(Description.topic == topic)
            descript = session.scalar(descript)
        return descript.description

    def is_session(self, chat_id):
        with Session(self.engine) as session:
            session = session.scalar(select(GameSession).where(GameSession.game_id == chat_id))
            if session:
                return True

    def create_description(self, topic, description):
        with Session(self.engine) as session:
            new_line = Description(topic=topic, description=description)

            session.add(new_line)
            session.commit()
        return True

    @staticmethod
    def get_starts_cards(session, game_id):
        cities = session.scalars(select(City).where(City.game_id == game_id))
        wheat = session.scalar(select(Card).where(Card.name == 'wheat field'))
        bakery = session.scalar(select(Card).where(Card.name == 'bakery'))
        for city in cities:
            player_id = city.player_id
            player_wheat = PlayerCard(name_card=wheat.name, game_id=game_id, player_id=player_id,
                                      number=wheat.number, income=wheat.income, type_card=wheat.type_card,
                                      sign=wheat.sign, emoji_view=wheat.emoji_view, quantity=1,
                                      number_str=wheat.number_str, original=True)
            player_bakery = PlayerCard(name_card=bakery.name, game_id=game_id, player_id=player_id,
                                       number=bakery.number, income=bakery.income, type_card=bakery.type_card,
                                       sign=bakery.sign, emoji_view=bakery.emoji_view, quantity=1,
                                       number_str=bakery.number_str, original=True)
            player_bakery_dup = PlayerCard(name_card=bakery.name, game_id=game_id, player_id=player_id,
                                           number=int(bakery.extra_numbers), income=bakery.income,
                                           type_card=bakery.type_card, sign=bakery.sign,
                                           emoji_view=bakery.emoji_view, quantity=1, number_str=bakery.number_str,
                                           original=False)
            session.add_all([player_wheat, player_bakery, player_bakery_dup])

    def create_new_city(self, game_id, player_id, player_name):
        with Session(self.engine) as session:
            game_session = session.scalar(select(GameSession).where(GameSession.game_id == game_id))
            game_session.count_player += 1
            session.add(game_session)

            new_city = City(game_id=game_id, player_id=player_id, money=0, turn=0, count_attractions=0,
                            bot=False, player_name=player_name)
            session.add(new_city)
            session.commit()

    def is_bot(self, game_id, player_id):
        with Session(self.engine) as session:
            city = session.scalar(select(City).filter(City.game_id == game_id, City.player_id == player_id))
            return city.bot

    def create_bot_city(self, game_id):
        with Session(self.engine) as session:
            game_session = session.scalar(select(GameSession).where(GameSession.game_id == game_id))
            game_session.count_player += 1
            session.add(game_session)
            cities = session.scalars(select(City).where(City.game_id == game_id))
            bot_ids = [1, 2, 3, 4, 5]
            bot_names = ['Gena', 'Valera', 'Monica', 'Tanya', 'Petya']
            for city in cities:
                if city.bot:
                    bot_ids.remove(city.player_id)
                    bot_names.remove(city.player_name)
            random.shuffle(bot_names)
            bot_id = bot_ids[0]
            bot_name = bot_names[0]

            new_city = City(game_id=game_id, player_id=bot_id, money=0, turn=0, count_attractions=0,
                            bot=True, player_name=bot_name)
            session.add(new_city)
            session.commit()

    def get_all_card_from_table(self, game_id):
        with Session(self.engine) as session:
            cards = session.scalars(select(TableCard).where(TableCard.game_id == game_id))
            dict_cards = {card.name: card.quantity for card in cards}
            return dict_cards

    def get_player_card(self, game_id, player_id):
        with Session(self.engine) as session:
            cards = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                              PlayerCard.player_id == player_id))
            dict_cards = {card.name_card: card.quantity for card in cards if card.original}
            return dict_cards

    def get_all_card_from_people_and_cities(self, game_id):
        session = Session(self.engine)
        cards = session.scalars(select(PlayerCard).where(PlayerCard.game_id == game_id))
        cities = session.scalars((select(City).where(City.game_id == game_id)))
        return cards, cities, session

    def town_hall(self, game_id, player_id):
        with Session(self.engine) as session:
            game_session = session.scalar(select(GameSession).where(GameSession.game_id == game_id))
            if game_session.type_game == 'additions':
                city = session.scalar(select(City).filter(City.game_id == game_id, City.player_id == player_id))
                if city.money == 0:
                    city.money = 1
                    session.add(city)
                    session.commit()
                    new_story = f'\n    -  {city.player_name}  + 1  :dollar_banknote:    :left_arrow:   :hut:'
                    self.put_new_story(new_story, game_id)
                    return True
            return False

    def get_first_player_name(self, game_id):
        with Session(self.engine) as session:
            city = session.scalar(select(City).filter(City.game_id == game_id, City.turn == 1))
            return city.player_name, city.bot

    @staticmethod
    def get_cards_to_table(session,  game_id, type_game):
        if type_game == 'basic':
            card_pack = session.scalars(select(Card).where(Card.type_game == 'basic'))
        else:  # type_game == 'additions'
            card_pack = session.scalars(select(Card).filter(or_(Card.type_game == 'basic',
                                                            Card.type_game == 'additions')))

        for card in card_pack:
            new_line = TableCard(game_id=game_id, name=card.name, number=card.number, income=card.income,
                                 extra_numbers=card.extra_numbers, type_card=card.type_card, sign=card.sign,
                                 emoji_view=card.emoji_view, quantity=card.quantity, number_str=card.number_str)
            session.add(new_line)

    def start_game(self, game_id, type_game):
        with Session(self.engine) as session:
            first_player_id = self.set_start_money_and_turn(session, game_id, type_game)
            self.set_up_game_type(session, game_id, type_game, first_player_id)
            self.get_cards_to_table(session, game_id, type_game)
            self.get_starts_cards(session, game_id)
            self.create_game_history_in_table(session, game_id)
            session.commit()

    @staticmethod
    def set_start_money_and_turn(session, game_id, type_game):
        if type_game == 'basic':
            start_money = 3
        else:  # type_game == 'additions'
            start_money = 1
        cities = session.scalars(select(City).where(City.game_id == game_id))
        turn = 0
        first_player_id = None
        for city in cities:
            turn += 1
            if turn == 1:
                first_player_id = city.player_id
            city.turn = turn
            city.money = start_money
            session.add(city)
        return first_player_id

    @staticmethod
    def set_up_game_type(session, game_id, type_game, first_player_id):
        game_session = session.scalar(select(GameSession).where(GameSession.game_id == game_id))
        game_session.type_game = type_game
        game_session.turn_now = first_player_id
        session.add(game_session)

    def get_players_id_for_start(self, game_id):
        with Session(self.engine) as session:
            cities = session.scalars(select(City).where(City.game_id == game_id))
            all_players_id = []
            for city in cities:
                if city.turn == 1:
                    first_player_bot = city.bot
                    first_player_id = city.player_id
                    first_player_name = city.player_name
                all_players_id.append(city.player_id)
                print(city.player_id, 'DB')
            return first_player_id, first_player_name, first_player_bot, all_players_id

    def save_id_messages(self, game_id: int, messages: dict):
        with Session(self.engine) as session:
            for player_id, mess in messages.items():
                new_line = MessagesId(game_id=game_id, player_id=player_id, history=mess['history'],
                                      cities=mess['cities'], action_1=mess['action_1'], action_2=mess['action_2'])
                session.add(new_line)
                session.commit()

    def get_messages_history(self, game_id):
        with Session(self.engine) as session:
            messages = session.scalars(select(MessagesId).where(MessagesId.game_id == game_id))
            messages_id = {}
            for mess in messages:
                messages_id[mess.player_id] = mess.history
            return messages_id

    def get_messages_cities(self, game_id):
        with Session(self.engine) as session:
            messages = session.scalars(select(MessagesId).where(MessagesId.game_id == game_id))
            messages_id = {}
            for mess in messages:
                messages_id[mess.player_id] = mess.cities
            return messages_id

    def get_messages_action_1(self, game_id):
        with Session(self.engine) as session:
            messages = session.scalars(select(MessagesId).where(MessagesId.game_id == game_id))
            messages_id = {}
            for mess in messages:
                messages_id[mess.player_id] = mess.action_1
            return messages_id

    def get_actions_messages(self, game_id):
        with Session(self.engine) as session:
            messages = session.scalars(select(MessagesId).where(MessagesId.game_id == game_id))
            messages_id = {'action_1': {}, 'action_2': {}}
            for mess in messages:
                messages_id['action_1'][mess.player_id] = mess.action_1
                messages_id['action_2'][mess.player_id] = mess.action_2
            return messages_id

    def get_count_player(self, game_id):
        with Session(self.engine) as session:
            session_game = session.scalar(select(GameSession).where(GameSession.game_id == game_id))
            return session_game.count_player

    def is_player_in_lobby(self, game_id, player_id):
        with Session(self.engine) as session:
            city = session.scalar(select(City).filter(City.game_id == game_id, City.player_id == player_id))
            if city:
                return True
            return False

    def create_session(self, chat_id, message_id):
        with Session(self.engine) as session:
            new_session = GameSession(game_id=chat_id, count_player=0, turn_now=0, duple=False,
                                      lock=True, mess=message_id, type_game=None, moves=1, laps=0)
            session.add(new_session)
            session.commit()

    def save_number_messages(self, game_id, messages):
        with Session(self.engine) as session:
            game_session = session.scalar(select(GameSession).where(GameSession.game_id == game_id))
            game_session.messages = ','.join([str(message.message_id) for message in messages])
            session.add(game_session)
            session.commit()

    def is_radio_tower(self, game_id, player_id):
        with Session(self.engine) as session:
            player_card = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                                    PlayerCard.player_id == player_id,
                                                                    PlayerCard.name_card == 'radio tower'))
            if player_card.one_or_none():
                return True
            return False

    def duple_rolled(self, game_id, player_id):
        with Session(self.engine) as session:
            amusement_park = session.scalar(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                                      PlayerCard.player_id == player_id,
                                                                      PlayerCard.name_card == 'amusement park'))
            if amusement_park:
                self.put_new_story('  :ferris_wheel:', game_id)
                game_session = session.scalar(select(GameSession).where(GameSession.game_id == game_id))
                game_session.duple = True
                session.add(game_session)
                session.commit()

    def is_train_station(self, game_id):
        with Session(self.engine) as session:
            game_session = session.scalar(select(GameSession).where(GameSession.game_id == game_id))
            player_id = game_session.turn_now
            player_card = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                                    PlayerCard.player_id == player_id,
                                                                    PlayerCard.name_card == 'train station'))
            if player_card.one_or_none():
                return True
            return False

    def is_stadium(self, game_id, player_id):
        with Session(self.engine) as session:
            player_card = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                                    PlayerCard.player_id == player_id,
                                                                    PlayerCard.name_card == 'stadium'))
            if player_card.one_or_none():
                return True
            return False

    def is_tv_station(self, game_id, player_id):
        with Session(self.engine) as session:
            player_card = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                                    PlayerCard.player_id == player_id,
                                                                    PlayerCard.name_card == 'tv station'))
            if player_card.one_or_none():
                return True
            return False

    def is_office(self, game_id, player_id):
        with Session(self.engine) as session:
            player_card = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                                    PlayerCard.player_id == player_id,
                                                                    PlayerCard.name_card == 'office'))
            if player_card.one_or_none():
                return True
            return False

    def money(self, game_id, player_id):
        with Session(self.engine) as session:
            city = session.scalar(select(City).filter(City.game_id == game_id, City.player_id == player_id))
            return city.money

    def pull_money_changes(self, game_id, money_changes):
        with Session(self.engine) as session:
            cities = session.scalars(select(City).where(City.game_id == game_id))
            for city in cities:
                if city.player_id in money_changes:
                    city.money += money_changes[city.player_id]
                    session.add(city)
            session.commit()

    def is_shopping_mall(self, game_id, player_id):
        with Session(self.engine) as session:
            player_card = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                                    PlayerCard.player_id == player_id,
                                                                    PlayerCard.name_card == 'shopping mall'))
            if player_card.one_or_none():
                return True
            return False

    def get_number_next_player(self, game_id, player_id):
        with Session(self.engine) as session:
            laps_story = False
            game_session = session.scalar(select(GameSession).where(GameSession.game_id == game_id))
            city = session.scalar(select(City).filter(City.game_id == game_id, City.player_id == player_id))
            game_session.moves += 1
            need_refresh = False
            if game_session.duple:
                duple_story = '\n:plus:  :footprints:'   # :ferris_wheel:
                self.put_new_story(duple_story, game_id)
                game_session.duple = False
                session.add(game_session)
                session.commit()
                need_refresh = True
                return city.player_id, city.player_name, need_refresh
            if city.turn == game_session.count_player:
                next_city = session.scalar(select(City).filter(City.game_id == game_id, City.turn == 1))
                game_session.laps += 1
                counter_laps = ''
                for number in str(game_session.laps + 1):
                    counter_laps += f':keycap_{number}:'
                laps_story = f'\n\n       {counter_laps}:recycling_symbol:\n'
                need_refresh = True
            else:
                next_city = session.scalar(select(City).filter(City.game_id == game_id, City.turn == city.turn + 1))
            game_session.turn_now = next_city.player_id
            session.add(game_session)
            session.commit()
            if laps_story:
                self.put_new_story(laps_story, game_id)
            return next_city.player_id, next_city.player_name, need_refresh

    def get_card_view(self, card_name):
        with Session(self.engine) as session:
            card = session.scalar(select(Card).where(Card.name == card_name))
            card_view = f'[ {card.number_str}  :{card.emoji_view}: ]'
            return card_view

    def get_card_emoji(self, card_name):
        with Session(self.engine) as session:
            card = session.scalar(select(Card).where(Card.name == card_name))
            return card.emoji_view

    def count_card_sign(self, game_id, player_id, sign):
        with Session(self.engine) as session:
            cards = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                              PlayerCard.player_id == player_id,
                                                              PlayerCard.sign == sign))
            count = 0
            for card in cards:
                if card.original:
                    count += card.quantity
            return count

    def count_card_name(self, game_id, player_id, name_card):
        with Session(self.engine) as session:
            card = session.scalar(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                            PlayerCard.player_id == player_id,
                                                            PlayerCard.name_card == name_card))

            return card.quantity

    def get_cities_info(self, game_id):
        with Session(self.engine) as session:
            cities = session.scalars(select(City).where(City.game_id == game_id))
            players_name = {}
            # {city.player_id: f'{city.player_name}  :money_bag: {city.money}' for city in cities}
            for city in cities:
                if city.bot:
                    icon = self.bot_cldr
                else:
                    icon = self.human_cldr
                players_name[city.player_id] = f'{icon} {city.player_name}  :money_bag: {city.money}'
            cards_list = {player: [] for player in players_name.values()}
            all_cards = session.scalars(select(PlayerCard).where(PlayerCard.game_id == game_id))
            for card in all_cards:
                card_owner = players_name[card.player_id]
                cards_list[card_owner].append(card)
            cities_info = ''
            for player, cards in cards_list.items():
                cities_info += f'<b>{player} :</b>'
                attractions = ''
                card_in_line = 0
                cards.sort(key=lambda obj: (obj.number, obj.number_str))
                for card in cards:
                    if card.original:
                        if card.type_card == 'attraction':
                            attractions += f'[:{card.emoji_view}:]  '
                        else:
                            if card_in_line % 6 == 0:
                                cities_info += '\n'
                            card_in_line += 1
                            cities_info += f'<b>[{card.number_str}:{card.emoji_view}:]</b>x{card.quantity}    '
                if attractions:
                    cities_info += f'\n{attractions}'
                cities_info += '\n\n'
            cities_info = '<b>' + cities_info + '</b>'
            return cities_info

    def get_player_cards(self, game_id, player_id):
        session = Session(self.engine)
        cards = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                          PlayerCard.player_id == player_id))
        return cards, session

    def get_players_cards(self, game_id):
        session = Session(self.engine)
        cards = session.scalars(select(PlayerCard).where(PlayerCard.game_id == game_id))
        return cards, session

    def get_table_card(self, game_id):
        session = Session(self.engine)
        all_card = session.scalars(select(TableCard).where(TableCard.game_id == game_id))
        sorted_cards = {'blue': [], 'green': [], 'red': [], 'pink': [], 'attraction': []}
        for card in all_card:
            sorted_cards[card.type_card].append(card)
        return sorted_cards, session

    def get_cards_rolled_number(self, game_id, number):
        with Session(self.engine) as session:
            cards = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                              PlayerCard.number == number))
            return cards

    def get_city(self, game_id, player_id):
        with Session(self.engine) as session:
            city = session.scalar(select(City).filter(City.game_id == game_id, City.player_id == player_id))
            return city

    def get_red_cards(self, game_id, number):
        session = Session(self.engine)
        cards = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                          PlayerCard.number == number,
                                                          PlayerCard.type_card == 'red'))
        return cards, session

    def get_pink_card(self, game_id, number, player_id):
        session = Session(self.engine)
        cards = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                          PlayerCard.number == number,
                                                          PlayerCard.type_card == 'pink',
                                                          PlayerCard.player_id == player_id))
        return cards, session

    def get_all_cities(self, game_id):
        session = Session(self.engine)
        cities = session.scalars(select(City).where(City.game_id == game_id))
        return cities, session

    def get_blue_cards(self, game_id, number):
        session = Session(self.engine)
        cards = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                          PlayerCard.number == number,
                                                          PlayerCard.type_card == 'blue'))
        return cards, session

    def get_green_cards(self, game_id, player_id, number):
        session = Session(self.engine)
        cards = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                          PlayerCard.number == number,
                                                          PlayerCard.player_id == player_id,
                                                          PlayerCard.type_card == 'green'))
        return cards, session

    def is_trawler(self, game_id):
        with Session(self.engine) as session:
            card = session.scalar(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                            PlayerCard.name_card == 'trawler'))
            if card:
                return True

    def get_trawlers_cards(self, game_id):
        session = Session(self.engine)
        cards = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                          PlayerCard.name_card == 'trawler'))
        return cards, session

    def get_cost_card(self, card_name):
        with Session(self.engine) as session:
            card = session.scalar(select(Card).where(Card.name == card_name))
            return card.cost

    def get_card_description(self, card_name, game_id):
        with Session(self.engine) as session:
            card = session.scalar(select(Card).where(Card.name == card_name))
            card_table = session.scalar(select(TableCard).filter(TableCard.game_id == game_id,
                                                                 TableCard.name == card_name))
            description = str(card.description).replace('#', f':keycap_{card_table.quantity}:')
            description = description.replace('-', '\n  -  ').replace('*', f'\n  :{card.emoji_view}:  ')
            return description

    def get_name(self, game_id, player_id):
        with Session(self.engine) as session:
            city = session.scalar(select(City).filter(City.game_id == game_id, City.player_id == player_id))
            return city.player_name

    def is_card_in_city(self, game_id, player_id, name_card):
        with Session(self.engine) as session:
            card = session.scalar(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                            PlayerCard.player_id == player_id,
                                                            PlayerCard.name_card == name_card))
            if card:
                return True
            else:
                return False

    def add_card_to_player(self, game_id, name_card, player_id):

        with Session(self.engine) as session:
            game_session = session.scalar(select(GameSession).where(GameSession.game_id == game_id))
            if game_session.type_game == 'basic':
                count_for_win = 4
            elif game_session.type_game == 'additions':
                count_for_win = 6
            card_subject = select(TableCard).where(TableCard.game_id == game_id).where(TableCard.name == name_card)
            card = session.scalar(card_subject)
            win = False
            if not card:
                print(name_card, '   <--   it`s card !!!!!')
            if card.type_card == 'attraction':
                city = session.scalar(select(City).filter(City.player_id == player_id, City.game_id == game_id))
                city.count_attractions += 1
                session.add(city)
                if city.count_attractions == count_for_win:
                    win = True
            if card.quantity == 1:
                session.delete(card)
            else:
                card.quantity -= 1
                session.add(card)

            player_card = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                                    PlayerCard.player_id == player_id,
                                                                    PlayerCard.name_card == name_card))
            update_complete = False
            for duplicate in player_card:
                duplicate.quantity += 1
                session.add(duplicate)
                update_complete = True

            if not update_complete:
                player_card = PlayerCard(name_card=card.name, game_id=card.game_id, player_id=player_id,
                                         number=card.number, income=card.income, type_card=card.type_card,
                                         sign=card.sign, emoji_view=card.emoji_view, quantity=1,
                                         number_str=card.number_str, original=True)
                session.add(player_card)
                if card.extra_numbers:
                    for number in card.extra_numbers.split(','):
                        extra_card = PlayerCard(name_card=card.name, game_id=card.game_id, player_id=player_id,
                                                number=number, income=card.income, type_card=card.type_card,
                                                sign=card.sign, emoji_view=card.emoji_view, quantity=1,
                                                number_str=card.number_str, original=False)
                        session.add(extra_card)
            session.commit()
        return win

    def swap_cards(self, name_gift_card, name_taken_card, player_id, victim_player, game_id):
        with Session(self.engine) as session:
            cards_self = session.scalars(select(PlayerCard).filter(PlayerCard.name_card == name_gift_card,
                                                                   PlayerCard.player_id == player_id,
                                                                   PlayerCard.game_id == game_id))
            cards_other = session.scalars(select(PlayerCard).filter(PlayerCard.name_card == name_taken_card,
                                                                    PlayerCard.player_id == victim_player,
                                                                    PlayerCard.game_id == game_id))
            cards_self = [card for card in cards_self]
            cards_other = [card for card in cards_other]
            view_self_card = f':{cards_self[0].emoji_view}:'
            view_other_card = f':{cards_other[0].emoji_view}:'
            self.add_cards_office(game_id, player_id, cards_other, session)
            self.add_cards_office(game_id, victim_player, cards_self, session)
            self.delete_cards_office(game_id, player_id, cards_self, session)
            self.delete_cards_office(game_id, victim_player, cards_other, session)
            session.commit()
        name_player = self.get_name(game_id, player_id)
        name_victim = self.get_name(game_id, victim_player)
        new_story = f'\n       {name_player}  {view_self_card}  :counterclockwise_arrows_button:  ' \
                    f'{view_other_card}  {name_victim}'
        self.put_new_story(new_story, game_id)

    @staticmethod
    def add_cards_office(game_id, player_id, cards, session):
        for card in cards:
            had_card = session.scalar(select(PlayerCard).filter(PlayerCard.name_card == card.name_card,
                                                                PlayerCard.game_id == game_id,
                                                                PlayerCard.player_id == player_id,
                                                                PlayerCard.number == card.number))
            if had_card:
                had_card.quantity += 1
                session.add(had_card)
            else:
                new_card = PlayerCard(name_card=card.name_card, game_id=card.game_id, player_id=player_id,
                                      number=card.number, income=card.income, type_card=card.type_card,
                                      sign=card.sign, emoji_view=card.emoji_view, quantity=1,
                                      number_str=card.number_str, original=card.original)

                session.add(new_card)

    @staticmethod
    def delete_cards_office(game_id, player_id, cards, session):
        for card in cards:
            had_card = session.scalar(select(PlayerCard).filter(PlayerCard.name_card == card.name_card,
                                                                PlayerCard.game_id == game_id,
                                                                PlayerCard.player_id == player_id,
                                                                PlayerCard.number == card.number))
            if had_card.quantity > 1:
                had_card.quantity -= 1
                session.add(had_card)
            else:
                session.delete(had_card)

    def lock_game(self, game_id):
        with Session(self.engine) as session:
            game = session.scalar(select(GameSession).where(GameSession.game_id == game_id))
            game.lock = False
            session.add(game)
            print('lock')
            session.commit()

    def check_and_lock(self, game_id):
        with Session(self.engine) as session:
            game = session.scalar(select(GameSession).where(GameSession.game_id == game_id))
            print('check')
            if not game.lock:
                return False
            game.lock = False
            session.add(game)
            session.commit()
            print('lock')
            return True

    def unlock_game(self, game_id):
        with Session(self.engine) as session:
            game = session.scalar(select(GameSession).where(GameSession.game_id == game_id))
            try:
                game.lock = True
                session.add(game)
                print('unlock')
            except AttributeError:
                pass
            except Exception as error:
                print(error)
            session.commit()

    def is_unlock(self, game_id, player_id):
        with Session(self.engine) as session:
            game = session.scalar(select(GameSession).where(GameSession.game_id == game_id))
            print('check')
            if game.lock or game.turn_now == player_id:
                return game.turn_now

    @staticmethod
    def create_game_history_in_table(session, game_id):
        new_line = GameHistory(game_id=game_id, all_history='       :recycling_symbol::keycap_1:\n')
        session.add(new_line)

    def put_new_story(self, story, game_id):
        with Session(self.engine) as session:
            history = session.scalar(select(GameHistory).where(GameHistory.game_id == game_id))
            all_history = str(history.all_history)
            all_history += story
            if len(all_history) > 7300:
                all_history = all_history[1000:]
            history.all_history = all_history
            session.add(history)
            session.commit()

    def get_history(self, game_id):
        with Session(self.engine) as session:
            history = session.scalar(select(GameHistory).where(GameHistory.game_id == game_id))
            return history.all_history

    def test(self):
        with Session(self.engine) as session:
            tatata = session.scalar(select(PlayerCard).where(PlayerCard.id == 260))
            tatata.player_id = 2000
            obj_dict = tatata.__dict__
            del obj_dict['_sa_instance_state']
            new_obj = PlayerCard(**obj_dict)
            new_obj.id = None
            session.add(new_obj)
            session.commit()

    def delete_chat_session(self, chat_id):
        with Session(self.engine) as session:
            try:
                tables = [PlayerCard, TableCard, City, GameHistory, Audience]
                notes_of_tables = [session.scalars(select(tabl).where(tabl.game_id == chat_id)) for tabl in tables]
                chat_session = session.scalar(select(GameSession).where(GameSession.game_id == chat_id))
                messages = {chat_id: [chat_session.mess]}
                session.delete(chat_session)
                messages_session = session.scalars(select(MessagesId).where(MessagesId.game_id == chat_id))
                for mess in messages_session:
                    messages[mess.player_id] = [mess.action_1, mess.action_2]
                    session.delete(mess)
                for notes in notes_of_tables:
                    for note in notes:
                        session.delete(note)
                session.commit()
                return messages
            except AttributeError:
                return False

    def card_info_for_bot_build(self, card_name):
        with Session(self.engine) as session:
            card = session.scalar(select(Card).where(Card.name == card_name))
            return card.cost, card.emoji_view

    def type_game(self, game_id):
        with Session(self.engine) as session:
            game_session = session.scalar(select(GameSession).where(GameSession.game_id == game_id))
            return game_session.type_game, game_session.count_player

    def not_much_cafe(self, game_id, bot_id):
        with Session(self.engine) as session:
            cards_cafe = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                                   PlayerCard.name_card == 'cafe'))
            cafe_count = 0
            for cafe in cards_cafe:
                if cafe.player_id != bot_id:
                    cafe_count += cafe.quantity
            if cafe_count < 3:
                return True

    def kick_player_lobby(self, game_id, player_id):
        with Session(self.engine) as session:
            city = session.scalar(select(City).filter(City.game_id == game_id, City.player_id == player_id))
            session.delete(city)
            game_session = session.scalar(select(GameSession).where(GameSession.game_id == game_id))
            game_session.count_player -= 1
            session.add(game_session)
            session.commit()

    def get_game_last_info(self, game_id):
        with Session(self.engine) as session:
            game_session = session.scalar(select(GameSession).where(GameSession.game_id == game_id))
            return game_session.moves, game_session.laps, game_session.mess

    def is_money_other_player(self, game_id, player_id):
        with Session(self.engine) as session:
            cities = session.scalars(select(City).where(City.game_id == game_id))
            for city in cities:
                if city.player_id == player_id:
                    continue
                if city.money > 0:
                    return True
            return False

    def get_needed_numbers(self, game_id, player_id):
        with Session(self.engine) as session:
            cards = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                              PlayerCard.player_id == player_id))
            needed_numbers = {}
            for card in cards:
                if card.type_card in ['blue', 'green']:
                    card_income = card.income * card.quantity
                    if card.number in needed_numbers:
                        needed_numbers[card.number] += card_income
                    else:
                        needed_numbers[card.number] = card_income
            needed_numbers = [number for number in needed_numbers if needed_numbers[number] > 2]
            if needed_numbers:
                return needed_numbers
            else:
                return [1, 2, 3]

    def get_needed_numbers_add(self, game_id, player_id):
        with Session(self.engine) as session:
            cards = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                              PlayerCard.player_id == player_id))
            port = self.is_card_in_city(game_id, player_id, 'port')
            needed_numbers = []
            for card in cards:
                if card.type_card == 'red':
                    continue
                if card.name_card == 'tax office':
                    cities = session.scalars(select(City).where(City.game_id == game_id))
                    for city in cities:
                        if (city.player_id != player_id) and (city.money > 9):
                            needed_numbers.append(card.number)
                            break
                elif card.number > 6:
                    needed_numbers.append(card.number)
                if card.number > 11 and port:
                    needed_numbers.append(card.number - 2)
            return needed_numbers

    def get_laps_and_moves(self, game_id):
        with Session(self.engine) as session:
            game_session = session.scalar(select(GameSession).where(GameSession.game_id == game_id))
            return game_session.laps, game_session.moves

    def check_number_for_port(self, game_id, player_id):
        with Session(self.engine) as session:
            cards = session.scalars(select(PlayerCard).filter(PlayerCard.game_id == game_id,
                                                              PlayerCard.player_id == player_id))
            numbers = []
            for card in cards:
                if card.number > 11:
                    numbers.append(card.number - 2)
            return numbers

    def create_new_audience(self, game_id, user_id, user_name):
        with Session(self.engine) as session:
            audiencer = session.scalar(select(Audience).filter(Audience.game_id == game_id,
                                                               Audience.user_id == user_id))
            if audiencer:
                return False
            new_audiencer = Audience(game_id=game_id, user_id=user_id, user_name=user_name)
            session.add(new_audiencer)
            session.commit()
            return True

    def is_audience_in_lobby(self, game_id, user_id):
        with Session(self.engine) as session:
            audiencer = session.scalar(select(Audience).filter(Audience.game_id == game_id,
                                                               Audience.user_id == user_id))
            if audiencer:
                return True
            return False

    def select_all_audiences(self, game_id):
        with Session(self.engine) as session:
            audiencers = session.scalars(select(Audience).where(Audience.game_id == game_id))
            return [user for user in audiencers]

    def kick_audience_lobby(self, game_id, user_id):
        with Session(self.engine) as session:
            audiencer = session.scalar(select(Audience).filter(Audience.game_id == game_id,
                                                               Audience.user_id == user_id))
            session.delete(audiencer)
            session.commit()

    def get_all_audiencers(self, game_id):
        with Session(self.engine) as session:
            audiencers = session.scalars(select(Audience).where(Audience.game_id == game_id))
            return [user.user_id for user in audiencers]

    def is_bot(self, game_id, player_id):
        with Session(self.engine) as session:
            city = session.scalar(select(City).filter(City.game_id == game_id, City.player_id == player_id))
            return city.bot


if __name__ == '__main__':
    ...
