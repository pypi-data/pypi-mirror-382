<p align="center">
  <a rel="nofollow">
    <img alt="modrl" src="assets/modrl.png" width="35%">
  </a>
</p>

<p align="center">
  <a href="https://twallett.com/courses/reinforcement-learning/">
    <img alt="RL Course" src="https://img.shields.io/badge/docs-Course%20Website-success.svg">
  </a>
  <a href="https://python.org/">
    <img alt="Language: Python" src="https://img.shields.io/badge/language-Python-orange.svg">
  </a>
  <a href="https://spdx.org/licenses/MIT.html">
    <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue.svg">
  </a>
<!-- <a href="https://join.slack.com/t/hydrogym/shared_invite/zt-27u914dfn-UFq3CkaxiLs8dwZ_fDkBuA"><img alt="Slack" src="https://img.shields.io/badge/slack-hydrogym-brightgreen.svg?logo=slack"></a> -->
</p>

## The motivation behind `modrl`

•	**Modular Reinforcement Learning Framework** — Unlike many RL libraries that run monolithic end-to-end experiments, `modrl` emphasizes modularity. Its components—such as `modrl.agents`, `modrl.bandits`, and `modrl.policies`—are designed to be interchangeable, enabling users to mix, match, and customize elements for their own research or teaching use cases.

•	**Seamless gymnasium Integration** — `modrl` is fully compatible with the OpenAI `gymnasium` API, making it straightforward to test algorithms across a wide range of established environments.

•	**Educational Alignment** — Every algorithm implementation in modrl is directly tied to specific chapters in the [Reinforcement Learning](https://twallett.com/courses/reinforcement-learning/) Quarto book, making it a hands-on learning tool for students and instructors alike.

•	**Designed for Research and Experimentation** — The library’s modular design facilitates rapid prototyping and experimentation, supporting both academic research and practical exploration of new algorithmic ideas.

•	**Open Source and Community-Driven** — `modrl` welcomes open source contributions, encouraging collaboration to expand functionality, improve documentation, and advance the broader reinforcement learning ecosystem.

## How to install `modrl`?

Run the following pip command:

```bash
pip install modrl
```

## `modrl` repository structure

Version 0.0.1 (Demo):

```bash
.
├── __init__.py
├── bandits
│   ├── classical
│   │   └── egreedy.py
│   └── contextual
└── evaluation
    └── regret.py
```

Version 0.0.2:

```bash
.
├── __init__.py
├── agents
│   ├── classical
│   │   ├── onp-monte-carlo.py # available but not implemented yet
│   │   ├── offp-monte-carlo.py # available but not implemented yet
│   │   ├── td-sarsa.py # available but not implemented yet
│   │   ├── td-q.py # available but not implemented yet
│   │   ├── td-doubleq.py # available but not implemented yet
│   │   ├── n-offp-sarsa.py # available but not implemented yet
│   │   └── n-tree.py # available but not implemented yet
│   └── deep
│       ├── semi-gradient-sarsa.py # available but not implemented yet
│       ├── dqn.py # available but not implemented yet
│       ├── vpg.py # available but not implemented yet
│       └── ppo.py # available but not implemented yet
├── bandits
│   ├── classical
│   │   ├── epsilon-greedy.py 
│   │   ├── ucb.py # available but not implemented yet
│   │   ├── thompson-sampling.py # available but not implemented yet
│   │   ├── gradient-bandit.py # available but not implemented yet
│   │   └── exp3.py # available but not implemented yet
│   └── contextual
│       └── linucb.py # available but not implemented yet
├── evaluation
│   ├── regret.py
│   └── cum-rew.py # available but not implemented yet
├── nn
│   ├── mlp.py # available but not implemented yet
│   └── cnn.py # available but not implemented yet
├── policies
│   ├── softmax.py # available but not implemented yet
│   └── e-soft.py # available but not implemented yet
└── utils
    ├── replay-buffer.py # available but not implemented yet
    └── epsilon-scheduler.py # available but not implemented yet
```

## Requirements

```bash
pip install requirements.txt
```

<!-- ## Citation 

If you use `modrl` in your research, please cite the following paper:

```bibtex

``` -->