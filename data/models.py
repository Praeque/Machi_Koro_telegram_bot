from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String


class Base(DeclarativeBase):
    pass


class Description(Base):

    __tablename__ = 'description'

    id: Mapped[int] = mapped_column(primary_key=True)
    topic: Mapped[str]
    description: Mapped[str]

    def str(self):
        return f'description  {self.topic})'


class Card(Base):

    __tablename__ = 'card'

    name: Mapped[str] = mapped_column(primary_key=True)
    number: Mapped[int]
    income: Mapped[int]
    cost: Mapped[int]
    extra_numbers: Mapped[str] = mapped_column(nullable=True)
    type_card: Mapped[str]
    sign: Mapped[str] = mapped_column(nullable=True)
    emoji_view: Mapped[str]
    quantity: Mapped[int]
    number_str: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str]
    type_game: Mapped[str]


class TableCard(Base):

    __tablename__ = 'table_card'

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int]
    name: Mapped[str]
    number: Mapped[int]
    income: Mapped[int]
    extra_numbers: Mapped[str] = mapped_column(nullable=True)
    type_card: Mapped[str]
    sign: Mapped[str] = mapped_column(nullable=True)
    emoji_view: Mapped[str]
    quantity: Mapped[int]
    number_str: Mapped[str] = mapped_column(nullable=True)


class PlayerCard(Base):

    __tablename__ = 'player_card'

    id: Mapped[int] = mapped_column(primary_key=True)
    name_card: Mapped[str]
    game_id: Mapped[int]
    player_id: Mapped[int]
    number: Mapped[int]
    income: Mapped[int]
    type_card: Mapped[str]
    sign: Mapped[str] = mapped_column(nullable=True)
    emoji_view: Mapped[str]
    quantity: Mapped[int]
    number_str: Mapped[str] = mapped_column(nullable=True)
    original: Mapped[bool]


class City(Base):

    __tablename__ = 'city'

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int]
    player_id: Mapped[int]
    player_name: Mapped[str]
    money: Mapped[int]
    count_attractions: Mapped[int]
    turn: Mapped[int]
    bot: Mapped[bool]


class GameSession(Base):

    __tablename__ = 'game_session'

    game_id: Mapped[int] = mapped_column(primary_key=True)
    count_player: Mapped[int]
    turn_now: Mapped[int]
    duple: Mapped[bool]
    lock: Mapped[bool]
    mess: Mapped[int]
    type_game: Mapped[str] = mapped_column(nullable=True)
    moves: Mapped[int]
    laps: Mapped[int]


class GameHistory(Base):

    __tablename__ = 'game_history'

    game_id: Mapped[int] = mapped_column(primary_key=True)
    all_history: Mapped[str] = mapped_column(String(10000))


class MessagesId(Base):

    __tablename__ = 'messages_id'

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int]
    player_id: Mapped[int]
    history: Mapped[int]
    cities: Mapped[int]
    action_1: Mapped[int]
    action_2: Mapped[int]


class Audience(Base):

    __tablename__ = 'audience'
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int]
    user_id: Mapped[int]
    user_name: Mapped[str]


if __name__ == '__main__':

    from sqlalchemy import create_engine

    engine = create_engine('sqlite:///data/data.db')
    Base.metadata.create_all(bind=engine)
