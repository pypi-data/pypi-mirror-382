import pandas as pd
import yaml
from pathlib import Path

from metacraft import Metadata


def test_df_upgrade_updates_meta(tmp_path):
    df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    schema = {
        'schema': [
            {'identity': {'name': 'a'}, 'type': {'logical_type': 'integer'}},
            {'identity': {'name': 'b'}, 'type': {'logical_type': 'integer'}},
        ]
    }
    yaml_path = tmp_path / 'schema.yaml'
    yaml_path.write_text(yaml.safe_dump(schema, sort_keys=False, allow_unicode=True))

    m = Metadata()
    m.update(df, yaml_path, inplace=True, verbose=False)
    m.df.loc['a', 'type.logical_type'] = 'float'
    m.df.upgrade()

    assert m._meta['a']['type']['logical_type'] == 'float'
