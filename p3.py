from fastapi import FastAPI

app = FastAPI()

data = []
@app.get("/")
def home():
    return {"message": "Basic FastAPI CRUD"}

@app.post("/add")
def add_item(name: str):
    data.append(name)
    return {"added": name}

@app.get("/list")
def list_items():
    return data

@app.put("/update/{index}")
def update_item(index: int, name: str):
    if index < len(data):
        data[index] = name
        return {"updated": name}
    return {"error": "Index out of range"}

@app.delete("/delete/{index}")
def delete_item(index: int):
    if index < len(data):
        removed = data.pop(index)
        return {"deleted": removed}
    return {"error": "Index out of range"}