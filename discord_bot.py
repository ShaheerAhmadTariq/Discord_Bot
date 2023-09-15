import os
import time
import discord
import aiohttp
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
from util import update_time, update_text_time
from helpers import check_if_user_exists, create_cache_history, add_user_to_user_json, get_conversation_history, delete_cache_history, delete_last_message_cache_history
from database import save_message_to_db, connect_to_db, create_user, get_user, update_user, update_user_time, delete_message_history, save_preferences_to_db, get_preferences, change_preferences, save_message_llm_to_db, change_voice, update_user_time, create_user_free, get_user_free, update_user_free, create_or_update_user_extra, get_user_extras
TOKEN = os.environ.get('TOKEN')

intents = discord.Intents.all()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

def parse_response(str_with_quotes):
    # Remove all double quotations from the beginning
    while str_with_quotes.startswith('"'):
        str_with_quotes = str_with_quotes[1:]

    # Remove all double quotations from the end
    while str_with_quotes.endswith('"'):
        str_with_quotes = str_with_quotes[:-1]

    return str_with_quotes

def print_current_time(str_to_print):
    current_time = datetime.now().time()
    formatted_time = current_time.strftime("%H:%M:%S")
    print(f"\n *****************************************************\n{str_to_print} is {formatted_time}")
async def fetch_post(session, url, json_data):
    async with session.post(url, json=json_data) as response:
        return await response.text()
async def send_message_llm(user):
    async with aiohttp.ClientSession() as session:
            url = 'http://127.0.0.1:8000/generate_response_llm'
            user_id = str(user.author.id)
            user_name = user.author.display_name
            message_content = {"message": user.content, "user_id": user_id, "user_name": user_name}
            model_res = await fetch_post(session, url, message_content)
    current_time = datetime.now().time()
    formatted_time = current_time.strftime("%H:%M:%S")
    print(f"\n *****************************************************\nThe Local LLM current time is {formatted_time}")
    return parse_response(model_res)
async def send_message_chatgpt(user):
    async with aiohttp.ClientSession() as session:
            url = 'http://127.0.0.1:8000/generate_response_chatgpt'
            user_id = str(user.author.id)
            user_name = user.author.display_name
            message_content = {"message": user.content, "user_id": user_id, "user_name": user_name}
            model_res = await fetch_post(session, url, message_content)
    current_time = datetime.now().time()
    formatted_time = current_time.strftime("%H:%M:%S")
    print(f"\n *****************************************************\nThe ChatGPT current time is {formatted_time}")
    return parse_response(model_res)  
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


@bot.tree.command(name='clear', description='Feeling like starting fresh? This command clears the chat history with me.')
async def clear_history_command(ctx: discord.Interaction):
   user_id = str(ctx.user.mention).replace('<@', '').replace('>', '')
   delete_cache_history(user_id)
   delete_message_history(user_id)
   return await ctx.response.send_message("history cleared")
    
@bot.tree.command(name='balance', description='Prints remaining balance')
async def balance(ctx: discord.Interaction):
    user_id = str(ctx.user.mention).replace('<@', '').replace('>', '')
    found, user = get_user(user_id)
    if found:
        amount = round(user['last_message_time']/60, 2)
        message_str = f"Your remaining balance is **{amount}$**."
        return await ctx.response.send_message(message_str)
    else:
        message_str = f"Your balance is **0$**."
        return await ctx.response.send_message(message_str)

