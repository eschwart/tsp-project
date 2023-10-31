from config import *
from data import *

# retrieve bot env token
token = get_token()

# instantiate `Bot`
bot = init_bot()

# instantiate user data map
data = Database()


@bot.before_invoke
async def validate_user(ctx: Context):
    """Ensure the user is in the database before running any commands"""
    user_id: int = ctx.author.id  # id of the author of the message

    # instantiate the user if not found
    if not data.has_user(user_id):
        data.new_user(user_id)


@bot.command()
async def get_height(ctx: Context):
    """Send the current height of the user"""
    user = data.get_user(ctx.author.id)
    msg = f"Height of {ctx.author.mention}: `{user.get_height()}`"
    await ctx.send(msg)


@bot.command()
async def get_weight(ctx: Context):
    """Send the current weight of the user"""
    user = data.get_user(ctx.author.id)
    msg = f"Weight of {ctx.author.mention}: `{user.get_weight()}`"
    await ctx.send(msg)


@bot.command()
async def set_height(ctx, arg):
    """Set the current height of the user"""
    user = data.get_user(ctx.author.id)
    user.set_height(arg)
    await ctx.send("Done")


@bot.command()
async def set_weight(ctx, arg):
    """Set the current weight of the user"""
    user = data.get_user(ctx.author.id)
    user.set_weight(arg)
    await ctx.send("Done")


# TODO: figure out how we want to structure the food/calorie system
@bot.command()
async def add_food(ctx, item, calories):
    """Add a food item with its number of calories for the user"""
    pass


# TODO: implement `User::add_workout``
@bot.command()
async def add_workout(ctx, *, args):
    """Add a workout for the user"""
    pass


# Debugging
@bot.command()
async def ping(ctx: Context):
    """Send a reply message with the latency in milliseconds"""
    await ctx.send(f"pong `{int(ctx.bot.latency * 1000)} ms`")


# run the bot
bot.run(token)
