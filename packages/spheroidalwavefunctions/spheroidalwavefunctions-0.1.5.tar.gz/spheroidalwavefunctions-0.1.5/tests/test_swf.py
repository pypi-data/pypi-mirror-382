import pytest
from math import isclose
from collections import namedtuple
swf_t = namedtuple('swf', ['r1c', 'ir1e', 'r1dc', 'ir1de', 'r2c', 'ir2e', 'r2dc', 'ir2de',
                           'naccr', 's1c', 'is1e', 's1dc', 'is1de', 'naccs'])


def test_swf_import():
    from spheroidalwavefunctions import prolate_swf
    assert hasattr(prolate_swf, 'profcn')

def test_pro_ang1():
    # prolate spheroidal angular of first kind and derivative
    from spheroidalwavefunctions import prolate_swf

    # Equivalent to scipy.special.pro_ang1(m=0, n=0, c=0.5, x=0.1)
    r = prolate_swf.profcn(c=0.5, m=0, lnum=2, x1=0.0, ioprad=0, iopang=2, iopnorm=0, arg=[0.1])
    p = swf_t._make(r)

    assert isclose(p.s1c[0][0], 1.013327494048905, rel_tol=1e-7) and p.is1e[0] == 0
    assert isclose(p.s1dc[0][0], -8.352682750613074, rel_tol=1e-7) and p.is1de[0] == -3  # the derivative

def test_pro_rad1():
    # prolate spheroidal radial of first kind and derivative
    from spheroidalwavefunctions import prolate_swf

    # Equivalent to scipy.special.pro_rad1(m=0, n=0, c=0.5, x=1.1)
    r = prolate_swf.profcn(c=0.5, m=0, lnum=2, x1=0.1, ioprad=1, iopang=0, iopnorm=0, arg=[0])
    p = swf_t._make(r)

    assert isclose(p.r1c[0], 9.77710828562897, rel_tol=1e-7) and p.ir1e[0] == -1
    assert isclose(p.r1dc[0], -9.043768088081511, rel_tol=1e-7) and p.ir1de[0] == -2  # the derivative

def test_pro_rad2():
    # prolate spheroidal radial of second kind and derivative
    from spheroidalwavefunctions import prolate_swf

    # Equivalent to scipy.special.pro_rad2(m=0, n=0, c=0.5, x=1.1)
    r = prolate_swf.profcn(c=0.5, m=0, lnum=2, x1=0.1, ioprad=2, iopang=0, iopnorm=0, arg=[0])
    p = swf_t._make(r)

    assert isclose(p.r2c[0], -2.8796530156285103, rel_tol=1e-7) and p.ir2e[0] == 0
    assert isclose(p.r2dc[0], 1.0007292932068599, rel_tol=1e-7) and p.ir2de[0] == 1  # the derivative