@bot.event
async def on_message(message):
    if message.author.bot or not isinstance(message.channel, discord.DMChannel):
        return
    view = View()
    # Define payment links for different amounts
    payment_links = {
        # "🌸 $5": "https://buy.stripe.com/4gw153gfB2uWevC3cc",
        # "🌸 $5": "https://buy.stripe.com/test_fZefZV8Z0cDLfMQcMO",
        "🔥 $10": "https://buy.stripe.com/9AQ6pn8N95H82MUeUV",
        "❤️ $15": "https://buy.stripe.com/aEU4hf5AXd9Acnu9AC",
        "💎 $25": "https://buy.stripe.com/00g4hf9RdfhI3QY6or",
        "⭐ $Custom": "https://buy.stripe.com/6oE00Zd3p5H8cnu148"
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
        if user['last_message_time'] <= 0:
            update_user(user_id)
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
    if message.attachments:
        attachment = message.attachments[0]
        if attachment.filename.endswith(".ogg"):
            # Download the voice message
            await attachment.save(f"{user_id}.ogg")

            # Convert voice message to text
            transcription = oga_2_mp3_2_text(user_id)
            text_start_time = time.time()
            if local_llm:
                # model_res = "local_llm"
                model_res = await send_message_llm(message)
                # save_message_llm_to_db(user_id, user_text, model_res)
            else:
                model_res = await send_message_chatgpt(message)
                # Save message to database
                save_message_to_db(user_id, transcription, model_res)
            text_end_time = time.time()
                # Convert response to audio
            if voice_response:
                audio_path, audio_duration = get_audio(user_id, model_res)
    
                # Send audio as reply to the user's message
                audio_file = discord.File(audio_path)
                await message.reply(file=audio_file)
                update_time(user['last_message_time'], start_time, user_id, audio_duration)

                # Remove the audio file
                os.remove(audio_path)
            else:
                # If content is too long, split it into multiple messages
                if len(model_res) <= 2000:
                    # If within limit, send the content as a single message
                    await message.reply(model_res)
                else:
                    # If content is too long, split it into multiple messages
                    chunks = [model_res[i:i + 2000] for i in range(0, len(model_res), 2000)]
                    for chunk in chunks:
                        await message.channel.send(chunk)
                # await message.reply(model_res)
                length_of_message = len(model_res.split())
                update_text_time(user['last_message_time'], text_start_time, user_id, text_end_time, local_llm, length_of_message)
            # Remove the voice message file
            # os.remove(f"{user_id}.ogg")

    else:
        # Get response
        text_start_time = time.time()
        if local_llm:
            # model_res = "local_llm"
            print_current_time("Local LLM start time")
            model_res = await send_message_llm(message)
            # save_message_llm_to_db(user_id, user_text, model_res)
        else:
            print_current_time("ChatGPT start time")
            # model_res = get_chain_response(user_id, user_text, user_name)
            model_res = await send_message_chatgpt(message)
            print("\n\n ******************************\nModel res: ",model_res)
            # model_res = "testing on message"
        # Save message to database
            save_message_to_db(user_id, user_text, model_res)
        text_end_time = time.time()
        if voice_response:
            # Convert response to audio
            audio_path, audio_duration = get_audio(user_id, model_res)
    
            # Send audio as reply to the user's message
            audio_file = discord.File(audio_path)
            await message.reply(file=audio_file)
        # audio_duration = 10
            update_time(user['last_message_time'], start_time, user_id, audio_duration)
            # Remove the audio file
            os.remove(audio_path)
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
            length_of_message = len(model_res.split())
            update_text_time(user['last_message_time'], text_start_time, user_id, text_end_time, local_llm, length_of_message)
        

bot.run(TOKEN)import os
import time
import discord
import aiohttp
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
from util import update_time, update_text_time
from helpers import check_if_user_exists, create_cache_history, add_user_to_user_json, get_conversation_history, delete_cache_history, delete_last_message_cache_history
from database import save_message_to_db, connect_to_db, create_user, get_user, update_user, update_user_time, delete_message_history, save_preferences_to_db, get_preferences, change_preferences, save_message_llm_to_db, change_voice, update_user_time, create_user_free, get_user_free, update_user_free, create_or_update_user_extra, get_user_extras
TOKEN = os.environ.get('TOKEN')

intents = discord.Intents.all()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

def parse_response(str_with_quotes):
    # Remove all double quotations from the beginning
    while str_with_quotes.startswith('"'):
        str_with_quotes = str_with_quotes[1:]

    # Remove all double quotations from the end
    while str_with_quotes.endswith('"'):
        str_with_quotes = str_with_quotes[:-1]

    return str_with_quotes

def print_current_time(str_to_print):
    current_time = datetime.now().time()
    formatted_time = current_time.strftime("%H:%M:%S")
    print(f"\n *****************************************************\n{str_to_print} is {formatted_time}")
async def fetch_post(session, url, json_data):
    async with session.post(url, json=json_data) as response:
        return await response.text()
async def send_message_llm(user):
    async with aiohttp.ClientSession() as session:
            url = 'http://127.0.0.1:8000/generate_response_llm'
            user_id = str(user.author.id)
            user_name = user.author.display_name
            message_content = {"message": user.content, "user_id": user_id, "user_name": user_name}
            model_res = await fetch_post(session, url, message_content)
    current_time = datetime.now().time()
    formatted_time = current_time.strftime("%H:%M:%S")
    print(f"\n *****************************************************\nThe Local LLM current time is {formatted_time}")
    return parse_response(model_res)
async def send_message_chatgpt(user):
    async with aiohttp.ClientSession() as session:
            url = 'http://127.0.0.1:8000/generate_response_chatgpt'
            user_id = str(user.author.id)
            user_name = user.author.display_name
            message_content = {"message": user.content, "user_id": user_id, "user_name": user_name}
            model_res = await fetch_post(session, url, message_content)
    current_time = datetime.now().time()
    formatted_time = current_time.strftime("%H:%M:%S")
    print(f"\n *****************************************************\nThe ChatGPT current time is {formatted_time}")
    return parse_response(model_res)  
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


@bot.tree.command(name='clear', description='Feeling like starting fresh? This command clears the chat history with me.')
async def clear_history_command(ctx: discord.Interaction):
   user_id = str(ctx.user.mention).replace('<@', '').replace('>', '')
   delete_cache_history(user_id)
   delete_message_history(user_id)
   return await ctx.response.send_message("history cleared")
    
@bot.tree.command(name='balance', description='Prints remaining balance')
async def balance(ctx: discord.Interaction):
    user_id = str(ctx.user.mention).replace('<@', '').replace('>', '')
    found, user = get_user(user_id)
    if found:
        amount = round(user['last_message_time']/60, 2)
        message_str = f"Your remaining balance is **{amount}$**."
        return await ctx.response.send_message(message_str)
    else:
        message_str = f"Your balance is **0$**."
        return await ctx.response.send_message(message_str)

@bot.event
async def on_message(message):
    if message.author.bot or not isinstance(message.channel, discord.DMChannel):
        return
    view = View()
    # Define payment links for different amounts
    payment_links = {
        # "🌸 $5": "https://buy.stripe.com/4gw153gfB2uWevC3cc",
        # "🌸 $5": "https://buy.stripe.com/test_fZefZV8Z0cDLfMQcMO",
        "🔥 $10": "https://buy.stripe.com/9AQ6pn8N95H82MUeUV",
        "❤️ $15": "https://buy.stripe.com/aEU4hf5AXd9Acnu9AC",
        "💎 $25": "https://buy.stripe.com/00g4hf9RdfhI3QY6or",
        "⭐ $Custom": "https://buy.stripe.com/6oE00Zd3p5H8cnu148"
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
        if user['last_message_time'] <= 0:
            update_user(user_id)
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
    if message.attachments:
        attachment = message.attachments[0]
        if attachment.filename.endswith(".ogg"):
            # Download the voice message
            await attachment.save(f"{user_id}.ogg")

            # Convert voice message to text
            transcription = oga_2_mp3_2_text(user_id)
            text_start_time = time.time()
            if local_llm:
                # model_res = "local_llm"
                model_res = await send_message_llm(message)
                # save_message_llm_to_db(user_id, user_text, model_res)
            else:
                model_res = await send_message_chatgpt(message)
                # Save message to database
                save_message_to_db(user_id, transcription, model_res)
            text_end_time = time.time()
                # Convert response to audio
            if voice_response:
                audio_path, audio_duration = get_audio(user_id, model_res)
    
                # Send audio as reply to the user's message
                audio_file = discord.File(audio_path)
                await message.reply(file=audio_file)
                update_time(user['last_message_time'], start_time, user_id, audio_duration)

                # Remove the audio file
                os.remove(audio_path)
            else:
                # If content is too long, split it into multiple messages
                if len(model_res) <= 2000:
                    # If within limit, send the content as a single message
                    await message.reply(model_res)
                else:
                    # If content is too long, split it into multiple messages
                    chunks = [model_res[i:i + 2000] for i in range(0, len(model_res), 2000)]
                    for chunk in chunks:
                        await message.channel.send(chunk)
                # await message.reply(model_res)
                length_of_message = len(model_res.split())
                update_text_time(user['last_message_time'], text_start_time, user_id, text_end_time, local_llm, length_of_message)
            # Remove the voice message file
            # os.remove(f"{user_id}.ogg")

    else:
        # Get response
        text_start_time = time.time()
        if local_llm:
            # model_res = "local_llm"
            print_current_time("Local LLM start time")
            model_res = await send_message_llm(message)
            # save_message_llm_to_db(user_id, user_text, model_res)
        else:
            print_current_time("ChatGPT start time")
            # model_res = get_chain_response(user_id, user_text, user_name)
            model_res = await send_message_chatgpt(message)
            print("\n\n ******************************\nModel res: ",model_res)
            # model_res = "testing on message"
        # Save message to database
            save_message_to_db(user_id, user_text, model_res)
        text_end_time = time.time()
        if voice_response:
            # Convert response to audio
            audio_path, audio_duration = get_audio(user_id, model_res)
    
            # Send audio as reply to the user's message
            audio_file = discord.File(audio_path)
            await message.reply(file=audio_file)
        # audio_duration = 10
            update_time(user['last_message_time'], start_time, user_id, audio_duration)
            # Remove the audio file
            os.remove(audio_path)
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
            length_of_message = len(model_res.split())
            update_text_time(user['last_message_time'], text_start_time, user_id, text_end_time, local_llm, length_of_message)
        

bot.run(TOKEN)import os
import time
import discord
import aiohttp
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
from util import update_time, update_text_time
from helpers import check_if_user_exists, create_cache_history, add_user_to_user_json, get_conversation_history, delete_cache_history, delete_last_message_cache_history
from database import save_message_to_db, connect_to_db, create_user, get_user, update_user, update_user_time, delete_message_history, save_preferences_to_db, get_preferences, change_preferences, save_message_llm_to_db, change_voice, update_user_time, create_user_free, get_user_free, update_user_free, create_or_update_user_extra, get_user_extras
TOKEN = os.environ.get('TOKEN')

intents = discord.Intents.all()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

def parse_response(str_with_quotes):
    # Remove all double quotations from the beginning
    while str_with_quotes.startswith('"'):
        str_with_quotes = str_with_quotes[1:]

    # Remove all double quotations from the end
    while str_with_quotes.endswith('"'):
        str_with_quotes = str_with_quotes[:-1]

    return str_with_quotes

def print_current_time(str_to_print):
    current_time = datetime.now().time()
    formatted_time = current_time.strftime("%H:%M:%S")
    print(f"\n *****************************************************\n{str_to_print} is {formatted_time}")
async def fetch_post(session, url, json_data):
    async with session.post(url, json=json_data) as response:
        return await response.text()
async def send_message_llm(user):
    async with aiohttp.ClientSession() as session:
            url = 'http://127.0.0.1:8000/generate_response_llm'
            user_id = str(user.author.id)
            user_name = user.author.display_name
            message_content = {"message": user.content, "user_id": user_id, "user_name": user_name}
            model_res = await fetch_post(session, url, message_content)
    current_time = datetime.now().time()
    formatted_time = current_time.strftime("%H:%M:%S")
    print(f"\n *****************************************************\nThe Local LLM current time is {formatted_time}")
    return parse_response(model_res)
async def send_message_chatgpt(user):
    async with aiohttp.ClientSession() as session:
            url = 'http://127.0.0.1:8000/generate_response_chatgpt'
            user_id = str(user.author.id)
            user_name = user.author.display_name
            message_content = {"message": user.content, "user_id": user_id, "user_name": user_name}
            model_res = await fetch_post(session, url, message_content)
    current_time = datetime.now().time()
    formatted_time = current_time.strftime("%H:%M:%S")
    print(f"\n *****************************************************\nThe ChatGPT current time is {formatted_time}")
    return parse_response(model_res)  
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


@bot.tree.command(name='clear', description='Feeling like starting fresh? This command clears the chat history with me.')
async def clear_history_command(ctx: discord.Interaction):
   user_id = str(ctx.user.mention).replace('<@', '').replace('>', '')
   delete_cache_history(user_id)
   delete_message_history(user_id)
   return await ctx.response.send_message("history cleared")
    
@bot.tree.command(name='balance', description='Prints remaining balance')
async def balance(ctx: discord.Interaction):
    user_id = str(ctx.user.mention).replace('<@', '').replace('>', '')
    found, user = get_user(user_id)
    if found:
        amount = round(user['last_message_time']/60, 2)
        message_str = f"Your remaining balance is **{amount}$**."
        return await ctx.response.send_message(message_str)
    else:
        message_str = f"Your balance is **0$**."
        return await ctx.response.send_message(message_str)

@bot.event
async def on_message(message):
    if message.author.bot or not isinstance(message.channel, discord.DMChannel):
        return
    view = View()
    # Define payment links for different amounts
    payment_links = {
        # "🌸 $5": "https://buy.stripe.com/4gw153gfB2uWevC3cc",
        # "🌸 $5": "https://buy.stripe.com/test_fZefZV8Z0cDLfMQcMO",
        "🔥 $10": "https://buy.stripe.com/9AQ6pn8N95H82MUeUV",
        "❤️ $15": "https://buy.stripe.com/aEU4hf5AXd9Acnu9AC",
        "💎 $25": "https://buy.stripe.com/00g4hf9RdfhI3QY6or",
        "⭐ $Custom": "https://buy.stripe.com/6oE00Zd3p5H8cnu148"
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
        if user['last_message_time'] <= 0:
            update_user(user_id)
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
    if message.attachments:
        attachment = message.attachments[0]
        if attachment.filename.endswith(".ogg"):
            # Download the voice message
            await attachment.save(f"{user_id}.ogg")

            # Convert voice message to text
            transcription = oga_2_mp3_2_text(user_id)
            text_start_time = time.time()
            if local_llm:
                # model_res = "local_llm"
                model_res = await send_message_llm(message)
                # save_message_llm_to_db(user_id, user_text, model_res)
            else:
                model_res = await send_message_chatgpt(message)
                # Save message to database
                save_message_to_db(user_id, transcription, model_res)
            text_end_time = time.time()
                # Convert response to audio
            if voice_response:
                audio_path, audio_duration = get_audio(user_id, model_res)
    
                # Send audio as reply to the user's message
                audio_file = discord.File(audio_path)
                await message.reply(file=audio_file)
                update_time(user['last_message_time'], start_time, user_id, audio_duration)

                # Remove the audio file
                os.remove(audio_path)
            else:
                # If content is too long, split it into multiple messages
                if len(model_res) <= 2000:
                    # If within limit, send the content as a single message
                    await message.reply(model_res)
                else:
                    # If content is too long, split it into multiple messages
                    chunks = [model_res[i:i + 2000] for i in range(0, len(model_res), 2000)]
                    for chunk in chunks:
                        await message.channel.send(chunk)
                # await message.reply(model_res)
                length_of_message = len(model_res.split())
                update_text_time(user['last_message_time'], text_start_time, user_id, text_end_time, local_llm, length_of_message)
            # Remove the voice message file
            # os.remove(f"{user_id}.ogg")

    else:
        # Get response
        text_start_time = time.time()
        if local_llm:
            # model_res = "local_llm"
            print_current_time("Local LLM start time")
            model_res = await send_message_llm(message)
            # save_message_llm_to_db(user_id, user_text, model_res)
        else:
            print_current_time("ChatGPT start time")
            # model_res = get_chain_response(user_id, user_text, user_name)
            model_res = await send_message_chatgpt(message)
            print("\n\n ******************************\nModel res: ",model_res)
            # model_res = "testing on message"
        # Save message to database
            save_message_to_db(user_id, user_text, model_res)
        text_end_time = time.time()
        if voice_response:
            # Convert response to audio
            audio_path, audio_duration = get_audio(user_id, model_res)
    
            # Send audio as reply to the user's message
            audio_file = discord.File(audio_path)
            await message.reply(file=audio_file)
        # audio_duration = 10
            update_time(user['last_message_time'], start_time, user_id, audio_duration)
            # Remove the audio file
            os.remove(audio_path)
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
            length_of_message = len(model_res.split())
            update_text_time(user['last_message_time'], text_start_time, user_id, text_end_time, local_llm, length_of_message)
        

bot.run(TOKEN)