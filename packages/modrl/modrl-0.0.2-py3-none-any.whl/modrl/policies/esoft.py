import numpy as np 

def esoft(q, state, epsilon, num_actions, return_probabilities=False):
    
    greedy_action = np.argmax(q[state,:])
    
    behavior_probabilities = np.ones(num_actions) * (epsilon / num_actions)
    behavior_probabilities[greedy_action] += (1 - epsilon)
    
    selected_action = np.random.choice(np.arange(num_actions), p=behavior_probabilities)
    
    target_probabilities = np.zeros(num_actions)
    target_probabilities[greedy_action] = 1
    
    if return_probabilities:
        return selected_action, behavior_probabilities, target_probabilities
    else:
        return selected_action