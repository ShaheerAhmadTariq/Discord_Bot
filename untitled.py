import os
import json
import requests
from helpers import get_cache_history, remove_special, update_cache_history, delete_last_message_cache_history
SERVER = os.environ.get('SERVER')

def get_character_data(user_id, character):
    # set the charcter by loading the json file
   with open(f'characters/{character}.json') as read_file:
        data = json.load(read_file)
        file_name = character
        char_name = data['char_name']
        char_greeting = data['char_greeting']
        char_persona = data['char_persona']
        example_dialogue = data['example_dialogue'].replace("{{user}}", "You").replace("{{char}}", char_name)
        context = (f'{char_persona}\n<START>\n{example_dialogue}\n')
        history = get_cache_history(user_id)
        return {'file_name': file_name, 'char_name': char_name, 'char_greeting': char_greeting, 'char_persona': char_persona, 'example_dialogue': example_dialogue, 'context': context, 'history': history}

def get_prompt(user, regenerate, character_data):
    with open(f'settings.json') as read_file:
        params = json.load(read_file) 
    # character_data['history'] = get_user_history(user.id)
    print("char data",character_data['history'])
    #Generation parameters are set in settings.json file... atleast most of them are....
    request = {
        'user_input': user.content,
        'history': character_data['history'],
        'mode': 'chat',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'character': character_data['file_name'],
        'instruction_template': 'None', #I'm really not sure why we have instruction templates now...
        'your_name': user.author.display_name,

        'regenerate': regenerate,
        '_continue': False,
        'stop_at_newline': params['stop_generating_at_new_line'],
        'chat_prompt_size': 2048,
        'chat_generation_attempts': params['generation_attempts'],
        'chat-instruct_command': 'Continue the chat dialogue below. Write a single reply for the character "<|character|>".\n\n<|prompt|>',

        'max_new_tokens': params['max_new_tokens'],
        'do_sample': params['do_sample'],
        'temperature': params['temperature'],
        'top_p': params['top_p'],
        'typical_p': params['typical_p'],
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'repetition_penalty': params['repetition_penalty'],
        'top_k': params['top_k'],
        'min_length': params['min_length'],
        'no_repeat_ngram_size': params['no_repeat_ngram_size'],
        'num_beams': params['num_beams'],
        'penalty_alpha': params['penalty_alpha'],
        'length_penalty': params['length_penalty'],
        'early_stopping': params['early_stopping'],
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,
        'seed': -1, #-1 for random seed
        'add_bos_token': True,
        'truncation_length': 2048,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': ['You:', f'{user.author.display_name}:', '</START>', '<START>', '<']
    }
    return request
def get_prompt_regen(user_id, user_name, user_message, character_data):
    with open(f'settings.json') as read_file:
        params = json.load(read_file) 
    # character_data['history'] = get_user_history(user.id)
    print("char data",character_data['history'])
    #Generation parameters are set in settings.json file... atleast most of them are....
    request = {
        'user_input': user_message,
        'history': character_data['history'],
        'mode': 'chat',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'character': character_data['file_name'],
        'instruction_template': 'None', #I'm really not sure why we have instruction templates now...
        'your_name': user_name,

        'regenerate': True,
        '_continue': False,
        'stop_at_newline': params['stop_generating_at_new_line'],
        'chat_prompt_size': 2048,
        'chat_generation_attempts': params['generation_attempts'],
        'chat-instruct_command': 'Continue the chat dialogue below. Write a single reply for the character "<|character|>".\n\n<|prompt|>',

        'max_new_tokens': params['max_new_tokens'],
        'do_sample': params['do_sample'],
        'temperature': params['temperature'],
        'top_p': params['top_p'],
        'typical_p': params['typical_p'],
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'repetition_penalty': params['repetition_penalty'],
        'top_k': params['top_k'],
        'min_length': params['min_length'],
        'no_repeat_ngram_size': params['no_repeat_ngram_size'],
        'num_beams': params['num_beams'],
        'penalty_alpha': params['penalty_alpha'],
        'length_penalty': params['length_penalty'],
        'early_stopping': params['early_stopping'],
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,
        'seed': -1, #-1 for random seed
        'add_bos_token': True,
        'truncation_length': 2048,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': ['You:', f'{user_name}:', '</START>', '<START>', '<']
    }
    return request
async def generate_response(user):
    character_data = get_character_data(user.author.id, "main_joe-rogan_json")
    prompt = get_prompt(user, False, character_data)
    send_gen_request = requests.post(f"{SERVER}/api/v1/chat", json=prompt) 
    if send_gen_request.status_code == 200:
        result = send_gen_request.json()['results'][0]['history']
        response_text = remove_special(result['visible'][-1][1])
        print("result visible",result['visible'][-1][1])
        print("result: ",result)
        character_data['history'] = result

        print(f"{character_data['char_name']}(AI) responded: {str(response_text)}")
        update_cache_history(user.author.id, result)
        return response_text
    else:
        print (f"Error: {send_gen_request.status_code}")
        return "Error: " + str(send_gen_request.status_code)
    
async def regenerate_message_llm(user_id, user):
    character_data = get_character_data(user_id, "main_joe-rogan_json")
    cache_history = get_cache_history(user_id)
    message = cache_history['visible'][-1][0]
    delete_last_message_cache_history(user_id)
    prompt = get_prompt_regen(user_id,user['user_name'] , message, character_data)
    send_gen_request = requests.post(f"{SERVER}/api/v1/chat", json=prompt) 
    if send_gen_request.status_code == 200:
        result = send_gen_request.json()['results'][0]['history']
        response_text = remove_special(result['visible'][-1][1])
        print("result visible",result['visible'][-1][1])
        print("result: ",result)
        character_data['history'] = result

        print(f"{character_data['char_name']}(AI) responded: {str(response_text)}")
        update_cache_history(user_id, result)

        return response_text
    else:
        print (f"Error: {send_gen_request.status_code}")
        return "Error While regeneratnig " 
    