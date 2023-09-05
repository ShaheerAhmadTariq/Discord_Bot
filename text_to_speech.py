import os
import requests
import tempfile
# import nacl
from datetime import datetime
from util import get_audio_duration
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")




def get_audio(user_id, bot_reply):
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL"
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }

    data = {
        "text": bot_reply,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    response = requests.post(url, json=data, headers=headers)
    file_path = f'audio_outputs/{user_id}/JenFoxxx.mp3'
    # Create directories if they don't exist
    os.makedirs(f'audio_outputs/{user_id}', exist_ok=True)

    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
    duration_seconds = get_audio_duration(file_path)

    if duration_seconds is not None:
        print(f"Audio duration: {duration_seconds:.2f} seconds")
        return file_path, duration_seconds
    return file_path, 0.0

def tts(user_id, bot_reply):
    url = "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL"
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }

    data = {
        "text": bot_reply,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    response = requests.post(url, json=data, headers=headers)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio:
        audio.write(response.content)
        audio.flush()
        audio.seek(0)

        # if you get an error saying ffmpeg isnt defined or something along those lines you need to install ffmpeg (brew install ffmpeg)
        prepared_audio = discord.FFmpegOpusAudio(audio.name, executable="ffmpeg")
        ctx.guild.voice_client.play(prepared_audio, after=None)
        audio.close
