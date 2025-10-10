# Copyright 2023-2024 Geoffrey R. Scheller
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from boring_math.integer_math.number_theory import gcd, lcm, coprime
from boring_math.integer_math.number_theory import is_prime, primes, primes_wilson
from boring_math.integer_math.number_theory import legendre_symbol, jacobi_symbol

class Test_simple_ones:
    def test_gcd(self)-> None:
        assert gcd(0, 0) == 1   # mathematically does not exist
        assert gcd(1, 1) == 1
        assert gcd(1, 5) == 1
        assert gcd(5, 1) == 1
        assert gcd(0, 5) == 5
        assert gcd(21, 0) == 21 
        assert gcd(2, 5) == 1
        assert gcd(5, 2) == 1
        assert gcd(15, 35) == 5
        assert gcd(35, 15) == 5
        assert gcd(2*3*5*7, 3*5*7*11) == 3*5*7
        assert gcd(123454321, 11111) == 11111
        assert gcd(123454321, 1111) == 1

    def test_lcm(self) -> None:
        assert lcm(5, 0) == 0
        assert lcm(0, 11) == 0
        assert lcm(0, 0) == 0
        assert lcm(3, 5) == 15
        assert lcm(2*3*25*7, 3*5*11) == 2*3*25*7*11

    def test_mkCoprime(self) -> None:
        assert coprime(0, 0) == (0, 0)
        assert coprime(5, 0) == (1, 0)
        assert coprime(0, 4) == (0, 1)
        assert coprime(1, 4) == (1, 4)
        assert coprime(6, 15) == (2, 5)
        assert coprime(2*3*4*5, 3*4*5*11) == (2, 11)

    def test_primes(self) -> None:
        assert len(list(primes(10, 5))) == 0
        assert len(list(primes(11, 5))) == 0
        assert len(list(primes(end=11))) == 5
        assert len(list(primes(end=12))) == 5
        assert len(list(primes(start=5, end=11))) == 3
        assert len(list(primes(start=4, end=12))) == 3

        cnt = 0
        primeList: list[int] = []
        for kk in primes_wilson(36):
            cnt += 1
            if cnt > 5:
                assert False
            primeList.append(kk)
            if kk >= 53:
                break
        assert primeList == [37, 41, 43, 47, 53]

        cnt = 0
        primeList = []
        for kk in primes(36):
            cnt += 1
            if cnt > 5:
                assert False
            primeList.append(kk)
            if kk >= 53:
                break
        assert primeList == [37, 41, 43, 47, 53]

        generated = list(primes(10, 50))
        assert generated == [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        generated = list(primes(10, 8))
        assert generated == []
        generated = list(primes(0, 3))
        assert generated == [2, 3]
        generated = list(primes(-5, 4))
        assert generated == [2, 3]

    def test_is_prime(self) -> None:
        assert not is_prime(0)
        assert not is_prime(1)
        assert is_prime(2)
        assert is_prime(3)
        assert not is_prime(4)
        assert is_prime(5)
        assert not is_prime(6)
        assert is_prime(7)
        assert not is_prime(100)
        assert is_prime(101)
        assert not is_prime(111)
        assert not is_prime(11111)

    def test_symbols(self) -> None:
        legendre3 = [0, 1, -1, 0, 1, -1, 0, 1, -1]
        for ii in range(0, 9):
            assert legendre_symbol(ii, 3) == jacobi_symbol(ii, 3) == legendre3[ii]

        legendre5 = [0, 1, -1, -1, 1, 0, 1, -1, -1, 1]
        for ii in range(0, 10):
            assert legendre_symbol(ii, 5) == jacobi_symbol(ii, 5) == legendre5[ii]

        legendre127 = [0, 1, 1, -1, 1, -1, -1, -1,  1,  1, -1, 1, -1,  1, -1,
                       1, 1, 1,  1, 1, -1,  1,  1, -1, -1,  1, 1, -1, -1, -1, 1]
        for ii in range(0, 31):
            assert legendre_symbol(ii, 127) == jacobi_symbol(ii, 127) == legendre127[ii]

        jacobi1 = [1] * 100
        for ii in range(0, 100):
            assert jacobi_symbol(ii, 1) == jacobi1[ii] == 1

        jacobi7 =[0, 1, 1, -1, 1, -1, -1, 0, 1, 1, -1, 1, -1, -1]
        for ii in range(0, 14):
            assert jacobi_symbol(ii, 7) == jacobi7[ii]

        jacobi15 = [0, 1, 1, 0, 1, 0, 0, -1, 1, 0, 0, -1, 0, -1, -1,
                    0, 1, 1, 0, 1, 0, 0, -1, 1, 0, 0, -1, 0, -1, -1]
        for ii in range(0, 30):
            assert jacobi_symbol(ii, 15) == jacobi15[ii]
