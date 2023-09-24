import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import asyncio
from pydantic import BaseModel
from local_llm import generate_response
from transcribe_audio import oga_2_mp3_2_text, speech_to_text, base64_to_audio
from server_utils import check_user, parse_response
from helpers import delete_cache_history
from database import get_user, change_voice
from text_to_speech import get_audio
from util import update_time, update_text_time
app = FastAPI()
origins = ["http://localhost:3000"]  # Replace with the actual URL of your Next.js app
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])



@app.get("/")
def root():
    return {"message": "Hello World"}
class Message(BaseModel):
    message: str
    user_id: str
    user_name: str
@app.post("/generate_response_llm")
async def generate_response_llm(message: Message):
    try:
        g_response, response = check_user(user_id=message.user_id, user_name=message.user_name)
        
        print("message: ", message)
        if g_response:
            found, user = get_user(message.user_id)
            voice_response = False
            if 'voice_response' in response:
                voice_response = response['voice_response']
            # response = "hello from local_llm"
            text_start_time = time.time()
            response = await generate_response(message.user_id, message.user_name, message.message)
            text_end_time = time.time()
            if voice_response:
                audio_path, audio_duration = get_audio(message.user_id, response)
                if found:
                    update_time(user['last_message_time'], 0, message.user_id, audio_duration)
                return {"message": audio_path, "is_audio": True}
            else:
                length_of_message = len(response.split())
                if found:
                    update_text_time(user['last_message_time'], text_start_time, message.user_id, text_end_time, True, length_of_message)
                return {"message": parse_response(response), "is_audio": False}    
        else:
            return {"message": response, "is_audio": False}    
        return message
    except Exception as e:
        print("Error is", e)
        return {"message": "Please ask again"}


class AudioMessage(BaseModel):
    audio_file_path: str
    user_id: str
    user_name: str
@app.post("/generate_response_llm_audio")
async def generate_response_llm_audio(message: AudioMessage):
    try:
        g_response, response = check_user(user_id=message.user_id, user_name=message.user_name)
        print("message: ", response)
        if g_response:
            found, user = get_user(message.user_id)
            voice_response = False
            if 'voice_response' in response:
                voice_response = response['voice_response']
            # message.audio_file_path = "./audio_inputs/"+message.audio_file_path.split(".ogg")[0]
            # message.audio_file_path = "./audio_inputs/" + message.audio_file_path
            base64_to_audio(message.audio_file_path, output_file_path=f"./audio_inputs/{message.user_id}_output.wav")
            transcription = speech_to_text(f"./audio_inputs/{message.user_id}_output.wav")
            text_start_time = time.time()
            response = await generate_response(message.user_id, message.user_name, transcription)
            text_end_time = time.time()
            if voice_response:
                audio_path, audio_duration = get_audio(message.user_id, response)
                if found:
                    update_time(user['last_message_time'], 0, message.user_id, audio_duration)
                return {"message": audio_path, "is_audio": True}
            else:
                length_of_message = len(response.split())
                if found:
                    update_text_time(user['last_message_time'], text_start_time, message.user_id, text_end_time, True, length_of_message)
                return {"message": parse_response(response), "is_audio": False}    
        else:
            return {"message": response, "is_audio": False}       
       
    except Exception as e:
        print("Error is", e)
        return {"message": "Please ask again"}
    
class ClearMessage(BaseModel):
    user_id: str
@app.post("/clear")
async def clear(user: ClearMessage):
    user_id = user.user_id
    delete_cache_history(user_id)
    return {"message": True}

class BalanceMessage(BaseModel):
    user_id: str
@app.post("/balance")
async def balance(user: BalanceMessage):
    user_id = user.user_id
    found, user = get_user(user_id)
    if found:
        amount = round(user['last_message_time']/60, 2)
        message_str = str(amount)
        return {"message": message_str}
    else:
        message_str = "0"
        return {"message": message_str}

class Preferencetext(BaseModel):
    user_id: str
@app.post("/preference_text")
async def preference_text(user: Preferencetext):
    user_id = user.user_id
    change_voice(user_id, False)
    return {"message": True}

class Preferenceaudio(BaseModel):
    user_id: str
@app.post("/preference_audio")
async def preference_text(user: Preferenceaudio):
    user_id = user.user_id
    change_voice(user_id, True)
    return {"message": True}
