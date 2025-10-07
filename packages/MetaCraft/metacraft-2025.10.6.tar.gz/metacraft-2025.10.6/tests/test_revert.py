import pandas as pd
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from metacraft import Metadata


def test_df_revert_recovers_previous_state(tmp_path):
    df = pd.DataFrame({'a': [1], 'b': [2]})
    schema = {
        'schema': [
            {'identity': {'name': 'a'}, 'type': {'logical_type': 'integer'}},
            {'identity': {'name': 'b'}, 'type': {'logical_type': 'integer'}},
        ]
    }
    path = tmp_path / 'schema.yaml'
    path.write_text(yaml.safe_dump(schema, sort_keys=False, allow_unicode=True))

    m = Metadata()
    m.update(df, path, inplace=True, verbose=False)
    original = m.df.copy()
    m.df.loc['a', 'type.logical_type'] = 'float'
    m.df.revert()

    assert m.df.equals(original)


def test_cache_dir_loads_previous_df(tmp_path):
    df = pd.DataFrame({'a': [1]})
    schema = {
        'schema': [
            {'identity': {'name': 'a'}, 'type': {'logical_type': 'integer'}},
        ]
    }
    path = tmp_path / 'schema.yaml'
    path.write_text(yaml.safe_dump(schema, sort_keys=False, allow_unicode=True))

    m = Metadata(cache_dir=tmp_path)
    m.update(df, path, inplace=True, verbose=False)
    cached = m.df.copy()

    # create new instance to load from cache
    m2 = Metadata(cache_dir=tmp_path)
    assert m2.df is not None
    assert m2.df.equals(cached)
