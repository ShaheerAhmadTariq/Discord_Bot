import os
import json

def check_if_user_exists(user_id):
    with open(f'./user_names.json') as read_file:
        data = json.load(read_file)
        if user_id in data['user']:
            return True
        else:
           return False
def delete_user_from_json(user_id):
    with open('./user_names.json', 'r') as read_file:
        data = json.load(read_file)
        if user_id in data['user']:
            data['user'].remove(user_id)
    with open('./user_names.json', 'w') as write_file:
        json.dump(data, write_file, indent=4)

def add_user_to_user_json(user_id):
    with open('./user_names.json', 'r') as read_file:
        data = json.load(read_file)
        data['user'].append(user_id)
    with open('./user_names.json', 'w') as write_file:
        json.dump(data, write_file, indent=4)
    print("user name appended to user.json")
def create_cache_history(user_id):
    content = {'internal': [['', '*"3,2,1 {{user}} ladies and gentlemen, thank you for doing this. Why don\'t you start by saying what you are known for or whatever you want to talk about?"*']], 'visible': [['', '*"3,2,1 {{user}} ladies and gentlemen, thank you for doing this. Why don\'t you start by saying what you are known for or whatever you want to talk about?"*']]}
    with open(f"./history_cache/history_{user_id}.json", 'w') as file:
        # file.write(content)
        json.dump(content, file, indent=4)
    print(f"created cache for {user_id}")
    return
def get_cache_history(user_id):
    cache_file_path = f"./history_cache/history_{user_id}.json"
    if not os.path.exists(cache_file_path):
        create_cache_history(user_id)
    with open(cache_file_path, 'r') as file:
        data = json.load(file)
    return data
def update_cache_history(filename, content):
    with open(f"./history_cache/history_{filename}.json", 'w') as file:
        json.dump(content, file, indent=4)
def delete_last_message_cache_history(filename):
    with open(f"./history_cache/history_{filename}.json", 'r') as file:
        data = json.load(file)
    data['visible'].pop()
    data['internal'].pop()
    with open(f"./history_cache/history_{filename}.json", 'w') as file:
        json.dump(data, file, indent=4)
def delete_cache_history(user_id):
    content = {'internal': [['', '*"3,2,1 {{user}} ladies and gentlemen, thank you for doing this. Why don\'t you start by saying what you are known for or whatever you want to talk about?"*']], 'visible': [['', '*"3,2,1 {{user}} ladies and gentlemen, thank you for doing this. Why don\'t you start by saying what you are known for or whatever you want to talk about?"*']]}
    with open(f'./history_cache/history_{user_id}.json', 'w') as write_file:
        json.dump(content, write_file, indent=4)
    # print("user name appended to user.json")
    # os.remove(f"./history_cache/history_{user_id}.json")
    print(f"deleted cache for {user_id}")
def remove_special(text):
    output = text.replace('</s>', '')
    return output
def get_conversation_history(user_id):
    if check_if_user_exists(user_id):
        cache_history = get_cache_history(user_id)
        history = '#This data does not contain usernames of senders.\n'
        for prompt in cache_history['visible']:
            history += f'USER: {prompt[0]}\n'
            history += f'AI: {prompt[1]}\n'
        # delete_user_from_json(user_id)  
        return history
    else:
        return "history is empty"
