import discord
from discord.ext import commands

from karen.evaluate import evaluate
from karen.getCombo import *
from karen.output import Output
from karen.parameters import *

import random

import os
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN") # save your bot token as an environment variable or paste it here

intents = discord.Intents.default()
intents.guild_messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

COMMAND_LOG = {}

# Dev channel runs commands if and only if the build is run in dev mode
DEV_SERVER = int(os.getenv("DEV_SERVER"))
DEV_CHANNEL = int(os.getenv("DEV_CHANNEL"))
DEV_BUILD = bool(os.getenv("DEV_BUILD"))
def developmentFilter(ctx):
    return bool(ctx.guild.id == DEV_SERVER and ctx.channel.id == DEV_CHANNEL) ^ bool(DEV_BUILD)

def logCommand(command, ctx, inputString):
    if not ctx.guild in COMMAND_LOG:
        COMMAND_LOG[ctx.guild] = {}
    if not ctx.channel in COMMAND_LOG[ctx.guild]:
        COMMAND_LOG[ctx.guild][ctx.channel] = []
    
    COMMAND_LOG[ctx.guild][ctx.channel].append(f"{str(ctx.author).replace("\\", "\\\\").replace("_", "\_").replace("*", "\*")} sent \"{command} {inputString}\"")
    if len(COMMAND_LOG[ctx.guild][ctx.channel]) > 5:
        COMMAND_LOG[ctx.guild][ctx.channel] = COMMAND_LOG[ctx.guild][ctx.channel][-5:]

@bot.command()
async def eval(ctx, *arr):
    if developmentFilter(ctx):
        return
    inputString = " ".join(str(x) for x in arr)
    warnings = []
    inputString, params = splitParameters(inputString, warnings)
    output = evaluate(inputString, params, warnings)
    await output.printToDiscord(ctx=ctx, color=0x8C7FFF)
    logCommand("!eval", ctx, inputString)

@bot.command()
async def combo(ctx, *arr):
    if developmentFilter(ctx):
        return
    inputString = " ".join(str(x) for x in arr)
    warnings = []
    inputString, params = splitParameters(inputString, warnings)
    output = getCombo(inputString, params, warnings)
    await output.printToDiscord(ctx=ctx, color=0x0094FF)
    logCommand("!combo", ctx, inputString)

@bot.command()
async def combos(ctx, *arr):
    if developmentFilter(ctx):
        return
    inputString = " ".join(str(x) for x in arr)
    warnings = []
    inputString, params = splitParameters(inputString, warnings)
    output = listCombos(inputString, params, warnings)
    await output.printToDiscord(ctx=ctx, color=0x0094FF)
    logCommand("!combos", ctx, inputString)

@bot.command()
async def report(ctx, *arr):
    if developmentFilter(ctx):
        return
    reportMessage = " ".join(str(x) for x in arr)

    title = "Report Sent"
    description = "Thank you for your help. The report message that was sent can be seen below."
    block = ""
    error = ""

    if reportMessage.replace(" ", "") == "":
        error = "Please include a report description"

    elif ctx.guild in COMMAND_LOG and ctx.channel in COMMAND_LOG[ctx.guild]:
        reportHeading = f"## Report from {str(ctx.author).replace("\\", "\\\\").replace("_", "\_").replace("*", "\*")}"
        reportBody = f"**Server:** {ctx.guild}\n**Channel:** {ctx.channel}\n**Message:** {reportMessage}\n\n**Command log:**\n{"\n".join([f"{x}" for x in COMMAND_LOG[ctx.guild][ctx.channel]])}"
        description = reportBody
        
        try:
            dev = await bot.fetch_user(os.getenv("DEV_ID"))
            await dev.send(f"{reportHeading}\n{reportBody}")
        except Exception as e:
            print(e)
            error = "Report failed to send. Try again later, or reach out via DM to the developer, @evilduck_"

    else:
        error="No commands have been logged in this channel since Karen last rebooted"
    
    output = Output(title=title, description=description, block=block, error=error)
    output.printToDiscord(ctx=ctx, color=0x77C6FF)

@bot.command()
async def help(ctx, *arr):
    if developmentFilter(ctx):
        return
    command = "none" if len(arr) == 0 else arr[0]
    
    title = "Karen Help Desk"
    description = ""
    
    embed = discord.Embed(title="Karen Help Desk", description="", color=discord.Color(0x77C6FF))
    embed.set_footer(text=f"requested by {ctx.author}", icon_url=ctx.author.avatar)

    if command.lower() in ["eval", "!eval"]:
        description = "**!eval [combo sequence]**\nThe *evaluate* command takes a combo sequence as input, and evaluates the minimum time taken to execute the combo, as well as the damage dealt. This command automatically corrects common input mistakes - for more complete control, use \"--a\".\n\nExamples of combo sequences include \"tGu\", \"t goht upper\", or \"tracer > get over here targeting > uppercut\" (these are all equivalent). For a more complete description of combo notation, [see the documentation](https://github.com/EvilDuck14/Karen/)."
    
    elif command.lower() in ["combo", "!combo"]:
        description = "**!combo [combo name]**\nThe *combo* command runs \"!evala\" on a combo given its name. For a list of all documented combo names, use \"!combos\"."

    elif command.lower() in ["combos", "!combos"]:
        description = "**!combos**\nThe *combos* command prints a list of all documented combos, as well as their short-form notations. These are the labels added when a known command is evaluated, and these names can be passed into the \"!combo\" command."

    elif command.lower() in ["report", "!report"]:
        description = "**!report [report message]**\nThe *report* command sends a message to the bot developer (EvilDuck), along with last 5 commands issued in this channel. This is for reporting bugs/crashes, please don't spam it or use it before checking whether the unexpected output is caused by user error. Reports are not anonymous."

    elif command.lower() in ["help", "!help"]:
        descriptions = [ "The *help* command displays a detailed description of a given command. If no command is given, it instead lists all commands, giving brief descriptions." ] * 10 + [
            "Come on... you can figure this one out.",
            "The fact that you've made it here tells me you already know what this one does.",
            "Look at you go. You nailed it.",
            "You can use this to explain to someone what a command does when you don't want to explain it yourself.",
            "Are you looking for an easter egg? Well, you found it.",
        ]
        description = f"**!help [command]**\n{random.choice(descriptions)}"

    else:
        description += "**!eval [combo sequence]**\n"
        description += "Evaluates the time taken & damage dealt by a given combo.\n\n"

        description += "**!evala [combo sequence]**\n"
        description += "\"Advanced\" version of \"!eval\".\n\n"

        description += "**!evaln [combo sequence]**\n"
        description += "\"No warnings\" version of \"!evala\".\n\n"

        description += "**!combo [combo name]**\n"
        description += "Runs evaluation of a given combo.\n\n"

        description += "**!combos**\n"
        description += "Displays a list of all documented combos.\n\n"

        description += "**!report [report message]**\n"
        description += "Reports an issue to the bot developer.\n\n"

        description += "**!help [command]**\n"
        description += "Explains the given command in greater detail.\n\n"

        description = description[:-2] # removes trailing new lines

    output = Output(title=title, description=description)
    await output.printToDiscord(ctx=ctx, color=0x77C6FF)


@bot.command()
async def test(ctx, *arr):
    print(ctx.guild)
    print(ctx.channel)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        await bot.tree.sync()
        print(f"successfully connected to {len(bot.guilds)} servers")
    except Exception as e:
        print(e)
    

bot.run(BOT_TOKEN)