import random

def solution(current,existing):
    if random.randint(0,1):
        return {
            "action": "RETRY",
            "delay": 10,
            "message": "Please retry your payment in 10 seconds."
        }
    else:
        return {
                "action": "WAIT_AND_RETRY",
                "delay": 10,
                "message": "1"
            }