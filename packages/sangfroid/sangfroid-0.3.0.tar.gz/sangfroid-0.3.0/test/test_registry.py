import pytest
from test import *
from sangfroid.registry import Registry

r = Registry()

@r()
class Wombat():
    pass

@r()
class Tra_La_La():
    pass

@r(name='barney')
class Tahvo:
    pass

def test_registry():

    assert r.from_name('Wombat')==Wombat
    assert r.from_name('wombat')==Wombat
    assert r.from_name('WOMBAT')==Wombat

    assert r.from_name('tralala')==Tra_La_La
    assert r.from_name('tra_la_la')==Tra_La_La
    assert r.from_name('TRALALA')==Tra_La_La
    assert r.from_name('TRA_LA_LA')==Tra_La_La
    assert r.from_name('TrA_lA_La')==Tra_La_La
    assert r.from_name('tra_____la_________la')==Tra_La_La
    assert r.from_name('t_ral_a_la')==Tra_La_La

    assert r.from_name('Barney')==Tahvo
    assert r.from_name('BaRnEy')==Tahvo
    assert r.from_name('BARNEY')==Tahvo
    assert r.from_name('BARNE_____Y')==Tahvo

    with pytest.raises(KeyError):
        r.from_name('fred')

    with pytest.raises(KeyError):
        r.from_name('tahvo')
