import os
import time
import discord
import random
from discord.ext import commands, tasks 
from datetime import datetime, timedelta
from discord import app_commands
from free_trial import free_response
from discord.ui import Button, View
from local_llm import generate_response, regenerate_message_llm
from embed_messages import welcome_embed
from chain import chain_setup, get_chain_response
# from chain_ import get_chain_response
# from doc_memory_chain import chain_setup, get_chain_response

from embed_messages import welcome_embed, help_embed, balance_embed
from text_to_speech import get_audio
from transcribe_audio import oga_2_mp3_2_text
from util import is_subscription_active 
from helpers import check_if_user_exists, create_cache_history, add_user_to_user_json, get_conversation_history, delete_cache_history, delete_last_message_cache_history
from database import save_message_to_db, connect_to_db, create_user, get_user, update_user, update_user_time, delete_message_history, save_preferences_to_db, get_preferences, change_preferences, save_message_llm_to_db, change_voice, update_user_time, create_user_free, get_user_free, update_user_free, create_or_update_user_extra, get_user_extras
TOKEN = os.environ.get('TOKEN')

intents = discord.Intents.all()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

async def send_message_llm(user):
    # if check_if_user_exists(user.author.id):
    #     print(f"{user.author.id} send message")
    response = await generate_response(user)
    return response
    # else:
    #     print(f"{user.author.id} send message for first time")
    #     create_cache_history(user.author.id)
    #     add_user_to_user_json(user.author.id)
    #     # return await ctx.response.send_message("You have already set your character", ephemeral=True)
    #     return "welcome_embed"
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {synced} slash commands.")
    except Exception as e:
        print(e)

predefined_messages = ["Hey there! It's been a day since we chatted. Want to catch up?", "Time flies! It's been 24 hours since our last chat. Let's continue our conversation!","Hey, don't leave me hanging! It's been a whole day since we talked. Let's dive back in!", "Hope you're doing well! Just a friendly reminder that we haven't chatted in a day. Let's chat again soon!","Hi! It's been 24 hours since our last interaction. Let's pick up where we left off!","Missing our conversations! It's been a day. Ready to continue?","Hello! Can you believe it's been 24 hours? Let's keep our chat going!","Time for a chat check-in! A day has passed since we last talked. What's new?","Hey, hope you're having a great day! Remember, we haven't talked in 24 hours. Let's chat!","Hey, it's been a day since our last chat. Let's not wait any longer to continue our conversation!"]

@tasks.loop(minutes=1)
async def check_inactive_users():
    all_users = get_user_extras()
    for user_details in all_users:
        print("user: ", user_details)
        # last_interaction = datetime.strptime(user_details['last_message_time'], "%Y-%m-%d %H:%M:%S")
        last_interaction = user_details['last_message_time']
        
        # Calculate the difference between current time and last interaction time
        time_since_last_message = datetime.now() - last_interaction

        # Check if the difference is more than 34 hours
        if time_since_last_message > timedelta(hours=0.01):
            user = bot.get_user(int(user_details['user_id']))
            if user is not None:
                random_message = random.choice(predefined_messages)
                await user.send(random_message)
            else:
                print(f"User {user_details['user_id']} not found!")

# @bot.tree.command(name='set', description='Sets the charcter you want /set (character)')
# # @slash_option(name='message', description='Character from /list', required=True)
# async def set_character(ctx: discord.Interaction, message: str):
#     user_id = str(ctx.user.mention).replace('<@', '').replace('>', '')
#     if check_if_user_exists(user_id):
#         # return await ctx.response.send_message(embed=welcome_embed, ephemeral=True)
#         return await ctx.response.send_message("already set embed")
#     else:
#         create_cache_history(user_id)
#         add_user_to_user_json(user_id)
#         # return await ctx.response.send_message("You have already set your character", ephemeral=True)
#         return await ctx.response.send_message("welcome_embed")
# @bot.tree.command(name='preference', description='Set your preference for the bot.\n press 1 for ChatGPT\n press 2 for Local LLM')
# async def preference(ctx: discord.Interaction, preference: int):
@bot.tree.command(name="preference")
@app_commands.describe(preference = "Set your preference for the bot.\n press 1 for ChatGPT\n press 2 for Local LLM")
async def preference(ctx:  discord.Interaction, preference: int):
    user_id = str(ctx.user.mention).replace('<@', '').replace('>', '')
    if preference == 1:
        change_preferences(user_id, False)
        return await ctx.response.send_message(f"Your preference has been set to ChatGPT")
    elif preference == 2:
        change_preferences(user_id, True)
        return await ctx.response.send_message(f"Your preference has been set to Local LLM")
    return await ctx.response.send_message(f"Invalid preference. Please try again.")

