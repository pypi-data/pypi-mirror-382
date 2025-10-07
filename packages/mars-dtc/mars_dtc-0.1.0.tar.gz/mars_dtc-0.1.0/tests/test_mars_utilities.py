import pytest
import mars_dtc.mars_dtc as mdt


def test_basic_sol_range():
    start = mdt.MarsDate(214, 14, 25)
    end = mdt.MarsDate(214, 14, 28)
    dates = mdt.mars_date_range(start, end, freq="sol")
    assert len(dates) == 4
    assert dates[0] == start
    assert dates[-1] == end

    for i in range(1, len(dates)):
        assert (dates[i] - dates[i - 1]).sols == 1


def test_string_inputs_are_parsed():
    dates = mdt.mars_date_range("0214/14/25", "0214/14/28", freq="sol")
    assert isinstance(dates[0], mdt.MarsDate)
    assert len(dates) == 4
    assert dates[0].year == 214
    assert dates[-1].sol == 28


def test_month_frequency_steps():
    start = mdt.MarsDate(214, 10, 1)
    end = mdt.MarsDate(214, 13, 1)
    dates = mdt.mars_date_range(start, end, freq="month")
    assert len(dates) == 4
    assert all(isinstance(d, mdt.MarsDate) for d in dates)
    assert dates[1].month == 11
    assert dates[-1].month == 13


def test_year_frequency_steps():
    start = mdt.MarsDate(210, 1, 1)
    end = mdt.MarsDate(213, 1, 1)
    dates = mdt.mars_date_range(start, end, freq="year")
    assert len(dates) == 4
    assert [d.year for d in dates] == [210, 211, 212, 213]


def test_invalid_frequency_raises():
    start = mdt.MarsDate(214, 14, 25)
    end = mdt.MarsDate(214, 14, 28)
    with pytest.raises(ValueError):
        mdt.mars_date_range(start, end, freq="decade")


def test_start_after_end_raises():
    start = mdt.MarsDate(214, 14, 28)
    end = mdt.MarsDate(214, 14, 25)
    with pytest.raises(ValueError):
        mdt.mars_date_range(start, end, freq="sol")


def test_single_value_when_start_equals_end():
    start = mdt.MarsDate(214, 14, 28)
    end = mdt.MarsDate(214, 14, 28)
    dates = mdt.mars_date_range(start, end, freq="sol")
    assert len(dates) == 1
    assert dates[0] == start


def test_cross_month_transition():
    start = mdt.MarsDate(214, 14, 27)
    end = mdt.MarsDate(214, 15, 2)
    dates = mdt.mars_date_range(start, end, freq="sol")
    assert dates[0].month == 14
    assert dates[-1].month == 15

    for i in range(1, len(dates)):
        assert (dates[i] - dates[i - 1]).sols == 1


def test_martian_week_and_sol_of_year():
    d = mdt.MarsDate(214, 1, 1)
    assert mdt.get_martian_week(d) == 1
    assert d.sol_of_year() == 1

    d_next = d.add_sols(14)
    assert mdt.get_martian_week(d_next) == 3
    assert d_next.sol_of_year() == 15


def test_full_martian_year_length():
    dates = mdt.mars_date_range("0214/01/01", "0215/01/01", freq="sol")

    assert len(dates) == 669
    assert str(dates[0]) == "214/01/01"
    assert str(dates[-1]) == "215/01/01"

def test_weekday_and_name_consistency():
    d = mdt.MarsDate(214, 14, 28)
    wd_num = d.weekday()
    wd_full = d.weekday_name()
    wd_short = d.weekday_name(short=True)

    assert 1 <= wd_num <= 7
    assert isinstance(wd_full, str)
    assert isinstance(wd_short, str)
    assert len(wd_short) <= len(wd_full)

    cal = d.calendar
    assert wd_full == cal.weekday_name(wd_num)
    assert wd_short == cal.weekday_name(wd_num, short=True)
