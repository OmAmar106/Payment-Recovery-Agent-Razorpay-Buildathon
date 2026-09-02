# Payment Recovery Agent

Razorpay Buildathon

cd frontend
python -m http.server 5500

cd backend
uvicorn main:app --reload

ngrok http 8000

created a webhook, on payment fail, success etc.
