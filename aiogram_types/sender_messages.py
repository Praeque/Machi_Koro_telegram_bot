from aiogram.utils.exceptions import RetryAfter, MessageNotModified
from asyncio import sleep
from aiogram import Bot
from aiogram.types import CallbackQuery


class MessageSender:

    def __init__(self, bot: Bot):
        self.bot = bot

    async def edit_message_this_chat(self, text, call: CallbackQuery, number=0, markup=None):
        try:
            await self.bot.edit_message_text(text, call.message.chat.id, call.message.message_id + number,
                                             reply_markup=markup, parse_mode='html')
        except RetryAfter as error:
            print('Flood Control!  Sleep:', error.timeout, 'second')
            await sleep(error.timeout)
            await self.edit_message_this_chat(text, call, number, markup)
        except MessageNotModified:
            print('Message has not been changed')
        except Exception as error:
            print(error)
            print(text)

    async def edit_message(self, text, chat_id, message_id, markup=None):
        try:
            await self.bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode='html')
        except RetryAfter as error:
            print('Flood Control!  Sleep:', error.timeout, 'second')
            await sleep(error.timeout)
            await self.edit_message(text, chat_id, message_id, markup)
        except MessageNotModified:
            print('Message has not been changed')
        except Exception as error:
            print(error)
            print(text)

    async def edit_markup(self, call: CallbackQuery, markup, number=0):
        try:
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id + number,
                                                     reply_markup=markup)
        except RetryAfter as error:
            print('Flood Control!  Sleep:', error.timeout, 'second')
            await sleep(error.timeout)
            await self.edit_markup(call, markup, number)
        except MessageNotModified:
            print('Markup has not been changed!')
        except Exception as error:
            print(error)

    async def edit_message_try(self, text, call: CallbackQuery, number=0, markup=None):
        try:
            await self.bot.edit_message_text(text, call.message.chat.id, call.message.message_id + number,
                                             reply_markup=markup, parse_mode='html')
        except RetryAfter as error:
            print('Flood Control!  Need wait!:', error.timeout, 'second')
        except MessageNotModified:
            print('Message has not been changed!')
        except Exception as error:
            print(error)
            print(text)

    async def edit_markup_try(self, call: CallbackQuery, markup, number=0):
        try:
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id + number,
                                                     reply_markup=markup)
        except RetryAfter as error:
            print('Flood Control!  Need wait!:', error.timeout, 'second')
        except MessageNotModified:
            print('Markup has not been changed!')
        except Exception as error:
            print(error)

    async def send_message(self, chat_id, text, markup=None):
        try:
            mess = await self.bot.send_message(chat_id, text, parse_mode='html', reply_markup=markup)
            print(mess.message_id)
            return mess
        except Exception as error:
            print(error)
            await sleep(1)
            return await self.send_message(chat_id, text)

    async def delete_message(self, chat_id, message_id):
        try:
            await self.bot.delete_message(chat_id, message_id)
        except Exception as error:
            print(error)

