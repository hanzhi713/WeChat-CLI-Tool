#!/usr/bin/env python
#  -*- coding: utf-8 -*-


import numba
from primesieve.numpy import *
import numpy as np
from math import ceil, sqrt
import itchat


class Factorize:
    __author__ = "Hanzhi Zhou"
    title = "Fast Factorization Algorithm"
    parameters = "[number]"
    description = "Find all prime factors of a positive integer less than 2^64"
    alias = "fc"
    interactive = False
    fast_execution = False
    maximum = 2**64 - 1

    @staticmethod
    def help(from_user):
        my_class = Factorize
        itchat.send_msg("\n\t".join(["/{} {}".format(my_class.alias, my_class.parameters),
                                 "{} by {}".format(my_class.title, my_class.__author__),
                                 my_class.description]), from_user)

    @staticmethod
    @numba.jit(numba.uint64[:](numba.uint64, numba.uint64[:]), nopython=True, cache=True)
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

        # append the number to the numpy array after it has been divided by the factors below sqrt(n)
        # if there's exactly only one space left
        if counter == factors.size:
            temp = np.zeros(factors.size + 1, np.uint64)
            temp[0:factors.size] = factors
            factors = temp
            factors[factors.size] = n
            return factors

        # if there are extra spaces, delete these spaces
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

    @staticmethod
    def call(from_user, n):
        itchat.auto_login(hotReload=True)
        try:
            n = int(n[0])
            if n > Factorize.maximum:
                itchat.send_msg("Number must be no larger than 2^64 - 1 ({})".format(Factorize.maximum), from_user)
                raise Exception
        except:
            itchat.send_msg("Argument Error\nOne positive integer parameter is required", from_user)
            raise Exception

        factors = [1]
        remain = n
        while True:

            # find all factors below sqrt(n)
            prime_list = primes(ceil(sqrt(remain))).astype(np.uint64)
            current_factors = Factorize.find_factors(remain, prime_list)

            # record factors
            factors.extend(current_factors[0:current_factors.size - 1])

            # get the unfactorized past
            remain = current_factors[current_factors.size - 1]
            del prime_list

            # break if the current factor (which is in fact the last factor) is a prime
            if len(current_factors) == 1:
                break

        if remain != 1:
            factors.append(remain)

        if len(factors) == 2:
            return itchat.send_msg(str(n) + ' is prime!', from_user)

        factors = [str(a) for a in factors]
        factors = " * ".join(factors)
        f = eval(factors)
        if f == n:
            itchat.send_msg("Factors of {} are found!\n{}".format(n, factors), from_user)
        else:
            itchat.send_msg("Unsuccessful factorization!", from_user)
