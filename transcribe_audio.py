import openai
import os 
import subprocess
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

def oga_2_mp3(filename):
    input_file = f"{filename}.ogg"
    output_file = f"{filename}.mp3"

    # Load .oga file
    audio = AudioSegment.from_file(input_file, format="ogg")

    # Export as .mp3
    audio.export(output_file, format="mp3")
    # Run the ffmpeg command to convert .oga to .mp3
    #subprocess.run(["ffmpeg", "-i", input_file, "-codec:a", "libmp3lame", "-qscale:a", "2", output_file])


def oga_2_mp3_2_text(filename):

    oga_2_mp3(filename)
    openai.api_key = OPENAI_API_KEY

    audio_file_path = f"{filename}.mp3"
    transcript = None

    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file, language="en")
            print(transcript)
            print(transcript.text)
    except Exception as e:
        print(f"Transcription failed: {str(e)}")

    # Delete audio files if the transcription was successful
    if transcript:
        os.remove(audio_file_path)
        os.remove(f"{filename}.ogg")
        print("Audio files deleted.")

    return transcript.text if transcript else ""
import whisper
model = whisper.load_model("base")


def speech_to_text(audio_file_path):
    return model.transcribe(audio_file_path)['text']

import base64
import subprocess

def base64_to_audio(base64_data, output_file_path="output.wav"):
    # try:
        # Decode Base64 data to binary
        audio_bytes = base64.b64decode(base64_data)

        # Use subprocess to run FFmpeg with the binary data as input
        ffmpeg_command = [
            "ffmpeg",
            "-f", "s16le",  # Input format as 32-bit float
            "-ar", "44100",  # Sample rate
            "-ac", "1",  # Mono audio
            "-i", "pipe:0",  # Read from stdin
            "-y",  # Overwrite output file if it exists
            "-f", "s16le",  # Output format as 16-bit signed integer
            output_file_path,  # Output file path
        ]
        # Run FFmpeg with the specified command
        subprocess.run(ffmpeg_command, input=audio_bytes, check=True)

        print(f"Successfully converted and saved to {output_file_path}")
    # except Exception as e:
        # print(f"Error converting Base64 to audio: {str(e)}")
