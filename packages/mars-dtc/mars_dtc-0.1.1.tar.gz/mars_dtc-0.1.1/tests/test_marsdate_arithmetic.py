import mars_dtc.mars_dtc as mdt

def test_marsdate_timedelta_addition():
    d = mdt.MarsDate(214, 14, 26)
    delta = mdt.MarsTimedelta(sols=10)
    d_plus = d + delta
    d_minus = d - delta
    assert isinstance(d_plus, mdt.MarsDate)
    assert isinstance(d_minus, mdt.MarsDate)
    assert (d_plus - d).sols == 10
    assert (d - d_minus).sols == 10

def test_marsdate_add_months_years_sols():
    d = mdt.MarsDate(201, 23, 15)

    d2 = d.add_months(3)
    assert isinstance(d2, mdt.MarsDate)
    assert d2.month in range(1, 25)

    d3 = d.add_months(-25)
    assert isinstance(d3, mdt.MarsDate)

    d4 = d.add_years(2)
    assert d4.year == d.year + 2

    d5 = d.add_sols(500)
    assert (d5.to_ordinal() - d.to_ordinal()) == 500

def test_date_subtraction_returns_timedelta():
    d1 = mdt.MarsDate(214, 14, 26)
    d2 = d1.add_sols(20)
    delta = d2 - d1
    assert isinstance(delta, mdt.MarsTimedelta)
    assert delta.sols == 20


def test_marsdate_addition_produces_int_fields():
    d = mdt.MarsDate(214, 14, 26)
    delta = mdt.MarsTimedelta(sols=10)
    d_plus = d + delta

    assert isinstance(d_plus.year, int)
    assert isinstance(d_plus.month, int)
    assert isinstance(d_plus.sol, int)

    s = str(d_plus)
    r = repr(d_plus)
    assert "/" in s and "Date" in r
