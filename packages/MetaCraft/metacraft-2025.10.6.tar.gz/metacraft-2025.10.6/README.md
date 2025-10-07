# MetaCraft Toolkit

`MetaCraft` is a Python package for enriching and validating YAML schemas from a `pandas.DataFrame`. The `metadata.update()` function can now read YAML directly from URLs and even download remote ZIP files with multiple schemas, just like `pandas.read_csv`.

## Features

- **update**: enriches YAML with statistics and sketches (`tdigest`, `HyperLogLog`), storing the results in `metadata.df`.
- **validate**: checks the consistency between a DataFrame and the YAML (types, ranges, nulls, ...).
- **compare**: detects schema drift between two schemas.
- **export_schema**: converts the YAML to other formats (Spark, SQL, etc.).
- **generate_expectations**: creates Great Expectations suites.
- **transform**: returns a DataFrame adjusted to the schema.
- **quality_report**: simple quality score (completeness + drift).
- **research**: uses OpenAI to explore relationships and anomalies.
- **loglevel**: controls verbosity via `Metadata(loglevel="DEBUG")`.

## Installation

```bash
pip install MetaCraft
```

Or from the repository:

```bash
pip install -r requirements.txt
```

Optional dependencies: `openai`, `tdigest`, `datasketch`.

## Quick example

```python
import pandas as pd
from metacraft import Metadata

# Example DataFrame
df = pd.DataFrame({
    'survived': [0, 1, 1, 0],
    'age': [22, 38, 26, 35],
})

# Minimal schema
yaml_schema = {
    'schema': [
        {'identity': {'name': 'survived'}},
        {'identity': {'name': 'age'}},
    ]
}

# Save YAML to disk
import yaml
with open('schema.yaml', 'w') as f:
    yaml.safe_dump(yaml_schema, f, sort_keys=False, allow_unicode=True)

m = Metadata(loglevel="INFO")
m.update(df, 'schema.yaml', inplace=True)
m.quality_report(df)
```

### Customising OpenAI usage

`Metadata` can reuse an existing OpenAI client (or API key) and lets you define
the exact parameters that will be sent to the chat endpoint. Provide default
values through the constructor and override any of them per call:

```python
from openai import OpenAI
from metacraft import Metadata

client = OpenAI(api_key="sk-...")
metadata = Metadata(
    openai_api=client,
    openai_params={"model": "gpt-4.1-mini", "temperature": 0.2, "max_tokens": 600},
)

# Override defaults ad-hoc when exporting a schema
spark_code = metadata.export_schema(
    "spark",
    response_format={"type": "text"},
    max_tokens=900,
)
```

### Results

```text
✔ schema.yaml updated
root
 |-- survived: integer (nullable = false)
 |-- age: integer (nullable = false)
<class 'metadata.dataset'>
Columns: 2 entries
 #   Column            Non-Null Count   Dtype
---  ------            --------------   -----
 0   survived                        4   integer
 1   age                             4   integer
dtypes: integer(2)
Validation passed: True
Quality score: 100.0 (A)
```

### Remote ZIP example

`metadata.update()` can also process ZIP files hosted on the web. Just pass a URL ending in `.zip`:

```python
m.update(df, 'https://example.com/schemas.zip', verbose=True)
```
This downloads the ZIP to a temporary directory, applies the updates and leaves the resulting file in the same folder (or in the path provided with `output`).

### Editing metadata via `metadata.df`

After `m.update()` the schema lives in `m.df`, an editable DataFrame. Changes
can be propagated back to YAML with `m.df.upgrade()`:

```python
# 1) If all columns are integers
m.df['type.logical_type'] = 'integer'

# 2) Change the description of `age`
m.df.loc['age', 'identity.description_i18n.es'] = 'Passenger age'

# 3) Adjust the allowed range for `age`
m.df.loc['age', ['domain.numeric.min', 'domain.numeric.max']] = [0, 120]

m.df.upgrade('schema.yaml')  # save the updated YAML
m.df.revert()                # discard the changes in memory
```

## Roadmap

- ✔️ Remote YAML support (v 2025‑07‑30)
- ✔️ Remote ZIP download (v 2025‑07‑30)
- ✔️ Optional local cache
- ⬜ CLI (`metadata-cli update titanic.csv titanic.yaml`)

## Metadata generator

You can try the [Metadata Generator](https://chatgpt.com/g/g-68807807e1a4819189df3d0023a6e429-generador-de-metadatos), a GPT that creates the YAML from a `.head`.

Contributions welcome!
