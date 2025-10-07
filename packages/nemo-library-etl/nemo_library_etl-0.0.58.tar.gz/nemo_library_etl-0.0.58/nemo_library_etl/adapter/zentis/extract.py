"""
Zentis ETL Extract Module.

This module handles the extraction phase of the Zentis ETL pipeline.
It provides functionality to extract data from Zentis systems and 
prepare it for the transformation phase.

The extraction process:
1. Connects to the Zentis system using configured credentials
2. Iterates through configured tables and extracts data
3. Handles inactive tables by skipping them
4. Uses ETLFileHandler for data persistence
5. Provides comprehensive logging throughout the process

Classes:
    ZentisExtract: Main class handling Zentis data extraction.
"""

import logging
from pathlib import Path
from typing import Union
from nemo_library_etl.adapter._utils.datatype_handler import normalize_na, read_csv_all_str
from nemo_library_etl.adapter.zentis.config_models import PipelineZentis
from nemo_library_etl.adapter._utils.enums import ETLAdapter, ETLStep
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library import NemoLibrary

import pandas as pd


class ZentisExtract:
    """
    Handles extraction of data from Zentis system.
    
    This class manages the extraction phase of the Zentis ETL pipeline,
    providing methods to connect to Zentis systems, retrieve data,
    and prepare it for subsequent transformation and loading phases.
    
    The extractor:
    - Uses NemoLibrary for core functionality and configuration
    - Integrates with Prefect logging for pipeline visibility
    - Processes tables based on configuration settings
    - Handles both active and inactive table configurations
    - Leverages ETLFileHandler for data persistence
    
    Attributes:
        nl (NemoLibrary): Core Nemo library instance for system integration.
        config: Configuration object from the Nemo library.
        logger: Prefect logger for pipeline execution tracking.
        cfg (PipelineZentis): Pipeline configuration with extraction settings.
    """
    
    def __init__(
        self, 
        nl: NemoLibrary, 
        cfg: PipelineZentis, 
        logger: Union[logging.Logger, object], 
        fh: ETLFileHandler,
    ) -> None:
        """
        Initialize the Zentis Extract instance.
        
        Sets up the extractor with the necessary library instances, configuration,
        and logging capabilities for the extraction process.
        
        Args:
            nl (NemoLibrary): Core Nemo library instance for system integration.
            cfg (PipelineZentis): Pipeline configuration object containing
                                                          extraction settings and rules.
            logger (Union[logging.Logger, object]): Logger instance for recording execution details.
                                                   Can be a standard Python logger or Prefect logger.
        """
        self.nl = nl
        self.cfg = cfg
        self.logger = logger
        self.fh = fh

        super().__init__()            
    
    def extract(self) -> None:
        """
        Execute the main extraction process for Zentis data.
        
        This method orchestrates the complete extraction process by:
        1. Logging the start of extraction
        2. Iterating through configured tables
        3. Skipping inactive tables
        4. Processing active tables and extracting their data
        5. Using ETLFileHandler for data persistence
        
        The method respects table activation settings and provides detailed
        logging for monitoring and debugging purposes.
        
        Note:
            The actual data extraction logic needs to be implemented based on
            the specific Zentis system requirements.
        """
        self.logger.info("Extracting all Zentis objects")

        src_dir = Path(self.cfg.source_directory)
        if not src_dir.exists():
            raise FileNotFoundError(f"Source directory does not exist: {src_dir}")

        # extract objects
        for table, model in self.cfg.extract.tables.items():
            if model.active is False:
                self.logger.info(f"Skipping inactive table: {table}")
                continue

            self.logger.info(f"Extracting object {table} from file {model.file_name}")

            df = read_csv_all_str(
                csv_path=src_dir / model.file_name,
                sep=";",
                encoding="latin1",
            )
            df = normalize_na(df)

            self.logger.info(f"Extracted {len(df):,} rows for table {table}")
            data = df.to_dict(orient="records")
            self.fh.writeJSONL(
                adapter=ETLAdapter.ZENTIS, step=ETLStep.EXTRACT, entity=table, data=data
            )
