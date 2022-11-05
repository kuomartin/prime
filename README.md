# prime

This is a module about prime number.

## Usage
```python=
Primes[:7]                  # (2, 3, 5, 7, 11, 13, 17)

is_sprp_by_bases(2047,2)    # True
is_prime(2047)              # False

a=PrimeDecomposition(48)    # PrimeDecomposition( 2⁴×3 )
a==48                       # True
b=a+5                       # PrimeDecomposition( 53 )
is_prime(b)                 # True
```