# local imports
from config import *
from data import *

# discord imports
from discord.ext.commands import Context, CommandError
from discord import File

# matplotlib import
import matplotlib.pyplot as plt

# std imports
from asyncio import sleep
from io import BytesIO
from io import StringIO
from csv import writer, reader


# retrieve bot env token
token = get_token()

# instantiate `Bot`
bot = init_bot()

# instantiate user data map
data = Database()

#TODO: Broken
@bot.command()
async def send_notification(user_id: int, delay: int):
    """If they have any, DM the user with the list of the user's workouts"""
    user = bot.get_user(user_id)

    while True:
        await sleep(delay)
        workouts = data.get_user(user_id).get_workouts()

        if len(workouts) > 0:
            workstring = ""
            for i in workouts:
                workstring += i.name + i.RepW + i.Reps + i.PRweight + ",\n"
            if workstring != "":
                await user.send(workstring)
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
async def remind(ctx, time: int, *, msg):
    """Set a workout reminder for the user (in seconds)"""
    try:
        await sleep(int(time))
        await ctx.send(f"{msg}, {ctx.author.mention}")
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
async def add_food(ctx: Context, name: str, calories):
    """Add a food item with its number of calories for the user if it doesn't exist"""
    user = data.get_user(ctx.author.id)

    try:
        calories = int(calories)
        name = name.capitalize()
        if user.get_food(name) == None:
            user.add_food(name, calories)
            await ctx.send("Done.")
        else:
            await ctx.send("Food has already been added to list")
    except ValueError as e:
        await ctx.send("Please indicate a number value for calories.")


@bot.command()
async def get_food(ctx: Context, name: str):
    """Return a food item with its number of calories for the user if it exists"""
    user = data.get_user(ctx.author.id)
    try:
        name = name.capitalize()
        food = user.get_food(name)

        if food != None:
            await ctx.send(f"{food.name} has {food.calories} calories.")
        else:
            await ctx.send("There is no food with that name")
    except ValueError as e:
        await ctx.send("Please indicate a name for food.")


# TODO: Check if text prints correctly
@bot.command()
async def get_foods(ctx: Context):
    """Return all food items with its number of calories for the user"""
    user = data.get_user(ctx.author.id)
    try:
        foodstring = ""
        Foods = user.get_foods()
        for i in Foods:
            foodstring += i.name + " " + str(i.calories) + ",\n"
        if foodstring != "":
            await ctx.send(foodstring)
        else:
            await ctx.send("No food items currently added")
    except ValueError as e:
        await ctx.send(
            "Unknown error"
        )  # unless the for loop throws an error shouldn't need this.


# TODO: finish implementing `User::add_workout``
@bot.command()
async def add_workout(ctx: Context, name: str, RepWeight: int|None, Reps: int|None, PRweight:int|None):
    """If it doesn't already exist, add the workout for the user"""
    user = data.get_user(ctx.author.id)

    try:
        name = name.capitalize()

        if user.get_workout(name) == None:
            user.add_workout(name, RepWeight, Reps, PRweight)
            await ctx.send("Done.")
        else:
            await ctx.send("Workout has already been added to list")
    except ValueError as e:
        await ctx.send("Please indicate a Name, then if wanted add RepWeight, Reps, and PR Weight for the workout.")


#TODO comment says to remove workout if button is pressed. Needs to be done after rewrite.
@bot.command()
async def workouts(ctx: Context):
    """List the workouts for the user. If the cooresponding button is pressed, remove that workout"""
   
    """ workouts = user.get_workouts()  # the workouts of the user
    if len(workouts) > 0:
        # format the workouts into a numbered list
        msg_sfx = "".join([f"\n{i}. {s}" for i, s in enumerate(workouts, 1)])
        await ctx.send(f"Here is {ctx.author.mention}'s workout schedule:{msg_sfx}") """
    
    user = data.get_user(ctx.author.id)  # the user
    workouts = user.get_workouts()

    if len(workouts) > 0:
        workstring = ""
        for i in workouts:
            workstring += i.name + " " + str(i.RepW) + " " + str(i.Reps) + " " + str(i.PRweight) + ",\n"
        if workstring != "":
            await ctx.send(workstring)
    else:
        await ctx.send(f"{ctx.author.mention} has nothing planned.")


