import discord 
def welcome_embed():
    embed = discord.Embed(title="Welcome to VoiceBot",
                        description="Here are some commands you should know about:", )

    embed.add_field(name="/balance",
                    value="to check the remaining amount in your account.", inline=False)
    embed.add_field(name="/clear",
                    value="to delete all previous conversation.", inline=False)
    embed.add_field(name="/help",
                    value="to check the remaining amount in your account.", inline=False)
    embed.add_field(name="To continue, Please make a payment",
                    value=".....", inline=False)
    embed.add_field(name="🌸 Mini",
                    value="5 minutes of \naudio responses for \n**$5**",
                    inline=True)
    embed.add_field(name="🔥 Spark",
                    value="10 minutes of \naudio responses for \n**$10**",
                    inline=True)
    embed.add_field(name="❤️ Classic",
                    value="15 minutes of \naudio responses for \n**$15**",
                    inline=True)
    embed.add_field(name="💎 Pro",
                    value="25 minutes of \naudio responses for \n**$25**",
                    inline=True)
    embed.add_field(name="⭐ Ultimate",
                    value="Custom minutes of \naudio responses for \n**<$50**",
                    inline=True)
    embed.set_footer(text="For any questions, suggestions or reports, feel free to contact us at: astralabsai@protonmail.com")
    return embed
def balance_embed():
    embed_repay = discord.Embed(title="Your balance is **0$**",
                        description="To continue, Please make a payment", )
    embed_repay.add_field(name="🌸 Mini",
                    value="5 minutes of \naudio responses for \n**$5**",
                    inline=True)
    embed_repay.add_field(name="🔥 Spark",
                    value="10 minutes of \naudio responses for \n**$10**",
                    inline=True)
    embed_repay.add_field(name="❤️ Classic",
                    value="15 minutes of \naudio responses for \n**$15**",
                    inline=True)
    embed_repay.add_field(name="💎 Pro",
                    value="25 minutes of \naudio responses for \n**$25**",
                    inline=True)
    embed_repay.add_field(name="⭐ Ultimate",
                    value="Custom minutes of \naudio responses for \n**<$50**",
                    inline=True)
    embed_repay.set_footer(text="For any questions, suggestions or reports, feel free to contact us at: astralabsai@protonmail.com")
    return embed_repay
def help_embed():

  
    embed_help = discord.Embed(title="Welcome to Astra Labs", description="To get started you need to deposit funds in your account.")

    # Add fields to the embed_help
    embed_help.add_field(name="/help",
                    value="Well, you just used it! This command shows you a list of available commands and how to use them.",
                    inline=False)
    embed_help.add_field(name="/balance",
                    value="Use this command to check the current balance in your account. Don't forget to keep an eye on it to ensure we can keep chatting without any interruptions.",
                    inline=False)
    embed_help.add_field(name="/clear",
                    value="Feeling like starting fresh? This command clears the chat history with me.",
                    inline=False)
    embed_help.add_field(name="/preference",
                    value="You have the power to choose how I respond to you! Use this command to switch between 'ChatGPT mode' and 'LLM mode' for roleplay. Each mode has its own charm, so feel free to explore!",
                    inline=False)
    embed_help.add_field(name="/mode",
                    value="You have the power to choose the format you want the response in! Use this command to switch between 'Voice mode' and 'Text mode' for response.",
                    inline=False)
    embed_help.add_field(name="/regenerate",
                    value="Delete the last response and message from history, So you can rewrite the query and i can generate fresh response.",
                    inline=False)
    # Add a blank field to create space
    embed_help.add_field(name="\u200b", value="\u200b", inline=False)
    # Add a footer for contact information
    embed_help.set_footer(text="For any questions, suggestions or reports, feel free to contact us at: astralabsai@protonmail.com")
    return embed_help