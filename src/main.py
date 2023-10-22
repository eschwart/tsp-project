from data import *
from bot import *

# retrieve bot env token
token = get_token()
if token == None:
    exit("Missing `TOKEN` variable")

# instantiate `Bot`
bot = init_bot()


@bot.command()
async def set_height(ctx, arg):
    pass

@bot.command()
async def set_weight(ctx, arg):
    pass

@bot.command()
async def add_food(ctx, arg):
    pass

@bot.command()
async def add_workout(ctx, *, args):
    pass


# debugging purposes
@bot.command()
async def ping(ctx):
    await ctx.send('pong')


bot.run(token)