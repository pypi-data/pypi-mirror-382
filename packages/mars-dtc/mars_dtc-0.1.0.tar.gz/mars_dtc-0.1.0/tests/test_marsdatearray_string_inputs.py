import pytest
import mars_dtc.mars_dtc as mdt


def test_construct_from_string_variants():

    arr = mdt.MarsDateArray(["214-12-22", "214/12/22", "214.12.22", "214 12 22"])
    assert all(isinstance(x, mdt.MarsDate) for x in arr)
    assert len(arr) == 4

    assert arr[0] == arr[1] == arr[2] == arr[3]


def test_construct_from_mixed_types():

    d = mdt.MarsDate(214, 12, 22)
    arr = mdt.MarsDateArray([d, "214-12-22", 143407])
    assert isinstance(arr[0], mdt.MarsDate)
    assert isinstance(arr[1], mdt.MarsDate)
    assert isinstance(arr[2], mdt.MarsDate)
    assert arr[0] == arr[1] == arr[2]


def test_construct_raises_on_invalid_strings():

    with pytest.raises((TypeError, ValueError)):
        mdt.MarsDateArray(["invalid-date", "214//22"])


def test_pandas_series_conversion_from_csv_strings(tmp_path):

    import pandas as pd

    csv_path = tmp_path / "mars_dates.csv"
    csv_path.write_text("darian_date\n214-12-22\n214/12/23\n214.12.24\n")

    df = pd.read_csv(csv_path)
    df["darian_date"] = mdt.MarsDateArray(df["darian_date"])


    assert str(df["darian_date"].dtype) == "marsdate"
    assert isinstance(df["darian_date"].array[0], mdt.MarsDate)