@bot.tree.command(name="mode")
@app_commands.describe(mode = "Set your Mode for the Response.\n press 1 for Text Response\n press 2 for Voice Response")
async def mode(ctx:  discord.Interaction, mode: int):
    user_id = str(ctx.user.mention).replace('<@', '').replace('>', '')
    if mode == 1:
        change_voice(user_id, False)
        return await ctx.response.send_message(f"Response Mode has been set to Text")
    elif mode == 2:
        change_voice(user_id, True)
        return await ctx.response.send_message(f"Response Mode has been set to Voice")
    return await ctx.response.send_message(f"Invalid Mode. Please try again.")


@bot.tree.command(name = "help")
async def help(ctx: discord.Interaction):
    embed_help = help_embed()
    return await ctx.response.send_message(embed=embed_help)


@bot.tree.command(name="regenerate", description="Delete the last response.")
async def regenerate(ctx: discord.Interaction):
    # await ctx.response.defer()  # Immediately acknowledge the interaction
    # await ctx.response.send_message("Bot is working")
    user_id = str(ctx.user.mention).replace("<@", "").replace(">", "")
    user_found, user = get_user(user_id)
    if user_found:
        # response = await regenerate_message_llm(user_id, user)
        delete_last_message_cache_history(user_id)
        return await ctx.response.send_message("Last message is delete")  # Send the actual response
    else:
        return await ctx.response.send_message("User Not Found!")
    
# @bot.tree.command(name='history', description='Prints the history of the character.')
# async def print_history(ctx: discord.Interaction):
#     user_id = str(ctx.user.mention).replace('<@', '').replace('>', '')
#     return await ctx.response.send_message(get_conversation_history(user_id))

@bot.tree.command(name='clear', description='Feeling like starting fresh? This command clears the chat history with me.')
async def clear_history_command(ctx: discord.Interaction):
   delete_cache_history(str(ctx.user.mention).replace('<@', '').replace('>', ''))
   delete_message_history(user_id)
   return await ctx.response.send_message("history cleared")
    
