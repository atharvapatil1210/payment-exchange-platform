from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bson.objectid import ObjectId
from pymongo import MongoClient
from typing import Optional, List
from datetime import datetime

# Initialize FastAPI app
app = FastAPI()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["p2p_exchange"]
users_collection = db["users"]
transactions_collection = db["transactions"]

# Pydantic models
class User(BaseModel):
    name: str
    amount: float
    type: str  # "cash-to-online" or "online-to-cash"
    contact_info: dict

class MatchRequest(BaseModel):
    user_id: str

class TransactionCompleteRequest(BaseModel):
    transaction_id: str

class Message(BaseModel):
    transaction_id: str
    sender: str
    message: str

# Helper functions
def serialize_user(user):
    user["_id"] = str(user["_id"])
    return user

def serialize_transaction(transaction):
    transaction["_id"] = str(transaction["_id"])
    return transaction

# Endpoints
@app.post("/register")
def register_user(user: User):
    user_dict = user.dict()
    user_dict["verified"] = False  # Default verification status
    user_id = users_collection.insert_one(user_dict).inserted_id
    return {"message": "User registered successfully", "user_id": str(user_id)}

@app.post("/match")
def find_match(request: MatchRequest):
    user = users_collection.find_one({"_id": ObjectId(request.user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    match_type = "online-to-cash" if user["type"] == "cash-to-online" else "cash-to-online"
    tolerance = 50  # Set matching tolerance level

    match = users_collection.find_one({
        "type": match_type,
        "amount": {"$gte": user["amount"] - tolerance, "$lte": user["amount"] + tolerance},
        "verified": True
    })

    if match:
        transaction = {
            "user1": user["_id"],
            "user2": match["_id"],
            "amount": user["amount"],
            "status": "pending",
            "messages": []
        }
        transaction_id = transactions_collection.insert_one(transaction).inserted_id

        return {
            "message": "Match found!",
            "user1": serialize_user(user),
            "user2": serialize_user(match),
            "amount": user["amount"],
            "transaction_id": str(transaction_id)
        }
    else:
        return {"message": "No match found."}

@app.post("/complete_transaction")
def complete_transaction(request: TransactionCompleteRequest):
    transaction = transactions_collection.find_one({"_id": ObjectId(request.transaction_id)})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transactions_collection.update_one(
        {"_id": ObjectId(request.transaction_id)},
        {"$set": {"status": "completed"}}
    )
    return {"message": "Transaction completed successfully"}

@app.post("/verify_user")
def verify_user(user_id: str):
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"verified": True}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User verified successfully"}

@app.post("/send_message")
def send_message(message: Message):
    transaction = transactions_collection.find_one({"_id": ObjectId(message.transaction_id)})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transactions_collection.update_one(
        {"_id": ObjectId(message.transaction_id)},
        {"$push": {"messages": {
            "sender": message.sender,
            "message": message.message,
            "timestamp": datetime.utcnow()
        }}}
    )
    return {"message": "Message sent successfully"}

@app.get("/get_messages/{transaction_id}")
def get_messages(transaction_id: str):
    transaction = transactions_collection.find_one({"_id": ObjectId(transaction_id)})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"messages": transaction.get("messages", [])}
