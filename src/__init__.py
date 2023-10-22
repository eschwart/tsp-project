from discord import Intents
from discord.ext import commands
from os import environ


intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='s.', intents=intents)


class User():
    def __init__(calories: int, height: int, weight: int):
        self.calories = calories,
        self.height = height,
        self.weight = weight


user_data = {}

@bot.command()
async def ping(ctx, arg1, arg2):
    await ctx.send('pong')


@bot.command()
async def track(ctx, arg):
    calories_intake[ctx.author] = int(arg)
    await ctx.send("Done")


bot.run(environ["TOKEN"])