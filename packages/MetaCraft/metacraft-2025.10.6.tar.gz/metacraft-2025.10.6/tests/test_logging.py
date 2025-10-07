import logging
import pandas as pd
import yaml
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from metacraft import Metadata

def test_logger_level(tmp_path):
    df = pd.DataFrame({'a': [1]})
    schema = {'schema': [{'identity': {'name': 'a'}, 'type': {'logical_type': 'integer'}}]}
    path = tmp_path / 's.yaml'
    path.write_text(yaml.safe_dump(schema, sort_keys=False, allow_unicode=True))

    m = Metadata(loglevel='DEBUG')
    assert m.logger.level == logging.DEBUG
    m.update(df, path, inplace=True, verbose=False)


