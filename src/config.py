from os import environ
from discord import Intents
from discord.ext.commands import Bot


TOKEN_KEYWORD: str = "TRENFREN_TOKEN"
COMMAND_PREFIX: str = "s."


def get_token() -> str:
    """If it exists, retrieve the discord token from the user's environmental variables"""
    token = environ.get(TOKEN_KEYWORD)

    if token is None:
        exit(f"Missing `{TOKEN_KEYWORD}` variable")
    else:
        return token


def init_bot():
    """Instantiate a Discord Bot with a simple default configuration"""
    intents = Intents().all()
    bot = Bot(command_prefix=COMMAND_PREFIX, intents=intents)
    return bot
