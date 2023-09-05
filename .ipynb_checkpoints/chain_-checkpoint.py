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

import chromadb  # Assuming that's the import path
from typing import Optional, Dict
import json
class ChromaHandler:
    def __init__(self, path="./chroma"):
        # Initialize a persistent client
        self.client = chromadb.PersistentClient(path=path)
    
    def add_user_data_to_collection(self, user_id: str):
        print("add user data to collection")
        """Read a user's data from their file and add to their collection."""
        data = self.read_doc_file(user_id)
        print("data", data)
        documents = []
        # Separate the user_prompt and completion pairs into individual lists
        for item in data:
            documents.append(item)
        # Generate ids and metadatas based on the index
        ids = [f"{user_id}_{i}" for i in range(len(data))]
        metadatas = [{"index": i} for i in range(len(data))]
        collection = self.client.get_or_create_collection(user_id)
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
    def collection_exists(self, user_id: str) -> bool:
        print("collection exists ?")
        """Check if a collection exists for a given user_id."""
        collections = self.list_all_collections()
        return user_id in [collection.name for collection in collections]

    def get_or_query_collection(self, doc_id: str, query_texts: str, n_results: int):
        """Get or create and query a collection for a given user_id."""
        print("get or query collection")
        if not self.collection_exists(doc_id):
            print("collection does not exist")
            self.add_user_data_to_collection(doc_id)
        print("collection exists or continue")
        # Now, the collection either exists or has just been created
        collection = self.client.get_collection(doc_id)
        print("collection", collection)
        # Place your query logic here, for example:
        results = collection.query(query_texts=query_texts, n_results=n_results, include=["documents"])
        return results
    
    def create_document_collection(self, doc_id: str, metadata: Optional[Dict[str, str]] = None):
        """Create a collection for a specific user using their user_id."""
        collection_name = str(doc_id)  # Ensuring the user_id is in string format for collection name
        return self.client.get_or_create_collection(collection_name, metadata=metadata)
    
    def list_all_collections(self):
        """List all collections."""
        return self.client.list_collections()
    

    def read_doc_file(self, doc_id: str) -> list:
        """Read a user's JSON file and return the 'internal' data."""
        with open(f"./doc_cache/{doc_id}.txt", 'r') as file:
            # data = json.load(file)
            data = file.readlines()
        return data
    def add_doc_data_to_collection(self, doc_id: str):
        print("add user data to collection")
        """Read a user's data from their file and add to their collection."""
        data = self.read_doc_file(doc_id)
        # print("data", data)
        documents = []
        # Separate the user_prompt and completion pairs into individual lists
        for row in data:
            documents.append(row)
        # Generate ids and metadatas based on the index
        ids = [f"{doc_id}_{i}" for i in range(len(data))]
        metadatas = [{"index": i} for i in range(len(data))]
        collection = self.client.get_or_create_collection(doc_id)
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
# Load environment variables from .env file
load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")

def chain_setup(user_id, user_name):
    # get history msg and add it to memmory
    handler = ChromaHandler(path="./chroma")

    context = handler.get_or_query_collection("google", "customized financial budgets", 5)
    memory = ConversationBufferMemory()
    query_context = ""
    for row in context:
        query_context += row
    print("query_context: ", query_context)
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
        memory.chat_memory.add_user_message("use this")
        memory.chat_memory.add_ai_message(query_context)
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


def get_chain_response(user_id, user_text, user_name):
      conv_chain = chain_setup(user_id=user_id, user_name=user_name)
      out = conv_chain(user_text)
      print(out['history'])
      return out['response']

 