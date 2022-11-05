'''
This is a module about prime number.

Classes:

    PrimeDecomposition
    _Primes

Functions:

    is_prime(int)
    is_sprp_by_bases(int, Iterable[int])

Misc variables:

    Primes

....
'''
import operator
from abc import ABC, ABCMeta, abstractmethod
from functools import cache, reduce, total_ordering
from itertools import islice, count, takewhile, chain
from math import sqrt, log2
from numbers import Integral, Real
from typing import Iterable, Mapping, overload
from sys import maxsize


@cache
def is_prime(num: int) -> bool:
    '''Returns whether num is prime or not.'''
    if num == 2:
        return True
    if num < 2 or not num % 2:
        return False
    assert num < 3_3170_4406_4679_8873_8596_1981, "I don't know!"
    if num < 908_0191:
        bases = (31, 73)
    elif num < 47_5912_3141:
        bases = (2, 7, 61)
    elif num < 1_1220_0466_9633:
        bases = (2, 13, 23, 1662803)
    else:
        bases = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
    return is_sprp_by_bases(num, bases)


def is_sprp_by_bases(num: int, bases: Iterable[int]) -> bool:
    '''Takes a number and bases, returns whether it is a-SPRP for all a in bases.'''
    _u = int(f'{num-1:b}'.strip('0'), 2)
    _t = int(log2(num / _u))
    for base in bases:
        temp_a = base % num
        if temp_a in (0, 1, num - 1):
            continue
        pow_of_base = pow(temp_a, _u, num)
        if pow_of_base in (1, num - 1):
            continue
        for _ in range(_t):
            pow_of_base = pow_of_base ** 2 % num
            if pow_of_base == 1:
                return False
            if pow_of_base == num - 1:
                break
        if pow_of_base != num - 1:
            return False
    return True


class _Primes(Mapping[int, int]):
    __slots__ = ()
    __contains__ = is_prime

    def __len__(self):
        return len(self.__next__.__kwdefaults__['old'])

    def __hash__(self) -> int:
        try:
            return hash(id(self.__next__.__kwdefaults__['old']))
        except KeyError:
            return NotImplemented

    def __iter__(self):
        return self

    def __next__(self, number=1, *, old=[],
                 it=(i for i in count(2) if is_prime(i))):
        for _ in range(number):
            old.append(next(it))
        return old[-1]

    @overload
    def __getitem__(self, key: int) -> int: ...
    @overload
    def __getitem__(self, key: slice) -> tuple[int]: ...

    def __getitem__(self, key):

        if isinstance(key, slice):
            # Get the start, stop, and step from the slice
            assert key.indices(maxsize)[-1] < maxsize / 10, 'Too big...'
            return tuple(islice(chain(self.__next__.__kwdefaults__[
                         'old'], self), *key.indices(maxsize)))
        if isinstance(key, int):
            assert key >= 0, 'Do not support negative index'
            if key < len(self):
                return self.__next__.__kwdefaults__['old'][key]
            return self.__next__(len(self) - key + 1)
        raise ValueError('Invalid argument type.')


Primes = _Primes()


class JustLikeInt(ABCMeta, type):
    '''Make class just like int'''
    @total_ordering
    class CompareByGt(ABC):
        @abstractmethod
        def __eq__(self, __o: object) -> bool: pass
        @abstractmethod
        def __gt__(self, __o: object) -> bool: pass

    def __new__(cls, name, base, attribs):
        def f_factory(fname, act):
            def _(self, *args):
                ans = act(int(self), *args)
                if ans != int(ans):
                    return ans
                return self.__class__(int(ans))
            _.__name__ = f'__{fname}__'
            return _

        def r_factory(fname, act):
            def _(self, arg1, *args):
                ans = act(arg1, int(self), *args)
                if ans != int(ans):
                    return ans
                return self.__class__(int(ans))
            _.__name__ = f'__r{fname}__'
            return _
        two_arg_magic = {
            'add': operator.add,
            'and': operator.and_,
            'floordiv': operator.floordiv,
            'truediv': operator.truediv,
            'lshift': operator.lshift,
            'mod': operator.mod,
            'mul': operator.mul,
            'pow': operator.pow,
            'rshift': operator.rshift,
            'sub': operator.sub,
        }
        one_arg_magic = {
            'abs': operator.abs,
            'neg': operator.neg,
            'pos': operator.pos,
        }
        for fname, act in (two_arg_magic | one_arg_magic).items():
            attribs[f'__{fname}__'] = f_factory(fname, act)

        for fname, act in two_arg_magic.items():
            attribs[f'__r{fname}__'] = r_factory(fname, act)
        return super().__new__(cls, name, (cls.CompareByGt, *base), attribs)


class PrimeDecomposition(dict, metaclass=JustLikeInt):
    """
    A class to represent prime decompositions.
    """

    def __init__(self, number: int):
        '''
        Returns prime decomposition of integer.
            Parameter:
                num (int): An integer
            Returns:
                dictionary with prime factors
        '''
        assert isinstance(number, Integral)
        self.sign = -1 if number < 0 else 1
        number = abs(number)
        if number == 0:
            self[0] = 1
        else:
            factor_dict: dict[int, int] = {}
            for prime in Primes:
                times = max(
                    takewhile(lambda x: number % (prime**x) == 0, count()))
                if times:
                    factor_dict[prime] = times
                    number //= prime**times
                if prime > sqrt(number):
                    if number != 1:
                        factor_dict[number] = factor_dict.get(number, 0) + 1
                    self.update(factor_dict)
                    return

    def __repr__(self) -> str:
        '''Return p1^n × p2^n ...'''
        def superscript(num: int):
            trans = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
            return str(num).translate(trans) if num > 1 else ''
        num_str = ' × '.join(f'{k}{superscript(v)}' for (
            k, v) in self.items()) or '1'
        if self.sign > 0:
            return num_str
        return '-' + num_str

    def __int__(self):
        return int(
            reduce(operator.mul, (k**v for (k, v) in self.items()), self.sign))

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Real):
            return int(self) == __o
        return super().__eq__(__o)

    def __gt__(self, __o: object) -> bool:
        if isinstance(__o, Real):
            return int(self) > __o
        return NotImplemented


if __name__ == '__main__':
    showpieces = ['Primes[:7]', 'PrimeDecomposition(49)']
    for piece in showpieces:
        print(f'{piece} = {eval(piece)}')
