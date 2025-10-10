import numpy as np

class EpsilonGreedy:
    def __init__(self, n_arms, epsilon=0.2, seed=0, manual_prior=None):
        """Initialize the epsilon-greedy bandit with optional prior values."""
        self.rng = np.random.default_rng(seed)
        self.n_arms = n_arms
        self.epsilon = epsilon
        self.actions = []
        self.rewards = []
        self.optimal_rewards = []
        if manual_prior:
            self.q = np.array(manual_prior[0]).reshape((n_arms, 1))
            self.n = np.array(manual_prior[1]).reshape((n_arms, 1))
        else:
            self.q = np.zeros((n_arms, 1))
            self.n = np.zeros((n_arms, 1))
    
    def act(self):
        """Choose an action using epsilon-greedy exploration."""
        if self.rng.random() <= self.epsilon:
            A = self.rng.integers(0, self.n_arms)
            self.actions.append(A)
            return A
        else:
            A = np.argmax(self.q)
            self.actions.append(A)
            return A

    def pull_bandit(self, data, A, t):
        """Pull the selected arm at time t and record the reward."""
        R = data[t][A]
        self.optimal_rewards.append(np.max(data[t]))   
        self.rewards.append(R)
        return R

    def update(self, A, R):
        """Update the estimated value of the chosen arm with the new reward."""
        self.n[A] += 1
        self.q[A] += (1 / self.n[A]) * (R - self.q[A])

    def train(self, data):
        """Run the epsilon-greedy algorithm over the provided dataset."""
        for t in range(len(data)):
            A = self.act()
            R = self.pull_bandit(data, A, t)
            self.update(A, R)
            
    def save(self, path="epsilon_greedy_params.npz"):
        """Save learned parameters and hyperparameters to a file."""
        np.savez(
            path,
            q=self.q,
            n=self.n,
            epsilon=self.epsilon,
            n_arms=self.n_arms,
        )

    @staticmethod
    def load(path):
        """Load saved parameters and return them as a manual_prior tuple."""
        data = np.load(path)
        q_prior = data["q"]
        n_prior = data["n"]
        manual_prior = (q_prior, n_prior)
        return manual_prior