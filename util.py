from database import update_user_time
from mutagen.mp3 import MP3
import time
def update_time(userTime, start_time, user_id, end_time):
    # end_time = time.time()
    print("end time", end_time, "start time", start_time, "user time", userTime)
    remaining_time = userTime - (end_time - start_time)
    print("remaining time", remaining_time)
    print("remaining_time_int", int(remaining_time))
    update_user_time(user_id, int(remaining_time))

def get_audio_duration(filename):
    try:
        audio = MP3(filename)
        duration_seconds = audio.info.length
        return duration_seconds
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def update_text_time(remaining_u_amount, start_time, user_id, end_time, local_llm, length_of_message):
    # Calculate charge
    if local_llm:
        charge_rate_per_character = 0.005
    else:
        charge_rate_per_character = 0.001
    charge = (charge_rate_per_character * length_of_message) * 60  # converting dollar into minute
    remaining_amount = remaining_u_amount - charge
    print("remaining_time_int", int(remaining_amount))
    update_user_time(user_id, int(remaining_amount))