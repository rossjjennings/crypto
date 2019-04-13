import numpy as np
from ruamel.yaml import YAML
yaml = YAML(typ='safe')

with open('all_counts.yml') as f:
    frequencies = yaml.load(f)
total = sum(frequencies.values())
freq_scores = {k: -np.log(frequencies[k]/total)
               for k in frequencies}
transitions = np.load('transitions.npy')
markov_scores = -np.log(transitions)

def ind(c):
    return 0 if c == ' ' else ord(c.upper()) - 64

def score_freq(cryptogram):
    score = 0
    for c in word:
        if c in freq_scores:
            score += freq_scores[c]
    return score

def score_markov(word):
    score = 0
    prev = 0
    for c in word:
        score += markov_scores[ind(c), prev]
        prev = ind(c)
    score += markov_scores[prev, 0]
    return score
