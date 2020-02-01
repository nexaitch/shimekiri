# Shimekiri – A simple deadline tracking telegram bot

A simple deadline tracking telegram bot written using [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot) and `sqlite3`.

## Getting Started

### Prerequisites

Tested using the following python packages

```
python-telegram-bot==12.3.0
dateparser==0.7.2
pytz==2019.3
Babel==2.8.0

```

### How to Run

- Get a bot API token using BotFather
- Set up your database using `sqlite3` (default filename `kiri.db`)
- Make a copy of `example_config.json` named `config.json` and update the API token/timezone/locale/database filename
- Run `python bot.py`

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
