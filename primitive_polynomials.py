import sympy
import itertools
import math

def multmod(size, poly):
    
    def product(n, m):
        p = 0
        factor = m
        for i in range(size):
            bit = (n & 2**i) // 2**i
            p ^= bit * factor % 2**size
            factor = factor << 1
            if factor & 2**size != 0:
                factor ^= poly
        return p
    
    return product


def powmod(size, poly):
    product = multmod(size, poly)
    
    def power(n, e):
        index = e.bit_length() - 1
        result = 1
        while index >= 0:
            result = product(result, result)
            if e & 2**index != 0:
                result = product(n, result)
            index -= 1
        return result
    
    return power


def all_factors(n):
    prime_factors = sympy.factorint(n)
    prime_powers = [[p**n for n in range(m+1)] for p, m in prime_factors.items()]
    return sorted(math.prod(l) for l in itertools.product(*prime_powers))


def polysearch(size, which='all'):
    factors = all_factors(2**size - 1)
    
    primitives = []
    for k in range(2**size):
        power = powmod(size, k)
        powers = [power(2, f) for f in factors]
        if powers[-1] == 1 and all(p != 1 for p in powers[:-1]):
            primitives.append(k)
            if which == 'first':
                break
    
    return primitives


def is_primitive(size, poly):
    factors = all_factors(2**size - 1)
    power = powmod(size, poly)
    powers = [power(2, f) for f in factors]
    return powers[-1] == 1 and all(p != 1 for p in powers[:-1])


def addmodp(p, size):
    
    def add(n, m):
        result = 0
        for i in range(size-1, -1, -1):
            digit_n = n // p**i % p
            digit_m = m // p**i % p
            digit_r = (digit_n + digit_m) % p
            result = p*result + digit_r
        return result
    
    return add


def scalarmult(p, size):
    
    def scalarprod(d, n):
        result = 0
        for i in range(size-1, -1, -1):
            digit_n = n // p**i % p
            digit_r = d * digit_n % p
            result = p*result + digit_r
        return result
    
    return scalarprod


def multmodp(p, size, poly):
    add = addmodp(p, size)
    scalarprod = scalarmult(p, size)
    
    def product(n, m):
        result = 0
        factor = m
        for i in range(size):
            digit_n = n // p**i % p
            result = add(result, scalarprod(digit_n, factor))
            factor = p*factor
            leading_coeff = factor // p**size % p
            factor = factor % p**size
            if leading_coeff != 0:
                factor = add(factor, scalarprod(leading_coeff, poly))
        return result
    
    return product


def powmodp(p, size, poly):
    product = multmodp(p, size, poly)
    
    def power(n, e):
        index = e.bit_length() - 1
        result = 1
        while index >= 0:
            result = product(result, result)
            if e & 2**index != 0:
                result = product(n, result)
            index -= 1
        return result
    
    return power


def polysearchp(p, size, which='all'):
    factors = all_factors(p**size - 1)
    
    primitives = []
    for k in range(p**size):
        power = powmodp(p, size, k)
        powers = [power(p, f) for f in factors]
        if powers[-1] == 1 and all(q != 1 for q in powers[:-1]):
            primitives.append(k)
            if which == 'first':
                break
    
    return primitives
