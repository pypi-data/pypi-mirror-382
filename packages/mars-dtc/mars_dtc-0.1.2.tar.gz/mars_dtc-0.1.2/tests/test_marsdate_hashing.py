import mars_dtc.mars_dtc as mdt

def test_hash_equality_consistency():
    d1 = mdt.MarsDate(214, 14, 28)
    d2 = mdt.MarsDate(214, 14, 28)
    d3 = mdt.MarsDate(214, 14, 27)

    assert hash(d1) == hash(d2)

    assert hash(d1) != hash(d3)

def test_hash_allows_dict_key_usage():
    d1 = mdt.MarsDate(214, 14, 28)
    d2 = mdt.MarsDate(214, 20, 2)
    d3 = mdt.MarsDate(214, 14, 28)

    dates_dict = {d1: "start", d2: "mid"}

    assert dates_dict[d1] == "start"
    assert dates_dict[d2] == "mid"

    assert dates_dict[d3] == "start"

def test_hash_uses_calendar_name():

    darian1 = mdt.DarianCalendar()
    class FakeCalendar:
        def month_lengths(self, year): return darian1.month_lengths(year)
        def is_leap_year(self, year): return darian1.is_leap_year(year)
        def to_ordinal(self, y, m, s): return darian1.to_ordinal(y, m, s)
        def from_ordinal(self, o): return darian1.from_ordinal(o)

    d_darian = mdt.MarsDate(214, 14, 28, calendar=darian1)
    d_fake = mdt.MarsDate(214, 14, 28, calendar=FakeCalendar())

    assert d_darian != d_fake
    assert hash(d_darian) != hash(d_fake)

def test_hash_stability_in_set():
    d = mdt.MarsDate(214, 14, 28)
    s = {d}
    assert d in s

    h_before = hash(d)
    _ = d.to_ordinal() 
    h_after = hash(d)
    assert h_before == h_after
