from database import *
def check_user(user_id, user_name):
    found, user = get_user(user_id)
    if not found:
        print("User not found in database.")
        found_free, user_free = get_user_free(user_id)
        if found_free:
            if user_free['left'] >= 0:
                update_user_free(user_id, user_free['left'] - 1)
                # 
                return True, {'message':""}
            else:
                # return await message.reply(embed=embed, view=view)
                return False,"You have used all your free messages, please subscribe to continue using the bot."
        else:
            print("Not found in Free Trial, adding 5 messages")
            create_user_free(user_id)
            update_user_free(user_id, 4)
            save_preferences_to_db(user_id, user_name ,False)
            return True, {'message':""}
        # return await message.reply(embed=embed, view=view)
    else:
        if not user['payment_status']:
            return False, "You have used all your credets, please subscribe to continue using the bot."
        # Calculate the elapsed time since the user started the conversation
        if user['last_message_time'] <= 0:
            update_user(user_id)
            
            return False, "You have used all your credets, please subscribe to continue using the bot."
    create_or_update_user_extra(user_id)
    # Remove the following line if you're not using MongoDB
    _, message_history,_, _ = connect_to_db()
    local_llm = True
    voice_response = False
    found, user_preference = get_preferences(user_id)
    found, user_preference = get_preferences(user_id)
    if not found:
        save_preferences_to_db(user_id, user_name ,False)
    else:
        voice_response = user_preference['voice']

    return True, {'voice_response': voice_response}

def parse_response(str_with_quotes):
    # Remove all double quotations from the beginning
    while str_with_quotes.startswith('"'):
        str_with_quotes = str_with_quotes[1:]

    # Remove all double quotations from the end
    while str_with_quotes.endswith('"'):
        str_with_quotes = str_with_quotes[:-1]

    char_to_remove = ['/', '\\']

    for char in char_to_remove:
        str_with_quotes = str_with_quotes.replace(char, '')

    return str_with_quotes