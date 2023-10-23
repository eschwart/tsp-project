from config import *
from data import *

# retrieve bot env token
token = get_token()
if token == None:
    exit("Missing `TOKEN` variable")

# instantiate `Bot`
bot = init_bot()

# instantiate user data map
data = Database()


@bot.command()
async def set_height(ctx, arg):
    user = data.get_user(ctx.author.id)
    user.set_height(arg)
    await ctx.send("Done!")

@bot.command()
async def get_height(ctx):
    user = data.get_user(ctx.author.id)
    await ctx.send(f"Height of {ctx.author}: {user.height}")

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


# run the bot
bot.run(token)