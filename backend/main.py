import os
import razorpay
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import payments.payment as payment
from mail.send_mail import send_mail

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

connections = {}

@app.websocket("/ws/{order_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    order_id: str
):
    await websocket.accept()
    connections[order_id] = websocket
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.pop(order_id, None)

async def send_to_client(order_id, data):
    websocket = connections.get(order_id)

    if websocket:
        await websocket.send_json(data)

@app.post("/create-order")
def create_order():
    order = client.order.create({
        "amount": 50000,
        "currency": "INR",
        "receipt": "receipt_001"
    })
    return order

WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

@app.post("/webhook/razorpay")
async def razorpay_webhook(request: Request):

    body = await request.body()
    signature = request.headers.get(
        "X-Razorpay-Signature"
    )

    if not signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Razorpay signature"
        )

    try:
        client.utility.verify_webhook_signature(
            body.decode("utf-8"),
            signature,
            WEBHOOK_SECRET
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook signature"
        )

    data = await request.json()

    order_id, result = payment.process_payment(data)

    if result and result.get("action"):
        # print(result)
        if result['action']=='EMAIL':
            # del = result['delay']
            try:send_mail(data,result)
            except:pass
        else:   
            await send_to_client(order_id, result)

    return {"status": "ok"}