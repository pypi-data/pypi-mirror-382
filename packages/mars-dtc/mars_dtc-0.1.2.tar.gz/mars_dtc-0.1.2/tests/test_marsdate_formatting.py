import mars_dtc.mars_dtc as mdt

def test_format_tokens():
    mdate = mdt.MarsDate(214, 14, 28)

    s1 = mdate.format("%Y/%m/%d")
    assert s1 == "214/14/28"

    s2 = mdate.format("%b %d, %Y")
    assert "Mit" in s2 and "28" in s2 and "214" in s2

    s3 = mdate.format("%B %d, %Y")
    assert "Mithuna" in s3

    s4 = mdate.format("%A, %B %d, %Y")
    assert "Sol" in s4 and "Mithuna" in s4

    s5 = mdate.format("%a, %b %d, %Y")
    assert len(s5.split(",")) >= 2

def test_isoformat_consistency():
    d1 = mdt.MarsDate(214, 14, 28)
    d2 = mdt.MarsDate(-214, 14, 28)
    assert d1.isoformat() == "+0214-14-28"
    assert d2.isoformat() == "-0214-14-28"
    assert len(d1.isoformat()) == len(d2.isoformat())

def test_marsdate_str_formatting_after_float_addition():

    d = mdt.MarsDate(214, 12, 27)
    td = mdt.MarsTimedelta(5.0)  
    result = d + td

    s = str(result)
    assert isinstance(s, str)
    assert "/" in s
    assert len(s.split("/")) == 3

    assert all(isinstance(getattr(result, f), int) for f in ("year", "month", "sol"))
    
def test_dataframe_repr_does_not_fail_with_marsdate(monkeypatch):
    import pandas as pd
    d = mdt.MarsDate(214, 12, 27)
    td = mdt.MarsTimedelta(5.0)
    df = pd.DataFrame({"darian_date": [d]})
    df["darian_date_plus5"] = df["darian_date"] + td

    df_repr = repr(df)
    assert "214" in df_repr
