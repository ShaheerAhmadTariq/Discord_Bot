import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import asyncio
from pydantic import BaseModel
from local_llm import generate_response
from transcribe_audio import oga_2_mp3_2_text
from server_utils import check_user
from helpers import delete_cache_history
from database import get_user
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
        g_response, message = check_user(user_id=message.user_id, user_name=message.user_name)
        print("message: ", message)
        if g_response:
            voice_response = False
            if 'voice_response' in message:
                voice_response = message['voice_response']
            response = "hello from local_llm"
            # response = await generate_response(message.user_id, message.user_name, message.message)
            if voice_response:
                return {"audio_file": 'hfajfafaa.wav'}
            else:
                return {"message": response}
        # response = "hello from local_llm"
        # await asyncio.sleep(10)
        return message
    except Exception as e:
        print("Error is", e)
        return {"message": "error in backend"}


class AudioMessage(BaseModel):
    audio_file_path: str
    user_id: str
    user_name: str
@app.post("/generate_response_llm_audio")
async def generate_response_llm_audio(message: AudioMessage):
    try:
        g_response, message = check_user(user_id=message.user_id, user_name=message.user_name)
        print("message: ", message)
        if g_response:
            voice_response = False
            if 'voice_response' in message:
                voice_response = message['voice_response']
            transcription = oga_2_mp3_2_text(message.audio_file_path)
            response = "hello from local_llm audio"
            # response = transcription
            # response = await generate_response(message.user_id, message.user_name, message.message)
            if voice_response:
                return {"audio_file": 'hfajfafaa.wav'}
            else:
                return {"message": response}
        # response = "hello from local_llm"
        # await asyncio.sleep(10)
        return message
    except Exception as e:
        print("Error is", e)
        return {"message": "error in backend"}
    
class ClearMessage(BaseModel):
    user_id: str
@app.post("/clear")
async def clear(user: ClearMessage):
    user_id = user.user_id
    delete_cache_history(user_id)
    return {"message": "success"}

class BalanceMessage(BaseModel):
    user_id: str
@app.post("/balance")
async def balance(user: BalanceMessage):
    user_id = user.user_id
    found, user = get_user(user_id)
    if found:
        amount = round(user['last_message_time']/60, 2)
        message_str = f"Your remaining balance is **{amount}$**."
        return {"message": message_str}
    else:
        message_str = f"Your balance is **0$**."
        return {"message": message_str}
    