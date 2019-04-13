from itertools import product
from score import score_markov
from subs import alphabet
import subs
import vigenere

def check(cryptogram):
    for i in range(26):
        ct_alpha = alphabet[i:] + alphabet[:i]
        guess = subs.decrypt(ct_alpha, cryptogram)
        print(ct_alpha + ':')
        print(guess)

def solve(cryptogram, return_key=False):
    min_score = score_markov(cryptogram)
    soln = cryptogram
    soln_ct_alpha = alphabet
    for i in range(26):
        ct_alpha = alphabet[i:] + alphabet[:i]
        guess = subs.decrypt(ct_alpha, cryptogram)
        score = score_markov(guess)
        if score < min_score:
            min_score = score
            soln = guess
            soln_ct_alpha = ct_alpha
    if return_key:
        return soln_ct_alpha, soln
    else:
        return soln

def atbash(message):
    return subs.encrypt(alphabet[::-1], message)

def solve_vig(cryptogram, key_length):
    min_score = score_markov(cryptogram)
    soln = cryptogram
    soln_alphas = [alphabet]*key_length
    for indices in product(*([range(26)]*key_length)):
        ct_alphas = []
        for i in indices:
            ct_alphas.append(alphabet[i:] + alphabet[:i])
        guess = vigenere.decrypt(ct_alphas, cryptogram)
        score = score_markov(guess)
        if score < min_score:
            min_score = score
            soln = guess
            soln_alphas = ct_alphas
    return soln_alphas, soln
