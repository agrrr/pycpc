"""
This script implements the CPC coding scheme, presented at:
H. Rabii, Y. Neumeier and O. Keren, "High Rate Robust Codes with Low Implementation Complexity," 
in IEEE Transactions on Dependable and Secure Computing, vol. 16, no. 3, pp. 511-520, 1 May-June 2019.
"""

from pyfinite import ffield
import numpy as np
import copy
from abc import ABC, abstractmethod
from bitarray import bitarray

__author__ = "David Peled, Yagel Ashkenazi"

def binlist2int(x: list) -> int:
    """
    :param x: list of bits (ints)
    :returns: 32-bit integer representation of x.
    """
    if not isinstance(x, list):
        raise Exception('x={} must be a list'.format(x))
    if x.count(0) + x.count(1) != len(x):
        raise Exception('x={} contains non-binary elements'.format(x))

    return int(''.join(np.char.mod('%d',x)),2)


def bitarray2ints(x: bitarray, r: int) -> int:
    """
    :param x: list of bits (ints)
    :param r: positive integer, specifies GF(2^r)
    :returns: Partition of x to elements of GF(2^r).
    """
    if len(x) % r != 0:
        raise Exception('Inconsisntent length')

    return [int(x[i:i+r].to01(), 2) for i in range(0, len(x), r)]


def int2bitarray(x: int, l: int) -> bitarray:
    """
    :param x: int
    :param l: positive integer, specifies length of binary string.
    :returns: binary representation of x with l bits. 
    """
    if not isinstance(x, int) or not isinstance(l, int):
        raise Exception('Type error')
    if x > 2 ** l:
        raise Exception('{x} can not feet in {l} bits'.format(x=x, l=l))

    x_str = ('{0:0' + str(l) + 'b}').format(x) # integer to binary string
    return bitarray(x_str)


class Code(ABC):
    """
    Represents an abstract binary code.
    """
    def __init__(self, k: int, r: int, name :str =''):
        """
        :param name: code name (str)
        :param k: code dimension (int)
        :param r: code redundancy length (int)
        """
        self.name = name
        self.k = k
        self.r = r
        self.n = k + r

    def __str__(self):
        return '{0}(n={1}+{2}, r={2})'.format(self.name, self.k, self.r)

    def encode(self, x: bitarray) -> bitarray:
        """
        :param x: word to encode (bitarray of length k)
        :returns: redundancy (bitarray of length r) of x using the virtual _encode() method.
        """
        if len(x) != self.k:
            raise Exception(f'len(x={len(x)})!=k={self.k}')

        return self._encode(x)

    @abstractmethod
    def _encode(self, x: bitarray) -> bitarray: 
        pass

    def encode_word(self, x: bitarray) -> bitarray:
        """
        :param x: word to encode (bitarray of length k)
        :returns: systematic encoding of x (bitarray of length n=k+r).
        """
        return x + self.encode(x)  

    def check(self, x: bitarray) -> bool:
        """
        :param x: word (bitarray of length n=k+r)
        :returns: True if x is a code word, False otherwise.
        """
        if len(x) != self.n:
            raise Exception('len(x={x})!=n={n}'.format(x=x, n=self.n))

        return (self._encode(x[:self.k]) == x[self.k:])
    
    def is_faulty(self, x: bitarray) -> bool:
        return not self.check(x)


class QS(Code):
    """
    This class represents a QS code.
    Example:
        QS(66, 11) generates a QS code with k=66 and r=11.
    """
    def __init__(self, k: int,  r: int, gen: list =None):
        super().__init__(k=k, r=r, name='QS')
        s = k / (2.0 * r)
        if int(s) != s:
            raise Exception('QS parameters error: k != 2*s*r')
        self.s = int(s) # convert double to int.
        if gen is None:
            self.F = ffield.FField(r)
        else:
            if not isinstance(gen, list) or len(gen) != r+1 or gen.count(0) + gen.count(1) != len(gen):
                raise Exception('generator polynom error')
            gen = binlist2int(gen)
            self.F = ffield.FField(r, gen, useLUT=0) # create GF(2^r)

    def _encode(self, x: bitarray) -> bitarray:
        X = bitarray2ints(x, self.r) # convert to element in GF(2^r)
        w = 0
        for i in range(0,self.s):
            w = self.F.Add(w, self.F.Multiply(X[2*i], X[2*i+1]))
        return int2bitarray(w, self.r)


class TS(Code):
    """
    This class represents a TS code.
    Example:
        TS(12, 4) generates a TS code with k=12 and r=4.
    """
    def __init__(self, k: int, r: int, gen: list =None):
        super().__init__(k=k, r=r, name='TS')
        s = (k / r - 1) / 2.0
        if int(s) != s:
            raise Exception('TS parameters error: k != (2*s+1)*r')
        self.s = int(s)                          # convert double to int.
        if gen is None:
            self.F = ffield.FField(r)
        else:
            if not isinstance(gen, list) or len(gen) != r+1 or gen.count(0) + gen.count(1) != len(gen):
                raise Exception('generator polynom error')
            gen = binlist2int(gen)
            self.F = ffield.FField(r, gen, useLUT=0) # create GF(2^r)

    def _encode(self, x: bitarray) -> bitarray:
        s = self.s
        X = bitarray2ints(x,self.r)         # convert to element in GF(2^r)
        w = self.F.Multiply(X[2*s-2], X[2*s-1])
        w = self.F.Multiply(w, X[2*s])           # X_(2s-1) * X_(2s) * X_(2s+1)
        for i in range(0,s-1):
            w = self.F.Add(w, self.F.Multiply(X[2*i], X[2*i+1]))
        return int2bitarray(w, self.r)


