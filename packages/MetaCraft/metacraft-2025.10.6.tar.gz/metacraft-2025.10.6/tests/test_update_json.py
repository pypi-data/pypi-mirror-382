import json
from pathlib import Path
import pandas as pd
import yaml

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from metacraft import Metadata


def test_update_reads_json(tmp_path):
    df = pd.DataFrame({'a': [1, 2]})
    schema = {
        'schema': [
            {'identity': {'name': 'a'}, 'type': {'logical_type': 'integer'}},
        ]
    }
    path = tmp_path / 'schema.json'
    path.write_text(json.dumps(schema))

    m = Metadata()
    m.update(df, path, inplace=True)

    loaded = yaml.safe_load(path.read_text())
    assert loaded['schema'][0]['statistics']['n_non_null'] == 2
