import json
import logging
from pathlib import Path
import pandas as pd

from nemo_library_etl.adapter.hubspotforecast.flow import hubspotforecast_flow


ETL_Path = Path(__file__).parent / "etl" / "hubspot"


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with open(path, mode="r", encoding="utf-8") as f:
        for ln, line in enumerate(f, start=1):
            s = line.strip()
            if not s:
                continue
            try:
                rec = json.loads(s)
            except Exception as e:
                raise ValueError(f"Invalid JSONL at {path}:{ln}: {e}") from e
            if not isinstance(rec, dict):
                raise ValueError(
                    f"Expected JSON object per line at {path}:{ln}, got {type(rec).__name__}"
                )
            records.append(rec)
    return records

def test_hubspot() -> None:

    # delete ETL folder if it exists
    if ETL_Path.exists():
        import shutil

        logging.info(f"Removing existing ETL folder: {ETL_Path}")
        shutil.rmtree(ETL_Path)
        
    try:
        args = {
            "config_ini": "./tests/config.ini",
            "config_json": "./tests/config/hubspot.json",
        }
        hubspotforecast_flow(args)
    except Exception as e:
        assert False, f"HubSpot flow failed with exception: {e}"

    # check if the flow created the expected files
    # we expect 3 folders in etl/hubspot: extract, transform, load

    etl_path = Path(__file__).parent / "etl" / "hubspot"
    assert etl_path.exists(), f"ETL path {etl_path} does not exist"
    extract_path = etl_path / "extract"
    transform_path = etl_path / "transform"
    load_path = etl_path / "load"
    assert extract_path.exists(), f"Extract path {extract_path} does not exist"
    assert transform_path.exists(), f"Transform path {transform_path} does not exist"
    assert load_path.exists(), f"Load path {load_path} does not exist"

    # check if the load folder has created 2 files:
    # - dealsforecastdeals.jsonl
    # - dealsforecastheader.jsonl

    dealsforecastdeals_file = load_path / "dealsforecastdeals.jsonl"
    dealsforecastheader_file = load_path / "dealsforecastheader.jsonl"
    assert (
        dealsforecastdeals_file.exists()
    ), f"File {dealsforecastdeals_file} does not exist"
    assert (
        dealsforecastheader_file.exists()
    ), f"File {dealsforecastheader_file} does not exist"

    # load the dealsforecastdeals.jsonl file and check if it has at least 1 row
    records = load_jsonl(dealsforecastheader_file)
    assert len(records) > 0, "Header data is empty"

    header_df = pd.DataFrame(records)

    # assert there are at least 1 row and not more than 4 rows with dealstage = "Unqualified lead"
    unqualified_lead_rows = header_df[header_df["dealstage"] == "Unqualified lead"]
    assert len(unqualified_lead_rows) >= 1, "There are no Unqualified lead rows"
    assert (
        len(unqualified_lead_rows) <= 4
    ), "There are more than 4 Unqualified lead rows"

    # clean up
    # delete ETL folder if it exists
    if ETL_Path.exists():
        import shutil

        logging.info(f"Removing existing ETL folder: {ETL_Path}")
        shutil.rmtree(ETL_Path)
    