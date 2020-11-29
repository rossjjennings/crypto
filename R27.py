import yaml
import gmpy2

with open('R27-compression.yml') as f:
    input_cipher = yaml.safe_load(f)
    
with open('R27.yml') as f:
    output_cipher = yaml.safe_load(f)

def index_recursive(item, tree): 
    if item in tree: 
        return [tree.index(item)] 
    for i, node in enumerate(tree): 
        if len(node) > 1: 
            index = index_recursive(item, node) 
            if index is not None: 
                index.insert(0, i) 
                return index 
    return None

def item_recursive(index, tree):
    item = tree
    for i in index:
        item = item[i]
    return item

def mux(indices):
    assert(len(indices) % 3 == 0)
    
    text = ""
    for j in range(len(indices) // 3):
        index = indices[3*j:3*(j+1)]
        #print(''.join(str(i) for i in index), end='.')
        text += item_recursive(index, output_cipher)
    #print()
    return text

def demux(text):
    text = text.upper()
    indices = []
    for c in text:
        if c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            c = '+'
        indices.extend(index_recursive(c, output_cipher))
    return indices

def compress(plaintext):
    plaintext = plaintext.upper()
    indices = []
    for c in plaintext:
        if c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            c = '+'
        index = index_recursive(c, input_cipher)
        #print(''.join(str(i) for i in index), end = ' ')
        indices.extend(index)
    #print()
    
    extend_by = {0: 0, 1: 2, 2: 1}[len(indices) % 3]
    indices.extend([0]*extend_by)
    ciphertext = mux(indices)
    
    return ciphertext

def decompress(ciphertext):
    indices = demux(ciphertext)
    
    node = input_cipher
    plaintext_chars = []
    while len(indices) > 0:
        if len(node) > 1:
            node = node[indices[0]]
            indices.pop(0)
        else:
            plaintext_chars.append(node)
            node = input_cipher
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

def heisenberg_add(key, plaintext):
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

def heisenberg_subtract(key, ciphertext):
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

#def frobnicate(plaintext):
#    z = int(''.join(str(c) for c in demux(plaintext)), 3)
#    digits = gmpy2.digits(z, 28)
#    digits = digits[::-1].replace('0', 's')
#    zfrob = int(digits, 29)
#    indices = [int(c) for c in gmpy2.digits(zfrob, 3)]
#    extend_by = {0: 0, 1: 2, 2: 1}[len(indices) % 3]
#    indices = [0]*extend_by + indices
#    return mux([int(c) for c in indices])

#def unfrobnicate(ciphertext):
#    zfrob = int(''.join(str(c) for c in demux(ciphertext)), 3)
#    digits = gmpy2.digits(zfrob, 29)
#    digits = digits[::-1].replace('s', '0')
#    z = int(digits, 28)
#    indices = [int(c) for c in gmpy2.digits(z, 3)]
#    extend_by = {0: 0, 1: 2, 2: 1}[len(indices) % 3]
#    indices = [0]*extend_by + indices
#    return mux([int(c) for c in indices])

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

def sum(text1, text2):
    exponent = 3*max(len(text1), len(text2))
    
    z1 = 0
    for digit in demux(text1):
        z1 = 3*z1 + digit
    
    z2 = 0
    for digit in demux(text2):
        z2 = 3*z2 + digit
    
    z_out = z1 + z2 % 3**exponent
    
    digits = []
    for i in range(exponent):
        z_new = z_out//3
        digits.append(z_out - 3*z_new)
        z_out = z_new
    return mux(digits[::-1])

def product(text, key):
    exponent = 3*max(len(text), len(key))
    
    z_text = 0
    for digit in demux(text):
        z_text = 3*z_text + digit
    
    z_key = 0
    for digit in demux(key):
        z_key = 3*z_key + digit
    
    z_out = z_text * z_key % 3**exponent
    
    digits = []
    for i in range(exponent):
        z_new = z_out//3
        digits.append(z_out - 3*z_new)
        z_out = z_new
    return mux(digits[::-1])

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

def inverse(key, length):
    exponent = 3*length
    
    z_key = 0
    for digit in demux(key):
        z_key = 3*z_key + digit
    
    assert(z_key < 3**exponent)
    assert(z_key % 3 != 0)
    gcd, coeff, inverse = euclid_gcd(z_key, 3**exponent)
    assert(gcd == 1)
    inverse = inverse % 3**exponent
    
    digits = []
    for i in range(exponent):
        z_new = inverse//3
        digits.append(inverse - 3*z_new)
        inverse = z_new
    return mux(digits[::-1])

def quotient(text, key):
    length = max(len(text), len(key))
    exponent = 3*length
    inverse_key = inverse(key, length)
    return product(text, inverse_key)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('text', type=str)
    parser.add_argument('-c', '--compress', action='store_true')
    parser.add_argument('-d', '--decompress', action='store_true')
    parser.add_argument('-m', '--mix', action='store_true')
    parser.add_argument('-u', '--unmix', action='store_true')
    parser.add_argument('-f', '--frobnicate', action='store_true')
    #parser.add_argument('-g', '--unfrobnicate', action='store_true')
    parser.add_argument('-k', '--key', type=str, default=None)
    parser.add_argument('-a', '--add', action='store_true')
    parser.add_argument('-s', '--subtract', action='store_true')
    parser.add_argument('-p', '--product', action='store_true')
    parser.add_argument('-q', '--quotient', action='store_true')
    args = parser.parse_args()

    text = args.text
    if args.compress:
        text = compress(text)
    if args.add:
        if args.key is None:
            print("Can't add without a key!") 
        else:
            text = heisenberg_add(args.key, text)
    if args.product:
        if args.key is None:
            print("Can't multiply without a key!") 
        else:
            text = product(text, args.key)
    if args.mix:
        text = trifid_mix(text)
    if args.frobnicate:
        text = frobnicate(text)
    #if args.unfrobnicate:
    #    text = unfrobnicate(text)
    if args.unmix:
        text = trifid_unmix(text)
    if args.quotient:
        if args.key is None:
            print("Can't divide without a key!") 
        else:
            text = quotient(text, args.key)
    if args.subtract:
        if args.key is None:
            print("Can't subtract without a key!") 
        else:
            text = heisenberg_subtract(args.key, text)
    if args.decompress:
        text = decompress(text)
    print(text)
