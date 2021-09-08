from R27 import *

class LCG:
    __slots__ = 'multiplier', 'offset', 'modulus'
    
    def __init__(self, multiplier, offset, modulus):
        self.multiplier = multiplier
        self.offset = offset
        self.modulus = modulus
    
    def step(self, start):
        return (self.multiplier*start + self.offset) % self.modulus
    
    def advance(self, start, steps):
        index = steps.bit_length() - 1
        multiplier = 1
        offset = 0
        while index >= 0:
            offset = ((multiplier + 1)*offset) % self.modulus
            multiplier = (multiplier*multiplier) % self.modulus
            if steps & 2**index != 0:
                offset = (self.multiplier*offset + self.offset) % self.modulus
                multiplier = (self.multiplier*multiplier) % self.modulus
            index -= 1
        result = (multiplier*start + offset) % self.modulus
        return result

class TernaryScheme:
    __slots__ = 'multiplier', 'offset'
    
    def __init__(self, text_multiplier, text_offset):
        self.multiplier = as_integer(text_multiplier)
        self.offset = as_integer(text_offset)
        if self.multiplier % 3 != 1:
            raise ValueError("Multiplier must be congruent to 1 modulo 3")
        if self.offset % 3 == 0:
            raise ValueError("Offset must not be divisible by 3")
    
    def encrypt(self, plaintext, key):
        length = len(plaintext)
        lcg = LCG(self.multiplier, self.offset, 27**length)
        result = lcg.advance(as_integer(plaintext), as_integer(key))
        return as_text(result, length)
    
    def decrypt(self, ciphertext, key):
        length = len(ciphertext)
        lcg = LCG(self.multiplier, self.offset, 27**length)
        result = lcg.advance(as_integer(ciphertext), lcg.modulus - as_integer(key))
        return as_text(result, length)
    
    def encrypt_double(self, plaintext, key1, key2):
        length = len(plaintext)
        lcg = LCG(self.multiplier, self.offset, 27**length)
        result1 = lcg.advance(as_integer(plaintext), as_integer(key1))
        intermediate = as_text(result1, length)[::-1]
        result2 = lcg.advance(as_integer(intermediate), as_integer(key2))
        return as_text(result2, length)
    
    def decrypt_double(self, ciphertext, key1, key2):
        length = len(ciphertext)
        lcg = LCG(self.multiplier, self.offset, 27**length)
        result1 = lcg.advance(as_integer(ciphertext), lcg.modulus - as_integer(key2))
        intermediate = as_text(result1, length)[::-1]
        result0 = lcg.advance(as_integer(intermediate), lcg.modulus - as_integer(key1))
        return as_text(result0, length)
