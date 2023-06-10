"""    If you want to try, it`s easy :

1. Step:
    You need to get the TELEGRAM_BOT_TOKEN , if you don't have it, go to https://t.me/BotFather.

2.Step:
    in the '.env'  file, insert your TOKEN  -->  TELEGRAM_BOT_TOKEN='YOR_BOT_TOKEN'

3.Step:
    Write command in terminal:
        pip install -r requirements.txt

Installation completed!

4.Step:
    run this file --> 'main.py'

5.Step:
    Open telegram, and write to your bot, the command:
        how_to_play

* Available languages now only Russian

"""


if __name__ == '__main__':

    from telegram_bot import run_bot

    run_bot()
