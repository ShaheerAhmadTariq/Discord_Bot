import chromadb  # Assuming that's the import path
from typing import Optional, Dict
import json
class ChromaHandler:
    def __init__(self, path="./chroma"):
        # Initialize a persistent client
        self.client = chromadb.PersistentClient(path=path)
   
    def collection_exists(self, user_id: str) -> bool:
        print("collection exists ?")
        """Check if a collection exists for a given user_id."""
        collections = self.list_all_collections()
        return user_id in [collection.name for collection in collections]
    
    def update_user_data_to_collection(self, user_id: str):
        """Read a user's data from their file and add to their collection. 
        If new_data is provided, append it to the collection."""
        
        # If new_data is not provided, read from user's file
        collection = self.client.get_collection(user_id)
        print("collection count: ", collection.count())
        # return
        data = self.read_user_file(user_id)
        documents = []
        for item in data:
            line1 = item[0].strip()
            line2 = item[1].strip()
            documents.append(line1 + " ~~~ " + line2)

        # Get the current number of entries in the collection to offset the new IDs
        current_entries = collection.count()
        documents = documents[current_entries:]
        ids = [f"{user_id}_{i + current_entries}" for i in range(len(documents))]
        metadatas = [{"index": i + current_entries} for i in range(len(documents))]

        # collection = self.client.get_or_create_collection(str(user_id))
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        
    async def get_or_query_collection(self, user_id: str, query_texts: str, n_results: int):
        """Get or create and query a collection for a given user_id."""
        print("get or query collection")
        if not self.collection_exists(user_id):
            print("collection does not exist")
            self.add_user_data_to_collection(user_id)
        print("collection exists or continue")
        # Now, the collection either exists or has just been created
        collection = self.client.get_collection(user_id)
        print("collection", collection)
        # Place your query logic here, for example:
        results = collection.query(query_texts=query_texts, n_results=n_results, include=["documents"])
        return results
    def create_user_collection(self, user_id: str, metadata: Optional[Dict[str, str]] = None):
        """Create a collection for a specific user using their user_id."""
        collection_name = str(user_id)  # Ensuring the user_id is in string format for collection name
        return self.client.get_or_create_collection(collection_name, metadata=metadata)
    
    def list_all_collections(self):
        """List all collections."""
        return self.client.list_collections()
    
    def add_to_user_collection(self, user_id: str, ids: list, embeddings=None, metadatas=None, documents=None):
        """Add data to a user's collection."""
        collection = self.client.get_or_create_collection(user_id)
        collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)

    def query_user_collection(self, user_id: str, query_texts: list, n_results=10):
        """Query a user's collection for nearest neighbors to the given texts."""
        collection = self.client.get_or_create_collection(user_id)
        return collection.query(query_texts=query_texts, n_results=n_results)

    def delete_from_user_collection(self, user_id: str, ids: list):
        """Delete specified ids from a user's collection."""
        collection = self.client.get_or_create_collection(user_id)
        collection.delete(ids=ids)

    async def read_user_file(self, user_id: str) -> list:
        """Read a user's JSON file and return the 'internal' data."""
        with open(f"./history_cache/history_{user_id}.json", 'r') as file:
            data = json.load(file)
        return data.get("internal", [])
    def add_user_data_to_collection(self, user_id: str):
        print("add user data to collection")
        """Read a user's data from their file and add to their collection."""
        data = self.read_user_file(user_id)
        # print("data", data)
        documents = []
        # Separate the user_prompt and completion pairs into individual lists
        for item in data:
            line1 = item[0].strip()
            line2 = item[1].strip()
            documents.append(line1 + " ~~~ " + line2)
        # Generate ids and metadatas based on the index
        ids = [f"{user_id}_{i}" for i in range(len(data))]
        metadatas = [{"index": i} for i in range(len(data))]
        collection = self.client.create_collection(str(user_id))
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
    
    def query_user_collection_with_completions(self, user_id: str, query_text: str, n_results=10):
        """Query a user's collection and return user_prompt and completion pairs."""
        collection = self.client.get_collection(user_id)
        results = collection.query(query_texts=[query_text], n_results=n_results, include=["documents"])
        return results

