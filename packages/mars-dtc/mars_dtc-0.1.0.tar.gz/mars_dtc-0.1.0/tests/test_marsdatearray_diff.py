import pytest
import mars_dtc.mars_dtc as mdt
import numpy as np


def make_sample_array():
    base = mdt.MarsDate(214, 14, 28)
    later = base.add_sols(10)
    earlier = base.add_sols(-5)
    return mdt.MarsDateArray([earlier, base, later]) 


def test_diff_basic_forward():
    arr = make_sample_array()
    diffs = arr.diff()
    assert len(diffs) == 3
    assert diffs[0] is None
    assert diffs[1].sols == 5
    assert diffs[2].sols == 10


def test_diff_unsorted():
    base = mdt.MarsDate(214, 14, 28)
    later = base.add_sols(10)
    earlier = base.add_sols(-5)
    arr_unsorted = mdt.MarsDateArray([base, later, earlier])  
    diffs = arr_unsorted.diff()

    assert diffs[1].sols == 10
    assert diffs[2].sols < 0


def test_diff_with_sort_before_flag():
    base = mdt.MarsDate(214, 14, 28)
    later = base.add_sols(10)
    earlier = base.add_sols(-5)
    arr_unsorted = mdt.MarsDateArray([base, later, earlier])

    diffs_sorted = arr_unsorted.diff(sort_before=True)
    sols = [d.sols if d else None for d in diffs_sorted]
    assert sols == [None, 5, 10]


def test_diff_periods_greater_than_one():
    arr = make_sample_array()
    diffs = arr.diff(periods=2)

    assert diffs[0] is None
    assert diffs[1] is None
    assert diffs[2].sols == 15


def test_diff_with_none_entries():
    base = mdt.MarsDate(214, 14, 28)
    arr = mdt.MarsDateArray([base, None, base.add_sols(5)])
    diffs = arr.diff()

    assert diffs[0] is None
    assert diffs[1] is None
    assert diffs[2] is None


def test_diff_returns_numpy_array():
    arr = make_sample_array()
    result = arr.diff()
    assert isinstance(result, np.ndarray)
    assert all(isinstance(d, (mdt.MarsTimedelta, type(None))) for d in result)