@bot.event
async def on_message(message):
    if message.author.bot or not isinstance(message.channel, discord.DMChannel):
        return
    view = View()
    # Define payment links for different amounts
    payment_links = {
        "🌸 $15": "https://buy.stripe.com/eVa5lj1kH6LcgDK8wD",
        "🔥 $50": "https://buy.stripe.com/00gcNL6F17Pg3QYaEM",
        "⭐ $100": "https://buy.stripe.com/7sI1530gDglMfzGdQZ"
    }
    # Create buttons for each payment link
    for amount, link in payment_links.items():
        button = Button(style=discord.ButtonStyle.green,label=amount, url=link)
        view.add_item(button)
    user_id = str(message.author.id)
    user_name = message.author.display_name
    print(f"User ID: {user_id}",message)

    
        
    found, user = get_user(user_id)
    embed = welcome_embed()
    embed_repay = balance_embed()
    if not found:
        print("User not found in database.")
        found_free, user_free = get_user_free(user_id)
        if found_free:
            if user_free['left'] >= 0:
                update_user_free(user_id, user_free['left'] - 1)
                # 
                return await free_response(message)
            else:
                return await message.reply(embed=embed, view=view)
        else:
            print("Not found in Free Trial, adding 5 messages")
            create_user_free(user_id)
            update_user_free(user_id, 4)
            return await free_response(message)
        # return await message.reply(embed=embed, view=view)
    else:
        if not user['payment_status']:
            await message.reply(embed=embed_repay, view=view)
            return
        # Calculate the elapsed time since the user started the conversation        
        if not is_subscription_active(user['last_subscription_time']):
            await message.reply(embed=embed_repay, view=view)
            return
    create_or_update_user_extra(user_id)
    # Remove the following line if you're not using MongoDB
    _, message_history,_, _ = connect_to_db()
    local_llm = True
    voice_response = False
    found, user_preference = get_preferences(user_id)
    if not found:
        save_preferences_to_db(user_id, user_name ,False)
    else:
        local_llm = user_preference['local_llm']
        voice_response = user_preference['voice']
    user_text = message.content
    start_time = 0
    payment_tier = user['subscription_payment']
    allowed_characters = 0
    if payment_tier == 15:
        allowed_characters = 12495
    elif payment_tier == 50:
        allowed_characters = 24990
    elif payment_tier == 100:
        allowed_characters = 49980
    if message.attachments:
        attachment = message.attachments[0]
        if attachment.filename.endswith(".ogg"):
            # Download the voice message
            await attachment.save(f"{user_id}.ogg")

            # Convert voice message to text
            transcription = oga_2_mp3_2_text(user_id)
            # text_start_time = time.time()
            if local_llm:
                # model_res = "local_llm"
                model_res = await send_message_llm(message)
                # save_message_llm_to_db(user_id, user_text, model_res)
            else:
                model_res = get_chain_response(user_id, transcription, user_name)
                # Save message to database
                save_message_to_db(user_id, transcription, model_res)
            # text_end_time = time.time()
                # Convert response to audio
            if voice_response:
                # Convert response to audio
                if len(model_res) - model_res.count(" ") <= allowed_characters:
                    audio_path, _ = get_audio(user_id, model_res)
                    audio_file = discord.File(audio_path)
                    await message.reply(file=audio_file)
                    os.remove(audio_path)
                if len(model_res) <= 2000:
                    # If within limit, send the content as a single message
                    await message.reply(model_res)
                else:
                    # If content is too long, split it into multiple messages
                    chunks = [model_res[i:i + 2000] for i in range(0, len(model_res), 2000)]
                    for chunk in chunks:
                        await message.channel.send(chunk)
        else:
            if len(model_res) <= 2000:
                # If within limit, send the content as a single message
                await message.reply(model_res)
            else:
                # If content is too long, split it into multiple messages
                chunks = [model_res[i:i + 2000] for i in range(0, len(model_res), 2000)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            # await message.reply(model_res)

    else:
        # Get response
        if local_llm:
            # model_res = "local_llm"
            model_res = await send_message_llm(message)
            # save_message_llm_to_db(user_id, user_text, model_res)
        else:
            model_res = get_chain_response(user_id, user_text, user_name)
            # model_res = "testing on message"
        # Save message to database
            save_message_to_db(user_id, user_text, model_res)

        if voice_response:
            # Convert response to audio
            if len(model_res) - model_res.count(" ") <= allowed_characters:
                audio_path, _ = get_audio(user_id, model_res)
                audio_file = discord.File(audio_path)
                await message.reply(file=audio_file)
                os.remove(audio_path)
            if len(model_res) <= 2000:
                # If within limit, send the content as a single message
                await message.reply(model_res)
            else:
                # If content is too long, split it into multiple messages
                chunks = [model_res[i:i + 2000] for i in range(0, len(model_res), 2000)]
                for chunk in chunks:
                    await message.channel.send(chunk)
        else:
            if len(model_res) <= 2000:
                # If within limit, send the content as a single message
                await message.reply(model_res)
            else:
                # If content is too long, split it into multiple messages
                chunks = [model_res[i:i + 2000] for i in range(0, len(model_res), 2000)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            # await message.reply(model_res)

# async def on_message(message):
#     if message.author.bot or not isinstance(message.channel, discord.DMChannel):
#         return

#     user_id = str(message.author.id)
#     user_name = message.author.display_name

#     found, user = get_user(user_id)
    
#     if not found or not user['payment_status']:
#         await handle_new_or_unpaid_user(message, user_id)
#         return

#     if not is_subscription_active(user['last_subscription_time']):
#         view, embed_repay = create_payment_embed()
#         await message.reply(embed=embed_repay, view=view)
#         return

#     await handle_existing_user(message, user_id, user_name, user)

# async def handle_new_or_unpaid_user(message, user_id):
#     found_free, user_free = get_user_free(user_id)
#     if found_free and user_free['left'] >= 0:
#         update_user_free(user_id, user_free['left'] - 1)
#         await free_response(message)
#     else:
#         view, embed = create_payment_embed()
#         await message.reply(embed=embed, view=view)

# def create_payment_embed():
#     view = View()
#     payment_links = {
#         "🌸 $15": "https://buy.stripe.com/eVa5lj1kH6LcgDK8wD",
#         "🔥 $50": "https://buy.stripe.com/00gcNL6F17Pg3QYaEM",
#         "⭐ $100": "https://buy.stripe.com/7sI1530gDglMfzGdQZ"
#     }
#     for amount, link in payment_links.items():
#         button = Button(style=discord.ButtonStyle.green, label=amount, url=link)
#         view.add_item(button)

#     embed = welcome_embed()
#     embed_repay = balance_embed()

#     return view, embed_repay

# async def handle_existing_user(message, user_id, user_name, user):
#     create_or_update_user_extra(user_id)
    
#     local_llm, voice_response = get_user_preferences(user_id, user_name)
#     allowed_characters = get_allowed_characters(user['subscription_payment'])

#     user_text = message.content

#     if message.attachments:
#         attachment = message.attachments[0]
#         if attachment.filename.endswith(".ogg"):
#             await handle_voice_message(message, user_id, user_text, allowed_characters, local_llm, voice_response)
#     else:
#         await handle_text_message(message, user_id, user_text, allowed_characters, local_llm, voice_response)

# def get_user_preferences(user_id, user_name):
#     found, user_preference = get_preferences(user_id)
#     if not found:
#         save_preferences_to_db(user_id, user_name, False)
#         return False, False

#     return user_preference['local_llm'], user_preference['voice']

# def get_allowed_characters(payment_tier):
#     if payment_tier == 15:
#         return 12495
#     elif payment_tier == 50:
#         return 24990
#     elif payment_tier == 100:
#         return 49980
#     return 0

# async def handle_voice_message(message, user_id, user_text, allowed_characters, local_llm, voice_response):
#     await attachment.save(f"{user_id}.ogg")
#     transcription = oga_2_mp3_2_text(user_id)

#     response = await get_response(user_id, transcription, user_text, local_llm)

#     await send_response(message, response, allowed_characters, voice_response)

# async def handle_text_message(message, user_id, user_text, allowed_characters, local_llm, voice_response):
#     response = await get_response(user_id, user_text, user_text, local_llm)

#     await send_response(message, response, allowed_characters, voice_response)

# async def get_response(user_id, text, user_text, local_llm):
#     if local_llm:
#         return await send_message_llm(text)
#     else:
#         model_res = get_chain_response(user_id, text, user_text)
#         save_message_to_db(user_id, text, model_res)
#         return model_res

# async def send_response(message, response, allowed_characters, voice_response):
#     if voice_response and len(response) - response.count(" ") <= allowed_characters:
#         audio_path, _ = get_audio(message.author.id, response)
#         audio_file = discord.File(audio_path)
#         await message.reply(file=audio_file)
#         os.remove(audio_path)

#     if len(response) <= 2000:
#         await message.reply(response)
#     else:
#         chunks = [response[i:i + 2000] for i in range(0, len(response), 2000)]
#         for chunk in chunks:
#             await message.channel.send(chunk)

bot.run(TOKEN)