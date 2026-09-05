# Payment Recovery Agent

An AI-powered payment recovery agent built for the **Razorpay Buildathon**.

When a payment fails, merchants usually lose revenue because the customer is simply shown an error and left to figure out what to do next.

**Payment Recovery Agent turns payment failures into automated recovery opportunities.**

It listens to Razorpay payment events through webhooks, analyzes the failure context using an AI model, decides the appropriate recovery action, and communicates with the customer.

## Design

<img width="4777" height="2786" alt="System-Design-Payment-Recovery-Agent" src="https://github.com/user-attachments/assets/5a82cd83-17d6-40e9-a056-5ccf40c85690" />

## Problem

Payment failures are common, but most payment flows handle them poorly.

A failed transaction can happen because of:

* Bank declines
* Insufficient funds
* Payment method issues
* Network failures
* Authentication problems
* Temporary failures
* Other payment-provider errors

The traditional experience is usually:

```text
Payment Failed
     ↓
Try Again
```

That puts the entire burden on the customer.

The merchant gets no intelligent recovery strategy, and potentially recoverable revenue is lost.

## Solution

Payment Recovery Agent adds an AI decision layer on top of Razorpay payment events.

Instead of blindly sending the same message for every failure, the agent determines what should happen based on the payment context.

For example:

```json
{
  "action": "EMAIL",
  "delay": 0,
  "message": "Your bank declined the netbanking payment. Please try an alternative payment method."
}
```

The AI response is structured so that the backend can execute the decision programmatically.

## Architecture

```text
                 ┌──────────────────┐
                 │     Customer     │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │    Razorpay      │
                 │     Payment      │
                 └────────┬─────────┘
                          │
                    Payment Event
                          │
                          ▼
                 ┌──────────────────┐
                 │ Razorpay Webhook │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │     FastAPI      │
                 │     Backend      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   AI Decision    │
                 │      Layer       │
                 └────────┬─────────┘
                          │
                    Structured JSON
                          │
                          ▼
             ┌─────────────────────────┐
             │    Recovery Action      │
             │                         │
             │ EMAIL / DELAY / ...     │
             └────────────┬────────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │     Customer     │
                 │   Notification   │
                 └──────────────────┘
```

## Tech Stack

### Backend

* Python
* FastAPI
* Uvicorn
* Razorpay APIs and webhooks
* AI API for payment recovery decisions

### Frontend

* HTML
* CSS
* JavaScript
* Python HTTP server for local development

### Development / Testing

* ngrok for exposing the local webhook endpoint to Razorpay

## Running Locally

### 1. Start the frontend

```bash
cd frontend
python -m http.server 5500
```

The frontend will be available at:

```text
http://localhost:5500
```

### 2. Start the backend

Open another terminal:

```bash
cd backend
uvicorn main:app --reload
```

The FastAPI backend will run on:

```text
http://localhost:8000
```

### 3. Expose the webhook

Razorpay needs to reach your locally running backend.

Start ngrok:

```bash
ngrok http 8000
```

ngrok will provide a public HTTPS URL.

Use the generated URL as the base for the Razorpay webhook endpoint.

For example:

```text
https://<your-ngrok-domain>/webhook/razorpay
```

## Razorpay Webhooks

The application uses Razorpay webhooks to react to payment lifecycle events.

The webhook endpoint receives the payment event and passes the relevant payment information to the recovery agent.

The general flow is:

```text
Razorpay
   ↓
POST /webhook/razorpay
   ↓
Validate / process event
   ↓
Extract payment information
   ↓
Send context to AI
   ↓
Receive structured recovery decision
   ↓
Execute action
```

This allows the recovery logic to operate automatically instead of requiring a merchant to manually inspect failed payments.

## AI Decision Layer

The AI is instructed to return a structured JSON response that the backend can consume directly.

The response contains fields such as:

```json
{
  "action": "EMAIL",
  "delay": 0,
  "message": "Your bank declined the netbanking payment. Please try an alternative payment method."
}
```
