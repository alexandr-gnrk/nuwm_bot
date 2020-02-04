
# Telegram bot
Telegram Bot that helps [NUWM](http://nuwm.edu.ua/ "NUWM") students view their schedule.

## Stack
- Python3
- SQLite
- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy/)
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI "pyTelegramBotAPI")
- [NUWM schedule API](http://calc.nuwm.edu.ua:3002/ "NUWM schedule API")

## Setup
Clone the repository and change the working directory:

    git clone https://github.com/alexandr-gnrk/nuwm_bot.git
    cd nuwm_bot
Create and activate the virtual environment:

    python3 -m venv ./venv
    source ./venv/bin/activate
Install requirements:

    pip3 install -r requirements.txt
Set an environment variable, with your token received from [BotFather](https://t.me/BotFather):

    export NUWM_TELEGRAM_BOT_TOKEN=<YOUR_TOKEN>
Run the bot:

    python3 bot.py
