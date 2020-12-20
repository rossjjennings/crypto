from primitive_polynomials import all_factors

def to_fl(n):
    '''
    Calculate the (ternary) Frieder-Luk encoding of a positive integer `n`.
    This consists of a pair of integers: one whose set bits correspond to
    the ones in the ternary expansion of `n`, and another whose set bits
    correspond to the twos.
    '''
    digits = []
    while n != 0:
        digits.append(n % 3)
        n //= 3
    
    ones = 0
    twos = 0
    for digit in digits[::-1]:
        ones = 2*ones + (digit == 1)
        twos = 2*twos + (digit == 2)
    
    return ones, twos


def from_fl(pair):
    '''
    Given a pair of numbers which constitute the ternary Frieder-Luk encoding
    of a single integer, determine that integer.
    '''
    ones, twos = pair
    digits = []
    while ones != 0 or twos != 0:
        digits.append(2*(twos % 2) + ones % 2)
        ones //= 2
        twos //= 2
    
    out = 0
    for digit in digits[::-1]:
        out = 3*out + digit
    return out


def add_fl(a, b):
    '''
    Add two integers in ternary Frieder-Luk encoding, without carrying.
    '''
    ones_a, twos_a = a
    ones_b, twos_b = b
    zeros_a = ~ones_a & ~twos_a
    zeros_b = ~ones_b & ~twos_b
    ones_out = zeros_a & ones_b | ones_a & zeros_b | twos_a & twos_b
    twos_out = zeros_a & twos_b | twos_a & zeros_b | ones_a & ones_b
    return ones_out, twos_out


def multmod_fl(size, poly):
    ones_p, twos_p = poly
    
    def product(a, b):
        ones_a, twos_a = a
        ones_b, twos_b = b
        ones_f, twos_f = ones_b, twos_b
        result = (0, 0)
        for i in range(size):
            one = (ones_a & 1 << i) >> i
            two = (twos_a & 1 << i) >> i
            if one:
                result = add_fl(result, (ones_f % (1 << size), twos_f % (1 << size)))
            elif two:
                result = add_fl(result, (twos_f % (1 << size), ones_f % (1 << size)))
            ones_f <<= 1
            twos_f <<= 1
            if ones_f & 1 << size:
                ones_f, twos_f = add_fl((ones_f, twos_f), (ones_p, twos_p))
            elif twos_f & 1 << size:
                ones_f, twos_f = add_fl((ones_f, twos_f), (twos_p, ones_p))
        return result
    
    return product


def powmod_fl(size, poly):
    product = multmod_fl(size, poly)
    
    def power(n, e):
        index = e.bit_length() - 1
        result = (1, 0)
        while index >= 0:
            result = product(result, result)
            if e & 2**index != 0:
                result = product(n, result)
            index -= 1
        return result
    
    return power


def polysearch_fl(size, which='all'):
    factors = all_factors(3**size - 1)
    
    primitives = []
    for k in range(3**size):
        power = powmod_fl(size, to_fl(k))
        powers = [power((2, 0), f) for f in factors]
        if powers[-1] == (1, 0) and all(q != (1, 0) for q in powers[:-1]):
            primitives.append(k)
            if which == 'first':
                break
    
    return primitives


def to_dfl(n):
    '''
    Calculate the decimal Frieder-Luk encoding of a positive integer `n`.
    This consists of four numbers -- the bits of the decimal digit in each
    position are given by the bits of each consituent integer in the 
    corresponding positions.
    '''
    digits = []
    while n != 0:
        digits.append(n % 10)
        n //= 10
    
    ones = 0
    twos = 0
    fours = 0
    eights = 0
    for digit in digits[::-1]:
        ones = 2*ones + digit % 2
        twos = 2*twos + digit//2 % 2
        fours = 2*fours + digit//4 % 2
        eights = 2*eights + digit//8 % 2
    
    return ones, twos, fours, eights


def from_dfl(quad):
    '''
    Given four numbers constituting the decimal Frieder-Luk encoding of an
    integer, determine that integer.
    '''
    ones, twos, fours, eights = quad
    digits = []
    while ones != 0 or twos != 0 or fours != 0 or eights != 0:
        digits.append(8*(eights % 2) + 4*(fours % 2) + 2*(twos % 2) + ones % 2)
        ones //= 2
        twos //= 2
        fours //= 2
        eights //= 2
    
    out = 0
    for digit in digits[::-1]:
        out = 10*out + digit
    return out


def add_dfl(a, b):
    '''
    Add two integers in decimal Frieder-Luk encoding, without carrying.
    Implements a bitwise ripple-carry adder, followed by a second ripple-carry
    addition of 6 in each digit where the first result exceeds 9.
    The final carry bit is discarded.
    '''
    ones_a, twos_a, fours_a, eights_a = a
    ones_b, twos_b, fours_b, eights_b = b
    sum0 = ones_a ^ ones_b
    carry0 = ones_a & ones_b
    sum1 = twos_a ^ twos_b ^ carry0
    carry1 = twos_a & twos_b | twos_a & carry0 | twos_b & carry0
    sum2 = fours_a ^ fours_b ^ carry1
    carry2 = fours_a & fours_b | fours_a & carry1 | fours_b & carry1
    sum3 = eights_a ^ eights_b ^ carry2
    carry3 = eights_a & eights_b | eights_a & carry2 | eights_b & carry2
    invalid = carry3 | sum3 & (sum1 | sum2)
    sum4 = sum1 ^ invalid
    carry4 = sum1 & invalid
    sum5 = sum2 ^ invalid ^ carry4
    carry5 = sum2 & invalid | sum2 & carry4 | invalid & carry4
    sum6 = sum3 ^ carry5
    return sum0, sum4, sum5, sum6


def add_no_carry(m, n):
    return from_dfl(add_dfl(to_dfl(m), to_dfl(n)))
