import mars_dtc.mars_dtc as mdt
import json
import yaml

def test_json_and_yaml_roundtrip():
    mdate = mdt.MarsDate(214, 14, 28)
    j = mdate.to_json()
    y = mdate.to_yaml()

    restored_json = mdt.MarsDate.from_json(j)
    assert isinstance(restored_json, mdt.MarsDate)
    assert restored_json == mdate

    restored_yaml = mdt.MarsDate.from_yaml(y)
    assert isinstance(restored_yaml, mdt.MarsDate)
    assert restored_yaml == mdate

    parsed_json = json.loads(j)
    parsed_yaml = yaml.safe_load(y)
    assert parsed_json["year"] == 214
    assert parsed_yaml["month"] == 14
