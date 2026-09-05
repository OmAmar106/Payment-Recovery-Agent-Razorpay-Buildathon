import random
from agent.agent_call import ag_call
from model.bayesian_model import predict

def solution(current,existing):
    text = str(current)+'\n'+str(existing)
    probablity = predict(current)
    # return {}
    print(probablity)

    ans = ag_call(text+'\nProbablity of fixing:'+'\n'+str(probablity))

    print(ans)
    return ans