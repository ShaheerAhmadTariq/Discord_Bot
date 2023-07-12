import bot

if __name__ == '__main__':
    bot.run_discord_bot()
# import discord
# import os
# import openai

# # Discord bot token
# TOKEN = "MTEyNzU2MjkzNDkwNjgwMjIxNg.GETg2p.-psmll_Sys4IrMLRHJrvLSXyyjj4ZfuhTi6zqM"

# # OpenAI API credentials
# # OPENAI_API_KEY = "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"
# # openai.api_key = OPENAI_API_KEY
# # Create a Discord client
# client = discord.Client()

# # # OpenAI ChatGPT API configuration
# # openai.ChatCompletion.create(
# #     model="gpt-3.5-turbo",
# #     messages=[
# #         {"role": "system", "content": "You are a helpful assistant."},{"role": "user", "content": ".."}]
# # )

# # Event: Bot is ready
# @client.event
# async def on_ready():
#     print(f"We have logged in as {client.user.name} - {client.user.id}")

# # Event: Message received
# @client.event
# async def on_message(message):
#     # Ignore messages from the bot itself
#     # if message.author == client.user:
#     #     return

#     # # Pass user message to ChatGPT for response
#     # chat_response = openai.ChatCompletion.create(
#     #     model="gpt-3.5-turbo",
#     #     messages=[
#     #         {"role": "system", "content": "You are a helpful assistant."},
#     #         {"role": "user", "content": message.content}
#     #     ]
#     # )

#     # Send the ChatGPT response to the Discord channel
#     # await message.channel.send(chat_response.choices[0].message.content)
#     await message.channel.send("Hello World") 

# # Run the Discord bot
# client.run(TOKEN)
