import numpy as np
from numpy.random import random, randint
from score import score_markov
import subs

def swap(alphabet, ind1, ind2):
    alpha = list(alphabet)
    alpha[ind1], alpha[ind2] = alpha[ind2], alpha[ind1]
    return ''.join(alpha)

def metropolis(cryptogram):
    cur_alpha = subs.alphabet
    cur_guess = cryptogram
    cur_score = score_markov(cryptogram)
    while True:
        ind1 = randint(26)
        ind2 = randint(25)
        if ind2 >= ind1: ind2 += 1
        next_alpha = swap(cur_alpha, ind1, ind2)
        next_guess = subs.decrypt(next_alpha, cryptogram)
        next_score = score_markov(next_guess)
        accept_thresh = next_score - cur_score
        if -np.log(random()) > accept_thresh:
            cur_alpha = next_alpha
            cur_guess = next_guess
            cur_score = next_score
        yield cur_alpha, cur_guess
    
