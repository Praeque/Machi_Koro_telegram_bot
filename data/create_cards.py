# -*- coding: utf-8 -*-
from data.models import Card
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


class AddCard:

    engine = create_engine('sqlite:///data/data.db')

    descriptions = {'wheat field': '*Пшеничное поле-Доход  1  :dollar_banknote:-Стоимость постройки'
                                   '  1  :money_with_wings:-Приносит доход, когда выпадает :game_die: 1  '
                                   '<u>в ход любого игрока</u>-Работает с  :herb:-Наличие предприятий  #',
                    'bakery': '*Пекарня-Доход  1  :dollar_banknote:-Стоимость постройки  '
                              '1  :money_with_wings:-Приносит доход, когда выпадает :game_die: 2 или 3  <u>'
                              'в ваш ход</u>-Вид предприятия   <u>Магазин :balance_scale:</u>-Наличие предприятий  #',
                    'farm': '*Ферма-Доход  1  :dollar_banknote:-Стоимость постройки  '
                            '1  :money_with_wings:-Приносит доход, когда выпадает :game_die: 2  '
                            '<u>в ход любого игрока</u>-Работает с  :cow_face:-Наличие предприятий  #',
                    'store': '*Круглосуточный магазин-Доход  3  :dollar_banknote:-Стоимость постройки  '
                              '2  :money_with_wings:-Приносит доход, когда выпадает :game_die: 4  '
                              '<u>в ваш ход</u>-Вид предприятия   <u>Магазин :balance_scale:</u>-Наличие предприятий  #',
                    'forest': '*Лес-Доход  1  :dollar_banknote:-Стоимость постройки  '
                              '3  :money_with_wings:-Приносит доход, когда выпадает :game_die: 5  '
                              '<u>в ход любого игрока</u>-Работает с  :gear:-Наличие предприятий  #',
                    'train station': '*Вокзал-Стоимость постройки  4  :money_with_wings:'
                                     '-Дает возможность кидать 2 кубика :game_die::game_die:',
                    'port': '*Порт-Стоимость постройки  2  :money_with_wings:-Дает возможность добавлять '
                            '+2 к сделанному броску:, если на кубиках выпало  :game_die::game_die: 10 или больше'
                            '-  +1 добавить нельзя, только +2',
                    'airport': '*Аэропорт-Стоимость постройки  30  :money_with_wings:-Если вы пропускаете ход, '
                               'ничего не построив, то получаете +10 :dollar_banknote:',
                    'shopping mall': '*Торговый центр-Стоимость постройки  10  :money_with_wings:'
                                     '-Вы получаете на 1 :dollar_banknote: больше за работу каждого :balance_scale:'
                                     '  и   :fork_and_knife_with_plate:-Так же в случае :fork_and_knife_with_plate:'
                                     ' вы и забираете на 1 :dollar_banknote: больше, у другого игрока',
                    'amusement park': '*Парк с аттракционами-Стоимость постройки  16  :money_with_wings:'
                                     '-Когда вы выбрасываете дубль, вы делаете еще один ход-Это будет полноценных ход:'
                                      ' как бросок кубика так и строительство.',
                    'radio tower': '*Радиовышка-Стоимость постройки  22  :money_with_wings:'
                                     '-Один раз за ход вы можете перебросить кубики :game_die::game_die:'
                                   ':counterclockwise_arrows_button:',
                    'mine': '*Шахта-Доход  5  :dollar_banknote:-Стоимость постройки  '
                              '6  :money_with_wings:-Приносит доход, когда выпадает :game_die::game_die: 9  '
                              '<u>в ход любого игрока</u>-Работает с  :gear:-Наличие предприятий  #',
                    'apple orchard': '*Яблочный сад-Доход  3  :dollar_banknote:-Стоимость постройки'
                                   '  3  :money_with_wings:-Приносит доход, когда выпадает :game_die::game_die: 10  '
                                   '<u>в ход любого игрока</u>-Работает с :herb:-Наличие предприятий  #',
                    'cheese factory': '*Сыроварня-Доход  3  :dollar_banknote: за каждый :cow_face:'
                                      '-Стоимость постройки  5  :money_with_wings:-Приносит доход, когда выпадает'
                                      ' :game_die::game_die: 7  <u>в ваш ход</u>-Наличие предприятий  #',
                    'furniture factory': '*Мебельная фабрика-Доход  3  :dollar_banknote: за каждый '
                                         ':evergreen_tree: и :mountain:'
                                      '-Стоимость постройки  3  :money_with_wings:-Приносит доход, когда выпадает'
                                      ' :game_die::game_die: 8  <u>в ваш ход</u>-Наличие предприятий  #',
                    'produce market': '*Продуктовый рынок-Доход  2  :dollar_banknote: за каждый  :sheaf_of_rice: , '
                                      ' :tulip:  и  :red_apple:-Стоимость постройки  2  :money_with_wings:'
                                      '-Приносит доход, когда выпадает :game_die::game_die: 11 или 12 '
                                      ' <u>в ваш ход</u>-Наличие предприятий  #',
                    'cafe': '*Кафе-Получаете  1 :dollar_banknote: от игрока который бросил :game_die:  3'
                            '-Стоимость постройки  2  :money_with_wings:-Приносит доход, только <u>в ход других'
                            ' игроков</u>-Наличие предприятий  #',
                    'restaurant': '*Ресторан-Получаете  2 :dollar_banknote: от игрока который бросил :game_die: '
                                  ':game_die:  9 ил 10-Стоимость постройки  3  :money_with_wings:-Приносит доход, '
                                  'только <u>в ход других игроков</u> -Наличие предприятий  #',
                    'stadium': '*Стадион-Получаете  2 :dollar_banknote: от каждого игрока когда выпадает'
                               ' :game_die: 6  <u>в ваш ход</u>-Стоимость постройки  6  :money_with_wings:'
                               '-Может быть только один Стадион в городе',
                    'tv station': '*Телевизионная Станция-Выберете одного игрока у которого вы заберете  5'
                                  ' :dollar_banknote:-Срабатывает когда выпадает'
                               ' :game_die: 6  <u>в ваш ход</u>-Стоимость постройки  7  :money_with_wings:'
                                  '-Может быть только одна Телевизионная Станция в городе',
                    'office': '*Офис-Вы обмениваетесь одним предприятием которые вы выберете, с выбранным вами игроком'
                              '-Вы можете выбирать любые предприятия, не считая Достопримечательности и Крупные'
                              ' предприятия-Срабатывает когда выпадает :game_die: 6  <u>в ваш ход</u>'
                              '-Стоимость постройки  8  :money_with_wings:-Может быть только один Офис в городе',
                    'flower garden': '*Цветник-Доход  1  :dollar_banknote:-Стоимость постройки'
                                   '  2  :money_with_wings:-Приносит доход, когда выпадает :game_die: 4  '
                                   '<u>в ход любого игрока</u>-Работает с  :herb:  и  :bouquet:-Наличие предприятий  #',
                    'flower shop': '*Цветочный магазин-Доход  1  :dollar_banknote: за каждый  :tulip:'
                                   '-Стоимость постройки  1  :money_with_wings:-Приносит доход, когда выпадает'
                                   ' :game_die:  6 <u>в ваш ход</u>-Вид предприятия   <u>Магазин :balance_scale:</u>'
                                   '-Наличие предприятий  #',
                    'food storage': '*Склад продовольствия-Доход  2  :dollar_banknote: за каждое заведения общепита'
                                    ' :fork_and_knife_with_plate:-Стоимость постройки  2  :money_with_wings:'
                                    '-Приносит доход, когда выпадает :game_die::game_die: 12 или 13  '
                                    '<u>в ваш ход</u>-Наличие предприятий  #',
                    'pizzeria': '*Пиццерия-Получаете  1 :dollar_banknote: от игрока который бросил :game_die::game_die:'
                                '  7-Стоимость постройки  1  :money_with_wings:-Приносит доход, только <u>в ход других'
                            ' игроков</u>-Наличие предприятий  #',
                    'diner': '*Закусочная-Получаете  1 :dollar_banknote: от игрока который бросил :game_die:'
                             ':game_die:  8-Стоимость постройки  1  :money_with_wings:-Приносит доход, только <u>в '
                             'ход других игроков</u>-Наличие предприятий  #',
                    'sushi bar': '*Суси бар-<u>Работает только если у вас есть "Порт" !</u>'
                                 '-Получаете  3 :dollar_banknote: от игрока который бросил :game_die:  1'
                                 '-Стоимость постройки  2  :money_with_wings:-Приносит доход, только <u>в ход других'
                                 ' игроков</u>-Наличие предприятий  #',
                    'fishing launch': '*Рыбацкий баркас-<u>Работает только если у вас есть "Порт" !</u>'
                                      '-Доход  3  :dollar_banknote:-Стоимость постройки'
                                   '  2  :money_with_wings:-Приносит доход, когда выпадает :game_die: :game_die: 8   '
                                   '<u>в ход любого игрока</u>-Наличие предприятий  #',
                    'trawler': '*Траулер-<u>Работает только если у вас есть "Порт" !</u>-Если выпадает :game_die:'
                               ':game_die: 12, 13 или 14, тогда активный игрок еще раз бросает 2 кубика  :game_die:'
                               ':game_die: и каждый у кого есть "Траулер" получает столько  :dollar_banknote:,'
                               ' сколько выпало на кубиках  :game_die::game_die:, <u>работает в ход любого игрока</u>'
                               '-Стоимость постройки  5  :money_with_wings: -Наличие предприятий  #',
                    'tax office': '*Налоговая Инспекция-Вы забираете половину :dollar_banknote: у всех у кого больше 10'
                                  ' :dollar_banknote: в казне  :money_bag:-Срабатывает когда выпадает'
                               ' :game_die::game_die: 8 или 9  <u>в ваш ход</u>-Стоимость постройки  4  '
                                  ':money_with_wings:-Может быть только одна Налоговая Инспекция в городе',
                    'publisher': '*Издательство-Вы забираете 1 :dollar_banknote: у каждого игрока за каждый их '
                                  ' :balance_scale: и  :fork_and_knife_with_plate:-Срабатывает когда выпадает'
                               ' :game_die::game_die: 7  <u>в ваш ход</u>-Стоимость постройки  5  :money_with_wings:'
                                  '-Может быть только одно Издательство в городе',



                    }
    all_card = [
        {'name': 'wheat field', 'number': 1, 'income': 1, 'cost': 1, 'extra_numbers': None, 'type_card': 'blue',
         'sign': 'fruit', 'emoji_view': 'sheaf_of_rice', "quantity": 6, 'number_str': '1', 'type_game': 'basic'},
        {'name': 'bakery', 'number': 2, 'income': 1, 'cost': 1, 'extra_numbers': '3', 'type_card': 'green',
         'sign': 'shop', 'emoji_view': 'bread', "quantity": 6, 'number_str': '2-3', 'type_game': 'basic'},
        {'name': 'farm', 'number': 2, 'income': 1, 'cost': 1, 'extra_numbers': None, 'type_card': 'blue',
         'sign': 'milk', 'emoji_view': 'cow_face', "quantity": 6, 'number_str': '2', 'type_game': 'basic'},
        {'name': 'store', 'number': 4, 'income': 3, 'cost': 2, 'extra_numbers': None, 'type_card': 'green',
         'sign': 'shop', 'emoji_view': 'convenience_store', "quantity": 6, 'number_str': '4', 'type_game': 'basic'},
        {'name': 'forest', 'number': 5, 'income': 1, 'cost': 3, 'extra_numbers': None, 'type_card': 'blue',
         'sign': 'mechanical', 'emoji_view': 'evergreen_tree', "quantity": 6, 'number_str': '5', 'type_game': 'basic'},
        {'name': 'port', 'number': 0, 'income': 0, 'cost': 2, 'extra_numbers': None, 'type_card': 'attraction',
         'sign': 'special', 'emoji_view': 'anchor', "quantity": 6, 'number_str': None, 'type_game': 'additions'},
        {'name': 'train station', 'number': 0, 'income': 0, 'cost': 4, 'extra_numbers': None, 'type_card': 'attraction',
         'sign': 'special', 'emoji_view': 'station', "quantity": 6, 'number_str': None, 'type_game': 'basic'},
        {'name': 'shopping mall', 'number': 0, 'income': 0, 'cost': 10, 'extra_numbers': None, 'type_card': 'attraction',
         'sign': 'special', 'emoji_view': 'kaaba', "quantity": 6, 'number_str': None, 'type_game': 'basic'},
        {'name': 'amusement park', 'number': 0, 'income': 0, 'cost': 16, 'extra_numbers': None, 'type_card': 'attraction',
         'sign': 'special', 'emoji_view': 'ferris_wheel', "quantity": 6, 'number_str': None, 'type_game': 'basic'},
        {'name': 'radio tower', 'number': 0, 'income': 0, 'cost': 22, 'extra_numbers': None, 'type_card': 'attraction',
         'sign': 'special', 'emoji_view': 'satellite_antenna', "quantity": 6, 'number_str': None, 'type_game': 'basic'},
        {'name': 'airport', 'number': 0, 'income': 0, 'cost': 30, 'extra_numbers': None, 'type_card': 'attraction',
         'sign': 'special', 'emoji_view': 'airplane', "quantity": 6, 'number_str': None, 'type_game': 'additions'},
        {'name': 'mine', 'number': 9, 'income': 5, 'cost': 6, 'extra_numbers': None, 'type_card': 'blue',
         'sign': 'mechanical', 'emoji_view': 'mountain', "quantity": 6, 'number_str': '9', 'type_game': 'basic'},
        {'name': 'apple orchard', 'number': 10, 'income': 3, 'cost': 3, 'extra_numbers': None, 'type_card': 'blue',
         'sign': 'fruit', 'emoji_view': 'red_apple', "quantity": 6, 'number_str': '10', 'type_game': 'basic'},
        {'name': 'cheese factory', 'number': 7, 'income': 3, 'cost': 5, 'extra_numbers': None, 'type_card': 'green',
         'sign': 'factory', 'emoji_view': 'cheese_wedge', "quantity": 6, 'number_str': '7', 'type_game': 'basic'},
        {'name': 'furniture factory', 'number': 8, 'income': 3, 'cost': 3, 'extra_numbers': None, 'type_card': 'green',
         'sign': 'factory', 'emoji_view': 'gear', "quantity": 6, 'number_str': '8', 'type_game': 'basic'},
        {'name': 'produce market', 'number': 11, 'income': 2, 'cost': 2, 'extra_numbers': '12', 'type_card': 'green',
         'sign': 'factory', 'emoji_view': 'herb', "quantity": 6, 'number_str': '11-12', 'type_game': 'basic'},
        {'name': 'cafe', 'number': 3, 'income': 1, 'cost': 2, 'extra_numbers': None, 'type_card': 'red',
         'sign': 'cook', 'emoji_view': 'hot_beverage', "quantity": 6, 'number_str': '3', 'type_game': 'basic'},
        {'name': 'restaurant', 'number': 9, 'income': 2, 'cost': 3, 'extra_numbers': '10', 'type_card': 'red',
         'sign': 'cook', 'emoji_view': 'steaming_bowl', "quantity": 6, 'number_str': '9-10', 'type_game': 'basic'},
        {'name': 'stadium', 'number': 6, 'income': 2, 'cost': 6, 'extra_numbers': None, 'type_card': 'pink',
         'sign': 'special', 'emoji_view': 'stadium', "quantity": 6, 'number_str': '6', 'type_game': 'basic'},
        {'name': 'tv station', 'number': 6, 'income': 5, 'cost': 7, 'extra_numbers': None, 'type_card': 'pink',
         'sign': 'special', 'emoji_view': 'television', "quantity": 6, 'number_str': '6', 'type_game': 'basic'},
        {'name': 'office', 'number': 6, 'income': 0, 'cost': 8, 'extra_numbers': None, 'type_card': 'pink',
         'sign': 'special', 'emoji_view': 'briefcase', "quantity": 6, 'number_str': '6', 'type_game': 'basic'},
        {'name': 'flower garden', 'number': 4, 'income': 1, 'cost': 2, 'extra_numbers': None, 'type_card': 'blue',
         'sign': 'fruit', 'emoji_view': 'tulip', "quantity": 6, 'number_str': '4', 'type_game': 'additions'},
        {'name': 'flower shop', 'number': 6, 'income': 1, 'cost': 1, 'extra_numbers': None, 'type_card': 'green',
         'sign': 'shop', 'emoji_view': 'bouquet', "quantity": 6, 'number_str': '6', 'type_game': 'additions'},
        {'name': 'food storage', 'number': 12, 'income': 2, 'cost': 2, 'extra_numbers': '13', 'type_card': 'green',
         'sign': 'factory', 'emoji_view': 'package', "quantity": 6, 'number_str': '12-13', 'type_game': 'additions'},
        {'name': 'pizzeria', 'number': 7, 'income': 1, 'cost': 1, 'extra_numbers': None, 'type_card': 'red',
         'sign': 'cook', 'emoji_view': 'pizza', "quantity": 6, 'number_str': '7', 'type_game': 'additions'},
        {'name': 'diner', 'number': 8, 'income': 1, 'cost': 1, 'extra_numbers': None, 'type_card': 'red',
         'sign': 'cook', 'emoji_view': 'hot_dog', "quantity": 6, 'number_str': '8', 'type_game': 'additions'},
        {'name': 'sushi bar', 'number': 1, 'income': 3, 'cost': 2, 'extra_numbers': None, 'type_card': 'red',
         'sign': 'cook', 'emoji_view': 'sushi', "quantity": 6, 'number_str': '1', 'type_game': 'additions'},
        {'name': 'fishing launch', 'number': 8, 'income': 3, 'cost': 2, 'extra_numbers': None, 'type_card': 'blue',
         'sign': 'boat', 'emoji_view': 'sailboat', "quantity": 6, 'number_str': '8', 'type_game': 'additions'},
        {'name': 'trawler', 'number': 15, 'income': 1, 'cost': 5, 'extra_numbers': None, 'type_card': 'blue',
         'sign': 'boat', 'emoji_view': 'passenger_ship', "quantity": 6, 'number_str': '12-14', 'type_game': 'additions'},
        {'name': 'tax office', 'number': 8, 'income': 5, 'cost': 4, 'extra_numbers': '9', 'type_card': 'pink',
         'sign': 'special', 'emoji_view': 'heavy_dollar_sign', "quantity": 6, 'number_str': '8-9', 'type_game': 'additions'},
        {'name': 'publisher', 'number': 7, 'income': 1, 'cost': 5, 'extra_numbers': None, 'type_card': 'pink',
         'sign': 'special', 'emoji_view': 'printer', "quantity": 6, 'number_str': '7', 'type_game': 'additions'},



    ]

    def create_all_card(self):
        for card in self.all_card:
            card['description'] = self.descriptions[card['name']]
            try:
                with Session(self.engine) as session:
                    new_line = Card(**card)
                    session.add(new_line)
                    session.commit()
            except Exception as ex:
                print(ex)


if __name__ == '__main__':
    AddCard().create_all_card()