@bot.command()
async def graph(ctx: Context):
    """Provide the user with a bar-graph of their data"""
    user = data.get_user(ctx.author.id)
    userWeights = user.records

    dates = [dt_as_str(x[0]) for x in userWeights]
    weights = [x[1] for x in userWeights]

    ### manual data entry for demo ###########
    dates.insert(0, "07/27/2003")
    weights.insert(0, 5)

    dates.insert(1, "07/27/2010")
    weights.insert(1, 85)
    ##########################################

    weight_beginning = weights[0]
    weight_end = weights[-1]

    if weight_beginning < weight_end:
        comparison_message = "You have gained weight!"
    elif weight_beginning > weight_end:
        comparison_message = "You have lost weight!"
    else:
        comparison_message = "You are the same"

    plt.xlabel("Date")
    plt.ylabel("Weight(in pounds)")

    plt.bar(dates, weights)
    plt.title(f"{ctx.author}'s Weight Over Time - {comparison_message}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.ylim(0, weight_end + 5)

    # save the bar graph as a PNG file
    plt.savefig("weight_graph.png")

    # read the file into `file_data`
    with open("weight_graph.png", "rb") as file:
        file_data = BytesIO(file.read())
        file.close()

    # send the PNG file as an attachment
    await ctx.send(file=File(file_data, "weight_graph.png"))


#TODO: csv output needs to be finished.
@bot.command()
async def output(ctx: Context, arg1: str, arg2: str):
    """List the workouts for the user. If the cooresponding button is pressed, remove that workout"""
    user = data.get_user(ctx.author.id)  # the user
    dmuser = ctx.message.author
    try:

        if arg1.lower() == "csv":
            temp = StringIO()
            csvwriter = writer(temp)
            if arg2.lower() == "workouts":
                workouts = user.get_workouts()
                fields = ['Name', 'Rep Weight', 'Reps', 'PR Weight']
                csvwriter.writerow(fields)
                for i in workouts:
                    tempinfo = [i.name, i.RepW, i.Reps, i.PRweight]
                    csvwriter.writerow(tempinfo)
            elif arg2.lower() == "foods":
                foods = user.get_foods()
                fields = ['Name', 'Calories']
                csvwriter.writerow(fields)
                for i in foods:
                    tempinfo = [i.name, i.calories]
                    csvwriter.writerow(tempinfo)
            else:
                await ctx.send("Please specify workouts or foods")
                return
            await dmuser.send(file=File(StringIO(temp.getvalue()), "output.csv"))
        
        elif arg1.lower() == "text":
            if arg2.lower() == "workouts":
                workouts = user.get_workouts()
                workstring = ""
                for i in workouts:
                    workstring += i.name + " " + str(i.RepW) + " " + str(i.Reps) + " " + str(i.PRweight) + ",\n"
                await dmuser.send(file=File(StringIO(workstring), "output.txt"))
            elif arg2.lower() == "foods":
                foods = user.get_foods()
                foodstring = ""
                for i in foods:
                    foodstring += i.name + " " + str(i.calories) + ",\n"
                await dmuser.send(file=File(StringIO(foodstring), "output.txt"))
            else:
                await ctx.send("Please specify workouts or foods")
                return  
        else:
            await ctx.send("Please specify text or csv")

    except ValueError as e:
        await ctx.send("Please input output format and workouts or foods")

# Debugging
@bot.command()
async def time(ctx: Context):
    # timestamp of the user's message
    cnt = ctx.message.created_at.timestamp()

    # send the timestamp as a Short Time styled unix timestamp
    await ctx.send(f"<t:{int(cnt)}:t>")


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
