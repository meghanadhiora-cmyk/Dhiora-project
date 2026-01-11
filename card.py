from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Details(BaseModel):
    name: str
    age: int
    aadhar: str
    legacy_id: str
    card_type: str
    status: str

cardholders = []

@app.on_event("startup")
def init_data():
    global cardholders
    cardholders.clear()
    cardholders.extend([
        Details(name="Ravi", age=32, aadhar="123456789012", legacy_id="LEG001", card_type="Debit", status="Active"),
        Details(name="Priya", age=28, aadhar="987654321098", legacy_id="LEG002", card_type="Credit", status="Suspended"),
        Details(name="Arun", age=45, aadhar="456789123456", legacy_id="LEG003", card_type="Debit", status="Active")
    ])

@app.get("/")
def welcome():
    return {"message": "Welcome to Card API"}

@app.get("/details")
def get_all():
    return cardholders

@app.post("/details")
def create(detail: Details):
    cardholders.append(detail)
    return {"msg": "Added"}

@app.put("/details/{id}")
def update(id: str, detail: Details):
    for i, c in enumerate(cardholders):
        if c.legacy_id == id:
            cardholders[i] = detail
            return {"msg": "Updated"}
    raise HTTPException(404, "Not found")

@app.delete("/details/{id}")
def delete(id: str):
    for i, c in enumerate(cardholders):
        if c.legacy_id == id:
            cardholders.pop(i)
            return {"msg": "Deleted"}
    raise HTTPException(404, "Not found")