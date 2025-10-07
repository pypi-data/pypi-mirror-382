import pytest
import mars_dtc.mars_dtc as mdt

def test_comparisons():
    mdate1 = mdt.MarsDate(214, 20, 2)
    mdate2 = mdt.MarsDate(214, 14, 28)

    assert mdate1 != mdate2
    assert not (mdate1 == mdate2)
    assert mdate2 < mdate1
    assert mdate2 <= mdate1
    assert mdate1 > mdate2
    assert mdate1 >= mdate2
    assert sorted([mdate1, mdate2]) == [mdate2, mdate1]


