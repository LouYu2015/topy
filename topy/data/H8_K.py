﻿"""
# =============================================================================
# Write the stiffness matrix of finite element to file. The created file name
# is equal to the string between the underscores of *this* file's name, plus a
# 'K' extension, e.g.,
#
#     python ELEM_K.py
#
# gives a file named ELEM.K in the same directory.
#
# Author: William Hunter
# Copyright (C) 2008, 2015, William Hunter.
# =============================================================================
"""
from __future__ import division

import os

from sympy import symbols, Matrix, diff, integrate, zeros
from numpy import abs, array

from ..utils import get_logger, get_data_file
from .matlcons import *

logger = get_logger(__name__)
# Get file name:
fname = get_data_file(__file__)

if os.path.exists(fname):
    logger.info('{} (stiffness matrix) exists!'.format(fname))
else:
    # SymPy symbols:
    a, b, c, x, y, z = symbols('a b c x y z')
    N1, N2, N3, N4 = symbols('N1 N2 N3 N4')
    N5, N6, N7, N8 = symbols('N5 N6 N7 N8')
    E, nu, g, G = symbols('E nu g G')
    o = symbols('o') #  dummy symbol
    xlist = [x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x]
    ylist = [y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y]
    zlist = [z, z, z, z, z, z, z, z, z, z, z, z, z, z, z, z, z, z, z, z, z, z, z, z]
    yxlist = [y, x, o, y, x, o, y, x, o, y, x, o, y, x, o, y, x, o, y, x, o, y, x, o]
    zylist = [o, z, y, o, z, y, o, z, y, o, z, y, o, z, y, o, z, y, o, z, y, o, z, y]
    zxlist = [z, o, x, z, o, x, z, o, x, z, o, x, z, o, x, z, o, x, z, o, x, z, o, x]

    # Shape functions:
    N1 = (a - x) * (b - y) * (c - z) / (8 * a * b * c)
    N2 = (a + x) * (b - y) * (c - z) / (8 * a * b * c)
    N3 = (a + x) * (b + y) * (c - z) / (8 * a * b * c)
    N4 = (a - x) * (b + y) * (c - z) / (8 * a * b * c)
    N5 = (a - x) * (b - y) * (c + z) / (8 * a * b * c)
    N6 = (a + x) * (b - y) * (c + z) / (8 * a * b * c)
    N7 = (a + x) * (b + y) * (c + z) / (8 * a * b * c)
    N8 = (a - x) * (b + y) * (c + z) / (8 * a * b * c)

    # Create strain-displacement matrix B:
    B0 = tuple(map(diff, [N1, 0, 0, N2, 0, 0, N3, 0, 0, N4, 0, 0,\
                    N5, 0, 0, N6, 0, 0, N7, 0, 0, N8, 0, 0], xlist))
    B1 = tuple(map(diff, [0, N1, 0, 0, N2, 0, 0, N3, 0, 0, N4, 0,\
                    0, N5, 0, 0, N6, 0, 0, N7, 0, 0, N8, 0], ylist))
    B2 = tuple(map(diff, [0, 0, N1, 0, 0, N2, 0, 0, N3, 0, 0, N4,\
                    0, 0, N5, 0, 0, N6, 0, 0, N7, 0, 0, N8], zlist))
    B3 = tuple(map(diff, [N1, N1, N1, N2, N2, N2, N3, N3, N3, N4, N4, N4,\
                    N5, N5, N5, N6, N6, N6, N7, N7, N7, N8, N8, N8], yxlist))
    B4 = tuple(map(diff, [N1, N1, N1, N2, N2, N2, N3, N3, N3, N4, N4, N4,\
                    N5, N5, N5, N6, N6, N6, N7, N7, N7, N8, N8, N8], zylist))
    B5 = tuple(map(diff, [N1, N1, N1, N2, N2, N2, N3, N3, N3, N4, N4, N4,\
                    N5, N5, N5, N6, N6, N6, N7, N7, N7, N8, N8, N8], zxlist))
    B = Matrix([B0, B1, B2, B3, B4, B5])

    # Create constitutive (material property) matrix:
    C = Matrix([[(1 - nu) * g, nu * g, nu * g, 0, 0, 0],
                [nu * g, (1 - nu) * g, nu * g, 0, 0, 0],
                [nu * g, nu * g, (1 - nu) * g, 0, 0, 0],
                [0, 0, 0,                      G, 0, 0],
                [0, 0, 0,                      0, G, 0],
                [0, 0, 0,                      0, 0, G]])

    dK = B.T * C * B

    # Integration:
    logger.info('SymPy is integrating: K for H8...')
    K = dK.integrate((x, -a, a),(y, -b, b),(z, -c, c))

    # Convert SymPy Matrix to NumPy array:
    K = array(K.subs({a:_a, b:_b, c:_c, E:_E, nu:_nu, g:_g, G:_G})).astype('double')

    # Set small (<< 0) values equal to zero:
    K[abs(K) < 1e-6] = 0

    # Create file:
    K.dump(fname)
    logger.info('Created ' + fname + ' (stiffness matrix).')

# EOF H8_K.py
