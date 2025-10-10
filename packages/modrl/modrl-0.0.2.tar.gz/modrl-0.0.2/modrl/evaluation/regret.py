import numpy as np

def cumulative_regret(rewards, optimal_reward):
    rewards = np.array(rewards)
    optimal_reward = np.array(optimal_reward)
    regret = np.sum(optimal_reward - rewards)
    return regret