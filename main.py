import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import json

bot = commands.Bot(".", intents=discord.Intents.all(), help_command=None)

fixedrate = 0  # 25


async def expUp(message, expincrease):
    userid = message.author.id

    # Create a file for a user if they do not have one
    if not os.path.isfile(f"users/{userid}.json"):
        with open(f"users/{userid}.json", "w") as file:
            data = {"totalexp": 0, "exp": 0, "level": 0}

            json.dump(data, file)
            print(f"Created JSON for user {userid}!")

    # Get exp
    with open(f"users/{userid}.json", "r") as file:
        global userdata
        userdata = json.load(file)

    userdata["totalexp"] += expincrease
    userdata["exp"] += expincrease

    # How much exp it takes for the user to level up (the default value is 25 exp per level)
    if fixedrate != 0:
        if userdata["totalexp"] % fixedrate == 0:
            # Level up
            if userdata["exp"] == fixedrate:
                userdata["level"] = userdata["totalexp"]

            await message.channel.send(
                f"{message.author.mention} has leveled up to level {userdata["level"]}!"
            )
            userdata["exp"] = 0
    else:  # Exp needed increases for every level
        global expneeded
        baserate = 30

        expneeded = baserate * ((userdata["level"] + 1) * 2)

        if userdata["exp"] % expneeded == 0:
            # Level up
            if userdata["exp"] == expneeded:
                userdata["level"] += 1
            await message.channel.send(
                f"{message.author.mention} has leveled up to level {userdata["level"]}!"
            )
            userdata["exp"] = 0

    # Write to the json file
    with open(f"users/{userid}.json", "w") as file:
        json.dump(userdata, file)
    pass


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author.id != bot.user.id:
        await expUp(message, 5)
    pass


# Start the bot.
load_dotenv()
bot.run(os.getenv("TOKEN"))
