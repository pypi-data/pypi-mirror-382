import pytest
import json
import yaml
import math
import mars_dtc.mars_dtc as mdt


def test_basic_construction_and_str_repr():
    t = mdt.MarsDateTime(214, 14, 28, 12, 30, 45)
    assert t.year == 214
    assert t.month == 14
    assert t.sol == 28
    assert t.hour == 12
    assert t.minute == 30
    assert t.second == 45
    assert "214/14/28 12:30:45" in str(t)
    assert "DateTime" in repr(t)


def test_isoformat_and_dict_serialization():
    t = mdt.MarsDateTime(214, 14, 28, 12, 30, 0)
    iso = t.isoformat()
    assert iso == "+0214-14-28T12:30:00"

    d = t.to_dict()
    assert d["hour"] == 12 and d["minute"] == 30 and d["second"] == 0

    rebuilt = mdt.MarsDateTime.from_dict(d)
    assert rebuilt == t


def test_to_and_from_ordinal_float():
    t = mdt.MarsDateTime(214, 14, 28, 12, 0, 0)
    val = t.to_ordinal_float()
    assert math.isclose(val % 1, 0.5, rel_tol=1e-9)
    rebuilt = mdt.MarsDateTime.from_ordinal_float(val)
    assert rebuilt.hour == 12 and rebuilt.minute == 0 and rebuilt.second == 0
    assert rebuilt == t


def test_arithmetic_with_timedelta_and_datetime():
    t1 = mdt.MarsDateTime(214, 14, 28, 12, 0, 0)
    t2 = mdt.MarsDateTime(214, 14, 28, 15, 0, 0)
    diff = t2 - t1
    assert isinstance(diff, mdt.MarsTimedelta)
    assert math.isclose(diff.sols, 3 / 24, rel_tol=1e-9)

    td = mdt.MarsTimedelta(0.5)
    t3 = t1 + td
    assert isinstance(t3, mdt.MarsDateTime)
    assert t3.hour == 0 or t3.hour == 12


def test_floor_hour_and_sol():
    t = mdt.MarsDateTime(214, 14, 28, 12, 45, 30)
    floored_hour = t.floor("hour")
    assert floored_hour.hour == 12 and floored_hour.minute == 0 and floored_hour.second == 0

    floored_sol = t.floor("sol")
    assert floored_sol.hour == 0 and floored_sol.minute == 0


def test_ceil_and_round_units():
    t = mdt.MarsDateTime(214, 14, 28, 12, 45, 30)


    ceil_hour = t.ceil("hour")
    assert ceil_hour.hour == 13 and ceil_hour.minute == 0 and ceil_hour.second == 0

    ceil_sol = t.ceil("sol")
    assert ceil_sol.hour == 23 and ceil_sol.minute == 59 and ceil_sol.second == 59


    t1 = mdt.MarsDateTime(214, 14, 28, 12, 29, 40)
    t2 = mdt.MarsDateTime(214, 14, 28, 12, 30, 30)
    assert t1.round("minute").minute in (29, 30)
    assert t2.round("minute").minute == 31 or t2.round("minute").minute == 30


def test_json_and_yaml_serialization_roundtrip():
    t = mdt.MarsDateTime(214, 14, 28, 12, 30, 0)
    j = t.to_json()
    y = t.to_yaml()

    from_j = mdt.MarsDateTime.from_json(j)
    from_y = mdt.MarsDateTime.from_yaml(y)
    assert from_j == t
    assert from_y == t
    assert json.loads(j)["hour"] == 12
    assert yaml.safe_load(y)["minute"] == 30


def test_comparison_and_sorting_behavior():
    t1 = mdt.MarsDateTime(214, 14, 28, 8, 0, 0)
    t2 = mdt.MarsDateTime(214, 14, 28, 9, 0, 0)
    t3 = mdt.MarsDateTime(214, 14, 28, 23, 59, 59)
    assert t1 < t2
    assert t2 < t3
    assert sorted([t3, t1, t2]) == [t1, t2, t3]


def test_invalid_construction_raises():
    with pytest.raises(ValueError):
        mdt.MarsDateTime(214, 14, 28, 25, 0, 0)
    with pytest.raises(ValueError):
        mdt.MarsDateTime(214, 14, 28, 23, 61, 0)
    with pytest.raises(ValueError):
        mdt.MarsDateTime(214, 14, 28, 23, 59, 61)
