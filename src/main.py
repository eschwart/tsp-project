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


async def ask_question(ctx: Context, question: str) -> str | None:
    """Helper Function for asking questions"""
    await ctx.send(question)
    try:
        response = await bot.wait_for(
            "message", check=lambda message: message.author == ctx.author, timeout=60
        )
        return response.content
    except TimeoutError:
        await ctx.send("Time's up! Please answer within 60 seconds.")
        return None


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
async def send_notification(ctx: Context, delay):
    """If they have any, DM the user with the list of the user's workouts"""
    user = data.get_user(ctx.author.id)

    try:
        delay = int(delay)
    except ValueError as e:
        await ctx.author.send("Please provide a valid number.")
        return

    while True:
        await sleep(delay)
        workouts = user.get_workouts()

        if len(workouts) > 0:
            await ctx.author.send(", ".join(map(lambda w: str(w), workouts)))
        else:
            await ctx.author.send("You currently have no workouts.")
            break


@bot.command()
async def remind(ctx: Context, time: int, *, msg):
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


@bot.command()
async def set_cals(ctx: Context, arg):
    """Set the current calorie maintenance of the user"""

    try:
        arg = int(arg)
    except ValueError as e:
        await ctx.send("Provide a valid number.")
        return

    user = data.get_user(ctx.author.id)
    user.set_cal_goal(arg)

    await ctx.send("Done.")


@bot.command()
async def calc_cals(ctx: Context):
    """In order to calculate calories we need to ask the user for various statistics"""
    user = data.get_user(ctx.author.id)
    await ctx.send(
        "In order to calculate your Base Metobolic Rate (BMR) I need to ask you a series of questions"
    )
    "Are you male or female?"
    Gender = await ask_question(ctx, "Are you male 'M' or Female 'F'")

    Height = await ask_question(
        ctx,
        "How tall are you in Feet? ie: " "4.5" " where 4 is feet and .5 is 6 inches",
    )
    numHeight = int(float(Height)) * 30.49
    "Weight"
    Weight = await ask_question(ctx, "How much do you weigh in lbs?")
    numWeight = int(float(Weight)) / 2.2
    "Age"
    Age = await ask_question(ctx, "How old are you?")
    numAge = int(float(Age))

    if Gender == "M":
        cals = int((10 * numWeight + 6.25 * numHeight - 5 * numAge + 5) * 1.2)
        user.set_cal_goal(cals)

        await ctx.send(
            f"{cals} is your caloric maitnence, remember to add your daily exercise using s.burn_cals in order to eat more!"
        )
    elif Gender == "F":
        cals = int((10 * numWeight + 6.25 * numHeight - 5 * numAge - 161) * 1.2)
        user.set_cal_goal(cals)

        await ctx.send(
            f"{cals} is your caloric maitnence, remember to add your daily exercise using s.burn_cals in order to eat more!"
        )
    else:
        await ctx.send(
            "You have to pick one or the other this is a "
            "science based"
            " calculator  XD "
        )


@bot.command()
async def eat_cals(ctx: Context, foodname: int | str):
    """Eat specified calories from the user's maintenance"""
    user = data.get_user(ctx.author.id)

    if user.get_cal_goal() == 0:
        await ctx.send("Please set your calorie maintenance first using !set_cals.")
    elif type(foodname) == int:
        user.burn_cals(int(foodname))
        await ctx.send("Done.")
    else:
        food = user.get_food(foodname.capitalize())
        if food != None:
            user.burn_cals(food.calories)
            await ctx.send("Food Eaten")
        else:
            await ctx.send("Food is not in list")


@bot.command()
async def burn_cals(ctx: Context, arg):
    """burn specified calories from the user's maintenance"""
    user = data.get_user(ctx.author.id)

    try:
        arg = int(arg)
    except ValueError as e:
        await ctx.send("Provide a valid number.")
        return

    if user.get_cal_goal() == 0:
        await ctx.send("Please set your calorie maintenance first using !set_cals.")
    else:
        user.burn_cals(arg)
        await ctx.send("Done.")


@bot.command()
async def show_cals(ctx: Context):
    """Show the remaining calories for the user"""
    user = data.get_user(ctx.author.id)

    if user.get_cal_goal() == 0:
        await ctx.send("Please set your calorie maintenance first using !set_cals.")
        return

    remaining_cals = user.get_cals()
    cal_goal = user.get_cal_goal()
    ratio = float(remaining_cals) / float(cal_goal)

    if ratio < 1.0:
        await ctx.send(
            f"You have consumed {int(ratio * 100)}% of your daily goal of {cal_goal}, you are still in a calorie deficit on the day"
        )

    else:
        await ctx.send(
            f"You have consumed {int(ratio * 100)}% completed with your daily goal of {cal_goal}, you are now eating in a surplus and this will lead to weight gain "
        )


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


@bot.command()
async def remove_food(ctx: Context, foodName: str):
    """Remove a food"""
    try:
        user = data.get_user(ctx.author.id)
        boolcheck = user.remove_food(foodName.capitalize())
        if boolcheck == True:
            await ctx.send("Food Removed")
        if boolcheck == False:
            await ctx.send("Food Not Removed")
    except ValueError as e:
        await ctx.send("Please indicate a Name for the food")


@bot.command()
async def add_workout(
    ctx: Context,
    name: str,
    RepWeight: int | None,
    Reps: int | None,
    PRweight: int | None,
):
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
        await ctx.send(
            "Please indicate a Name, then if wanted add RepWeight, Reps, and PR Weight for the workout."
        )


@bot.command()
async def workouts(ctx: Context):
    """Returns a list of workouts"""
    user = data.get_user(ctx.author.id)  # the user
    workouts = user.get_workouts()

    if len(workouts) > 0:
        workstring = ""
        for i in workouts:
            workstring += (
                i.name
                + " "
                + str(i.RepW)
                + " "
                + str(i.Reps)
                + " "
                + str(i.PRweight)
                + ",\n"
            )
        if workstring != "":
            await ctx.send(workstring)
    else:
        await ctx.send(f"{ctx.author.mention} has nothing planned.")


@bot.command()
async def remove_workout(ctx: Context, workoutName: str):
    """Remove a workout"""
    try:
        user = data.get_user(ctx.author.id)
        boolcheck = user.remove_workout(workoutName.capitalize())
        if boolcheck == True:
            await ctx.send("Workout Removed")
        if boolcheck == False:
            await ctx.send("Workout Not Removed")
    except ValueError as e:
        await ctx.send("Please indicate a Name for the workout")


@bot.command()
async def graph(ctx: Context):
    """Provide the user with a bar-graph of their data"""
    user = data.get_user(ctx.author.id)
    userWeights = user.records

    dates = [dt_as_str(x[0]) for x in userWeights]
    weights = [x[1] for x in userWeights]

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
                fields = ["Name", "Rep Weight", "Reps", "PR Weight"]
                csvwriter.writerow(fields)
                for i in workouts:
                    tempinfo = [i.name, i.RepW, i.Reps, i.PRweight]
                    csvwriter.writerow(tempinfo)
            elif arg2.lower() == "foods":
                foods = user.get_foods()
                fields = ["Name", "Calories"]
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
                    workstring += (
                        i.name
                        + " "
                        + str(i.RepW)
                        + " "
                        + str(i.Reps)
                        + " "
                        + str(i.PRweight)
                        + ",\n"
                    )
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
async def ping(ctx: Context):
    """Send a reply message with the latency in milliseconds"""
    await ctx.send(f"pong `{int(ctx.bot.latency * 1000)} ms`")


# run the bot
bot.run(token)
