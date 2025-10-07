import pytest
import mars_dtc.mars_dtc as mdt

def test_to_from_ordinal_positive():
    d = mdt.MarsDate(214, 12, 10)
    ord_val = d.to_ordinal()
    d2 = mdt.MarsDate.from_ordinal(ord_val)
    assert (d.year, d.month, d.sol) == (d2.year, d2.month, d2.sol)

def test_to_from_ordinal_negative():
    d = mdt.MarsDate(-214, 12, 10)
    ord_val = d.to_ordinal()
    d2 = mdt.MarsDate.from_ordinal(ord_val)
    assert (d.year, d.month, d.sol) == (d2.year, d2.month, d2.sol)
    assert ord_val < 0
