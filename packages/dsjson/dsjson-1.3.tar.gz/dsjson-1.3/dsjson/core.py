import pandas as pd
import numpy as np
from datetime import datetime
from collections import OrderedDict
from typing import Optional, Dict, Any, Union
from pathlib import Path
import json


def extract_labels(
    spec_path: str, 
    sheet_name: str, 
    variable_name_col: str = "Variable Name", 
    variable_label_col: str = "Variable Label"
) -> dict:
    """
    Extracts a mapping of variable names to variable labels from an Excel sheet.

    Args:
        spec_path (str): The file path to the Excel specification.
        sheet_name (str): The name of the sheet to read from.
        variable_name_col (str): The name of the column containing variable names.
        variable_label_col (str): The name of the column containing variable labels.

    Returns:
        dict: A dictionary mapping variable names to their corresponding labels.
        
    Raises:
        ValueError: If the required columns are not found in the sheet.
    """
    sheet_data = pd.read_excel(spec_path, sheet_name=sheet_name)
    
    if variable_name_col not in sheet_data.columns or variable_label_col not in sheet_data.columns:
        raise ValueError(
            f"'{variable_name_col}' or '{variable_label_col}' not found in sheet '{sheet_name}'"
        )
    
    return sheet_data.set_index(variable_name_col)[variable_label_col].to_dict()


def make_column_metadata(df: pd.DataFrame, variable_labels: dict, domain: str) -> pd.DataFrame:
    """
    Generates a CDISC-style column metadata DataFrame from a data DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        variable_labels (dict): A dictionary mapping column names to their labels.
        domain (str): The domain name (e.g., "VS", "DM") for creating itemOIDs.

    Returns:
        pd.DataFrame: A DataFrame formatted as column metadata.
    """
    columns = []
    
    # A simple mapping from pandas dtype to Dataset-JSON data type
    dtype_map = {
        'object': 'string',
        'int64': 'integer',
        'float64': 'float',
        'bool': 'boolean',
        'datetime64[ns]': 'datetime'
    }

    for i, col in enumerate(df.columns):
        dtype_str = str(df[col].dtype)
        columns.append({
            "itemOID": f"IT.{domain}.{col}",
            "name": col,
            "label": variable_labels.get(col, col),  # Default to column name if no label
            "dataType": dtype_map.get(dtype_str, "string"), # Default to string
            "length": int(df[col].astype(str).str.len().max() or 0),
            "keySequence": i + 1,
        })
        
    return pd.DataFrame(columns)


def load_metadata(
    source: Union[pd.DataFrame, str, Path], 
    file_type: str = "csv"
) -> pd.DataFrame:
    """
    Load column metadata from different formats (csv, excel, json, xml, DataFrame).
    """
    if isinstance(source, pd.DataFrame):
        return source
    if file_type == "csv":
        return pd.read_csv(source)
    elif file_type == "excel":
        return pd.read_excel(source)
    elif file_type == "json":
        return pd.read_json(source)
    elif file_type == "xml":
        return pd.read_xml(source)
    else:
        raise ValueError("Unsupported file_type. Use 'csv', 'excel', 'json', 'xml', or a DataFrame.")


