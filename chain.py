# define chain components
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.prompts.prompt import PromptTemplate
from database import save_message_to_db, connect_to_db
import os 
from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv
import openai
from embeddings import ChromaHandler
# Load environment variables from .env file
load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")

def chain_setup(user_id, user_name):
    # get history msg and add it to memmory
    memory = ConversationBufferMemory()

    _, message_history, _, _ = connect_to_db()

    conv = message_history.find_one({'user_id': user_id})
    
    if conv:
        messages = conv['messages']

        # Calculate how many messages are available
        num_messages = len(messages)
    
        # Start index for messages to be added
        start_index = max(num_messages - 5, 0)

        # Add messages to memory
        for i in range(start_index, num_messages):
            # Get message
            message = messages[i]

            #check if it is user/bot msg
            if 'user' in message:
                memory.chat_memory.add_user_message(message['user'])
            elif 'bot' in message:
                memory.chat_memory.add_ai_message(message['bot'])
    else:
        print("No previous conversation history found for this user.")


    chat = ChatOpenAI(temperature=0.5,
                      openai_api_key=os.getenv("OPENAI_API_KEY"))

    
    memory.ai_prefix = 'Professor'
    memory.human_prefix = 'Student'
    template = """

    You are as a role of my professor, now lets start with the following requirements:
    1/ your name is Adam, 35 years old, you work as an English professor
    2/ My name is """+ user_name +"""
    4/ don't be overly enthusiastic, don't be cringe; don't be overly negative, don't be too boring.

                                                                    
    Current conversation:
    {history}
    Student: {input}
    Professor: 
    """

    prompt = PromptTemplate(input_variables=["history", "input"], template=template)


    conversation = ConversationChain(
        prompt=prompt,
        llm=chat, 
        verbose=True, 
        memory=memory
        )
    
    return conversation
    
def return_context(query):
    handler = ChromaHandler(path="./chroma_doc")
    results = handler.get_or_query_collection(doc_id="google",query_texts=query, n_results=5)
    context = ""
    for row in results['documents'][0]:
        context += row
    return context

def get_chain_response(user_id, user_text, user_name):
      context = return_context(user_text)
      query = "Use this context: \n" + context + "( if it is related)to answer this " + user_text
      conv_chain = chain_setup(user_id=user_id, user_name=user_name)
      out = conv_chain(query)
      print(out['history'])
      return out['response']

 