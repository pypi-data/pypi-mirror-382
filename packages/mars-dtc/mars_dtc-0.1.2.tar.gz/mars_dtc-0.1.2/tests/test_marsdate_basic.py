import pytest
import mars_dtc.mars_dtc as mdt

def test_basic_construction():
    d = mdt.MarsDate(214, 5, 12)
    assert d.year == 214
    assert d.month == 5
    assert d.sol == 12

def test_from_string_variants():
    assert mdt.MarsDate.from_string("214-14-28")
    assert mdt.MarsDate.from_string("214/14/28")
    assert mdt.MarsDate.from_string("214.14.28")
    assert mdt.MarsDate.from_string("-214/14/28")
    assert mdt.MarsDate.from_string("-214-14-28")