def to_dataset_json(
    data_df: pd.DataFrame,
    columns_df: pd.DataFrame,
    datasetJSONVersion: str = "1.1",
    name: Optional[str] = None,
    label: str = None,
    itemGroupOID: str = None,  # Required
    # Compound top-level fields
    sourceSystem_name: str = None,
    sourceSystem_version: str = None,
    # Optional top-level fields
    fileOID: str = None,
    dbLastModifiedDateTime: str = None,
    originator: str = None,
    studyOID: str = None,
    metaDataVersionOID: str = None,
    metaDataRef: str = None,
    **kwargs
) -> dict[str, Any]:
    """
    Create a CDISC-compliant Dataset-JSON v1.1 structure with strict key ordering.
    """
        # Add input validation
    if not isinstance(data_df, pd.DataFrame):
        raise TypeError("data_df must be a pandas DataFrame")
    if not isinstance(columns_df, pd.DataFrame):
        raise TypeError("columns_df must be a pandas DataFrame")
    if columns_df.empty:
        raise ValueError("columns_df cannot be empty")

    # Auto-generate creation timestamp
    datasetJSONCreationDateTime = datetime.now().isoformat()

    # Validate required fields
    required_fields = {
        "datasetJSONVersion": datasetJSONVersion,
        "datasetJSONCreationDateTime": datasetJSONCreationDateTime,
        "name": name,
        "label": label,
        "itemGroupOID": itemGroupOID
    }
    for key, val in required_fields.items():
        if val is None:
            raise ValueError(f"{key} is required")

    # Validate metadata/data alignment
    column_names = columns_df["name"].tolist()
    missing = [col for col in column_names if col not in data_df.columns]
    if missing:
        raise ValueError(f"Missing columns in row data: {missing}")
    
    # Make a copy and handle missing values
    data_df = data_df[column_names].copy()
    # Replace NaN and None with None (which will be converted to null in JSON)
    data_df = data_df.replace({np.nan: None})
    data_df = data_df.where(pd.notna(data_df), None)

    # Assemble compound sourceSystem
    sourceSystem = None
    if sourceSystem_name or sourceSystem_version:
        if not (sourceSystem_name and sourceSystem_version):
            raise ValueError("Both sourceSystem_name and sourceSystem_version must be provided.")
        sourceSystem = {
            "name": sourceSystem_name,
            "version": sourceSystem_version
        }

    # Create final structure with enforced key order
    dataset_json = OrderedDict()
    dataset_json["datasetJSONCreationDateTime"] = datasetJSONCreationDateTime
    dataset_json["datasetJSONVersion"] = datasetJSONVersion
    if fileOID:
        dataset_json["fileOID"] = fileOID
    if dbLastModifiedDateTime:
        dataset_json["dbLastModifiedDateTime"] = dbLastModifiedDateTime
    if originator:
        dataset_json["originator"] = originator
    if sourceSystem:
        dataset_json["sourceSystem"] = sourceSystem
    if studyOID:
        dataset_json["studyOID"] = studyOID
    if metaDataVersionOID:
        dataset_json["metaDataVersionOID"] = metaDataVersionOID
    if metaDataRef:
        dataset_json["metaDataRef"] = metaDataRef

    dataset_json["itemGroupOID"] = itemGroupOID
    dataset_json["records"] = len(data_df)
    dataset_json["name"] = name
    dataset_json["label"] = label
    dataset_json["columns"] = columns_df.to_dict(orient="records")
# Use this for large datasets:
    dataset_json["rows"] = [
        [None if pd.isna(val) else val for val in row] 
        for row in data_df.values
    ]

    # Add any additional top-level metadata if provided via kwargs
    dataset_json.update(kwargs)

    return dataset_json


def read_dataset_json(source: Union[str, Path]) -> pd.DataFrame:
    """
    Reads a CDISC Dataset-JSON file and loads it into a pandas DataFrame.

    The function extracts the tabular data and attaches the top-level
    metadata from the JSON file to the DataFrame's `attrs` attribute.

    Args:
        source (Union[str, Path]): The file path to the Dataset-JSON file 
                                     or a string containing the JSON text.

    Returns:
        pd.DataFrame: A DataFrame containing the dataset, with metadata 
                      stored in its `.attrs` attribute.
    """
    if isinstance(source, Path) or (isinstance(source, str) and source.endswith('.json')):
        with open(source, 'r', encoding='utf-8') as f:
            dataset_data = json.load(f)
    elif isinstance(source, str):
        dataset_data = json.loads(source)
    else:
        raise TypeError("source must be a file path or a JSON string.")

    # Extract column names from the 'columns' metadata
    column_names = [col['name'] for col in dataset_data['columns']]
    
    # Extract the row data
    rows = dataset_data['rows']
    
    # Create the DataFrame
    df = pd.DataFrame(rows, columns=column_names)
    
    # Attach all top-level metadata (excluding data) to the .attrs attribute
    metadata = {
        key: value for key, value in dataset_data.items() 
        if key not in ['columns', 'rows']
    }
    df.attrs = metadata
    
    return df