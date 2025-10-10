## README.md

### Project: dsjson

A lightweight Python package to convert clinical tabular datasets (e.g., SDTM/ADaM) and metadata into **CDISC Dataset-JSON v1.1** format. It supports multiple metadata input formats including CSV, Excel, JSON, and XML (planned). If you don't have a specific column metadata file the it can also extracts variable label from specification file and create column metadata.


[![PyPI](https://img.shields.io/pypi/v/dsjson.svg)](https://pypi.org/project/dsjson/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

The CDISC Dataset-JSON standard is essential for regulatory submissions and data sharing in the clinical trial industry. This package simplifies the process of creating compliant JSON files from common data formats like CSV or pandas DataFrames, saving developers time and reducing the risk of manual errors.


### Features

* Converts `DataFrame` + column metadata to Dataset-JSON v1.1
* Supports CSV, Excel, JSON for metadata
* Auto-generates `datasetJSONCreationDateTime`
* Enforces required top-level metadata
* Extract Variable Label from Specification file
* Converts extracted Variable Label into column metadata
* loads a Dataset-JSON file into a pandas DataFrame and attaches the top-level metadata to the DataFrame's attrs attribute.

### Installation
```
pip install dsjson
```

### Quick Start

```python
from dsjson import load_metadata, to_dataset_json, extract_labels, make_column_metedata
import pandas as pd

my_excel_path = r"specification path"

# Load data
rows = pd.read_csv("examples/vs.csv")

# Extract variables from specification and convereted that to column metadata
variable_labels = extract_labels(spec_path=my_excel_path, sheet_name="DM", variable_name_col="Variable Name", variable_label_col="Variable Label")
columns = make_column_metadata(df=data_df, variable_labels=variable_labels, domain="DM")

# this can be used where we already have column metadata already defined in a file - if you make column metadata as per above code, then this is not required
columns = load_metadata("examples/columns_vs.csv", file_type="csv")

# Create Dataset-JSON
ds = to_dataset_json(
    data_df=rows,
    columns_df=columns,
    name="VS",
    label="Vital Signs",
    itemGroupOID="IG.VS",
    originator="My CRO",
    sourceSystem_name="Python",
    sourceSystem_version="3.10",
    fileOID="F.VS.001",
    studyOID="S.1234"
)

# loads a Dataset-JSON file into a pandas DataFrame and attaches the top-level metadata to the DataFrame's attrs attribute.
vs_df = read_dataset_json("examples/vs.json")

# Access the attached metadata from the .attrs attribute
print(f"File OID: {vs_df.attrs.get('fileOID')}")
print(f"Originator: {vs_df.attrs.get('originator')}")
```