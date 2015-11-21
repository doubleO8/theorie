#!/usr/bin/env python
"""
Copyright (C) 2010  WB

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
                
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
                                                
You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""


def natrange(start, end):
    for i in range(start, end + 1):
        yield i


def T(n):
    """
    T(n) fuer:

    for i in natrange(1, n-1):
        for j in natrange(i+1, n):
            for k in natrange(j, n):
                x += 1

    T(n) = (n^2 - 1)n / 6
    """
    x = 0
    for i in natrange(1, n - 1):
        for j in natrange(i + 1, n):
            for k in natrange(j, n):
                x += 1
    return x


def T_formel(n):
    return ((n ** 2 - 1) * n) / 6


def T2(n):
    """
    T(n) fuer:

    for i in natrange(1, 2*n):
        for j in natrange(1, n):
            for k in natrange(1, j):
                x += 1

    T(n) = n^2(n + 1)
    """
    x = 0

    for i in natrange(1, 2 * n):
        for j in natrange(1, n):
            for k in natrange(1, j):
                x += 1
    return x


def T2_formel(n):
    return (n ** 2 * (n + 1))


spacer = '=' * 10

print("%-30s %4s %30s" % (spacer, '<1>', spacer))
print T.__doc__
for n in natrange(2, 6):
    print("n=%d : %3d (%3d)" % (n, T(n), T_formel(n)))
print("%-30s %4s %30s" % (spacer, '</1>', spacer))

print

print("%-30s %4s %30s" % (spacer, '<2>', spacer))
print T2.__doc__
for n in natrange(1, 6):
    print("n=%d : %3d (%3d)" % (n, T2(n), T2_formel(n)))
print("%-30s %4s %30s" % (spacer, '</2>', spacer))
