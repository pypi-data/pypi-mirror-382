"""
HubSpot ETL Adapter Main Entry Point.

This module serves as the main entry point for the HubSpot ETL adapter, which handles
the extraction, transformation, and loading of data from HubSpot systems into Nemo.
"""
from nemo_library_etl.adapter._utils.argparse import parse_startup_args
from nemo_library_etl.adapter.hubspot.flow import hubspot_flow

def main() -> None:
    """
    Main function to execute the HubSpot ETL flow.

    This function initiates the complete HubSpot ETL process by calling the HubSpot_flow
    function, which orchestrates the extract, transform, and load operations.
    """
    args = parse_startup_args()
    hubspot_flow(args)


if __name__ == "__main__":
    main()
