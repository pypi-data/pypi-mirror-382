import numpy as np
import pandas as pd
import mars_dtc.mars_dtc as mdt


def make_sample_dataframe():
    dates = [
        mdt.MarsDate(214, 12, 22),
        mdt.MarsDate(214, 13, 2),
        mdt.MarsDate(214, 13, 12),
        mdt.MarsDate(214, 13, 22),
        mdt.MarsDate(214, 14, 2),
    ]
    temps = [210, 213, 215, 218, 220]
    press = [700, 705, 710, 715, 720]
    df = pd.DataFrame({
        "darian_date": mdt.MarsDateArray(dates),
        "ground_temperature_max": temps,
        "pressure_current": press
    })
    return df



# Sorting and indexing


def test_sorting_and_indexing():
    df = make_sample_dataframe()
    df_sorted = df.sort_values("darian_date")
    assert isinstance(df_sorted["darian_date"].array, mdt.MarsDateArray)

    df_sorted = df_sorted.set_index("darian_date")
    assert isinstance(df_sorted.index.array, mdt.MarsDateArray)
    assert df_sorted.index.min() < df_sorted.index.max()



# Filtering by MarsDate range


def test_filtering_by_date_range():
    df = make_sample_dataframe().sort_values("darian_date").set_index("darian_date")

    start = mdt.MarsDate(214, 13, 1)
    end = mdt.MarsDate(214, 13, 20)

    mask = (df.index >= start) & (df.index <= end)
    filtered = df.loc[mask]
    assert all(start <= idx <= end for idx in filtered.index)



# Arithmetic on MarsDate columns


def test_marsdate_add_timedelta():
    df = make_sample_dataframe()
    df["darian_date_plus5"] = df["darian_date"] + mdt.MarsTimedelta(sols=5)
    assert isinstance(df["darian_date_plus5"].array, mdt.MarsDateArray)
    for d1, d2 in zip(df["darian_date"], df["darian_date_plus5"]):
        assert (d2.to_ordinal() - d1.to_ordinal()) == 5



# Join / merge


def test_join_merge_on_marsdate():
    df1 = make_sample_dataframe()
    df2 = make_sample_dataframe()
    merged = pd.merge(df1, df2, on="darian_date", how="inner")
    assert not merged.empty
    assert "ground_temperature_max_x" in merged.columns



# Grouping and aggregation


def test_grouping_by_year_month():
    df = make_sample_dataframe()

    # Force reconversion to MarsDateArray explicitly
    mars_array = mdt.MarsDateArray(df["darian_date"])
    df["year"] = [d.year for d in mars_array]
    df["month"] = [d.month for d in mars_array]

    grouped = (
        df.groupby(["year", "month"])
        .agg(
            avg_temp=("ground_temperature_max", "mean"),
            avg_press=("pressure_current", "mean"),
        )
        .reset_index()
    )

    assert {"year", "month", "avg_temp", "avg_press"} <= set(grouped.columns)
    assert grouped.shape[0] > 0



def test_conversion_to_numpy_and_string():
    df = make_sample_dataframe()
    ordinals = df["darian_date"].to_numpy()
    assert np.all(np.diff(ordinals) > 0)  # increasing order

    as_str = df["darian_date"].astype(str)
    assert all(isinstance(x, str) for x in as_str)


def test_diff_between_rows():
    df = make_sample_dataframe().sort_values("darian_date")
    ords = np.array([v.to_ordinal() for v in df["darian_date"]])
    diffs = np.diff(ords)
    assert np.all(diffs > 0)
    assert np.mean(diffs) > 0



# Vectorized floor / grouping by floored month


def test_floor_and_group_by_month():
    df = make_sample_dataframe()
    df["month_floor"] = df["darian_date"].array.floor("month")

    grouped = (
        df.groupby("month_floor")["ground_temperature_max"]
        .mean()
        .reset_index()
    )
    assert isinstance(grouped["month_floor"].array, mdt.MarsDateArray)
    assert grouped.shape[0] > 0
