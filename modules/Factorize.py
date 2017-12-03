from modules.__templates__ import Static
import numpy as np
from math import floor, sqrt
import itchat
from modules.__config__ import multi_process, terminal_QR
import time

numba_present = False
try:
    import numba

    numba_present = True
except ImportError:
    pass

primesieve_present = False
try:
    if numba_present:
        from primesieve.numpy import *
    else:
        from primesieve import Iterator

    primesieve_present = True
except ImportError:
    import pyprimes

    pass


class Factorize(Static):
    __author__ = "Hanzhi Zhou"
    title = "Factorization Algorithm by Trial Division"
    parameters = "[number]"
    description = "Find all prime factors of a positive integer less than 2^64"
    alias = "fc"
    example = "Example: /fc 123801238094213"
    fast_execution = False
    maximum = 2 ** 64 - 1

    if numba_present:
        @staticmethod
        @numba.jit(numba.uint32[:](numba.uint64, numba.uint32[:]), nopython=True, cache=True)
        def find_factors(n, prime_list):
            counter = 0
            factors = np.zeros(5, np.uint32)
            for i in range(prime_list.size):

                # find the power of this factor
                while n % prime_list[i] == 0:
                    n = n // prime_list[i]
                    factors[counter] = prime_list[i]
                    counter += 1

                    # expand the array if these's insufficient space
                    if counter > factors.size - 1:
                        temp = np.zeros(counter * 2, np.uint32)
                        temp[0:counter] = factors
                        factors = temp

                if i ** 2 > n:
                    break

            return factors

    @staticmethod
    def call(from_user, n):
        if multi_process:
            itchat.auto_login(hotReload=True, enableCmdQR=terminal_QR)
        try:
            n = int(n[0])
            if n > Factorize.maximum:
                itchat.send_msg("Number must be no larger than 2^64 - 1 ({})".format(Factorize.maximum), from_user)
                raise Exception
        except:
            itchat.send_msg("Argument Error\nOne integer parameter is required", from_user)
            raise Exception

        if n < 0:
            remain = -n
            factors = [-1]
        else:
            remain = n
            factors = [1]

        t = time.clock()
        if primesieve_present:
            if numba_present:
                slice_length = 1000000
                for i in range(0, floor(sqrt(n)), slice_length):
                    current_factors = [f for f in
                                       Factorize.find_factors(remain, primes(i, i + slice_length).astype(np.uint32)) if
                                       f != 0]
                    for f in current_factors:
                        remain //= f
                    factors.extend(current_factors)
                    if i ** 2 > remain:
                        break

                if remain != 1:
                    factors.append(remain)

            else:
                it = Iterator()
                p = it.next_prime()
                while p ** 2 <= remain:
                    while remain % p == 0:
                        remain //= p
                        factors.append(p)
                    p = it.next_prime()
                if remain != 1:
                    factors.append(remain)
        else:
            factors.extend(pyprimes.factors(remain))

        if len(factors) == 2:
            itchat.send_msg(str(n) + ' is prime!', from_user)
            return itchat.send_msg("Time spent: {}s".format(round(time.clock() - t, 2)), from_user)

        factors = [str(a) for a in factors]
        factors = " * ".join(factors)
        f = eval(factors)
        if f == n:
            itchat.send_msg("Factors of {} are found!\n{}".format(n, factors), from_user)
        else:
            itchat.send_msg("Unsuccessful factorization!\nComputing error!", from_user)
        itchat.send_msg("Time spent: {}s".format(round(time.clock() - t, 2)), from_user)