class PC(Code):
    """
    This class represents a PC code.
    A puncturing vector may be provided, otherwise the trivial is used.
    Example:
        PC(9, 6) generates a PC code with k=9, r=6 and the trivial puncturing vector.
    """
    def __init__(self, k: int, r: int, pv: bitarray =None, gen: list=None):
        """
        pv: Punching vector. len(P)=k, w(P)=r
        gen: generating polynomial in binary vector form.
        """
        super().__init__(k=k, r=r, name='PC')
        if pv is None:
            pv = bitarray([0 for _ in range(k-r)] + [1 for _ in range(r)])
        if pv.count(1) != r or pv.count(0) != k-r:
            raise Exception('{pv} can not be used as punching vector (k={k}, r={r})'.format(pv=pv, k=k, r=r))
        self.PV = pv
        if gen is None:
            self.F = ffield.FField(k)
        else:
            if not isinstance(gen, list) or len(gen) != k+1 or gen.count(0) + gen.count(1) != len(gen):
                raise Exception('generator polynom error')
            gen = binlist2int(gen)
            self.F = ffield.FField(k, gen, useLUT=0) # create GF(2^k)

    def _encode(self, x: bitarray) -> bitarray:
        x = int(x.to01(), 2)
        x_pow3 = self.F.Multiply(self.F.Multiply(x, x), x)
        x_pow3 = int2bitarray(x_pow3, self.k)
        redundancy = bitarray('0' * self.r)
        red_idx = 0
        for idx, val in enumerate(x_pow3):
            if self.PV[idx] == 1:
                redundancy[red_idx] = val
                red_idx += 1
        return redundancy


class ADR(Code):

    def __init__(self, k, r, gen: list =None):
        super().__init__(k, r, name='ADR')

        if gen is None:
            self.F = ffield.FField(r)
        else:
            if not isinstance(gen, list) or len(gen) != r+1 or gen.count(0) + gen.count(1) != len(gen):
                raise Exception('generator polynom error')
            gen = binlist2int(gen)
            self.F = ffield.FField(r, gen, useLUT=0) # create GF(2^r)
    

    def _encode(self, x): #the incoding func for the address

        X = bitarray2ints(x, self.r) # convert to element in GF(2^r)
        w = 0


        return int2bitarray(w, self.r)

class CPC(Code):
    """
    CPC codes are constructed using smaller ground codes (as specified in the paper).
    To create a CPC instance, a list of Codes must be provided.
    Example:
        CPC([QS(66, 11), TS(33, 11), PC(16, 11)]) generates a CPC code with k=66+33+16=115 and r=max(11,11,11)=11.
    """
    def __init__(self, code_list: list):
        self._code_list = copy.deepcopy(code_list)
        r = max([c.r for c in code_list])
        k = sum([c.k for c in code_list])
        self.F = ffield.FField(r)
        super().__init__(k=k, r=r, name='CPC')

    def __str__(self):
        cpc = super().__str__()
        return cpc + ': {' + ', '.join([str(c) for c in self._code_list]) + '}'

    def _encode(self, x: bitarray) -> bitarray:
        w = 0
        last_k = 0
        for c in self._code_list:
            redundancy = c.encode(x[last_k:last_k+c.k])
            redundancy = int(redundancy.to01(), 2)
            last_k += c.k
            w = self.F.Add(w, redundancy)
        return int2bitarray(w, self.r)


def split_bitarray_to_ryot(bitarray:,r):
    

# test helpers:

def format_word(w):
    return ' '.join(list(w.to01()))

def test_code(code, amount=2**30):
    print('\n\nTesting', str(code))
    k = code.k
    for i in range(min(2**k, amount)):
        x = int2bitarray(i,k) #bitarray(list(np.random.choice([0, 1], size=(k,))))
        redundancy = code.encode(x)
        print(format_word(x) + ' | ' + format_word(redundancy))

if __name__=='__main__':
    
    # Test QS
    s = 1
    r = 2
    k = 2*s*r
    code = QS(k,r)
    test_code(code)

    # Test TS
    s = 1
    r = 2
    k = (2*s+1)*r
    code = TS(k,r)
    test_code(code)

    # Test PC
    r = 3
    k = 3
    code = PC(k,r)
    test_code(code)

    #Test CPC

    s_qs = 1
    r_qs = 2
    k_qs = 2*s_qs*r_qs
    qs = QS(k_qs,r_qs)
    test_code(qs)
    r_ts = 3
    k_ts = 3
    pc = PC(k_ts,r_ts)
    test_code(pc)

    code = CPC([qs, pc])
    test_code(code)
