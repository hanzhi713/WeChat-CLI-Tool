from modules.__templates__ import Static
import numpy as np
from math import floor, sqrt
import itchat
from modules.__config__ import multi_process, terminal_QR

numba_present = False
try:
    import numba

    numba_present = True
except ImportError:
    import pyprimes
    pass

primesieve_present = False
try:
    from primesieve.numpy import *

    primesieve_present = True
except ImportError:
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
        @numba.jit(numba.uint64[:](numba.uint64, numba.uint32[:]), nopython=True, cache=True)
        def find_factors(n, prime_list):
            counter = 0
            factors = np.zeros(10, np.uint64)
            for i in range(prime_list.size):

                # find the power of this factor
                while n % prime_list[i] == 0:
                    n = n // prime_list[i]
                    factors[counter] = prime_list[i]
                    counter += 1

                    # expand the array if these's insufficient space
                    if counter > factors.size - 1:
                        temp = np.zeros(counter * 2, np.uint64)
                        temp[0:counter] = factors
                        factors = temp

                if n == 1:
                    break

            # append the number to the numpy array after it has been divided by all factors below sqrt(n)
            # if there's exactly only one space left
            if counter == factors.size:
                temp = np.zeros(factors.size + 1, np.uint64)
                temp[0:factors.size] = factors
                factors = temp
                factors[factors.size - 1] = n
                return factors

            # if there are extra spaces, delete them
            else:
                num_of_zeros = 0
                for j in factors:
                    if j != 0:
                        num_of_zeros += 1
                    else:
                        break
                temp = np.zeros(num_of_zeros + 1, np.uint64)
                temp[0:num_of_zeros] = factors[0:num_of_zeros]
                temp[num_of_zeros] = n
                factors = temp
                return factors
    else:
        @staticmethod
        def find_factors(n, prime_list):
            factors = []
            for i in range(len(prime_list)):
                while n % prime_list[i] == 0:
                    n = n // prime_list[i]
                    factors.append(prime_list[i])

                if n == 1:
                    break
            if n != 1:
                factors.append(n)
            return np.array(factors, np.uint64)

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
            itchat.send_msg("Argument Error\nOne positive integer parameter is required", from_user)
            raise Exception

        factors = [1]
        if primesieve_present:
            # find all factors below sqrt(n)
            # unexpected calculation error will happen if using np.uint64
            prime_list = primes(floor(sqrt(n))).astype(np.uint32)
            current_factors = Factorize.find_factors(n, prime_list)

            # record factors
            factors.extend(current_factors[0:current_factors.size - 1])

            # remain is either 1 or a prime factor > sqrt(n)
            remain = current_factors[current_factors.size - 1]
            del prime_list

            if remain != 1:
                factors.append(remain)

            if len(factors) == 2:
                return itchat.send_msg(str(n) + ' is prime!', from_user)
        else:
            factors.extend(pyprimes.factors(n))

        factors = [str(a) for a in factors]
        factors = " * ".join(factors)
        f = eval(factors)
        if f == n:
            itchat.send_msg("Factors of {} are found!\n{}".format(n, factors), from_user)
        else:
            itchat.send_msg("Unsuccessful factorization!", from_user)
