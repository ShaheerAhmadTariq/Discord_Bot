from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    import json

    # Specify the path to your JSON file
    json_file_path = "./history_1140241431441719306.json"
    
    # Read and parse the JSON file
    with open(json_file_path, "r") as json_file:
        data = json.load(json_file)
    
    # Now 'data' contains the parsed JSON content
    print(data)  # You can process and use 'data' as needed

    return data

@app.get("/items/{item_id}")
def read_item(item_id: int, query_param: str = None):
    return {"item_id": item_id, "query_param": query_param}

@app.post("/items/")
def create_item(item: dict):
    return {"message": "Item created successfully", "item": item}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
