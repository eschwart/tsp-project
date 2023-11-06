from config import *
from data import *

from discord.ext.commands import Context, CommandError
from discord import File
from asyncio import sleep
from datetime import datetime
import matplotlib.pyplot as plt
import io


# retrieve bot env token
token = get_token()

# instantiate `Bot`
bot = init_bot()

# instantiate user data map
data = Database()


async def send_notification(user_id: int, delay: int):
    """If they have any, DM the user with the list of the user's workouts"""
    user = bot.get_user(user_id)

    while True:
        await sleep(delay)
        workouts = data.get_user(user_id).get_workouts()

        if len(workouts) > 0:
            await user.send(str(workouts))
        else:
            print("\nno workouts\n")


@bot.event
async def on_ready():
    """Used for realtime tracking of time as a background task"""
    print("Bot is online and ready.")


@bot.before_invoke
async def validate_user(ctx: Context):
    """Ensure the user is in the database before running any commands"""
    user_id: int = ctx.author.id  # id of the author of the message

    # instantiate the user if not found
    if not data.has_user(user_id):
        data.new_user(user_id)


@bot.command()
async def remind(ctx: Context, arg):
    """Set a workout reminder for the user (in seconds)"""
    try:
        delay = int(arg)  # seconds
        await send_notification(ctx.author.id, delay)
    except ValueError as e:
        await ctx.send("Please specify with a number.")


@bot.command()
async def info(ctx: Context):
    """Send user information, if applicable (all attrbutes are instantiated)"""
    user: User = data.get_user(ctx.author.id)
    height = user.get_height()
    weight = user.get_weight()

    # determine any unset attributes
    attrs = list(
        filter(
            lambda attr: attr is not None,
            [
                "height" if height is None else None,
                "weight" if weight is None else None,
            ],
        )
    )
    # determine if any attributes are unset
    if None not in attrs and len(attrs) > 0:
        # attributes as formatted strings
        attrs_fmt: str = " and ".join(map(lambda attr: f"**{attr}**", attrs))
        attrs_msg: str = "".join(
            map(lambda msg: f"\n- Use the `set_{msg} <ARG>` command.", attrs)
        )
        # send the missing required attributes
        await ctx.send(
            f"The {attrs_fmt} of {ctx.author.mention} is not set.{attrs_msg}"
        )
    else:
        # send user information
        await ctx.send(f"{ctx.author.mention}:\n- Height: {height}\n- Weight: {weight}")


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
async def set_height(ctx: Context, arg):
    """Set the current height of the user"""
    user = data.get_user(ctx.author.id)
    user.set_height(arg)
    await ctx.send("Done.")


@bot.command()
async def set_weight(ctx: Context, arg):
    """Set the current weight of the user"""
    user = data.get_user(ctx.author.id)
    dt = ctx.message.created_at
    user.set_weight(dt, int(arg))
    await ctx.send("Done.")


# TODO: figure out how we want to structure the food/calorie system
@bot.command()
async def add_food(ctx: Context, name, calories):
    """Add a food item with its number of calories for the user"""
    user = data.get_user(ctx.author.id)

    try:
        calories = int(calories)
        user.add_food(name, calories)
        await ctx.send("Done.")
    except ValueError as e:
        await ctx.send("Please indicate a number value for calories.")


# TODO: finish implementing `User::add_workout``
@bot.command()
async def add_workout(ctx: Context, arg):
    """If it doesn't already exist, add the workout for the user"""
    user = data.get_user(ctx.author.id)

    if arg in user.get_workouts():
        await ctx.send("Workout already exists.")
    else:
        user.add_workout(arg)
        await ctx.send("Done.")


@bot.command()
async def workouts(ctx: Context):
    """List the workouts for the user. If the cooresponding button is pressed, remove that workout"""
    user = data.get_user(ctx.author.id)  # the user
    workouts = user.get_workouts()  # the workouts of the user

    if len(workouts) > 0:
        # format the workouts into a numbered list
        msg_sfx = "".join([f"\n{i}. {s}" for i, s in enumerate(workouts, 1)])
        await ctx.send(f"Here is {ctx.author.mention}'s workout schedule:{msg_sfx}")
    else:
        await ctx.send(f"{ctx.author.mention} has nothing planned.")
#bargraph of data
# TODO: create a bar graph of users weight 
@bot.command()
async def graph(ctx: Context):
    user = data.get_user(ctx.author.id)
    userWeights = user.records
    
    

    dates = [dt_as_str(x[0]) for x in userWeights]
    weights = [x[1] for x in userWeights]

    """MANUAL DATA ENTRY FOR DEMONSTRATION"""
    dates.insert(0,'07/27/2003')
    weights.insert(0,5)


    dates.insert(1,'07/27/2010')
    weights.insert(1,85)

    weight_beginning = weights[0]
    weight_end = weights[-1]
   
    print(dates, weights)

    if weight_beginning < weight_end:
        comparison_message= 'You have gained weight!'
        print(comparison_message)
    elif weight_beginning > weight_end:
        comparison_message= 'You have lost weight!'
        print(comparison_message)
    else:
        comparison_message='You are the same'
        print(comparison_message)


        
    plt.xlabel('Date')
    plt.ylabel('Weight(in pounds)')
    
    plt.bar(dates,weights)
    plt.title(f'{ctx.author}\'s Weight Over Time - {comparison_message}')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.ylim(0, weight_end + 5)
   
   
    # Save the bar graph as a PNG file
    plt.savefig("weight_graph.png")
    
    plt.close()  # Close the plot to free resources

    # Send the saved PNG file as an attachment on Discord
    with open("weight_graph.png", "rb") as file:
        file_data = io.BytesIO(file.read())
        await ctx.send(file=File(file_data, "weight_graph.png"))
    
    

# Good base for reminders
# TODO: have it track in real-time for direct message reminders
# TODO: adjust for different time zones
@bot.command()
async def time(ctx: Context):
    # timestamp of the user's message
    cnt = ctx.message.created_at.timestamp()

    # send the timestamp as a Short Time styled unix timestamp
    await ctx.send(f"<t:{int(cnt)}:t>")

    print(cnt.strftime("%m/%d/%Y"))


# Debugging
@bot.command()
async def dm(ctx: Context):
    """Send a message to the user"""
    await ctx.message.author.send(f"Hello, {ctx.author}!")


# Debugging
@bot.command()
async def ping(ctx: Context):
    """Send a reply message with the latency in milliseconds"""
    await ctx.send(f"pong `{int(ctx.bot.latency * 1000)} ms`")


# run the bot
bot.run(token)
