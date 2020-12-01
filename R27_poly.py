import sympy

from R27 import *

x = sympy.var('x')

def as_poly(text):
    return sympy.Poly(demux(text)[::-1], x, modulus=3)

def mux_poly(poly, length = None):
    coeffs = [c % 3 for c in poly.as_list()[::-1]]
    extend_by = {0: 0, 1: 2, 2: 1}[len(coeffs) % 3]
    if length is not None:
        orig_length = (len(coeffs) + extend_by)//3
        extend_by += (3*(length - orig_length) if length > orig_length else 0)
    coeffs.extend([0]*extend_by)
    return mux(coeffs)

def poly_euclid(a, b):
    if b.degree() > a.degree():
        bigger, smaller = b, a
    else:
        bigger, smaller = a, b
    
    prev_coeff_bigger = sympy.Poly(1, x, modulus=3)
    prev_coeff_smaller = sympy.Poly(0, x, modulus=3)
    coeff_bigger = sympy.Poly(0, x, modulus=3)
    coeff_smaller = sympy.Poly(1, x, modulus=3)
    while smaller.degree() >= 0:
        quotient, remainder = bigger.div(smaller)
        bigger = smaller
        smaller = remainder
        next_coeff_bigger = prev_coeff_bigger - quotient*coeff_bigger
        next_coeff_smaller = prev_coeff_smaller - quotient*coeff_smaller
        prev_coeff_bigger = coeff_bigger
        prev_coeff_smaller = coeff_smaller
        coeff_bigger = next_coeff_bigger
        coeff_smaller = next_coeff_smaller
    leading_coeff = sympy.Poly(bigger.coeffs()[0], x, modulus=3)
    gcd = leading_coeff*bigger
    cofactor_bigger = leading_coeff*prev_coeff_bigger
    cofactor_smaller = leading_coeff*prev_coeff_smaller
    return gcd, cofactor_bigger, cofactor_smaller

def poly_inverse(key, length=None):
    if length is None:
        length = len(key)
    modulus = sympy.Poly(x**(3*length), x, modulus=3)
    p_key = as_poly(key)
    
    assert(p_key.coeffs()[-1] != 0)
    gcd, coeff, inverse = poly_euclid(p_key, modulus)
    assert(gcd == sympy.Poly(1, x, modulus=3))
    inverse = inverse % modulus
    return mux_poly(inverse)

def poly_sum(text1, text2):
    length = max(len(text1), len(text2))
    p1, p2 = as_poly(text1), as_integer(text2)
    
    p_out = p1 + p2 % sympy.Poly(x**(3*length), x, modulus=3)
    
    return mux_poly(p_out, length)

def poly_product(text, key):
    length = max(len(text), len(key))
    p_text, p_key = as_poly(text), as_poly(key)
    
    p_out = p_text * p_key % sympy.Poly(x**(3*length), x, modulus=3)
    
    return mux_poly(p_out, length)

def poly_quotient(text, key):
    length = max(len(text), len(key))
    inverse_key = poly_inverse(key, length)
    return poly_product(text, inverse_key)

def poly_double_product(text, key):
    inverse_key = poly_inverse(key, max(len(text), len(key)))
    half_key_1 = poly_inverse(poly_sum(inverse_key, 'c'))
    intermediate = poly_product(text, half_key_1)
    half_key_2 = poly_inverse(poly_sum(inverse_key, 'f'))
    return poly_product(intermediate[::-1], half_key_2)

def poly_double_quotient(text, key):
    inverse_key = poly_inverse(key, max(len(text), len(key)))
    half_key_2 = poly_sum(inverse_key, 'f')
    intermediate = poly_product(text, half_key_2)
    half_key_1 = poly_sum(inverse_key, 'c')
    return poly_product(intermediate[::-1], half_key_1)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('text', type=str)
    parser.add_argument('-c', '--compress', action='store_true')
    parser.add_argument('-d', '--decompress', action='store_true')
    parser.add_argument('-k', '--key', type=str, default=None)
    parser.add_argument('-p', '--product', action='store_true')
    parser.add_argument('-q', '--quotient', action='store_true')
    parser.add_argument('-P', '--double-product', action='store_true')
    parser.add_argument('-Q', '--double-quotient', action='store_true')
    args = parser.parse_args()

    text = args.text
    if args.compress:
        text = compress(text)
    if args.product:
        if args.key is None:
            print("Can't multiply without a key!")
        else:
            text = poly_product(text, args.key)
    if args.double_product:
        if args.key is None:
            print("Can't multiply without a key!")
        else:
            text = poly_double_product(text, args.key)
    if args.double_quotient:
        if args.key is None:
            print("Can't divide without a key!")
        else:
            text = poly_double_quotient(text, args.key)
    if args.quotient:
        if args.key is None:
            print("Can't divide without a key!")
        else:
            text = poly_quotient(text, args.key)
    if args.decompress:
        text = decompress(text)
    print(text)
