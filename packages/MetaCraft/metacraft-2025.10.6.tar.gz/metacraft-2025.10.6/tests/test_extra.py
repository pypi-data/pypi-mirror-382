import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from metacraft import Metadata


def test_snapshot_roundtrip():
    m = Metadata()
    m._meta = {"a": {"type": {"logical_type": "integer"}}}
    m.snapshot("v1")
    m._meta["a"]["type"]["logical_type"] = "float"
    m.snapshot("v2")
    m.load_snapshot("v1")
    assert m._meta["a"]["type"]["logical_type"] == "integer"
    assert set(m.list_snapshots()) == {"v1", "v2"}


def test_describe_returns_summary():
    m = Metadata()
    m._meta = {
        "a": {
            "type": {"logical_type": "integer"},
            "statistics": {
                "numeric_summary": {
                    "count": 2,
                    "mean": 1.5,
                    "std": 0.5,
                    "min": 1.0,
                    "p25": 1.25,
                    "p50": 1.5,
                    "p75": 1.75,
                    "p95": 1.95,
                    "max": 2.0,
                }
            },
            "identity": {"description_i18n": {"en": "a"}, "tags": []},
        }
    }
    desc = m.describe()
    assert desc.loc["mean", "a"] == 1.5
    assert list(desc.columns) == ["a"]


def test_filter_by_type_tag_domain():
    m = Metadata()
    m._meta = {
        "a": {
            "type": {"logical_type": "integer"},
            "identity": {"description_i18n": {"en": "a"}, "tags": ["keep"]},
            "domain": {"numeric": {"min": 0}}
        },
        "b": {
            "type": {"logical_type": "float"},
            "identity": {"description_i18n": {"en": "b"}, "tags": []}
        }
    }
    res = m.filter(logical_type="integer", tag="keep", has_domain=True)
    assert list(res["column"]) == ["a"]
