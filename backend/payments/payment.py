from payments.db import save_payment, get_payments_by_order, save_event

def process_payment(data):
    event = data.get("event")

    if not event:
        return {
            "success": False,
            "reason": "missing_event"
        }

    payload = data.get("payload", {})
    payment_payload = payload.get("payment", {})
    payment = payment_payload.get("entity")

    if not payment:
        return {
            "success": False,
            "reason": "missing_payment_entity"
        }

    payment_id = payment.get("id")
    order_id = payment.get("order_id")

    if not payment_id:
        return {
            "success": False,
            "reason": "missing_payment_id"
        }

    event_created_at = data.get("created_at")

    save_event(
        event=event,
        payment_id=payment_id,
        order_id=order_id,
        event_created_at=event_created_at,
        raw_data=data
    )

    existing_payments = get_payments_by_order(order_id)

    if event == "payment.failed":
        return process_failed_payment(
            payment=payment,
            existing_payments=existing_payments
        )

    if event == "payment.captured":
        return process_captured_payment(
            payment=payment,
            existing_payments=existing_payments
        )

    return

def process_failed_payment(
    payment,
    existing_payments
):
    payment_id = payment["id"]

    failed_payments = [
        p for p in existing_payments
        if p.status == "failed"
    ]

    failure_count = len(failed_payments) + 1

    first_failed_at = payment.get("created_at")

    if failed_payments:
        first_failed_at = (
            failed_payments[0].first_failed_at
            or failed_payments[0].created_at
        )

    payment_data = {
        "payment_id": payment_id,
        "order_id": payment.get("order_id"),
        "amount": payment.get("amount"),
        "currency": payment.get("currency"),
        "status": "failed",
        "method": payment.get("method"),
        "email": payment.get("email"),
        "contact": payment.get("contact"),
        "bank": payment.get("bank"),
        "wallet": payment.get("wallet"),
        "vpa": payment.get("vpa"),
        "error_code": payment.get("error_code"),
        "error_description": payment.get("error_description"),
        "error_source": payment.get("error_source"),
        "error_step": payment.get("error_step"),
        "error_reason": payment.get("error_reason"),
        "created_at": payment.get("created_at"),
        "first_failed_at": first_failed_at,
        "failure_count": failure_count,
        "was_recovered": 0,
        "raw_data": payment
    }

    save_payment(payment_data)

    return {
        "success": True,
        "event": "payment.failed",
        "payment_id": payment_id,
        "order_id": payment.get("order_id"),
        "status": "failed",
        "recovered": False
    }

def process_captured_payment(
    payment,
    existing_payments
):
    payment_id = payment["id"]

    failed_payments = [
        p for p in existing_payments
        if p.status == "failed"
    ]

    recovered = len(failed_payments) > 0

    payment_data = {
        "payment_id": payment_id,
        "order_id": payment.get("order_id"),
        "amount": payment.get("amount"),
        "currency": payment.get("currency"),
        "status": "captured",
        "method": payment.get("method"),
        "email": payment.get("email"),
        "contact": payment.get("contact"),
        "bank": payment.get("bank"),
        "wallet": payment.get("wallet"),
        "vpa": payment.get("vpa"),
        "error_code": None,
        "error_description": None,
        "error_source": None,
        "error_step": None,
        "error_reason": None,
        "created_at": payment.get("created_at"),
        "captured_at": payment.get("created_at"),
        "first_failed_at": (
            failed_payments[0].first_failed_at
            if failed_payments
            else None
        ),
        "failure_count": len(failed_payments),
        "was_recovered": int(recovered),
        "raw_data": payment
    }

    save_payment(payment_data)

    if recovered:
        update_ml_model(
            previous_failures=failed_payments,
            successful_payment=payment
        )

    return {
        "success": True,
        "event": "payment.captured",
        "payment_id": payment_id,
        "order_id": payment.get("order_id"),
        "status": "captured",
        "recovered": recovered,
        "previous_failures": len(failed_payments)
    }

def process_other_payment(
    payment,
    existing_payments
):
    failed_payments = [
        p for p in existing_payments
        if p.status == "failed"
    ]

    payment_data = {
        "payment_id": payment["id"],
        "order_id": payment.get("order_id"),
        "amount": payment.get("amount"),
        "currency": payment.get("currency"),
        "status": payment.get("status"),
        "method": payment.get("method"),
        "email": payment.get("email"),
        "contact": payment.get("contact"),
        "bank": payment.get("bank"),
        "wallet": payment.get("wallet"),
        "vpa": payment.get("vpa"),
        "error_code": payment.get("error_code"),
        "error_description": payment.get("error_description"),
        "error_source": payment.get("error_source"),
        "error_step": payment.get("error_step"),
        "error_reason": payment.get("error_reason"),
        "created_at": payment.get("created_at"),
        "first_failed_at": (
            failed_payments[0].first_failed_at
            if failed_payments
            else None
        ),
        "failure_count": len(failed_payments),
        "was_recovered": int(
            any(p.was_recovered for p in existing_payments)
        ),
        "raw_data": payment
    }

    save_payment(payment_data)

    return {
        "success": True,
        "event": "other",
        "payment_id": payment["id"],
        "status": payment.get("status")
    }


def update_ml_model(
    previous_failures,
    successful_payment
):
    print("ML UPDATE")
    print(
        "Successful payment:",
        successful_payment.get("id")
    )

    for payment in previous_failures:
        print(
            "Previous payment:",
            payment.payment_id
        )
        print(
            "Previous error:",
            payment.error_code
        )
        print(
            "Previous reason:",
            payment.error_reason
        )