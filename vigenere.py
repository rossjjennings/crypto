alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def shifted_alpha(c):
    ind = alphabet.index(c)
    return alphabet[ind:] + alphabet[:ind]

def encrypt(ct_alphas, message):
    if isinstance(ct_alphas, str):
        ct_alphas = [shifted_alpha(c) for c in ct_alphas]
    cryptogram = ''
    key_length = len(ct_alphas)
    i = 0
    for c in message.upper():
        if c in alphabet:
            ind = alphabet.index(c)
            cryptogram += ct_alphas[i % key_length][ind]
            i += 1
        else:
            cryptogram += c
    return cryptogram

def decrypt(ct_alphas, cryptogram):
    if isinstance(ct_alphas, str):
        ct_alphas = [shifted_alpha(c) for c in ct_alphas]
    message = ''
    key_length = len(ct_alphas)
    i = 0
    for c in cryptogram.upper():
        if c in alphabet:
            ind = ct_alphas[i % key_length].index(c)
            message += alphabet[ind]
            i += 1
        else:
            message += c
    return message
