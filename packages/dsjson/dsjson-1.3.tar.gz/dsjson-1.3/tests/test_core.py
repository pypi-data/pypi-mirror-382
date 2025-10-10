import pandas as pd
import os
import json
from dsjson import (
    load_metadata, 
    to_dataset_json, 
    extract_labels, 
    make_column_metadata, 
    read_dataset_json
)

# --- Setup paths to find example files ---
# Get the directory of the current test file
tests_dir = os.path.dirname(__file__)
# Construct the relative path to the examples directory
examples_dir = os.path.abspath(os.path.join(tests_dir, '..', 'examples'))

# --- Test Data ---
# Load sample data once to reuse in multiple tests
SAMPLE_DATA_DF = pd.read_csv(os.path.join(examples_dir, "vs.csv"))
SAMPLE_COLUMNS_DF = load_metadata(os.path.join(examples_dir, "columns_vs.csv"))

def test_to_dataset_json():
    """
    Tests the main function `to_dataset_json` to ensure it creates a valid structure.
    """
    result = to_dataset_json(
        data_df=SAMPLE_DATA_DF,
        columns_df=SAMPLE_COLUMNS_DF,
        name="VS",
        label="Vital Signs",
        itemGroupOID="IG.VS",
        sourceSystem_name="TestTool",
        sourceSystem_version="1.0"
    )

    assert result["name"] == "VS"
    assert result["records"] == len(SAMPLE_DATA_DF)
    assert "rows" in result
    assert "columns" in result
    assert result["sourceSystem"]["name"] == "TestTool"

def test_extract_labels(tmp_path):
    """
    Tests the `extract_labels` function by creating a temporary Excel file.
    """
    # 1. Create a mock Excel specification file
    spec_file = tmp_path / "spec.xlsx"
    mock_spec_data = pd.DataFrame({
        "Variable Name": ["STUDYID", "USUBJID"],
        "Variable Label": ["Study Identifier", "Unique Subject Identifier"]
    })
    mock_spec_data.to_excel(spec_file, sheet_name="DM", index=False)

    # 2. Call the function with the mock file
    labels = extract_labels(spec_path=spec_file, sheet_name="DM")

    # 3. Assert the result is correct
    expected_labels = {
        "STUDYID": "Study Identifier",
        "USUBJID": "Unique Subject Identifier"
    }
    assert labels == expected_labels

def test_make_column_metadata():
    """
    Tests the `make_column_metadata` function to ensure it generates a valid metadata DataFrame.
    """
    # 1. Define some test data and labels
    test_df = pd.DataFrame({
        "STUDYID": ["TEST01"],
        "SUBJID": [101],
        "VISIT": ["SCREENING"]
    })
    test_labels = {"STUDYID": "Study ID", "SUBJID": "Subject ID"}

    # 2. Call the function
    metadata_df = make_column_metadata(df=test_df, variable_labels=test_labels, domain="DM")

    # 3. Assert the structure and content are correct
    assert isinstance(metadata_df, pd.DataFrame)
    assert "itemOID" in metadata_df.columns
    assert metadata_df.loc[0, "label"] == "Study ID"
    assert metadata_df.loc[2, "label"] == "VISIT"  # Check default label
    assert metadata_df.loc[1, "dataType"] == "integer"

def test_read_and_write_cycle(tmp_path):
    """
    Tests the full "round trip": writing a Dataset-JSON file and then reading it back.
    This validates both `to_dataset_json` and `read_dataset_json`.
    """
    # 1. Create and save a Dataset-JSON object
    json_dict = to_dataset_json(
        data_df=SAMPLE_DATA_DF,
        columns_df=SAMPLE_COLUMNS_DF,
        name="VS",
        label="Vital Signs",
        itemGroupOID="IG.VS",
        originator="RoundTripTest"
    )
    json_file_path = tmp_path / "test_vs.json"
    with open(json_file_path, 'w') as f:
        json.dump(json_dict, f)

    # 2. Use the new `read_dataset_json` function to load it
    df_from_json = read_dataset_json(json_file_path)

    # 3. Assert that the data and metadata match the original
    assert isinstance(df_from_json, pd.DataFrame)
    assert df_from_json.attrs.get("name") == "VS"
    assert df_from_json.attrs.get("originator") == "RoundTripTest"
    
    # Ensure the DataFrame content is the same (ignoring type differences from JSON conversion)
    # Reorder columns of the original df to match the one read from JSON
    original_data_reordered = SAMPLE_DATA_DF[df_from_json.columns]
    pd.testing.assert_frame_equal(original_data_reordered, df_from_json, check_dtype=False)