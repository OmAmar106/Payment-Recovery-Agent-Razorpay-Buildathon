from payments.db import db, Payment

def predict(current):
    # print(current)
    # print(1)
    # return {}
    # print(current['parameters'][12])
    error = db.query(Payment).filter(Payment.payment_id==current['payment_id']).first().error_reason
    payments = db.query(Payment).filter(
        Payment.error_reason == error
    ).all()

    s = set()
    s1 = set()

    for payment in payments:
        if payment.status == "captured":
            s.add(payment.order_id)
        else:
            s1.add(payment.order_id)

    s &= s1
    successful = len(s)
    unsuccessful = len(s1)-len(s)

    alpha = unsuccessful + 1
    beta = successful + 1

    probability_intervention_better = alpha / (alpha + beta)
    probability_intervention_not_better = beta / (alpha + beta)

    return {
        "[EMAIL/HUMAN_ESCALATION]_might_be_better": probability_intervention_better,
        "[EMAIL/HUMAN_ESCALATION]_might_not_be_better": probability_intervention_not_better
    }