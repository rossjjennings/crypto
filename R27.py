import yaml
import gmpy2

with open('R27.yml') as f:
    basic_cipher = yaml.safe_load(f)

with open('R27-compression.yml') as f:
    compressed_cipher = yaml.safe_load(f)

def index_recursive(item, tree): 
    if item in tree: 
        return [tree.index(item)] 
    for i, node in enumerate(tree): 
        if len(node) > 1: 
            index = index_recursive(item, node) 
            if index is not None: 
                index.append(i) 
                return index 
    return None

def item_recursive(index, tree):
    item = tree
    for i in index[::-1]:
        item = item[i]
    return item

def mux(indices):
    assert(len(indices) % 3 == 0)
    
    text = ""
    for j in range(len(indices) // 3):
        index = indices[3*j:3*(j+1)]
        text += item_recursive(index, basic_cipher)
    return text

def demux(text):
    text = text.upper()
    indices = []
    for c in text:
        if c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            c = '+'
        indices.extend(index_recursive(c, basic_cipher))
    return indices

def compress(plaintext):
    plaintext = plaintext.upper()
    indices = []
    for c in plaintext:
        if c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            c = '+'
        index = index_recursive(c, compressed_cipher)[::-1]
        indices.extend(index)
    
    extend_by = {0: 0, 1: 2, 2: 1}[len(indices) % 3]
    indices.extend([0]*extend_by)
    ciphertext = mux(indices)
    
    return ciphertext

def decompress(ciphertext):
    indices = demux(ciphertext)
    
    node = compressed_cipher
    plaintext_chars = []
    while len(indices) > 0:
        if len(node) > 1:
            node = node[indices[0]]
            indices.pop(0)
        else:
            plaintext_chars.append(node)
            node = compressed_cipher
    if len(node) == 1:
        plaintext_chars.append(node)
    plaintext = ''.join(plaintext_chars)
    
    return plaintext

def trifid_mix(plaintext):
    indices = demux(plaintext)
    indices_mixed = indices[0::3] + indices[1::3] + indices[2::3]
    return mux(indices_mixed)

def trifid_unmix(ciphertext):
    n = len(ciphertext)
    indices = demux(ciphertext)
    indices_unmixed = [0]*(3*n)
    indices_unmixed[0::3] = indices[:n]
    indices_unmixed[1::3] = indices[n:2*n]
    indices_unmixed[2::3] = indices[2*n:3*n]
    return mux(indices_unmixed)

def heisenberg_add(plaintext, key):
    n = len(plaintext)
    cipher_indices = []
    for i in range(n):
        plain_indices = demux(plaintext[i])
        key_indices = demux(key[i % len(key)])
        cipher_indices.extend([
            (plain_indices[0] + key_indices[0]) % 3,
            (plain_indices[1] + key_indices[1]
             + plain_indices[0] * key_indices[2]) % 3,
            (plain_indices[2] + key_indices[2]) % 3
        ])
    return mux(cipher_indices)

def heisenberg_subtract(ciphertext, key):
    n = len(ciphertext)
    plain_indices = []
    for i in range(n):
        cipher_indices = demux(ciphertext[i])
        key_indices = demux(key[i % len(key)])
        key_indices = [
            -key_indices[0] % 3,
            (key_indices[0] * key_indices[2]
             - key_indices[1]) % 3,
            -key_indices[2] % 3
        ]
        plain_indices.extend([
            (cipher_indices[0] + key_indices[0]) % 3,
            (cipher_indices[1] + key_indices[1]
             + cipher_indices[0] * key_indices[2]) % 3,
            (cipher_indices[2] + key_indices[2]) % 3
        ])
    return mux(plain_indices)

symbols = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ+'

def frobnicate(text, modulus=2):
    text = text.upper()
    z = 0
    for c in text:
        if c not in symbols[:-1]:
            c = '+'
        z = 27*z + symbols.index(c) + 1
    
    digits = []
    while z > 0:
        z_new = z//modulus - (1 if z % modulus == 0 else 0)
        digits.append(z - modulus*z_new)
        z = z_new
    
    z = 0
    for digit in digits:
        z = modulus*z + digit
    
    digits = []
    while z > 0:
        z_new = z//27 - (1 if z % 27 == 0 else 0)
        digits.append(z - 27*z_new)
        z = z_new
    return ''.join(symbols[digit - 1] for digit in digits[::-1])

def as_integer(text):
    z = 0
    for digit in demux(text)[::-1]:
        z = 3*z + digit
    return z

def as_text(z, length=None):
    digits = []
    
    i = 0
    while z != 0 or (length is not None and i < 3*length):
        z_new = z//3
        digits.append(z - 3*z_new)
        z = z_new
        i += 1
    
    extend_by = {0: 0, 1: 2, 2: 1}[len(digits) % 3]
    digits.extend([0]*extend_by)
    return mux(digits)

def sum(text1, text2):
    length = max(len(text1), len(text2))
    z1, z2 = as_integer(text1), as_integer(text2)
    
    z_out = z1 + z2 % 3**(3*length)
    
    return as_text(z_out, length)

def difference(text1, text2):
    length = max(len(text1), len(text2))
    z1, z2 = as_integer(text1), as_integer(text2)
    
    z_out = z1 - z2 % 3**(3*length)
    
    return as_text(z_out, length)

def product(text, key):
    length = max(len(text), len(key))
    z_text, z_key = as_integer(text), as_integer(key)
    
    z_out = z_text * z_key % 3**(3*length)
    
    return as_text(z_out, length)

def euclid_gcd(a, b): 
    bigger, smaller = max(a, b), min(a, b) 
    prev_coeff_bigger, prev_coeff_smaller = 1, 0 
    coeff_bigger, coeff_smaller = 0, 1 
    while smaller > 0: 
        quotient = bigger//smaller 
        remainder = bigger - quotient*smaller 
        bigger = smaller 
        smaller = remainder 
        next_coeff_bigger = prev_coeff_bigger - quotient*coeff_bigger 
        next_coeff_smaller = prev_coeff_smaller - quotient*coeff_smaller 
        prev_coeff_bigger = coeff_bigger 
        prev_coeff_smaller = coeff_smaller 
        coeff_bigger = next_coeff_bigger 
        coeff_smaller = next_coeff_smaller 
    return bigger, prev_coeff_bigger, prev_coeff_smaller

def inverse(key, length=None):
    if length is None:
        length = len(key)    
    z_key = as_integer(key)
    
    assert(z_key < 3**(3*length))
    assert(z_key % 3 != 0)
    gcd, coeff, inverse = euclid_gcd(z_key, 3**(3*length))
    assert(gcd == 1)
    inverse = inverse % 3**(3*length)
    
    return as_text(inverse, length)

def quotient(text, key):
    length = max(len(text), len(key))
    exponent = 3*length
    inverse_key = inverse(key, length)
    return product(text, inverse_key)

def double_product(text, key, schedule='interleaved'):
    size = max(len(text), len(key))
    if schedule == 'nilpotent_shift':
        inverse_key = inverse(key, size)
        half_key_1 = inverse(sum(inverse_key, 'c'))
        half_key_2 = inverse(sum(inverse_key, 'f'))
    elif schedule == 'sequential':
        inverse_key = inverse(key, 2*size)
        half_key_1 = inverse_key[:size]
        half_key_2 = inverse_key[size:]
        if as_integer(half_key_2[0]) % 3 == 0:
            half_key_2 = sum(half_key_2, half_key_1)
        half_key_1 = inverse(half_key_1)
        half_key_2 = inverse(half_key_2)
    elif schedule == 'interleaved':
        inverse_key = inverse(key, 2*size)
        half_key_1 = inverse_key[0::2]
        half_key_2 = inverse_key[1::2]
        if as_integer(half_key_2[0]) % 3 == 0:
            half_key_2 = sum(half_key_2, half_key_1)
        half_key_1 = inverse(half_key_1)
        half_key_2 = inverse(half_key_2)
    intermediate = product(text, half_key_1)
    return product(intermediate[::-1], half_key_2)

def double_quotient(text, key, schedule='interleaved'):
    size = max(len(text), len(key))
    if schedule == 'nilpotent_shift':
        inverse_key = inverse(key, size)
        half_key_1 = sum(inverse_key, 'c')
        half_key_2 = sum(inverse_key, 'f')
    elif schedule == 'sequential':
        inverse_key = inverse(key, 2*size)
        half_key_1 = inverse_key[:size]
        half_key_2 = inverse_key[size:]
        if as_integer(half_key_2[0]) % 3 == 0:
            half_key_2 = sum(half_key_2, half_key_1)
    elif schedule == 'interleaved':
        inverse_key = inverse(key, 2*size)
        half_key_1 = inverse_key[0::2]
        half_key_2 = inverse_key[1::2]
        if as_integer(half_key_2[0]) % 3 == 0:
            half_key_2 = sum(half_key_2, half_key_1)
    intermediate = product(text, half_key_2)
    return product(intermediate[::-1], half_key_1)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('text', type=str)
    parser.add_argument('-c', '--compress', action='store_true')
    parser.add_argument('-d', '--decompress', action='store_true')
    parser.add_argument('-m', '--mix', action='store_true')
    parser.add_argument('-u', '--unmix', action='store_true')
    parser.add_argument('-f', '--frobnicate', action='store_true')
    parser.add_argument('-k', '--key', type=str, default=None)
    parser.add_argument('-a', '--add', action='store_true')
    parser.add_argument('-s', '--subtract', action='store_true')
    parser.add_argument('-A', '--heisenberg-add', action='store_true')
    parser.add_argument('-S', '--heisenberg-subtract', action='store_true')
    parser.add_argument('-p', '--product', action='store_true')
    parser.add_argument('-q', '--quotient', action='store_true')
    parser.add_argument('-P', '--double-product', action='store_true')
    parser.add_argument('-Q', '--double-quotient', action='store_true')
    args = parser.parse_args()

    text = args.text
    if args.compress:
        text = compress(text)
    if args.add:
        if args.key is None:
            print("Can't add without a key!") 
        else:
            text = sum(text, args.key)
    if args.heisenberg_add:
        if args.key is None:
            print("Can't add without a key!") 
        else:
            text = heisenberg_add(text, args.key)
    if args.product:
        if args.key is None:
            print("Can't multiply without a key!") 
        else:
            text = product(text, args.key)
    if args.double_product:
        if args.key is None:
            print("Can't multiply without a key!") 
        else:
            text = double_product(text, args.key)
    if args.mix:
        text = trifid_mix(text)
    if args.frobnicate:
        text = frobnicate(text)
    if args.unmix:
        text = trifid_unmix(text)
    if args.double_quotient:
        if args.key is None:
            print("Can't divide without a key!") 
        else:
            text = double_quotient(text, args.key)
    if args.quotient:
        if args.key is None:
            print("Can't divide without a key!") 
        else:
            text = quotient(text, args.key)
    if args.heisenberg_subtract:
        if args.key is None:
            print("Can't subtract without a key!") 
        else:
            text = heisenberg_subtract(text, args.key)
    if args.subtract:
        if args.key is None:
            print("Can't subtract without a key!") 
        else:
            text = difference(text, args.key)
    if args.decompress:
        text = decompress(text)
    print(text)
