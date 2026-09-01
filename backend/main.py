import os
import razorpay
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = razorpay.Client(
    auth=(
        os.getenv("key_id"),
        os.getenv("key_secret")
    )
)


@app.post("/create-order")
def create_order():

    order = client.order.create({
        "amount": 50000,
        "currency": "INR",
        "receipt": "receipt_001"
    })

    return order