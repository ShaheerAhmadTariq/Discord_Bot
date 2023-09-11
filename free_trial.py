import os
import time
import discord
import aiohttp
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
from datetime import datetime
from local_llm import generate_response, regenerate_message_llm
from embed_messages import welcome_embed
from chain import chain_setup, get_chain_response
from embed_messages import welcome_embed, help_embed, balance_embed
from text_to_speech import get_audio
from transcribe_audio import oga_2_mp3_2_text
from util import update_time, update_text_time
from helpers import check_if_user_exists, create_cache_history, add_user_to_user_json, get_conversation_history, delete_cache_history, delete_last_message_cache_history
from database import save_message_to_db, connect_to_db, create_user, get_user, update_user, update_user_time, delete_message_history, save_preferences_to_db, get_preferences, change_preferences, save_message_llm_to_db, change_voice, update_user_time, create_user_free, get_user_free, update_user_free

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
    return model_res
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
    return model_res 
async def free_response(message):
    user_id = str(message.author.id)
    user_name = message.author.display_name
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
                return await message.reply(file=audio_file)
                # update_time(user['last_message_time'], start_time, user_id, audio_duration)

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
                        return await message.channel.send(chunk)
                # await message.reply(model_res)
                # update_text_time(user['last_message_time'], text_start_time, user_id, text_end_time)
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
            # model_res = "testing on message"
        # Save message to database
            save_message_to_db(user_id, user_text, model_res)
        text_end_time = time.time()
        if voice_response:
            # Convert response to audio
            audio_path, audio_duration = get_audio(user_id, model_res)
    
            # Send audio as reply to the user's message
            audio_file = discord.File(audio_path)
            return await message.reply(file=audio_file)
        # audio_duration = 10
            # update_time(user['last_message_time'], start_time, user_id, audio_duration)
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
            # update_text_time(user['last_message_time'], text_start_time, user_id, text_end_time)
        