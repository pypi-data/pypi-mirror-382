import pandas as pd
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from metacraft import Metadata


def test_quality_report_scores(tmp_path):
    df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    schema = {
        'schema': [
            {'identity': {'name': 'a'}, 'type': {'logical_type': 'integer'}},
            {'identity': {'name': 'b'}, 'type': {'logical_type': 'integer'}},
        ]
    }
    path = tmp_path / 'schema.yaml'
    path.write_text(yaml.safe_dump(schema, sort_keys=False, allow_unicode=True))

    m = Metadata()
    m.update(df, path, inplace=True)

    report_good = m.quality_report(df, message=False)
    df_bad = pd.DataFrame({'a': [1, 2]})
    report_bad = m.quality_report(df_bad, message=False)

    assert report_good['score'] > report_bad['score']
