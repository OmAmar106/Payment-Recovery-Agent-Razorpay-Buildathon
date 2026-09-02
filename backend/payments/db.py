from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json

DATABASE_URL = "sqlite:///payments.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(String, primary_key=True, index=True)
    order_id = Column(String, index=True)

    amount = Column(Integer)
    currency = Column(String)

    status = Column(String)
    method = Column(String)

    email = Column(String)
    contact = Column(String)

    bank = Column(String)
    wallet = Column(String)
    vpa = Column(String)

    error_code = Column(String)
    error_description = Column(Text)
    error_source = Column(String)
    error_step = Column(String)
    error_reason = Column(String)

    created_at = Column(Integer)
    captured_at = Column(Integer)
    first_failed_at = Column(Integer)

    failure_count = Column(Integer, default=0)
    was_recovered = Column(Integer, default=0)

    raw_data = Column(Text)


class PaymentEvent(Base):
    __tablename__ = "payment_events"

    id = Column(Integer, primary_key=True, autoincrement=True)

    event = Column(String, index=True)
    payment_id = Column(String, index=True)
    order_id = Column(String, index=True)

    event_created_at = Column(Integer)
    received_at = Column(DateTime, default=datetime.utcnow)

    raw_data = Column(Text)


Base.metadata.create_all(bind=engine)

db = SessionLocal()

def save_event(
    event,
    payment_id,
    order_id,
    event_created_at,
    raw_data
):
    payment_event = PaymentEvent(
        event=event,
        payment_id=payment_id,
        order_id=order_id,
        event_created_at=event_created_at,
        raw_data=json.dumps(raw_data)
    )

    db.add(payment_event)
    db.commit()

    return payment_event


def get_payments_by_order(order_id):
    return (
        db.query(Payment)
        .filter(Payment.order_id == order_id)
        .order_by(Payment.created_at.asc())
        .all()
    )

def get_payment(payment_id):
    return (
        db.query(Payment)
        .filter(Payment.order_id ==payment_id)
        .order_by(Payment.created_at.asc())
        .all()
    )


def save_payment(payment_data):
    payment = get_payment(
        payment_data["payment_id"]
    )

    if not payment:
        payment = Payment(
            payment_id=payment_data["payment_id"]
        )
        db.add(payment)

    for key, value in payment_data.items():
        if key != "payment_id":
            setattr(payment, key, value)

    if payment_data.get("raw_data") is not None:
        payment.raw_data = json.dumps(
            payment_data["raw_data"]
        )

    db.commit()
    db.refresh(payment)

    return payment


def get_payments_by_order_id(order_id):
    try:
        return (
            db.query(Payment)
            .filter(Payment.order_id == order_id)
            .order_by(Payment.created_at.asc())
            .all()
        )
    finally:
        db.close()