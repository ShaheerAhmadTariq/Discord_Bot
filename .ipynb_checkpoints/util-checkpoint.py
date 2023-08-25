from database import update_user_time
from mutagen.mp3 import MP3
import time
import datetime
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
    
def update_text_time(userTime, start_time, user_id, end_time):
    time_taken_seconds = end_time - start_time
    # Convert time taken to minutes
    time_taken_minutes = time_taken_seconds
    # Calculate charge
    charge_rate_per_minute = 0.5
    charge = charge_rate_per_minute * time_taken_minutes
    remaining_amount = userTime - time_taken_minutes
    print("remaining_time_int", int(remaining_amount))
    update_user_time(user_id, int(remaining_amount))

def is_subscription_active(last_subscription_time):
    now = datetime.datetime.now()
    time_difference = now - last_subscription_time
    return time_difference <= datetime.timedelta(days=30)
