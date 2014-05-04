Title: Recursive karatsuba multiplication in Python
Author: Sam Stoelinga
Category: Algorithms
Date: 2014-05-04
Tags: coding, programming, python, algorithms
Slug: recursive-karatsuba-multiplication-python

I'm currently taking the class Algorithm: Design and Analysis of Stanford via Coursera and
in the class the Karatsuba algorithm got mentioned. I went ahead and implemented it based
on the lecture slides.

The Karatsuba algorithm is a fast multiplication algorithm. It's special because
it was the first multiplication algorithm to be faster than the quadratic "grade school"
algorithm. [Karatsuba algorithm - Wikipedia](https://en.wikipedia.org/wiki/Karatsuba_algorithm)
It also has a funny history, see the history at the Wikipedia article.


My Python implementation using a Divide and Conquer approach:

    :::Python
    from math import ceil

    memory = [[0,0,0,0,0,0,0,0,0,0],
              [0,1,2,3,4,5,6,7,8,9],
              [0,2,4,6,8,10,12,14,16,18],
              [0,3,6,9,12,15,18,21,24,27],
              [0,4,8,12,16,20,24,28,32,36],
              [0,5,10,15,20,25,30,35,40,45],
              [0,6,12,18,24,30,36,42,48,54],
              [0,7,14,21,28,35,42,49,56,63],
              [0,8,16,24,32,40,48,56,64,72],
              [0,9,18,27,36,45,54,63,72,81],
              [0,10,20,30,40,50,60,70,80,90]]

    def karatsuba(x, y):
        """ Recursive multiplication using karatsuba
        x = 10^n/2 * a + b
        y = 10^n/2 * c + d
        x * y = 10^n * ac + 10^(n/2) (ad+bc) + bd
        where (ad+bc) = (a+b)(c+d) - ac - bd
        """
        str_x, str_y = str(x), str(y)
        n = max(len(str_x), len(str_y))
        if n <= 1:
            # Just for fun to not use any multiplications haha
            return memory[x][y]

        str_x = prepend_zeros(str_x, n)
        str_y = prepend_zeros(str_y, n)
        n_2 = n / 2

        a, b = int(str_x[:n_2] or 0), int(str_x[n_2:] or 0)
        c, d = int(str_y[:n_2] or 0), int(str_y[n_2:] or 0)

        ac = karatsuba(a, c)
        bd = karatsuba(b, d)
        ad_bc = karatsuba((a + b), (c + d)) - ac - bd

        # for supporting edge case where n is not a multiple of 2
        n_2 = int(ceil(n / 2.0))
        n = n if n % 2 == 0 else n + 1
        return (10**(n) * ac)  + (10**n_2 * ad_bc) + bd


I also created a testcase to test whether my implementation is correct:

    :::Python
    class MultiplicationTestCase(unittest.TestCase):

        def test_small_numbers(self):
            self.assertEqual(karatsuba(5, 5), 25)

        def test_different_size(self):
            self.assertEqual(karatsuba(2, 21), 42)

        def test_different_size(self):
            self.assertEqual(karatsuba(103, 3097), 318991)

        def test_two_digits1(self):
            self.assertEqual(karatsuba(50, 50), 2500)

        def test_two_digits2(self):
            self.assertEqual(karatsuba(19, 21), 399)

        def test_three_digits1(self):
            self.assertEqual(karatsuba(500, 500), 250000)

        def test_three_digits2(self):
            self.assertEqual(karatsuba(223, 321), 71583)

        def test_four_digits1(self):
            self.assertEqual(karatsuba(1234, 4321), 5332114)

        def test_seven_digits(self):
            self.assertEqual(karatsuba(5000000, 5000000),
                             25000000000000)

        def test_random_cases(self):
            for i in range(1000):
                x = randint(1,100000)
                y = randint(1,100000)
                expected = x * y
                result = karatsuba(x, y)
                self.assertEqual(karatsuba(x, y), expected,
                                ("Failed with x: %s and y: %s. "
                                 "Expected: %s but got %s") % 
                                 (x, y, expected, result))

