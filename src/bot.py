from os import environ
from discord import Intents, Bot
from discord.ext import commands


def get_token() -> str:
    return environ.get("TOKEN")

def init_bot() -> Bot:
    intents = Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='s.', intents=intents)
    return bot