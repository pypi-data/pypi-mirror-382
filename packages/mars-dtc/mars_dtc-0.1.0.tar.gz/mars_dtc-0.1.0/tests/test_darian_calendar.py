import mars_dtc.mars_dtc as mdt

def test_leap_year_pattern():
    darian = mdt.DarianCalendar()

    assert darian.is_leap_year(10) is True
    assert darian.is_leap_year(20) is True
    assert darian.is_leap_year(100) is False
    assert darian.is_leap_year(500) is True

def test_month_lengths_consistency():
    darian = mdt.DarianCalendar()
    lengths_common = darian.month_lengths(2)
    lengths_leap = darian.month_lengths(10)
    assert len(lengths_common) == 24
    assert len(lengths_leap) == 24
    assert sum(lengths_common) == 668
    assert sum(lengths_leap) == 669
    assert sum(lengths_leap) == sum(lengths_common) + 1

