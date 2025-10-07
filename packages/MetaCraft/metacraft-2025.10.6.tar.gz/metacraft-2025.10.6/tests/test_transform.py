import sys
from pathlib import Path

import pandas as pd
import numpy as np
from pandas.testing import assert_series_equal

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from metacraft import Metadata


def test_transform_fillna_dict_missing_key():
    m = Metadata()
    m._meta = {
        "x": {"type": {"logical_type": "integer"}},
        "y": {"type": {"logical_type": "float"}},
    }
    df = pd.DataFrame({"x": [1, None], "y": [2.0, None]})
    result = m.transform(df, fillna={"x": 0})
    assert_series_equal(result["x"], pd.Series([1, 0], name="x", dtype="Int64"))
    assert_series_equal(result["y"], pd.Series([2.0, np.nan], name="y"))


def test_transform_fillna_adds_category():
    m = Metadata()
    m._meta = {
        "cat": {"type": {"logical_type": "categorical"}},
    }
    df = pd.DataFrame({"cat": pd.Series(["a", None], dtype="category")})
    result = m.transform(df, fillna={"cat": "b"})
    assert list(result["cat"].cat.categories) == ["a", "b"]
    expected = pd.Series(pd.Categorical(["a", "b"], categories=["a", "b"]), name="cat")
    assert_series_equal(result["cat"], expected)

