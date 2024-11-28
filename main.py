import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import json

bot = commands.Bot(".", intents=discord.Intents.all(), help_command=None)

# Change this value to 0 if you don't want a fixed rate.
fixedrate = 25

# How much exp is given to the user when they send a message
expgiven = 5


# Create a users folder if it doesn't exist

if not os.path.exists("users"):
    os.makedirs("users")



async def expUp(message, expincrease):
    global expneeded
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
        
        expneeded = fixedrate - userdata["exp"]
        if userdata["level"] != userdata["totalexp"] // fixedrate:
            # Level up
            userdata["level"] = (userdata["totalexp"] // fixedrate)

            # Make the level up embed
            levelembed = discord.Embed(title="**Level Up!**", description=f"**<@{userid}> has levelled up to level {userdata["level"]}\n\nExp needed for next level**: {fixedrate}")
            levelembed.set_thumbnail(url=message.author.avatar)
            levelembed.set_footer(text=bot.user.name, icon_url=bot.user.avatar)
            
            userdata["exp"] = 0
            await message.channel.send(embed=levelembed)
            
    else:  # Exp needed increases for every level
        
        baserate = 30

        expneeded = baserate * ((userdata["level"] + 1) * 2)
        if userdata["level"] != userdata["totalexp"] // expneeded:
            # Level up
            userdata["level"] = userdata["totalexp"] // expneeded
            
            # Make the level up embed
            levelembed = discord.Embed(title="**Level Up!**", description=f"<@{userid}> has levelled up to level {userdata["level"]}\n\nExp needed for next level: {baserate * ((userdata["level"] + 1) * 2)}")
            levelembed.set_thumbnail(url=message.author.avatar)
            levelembed.set_footer(text=bot.user.name, icon_url=bot.user.avatar)

            await message.channel.send(embed=levelembed)
            userdata["exp"] = 0

    # Write to the json file
    with open(f"users/{userid}.json", "w") as file:
        json.dump(userdata, file)
    pass


def fetchLevelLeaderboard():
    leaderboard = []
    for files in os.listdir("users/"):
        with open(f"users/{files}", "r") as file:
            global userdata
            userdata = json.load(file)
            leaderboard.append({"level": int(userdata["level"]), "userid": int(file.name.replace("users/", "").replace(".json", ""))})
            
            
    leaderboard.sort(reverse=True,key=lambda x: x["level"])
    print(leaderboard)
    
    leaderboardembed = discord.Embed(title="Level Leaderboard")
    
    placement = 0
    for value in leaderboard:
        placement+=1
        leaderboardembed.add_field(name=f"{placement}.", value=f"<@{int(value["userid"])}>: {value["level"]}", inline=False)
        
    leaderboardembed.set_thumbnail(url=bot.user.avatar)
    leaderboardembed.set_footer(text=bot.user.name, icon_url=bot.user.avatar)
            
    return leaderboardembed



def fetchExpLeaderboard():
    leaderboard = []
    for files in os.listdir("users/"):
        with open(f"users/{files}", "r") as file:
            global userdata
            userdata = json.load(file)
            leaderboard.append({"totalexp": int(userdata["totalexp"]), "userid": int(file.name.replace("users/", "").replace(".json", ""))})
            
            
    leaderboard.sort(reverse=True,key=lambda x: x["totalexp"])
    print(leaderboard)
    
    leaderboardembed = discord.Embed(title="EXP Leaderboard")
    
    placement = 0
    for value in leaderboard:
        placement+=1
        leaderboardembed.add_field(name=f"{placement}.", value=f"<@{int(value["userid"])}>: {value["totalexp"]}", inline=False)
        
    leaderboardembed.set_thumbnail(url=bot.user.avatar)
    leaderboardembed.set_footer(text=bot.user.name, icon_url=bot.user.avatar)
            
    return leaderboardembed


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author.id != bot.user.id:
        await expUp(message, expgiven)
    
    
    await bot.process_commands(message)
    

@bot.command("level")
async def self(ctx):
    userid = ctx.message.author.id
    with open(f"users/{userid}.json", "r") as file:
        userdata = json.load(file)    
        
        levelembed = discord.Embed(title="**Level Information**", description=f"Current Level: **{userdata["level"]}**\n\nCurrent EXP: **{userdata["exp"]}**\nEXP Needed: **{expneeded}**\n\nTotal EXP: **{userdata["totalexp"]}**")
        
        levelembed.set_thumbnail(url=ctx.message.author.avatar)
        levelembed.set_footer(text=bot.user.name, icon_url=bot.user.avatar)
        
        await ctx.send(embed=levelembed)


@bot.command("giveexp")
async def self(ctx, member:discord.User, exp:int):
    await expUp(ctx.message, exp)
    await ctx.send(f"Gave <@{member.id}> {exp} EXP!")
    
@bot.command("leaderboard")
async def self(ctx, choice = ""):
    if choice.lower() == "level":
        await ctx.send(embed=fetchLevelLeaderboard())
    elif choice.lower() == "totalexp":
        await ctx.send(embed=fetchExpLeaderboard())
    else:
        await ctx.send("Invalid choice! Please enter 'level' or 'totalexp'!")
    
# Start the bot.
load_dotenv()
bot.run(os.getenv("TOKEN"))
