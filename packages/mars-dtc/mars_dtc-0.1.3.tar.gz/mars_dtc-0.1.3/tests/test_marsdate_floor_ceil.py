import mars_dtc.mars_dtc as mdt

def test_floor_and_ceil_month_year():
    d = mdt.MarsDate(201, 22, 15)

    floored_month = d.floor("month")
    assert floored_month.sol == 1
    assert floored_month.month == d.month

    ceiled_month = d.ceil("month")
    assert ceiled_month.month == d.month
    assert ceiled_month.sol >= d.sol

    floored_year = d.floor("year")
    assert floored_year.month == 1 and floored_year.sol == 1

    ceiled_year = d.ceil("year")
    assert ceiled_year.month == 24
    assert ceiled_year.sol in (27, 28) 

def test_round_month_and_year():
    d = mdt.MarsDate(214, 14, 28)
    rounded_month = d.round("month")
    assert isinstance(rounded_month, mdt.MarsDate)
    rounded_year = d.round("year")
    assert isinstance(rounded_year, mdt.MarsDate)
