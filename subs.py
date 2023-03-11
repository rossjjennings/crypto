alphabet26 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
alphabet27 = '+ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def encrypt(ct_alpha, message):
    cryptogram = ''
    alphabet = alphabet27 if len(ct_alpha) == 27 else alphabet26
    for c in message.upper():
        if c in alphabet:
            ind = alphabet.index(c)
            cryptogram += ct_alpha[ind]
        else:
            cryptogram += c
    return cryptogram

def decrypt(ct_alpha, cryptogram):
    message = ''
    alphabet = alphabet27 if len(ct_alpha) == 27 else alphabet26
    for c in cryptogram.upper():
        if c in alphabet:
            ind = ct_alpha.index(c)
            message += alphabet[ind]
        else:
            message += c
    return message
