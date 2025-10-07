import discord
from discord.ext import commands

WARNING_COLOR = 0xB73A00

class Output:
    title = ""
    link = ""
    combo = ""
    description = ""
    block = ""
    warnings = []
    error = ""

    def __init__(self, title="", link="", combo="", description="", block="", warnings="", error=""):
        self.title = title
        self.link = link
        self.combo = combo
        self.description = description
        self.block = block
        self.warnings = warnings
        self.error = error

    def printToConsole(self):
        
        # Error message - overrides other output
        if self.error != "":
            print("ERROR: " + self.error)
            return

        # Formatting message
        message = ""

        if self.title != "":        
            message += f"{self.title}{f"({self.link})" if self.link != "" else ""}\n\n"

        if self.combo != "":
            message += f"{self.combo}\n\n"

        if self.description != "":
            message += f"{self.description}\n\n"

        if self.block != "":
            message += f"{self.block}\n\n"
        
        message = message[:-2] # remove trailing newlines
        
        # Warning Message
        if len(self.warnings) > 0:
            warningMessage = "\n\n" + "\n".join([f"WARNING: {warning}" for warning in self.warnings])
            message += warningMessage

        print(message)

    async def printToDiscord(self, ctx, color):
        
        # Formatting main message
        message = ""

        if self.title != "":
            title = self.title
            if self.link != "":
                title = f"[{title}]({self.link})"
            message += f"### {title}\n"

        if self.combo != "":
            message += f"> {self.combo}\n"

        if self.description != "":
            message += f"{self.description}\n"

        if self.block != "":
            message += f"```\n{self.block}\n```\n"
        
        message = message[:-1] # remove trailing newline

        if len(message) > 4000 and self.error == "":
            self.error == "combo content is too long for Discord message limit (4000 characters)"

        # Error message - overrides other output
        if self.error != "":
            errorMessage = "**ERROR:** " + self.error
            errorEmbed = discord.Embed(title="", description=errorMessage, color=discord.Color(WARNING_COLOR))
            try:
                await ctx.send(embed=errorEmbed)
            except Exception as e:
                print(e)
            return
        
        # Main message
        messageEmbed = discord.Embed(title="", description=message, color=discord.Color(color))
        messageEmbed.set_footer(text=f"requested by {ctx.author}", icon_url=ctx.author.avatar)
        try:
            await ctx.send(embed=messageEmbed)
        except Exception as e:
            print(e)

        # Warning Message
        if len(self.warnings) > 0:
            warningMessage = "\n".join([f"**WARNING:** {warning}" for warning in self.warnings])
            if len(warningMessage) > 4000:
                warningMessage = warningMessage[:3995]
                if warningMessage[-1] != "\n":
                    warningMessage += "\n"
                warningMessage += "..."
            warningEmbed = discord.Embed(title="", description=warningMessage, color=discord.Color(WARNING_COLOR))
            try:
                await ctx.send(embed=warningEmbed)
            except Exception as e:
                print(e)