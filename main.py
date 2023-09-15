import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import asyncio
from pydantic import BaseModel
from local_llm import generate_response
from chain import get_chain_response
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
    # try:
        print("message: ", message)
        response = await generate_response(message.user_id, message.user_name, message.message)
        # response = "hello from local_llm"
        # await asyncio.sleep(10)
        return response
    # except Exception as e:
    #     print("Error is", e)
    #     return "error in backend"

class MessageGPT(BaseModel):
    message: str
    user_id: str
    user_name: str
@app.post("/generate_response_chatgpt")
async def generate_response_chatgpt(message: MessageGPT):
    try:
        print("message: ", message)
        response = await get_chain_response(message.user_id, message.message, message.user_name)
        # response = "hello from chatgpt"
        # await asyncio.sleep(10)
        return response
    except Exception as e:
        print("Error is", e)
        return "error in backend"