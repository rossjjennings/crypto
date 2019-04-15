from itertools import product
from score import score_markov
from subs import alphabet
import subs
import vigenere

with open('alphabetic-words.txt') as f:
    words = f.read().split()

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
    soln_key = 'A'
    
    if key_length == 'words':
        test_keys = (word.upper() for word in words)
    else:
        test_keys = product(*([alphabet]*key_length))
    
    for test_key in test_keys:
        test_key = ''.join(test_key)
        guess = vigenere.decrypt(test_key, cryptogram)
        score = score_markov(guess)
        if score < min_score:
            min_score = score
            soln = guess
            soln_key = test_key
    
    return soln_key, soln
