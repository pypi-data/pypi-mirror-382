"""
InforCOM ETL Extract Module.

This module handles the extraction phase of the InforCOM ETL pipeline.
It provides functionality to extract data from InforCOM systems and 
prepare it for the transformation phase.

The extraction process:
1. Connects to the InforCOM system using configured credentials
2. Iterates through configured tables and extracts data
3. Handles inactive tables by skipping them
4. Uses ETLFileHandler for data persistence
5. Provides comprehensive logging throughout the process

Classes:
    InforCOMExtract: Main class handling InforCOM data extraction.
"""

import logging
from typing import Union
from nemo_library_etl.adapter._utils.generic_odbc import GenericODBCExtract
from nemo_library_etl.adapter.inforcom.config_models import PipelineInforCOM
from nemo_library_etl.adapter._utils.enums import ETLAdapter, ETLStep
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library import NemoLibrary


class InforCOMExtract:
    """
    Handles extraction of data from InforCOM system.
    
    This class manages the extraction phase of the InforCOM ETL pipeline,
    providing methods to connect to InforCOM systems, retrieve data,
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
        cfg (PipelineInforCOM): Pipeline configuration with extraction settings.
    """
    
    def __init__(
        self, 
        nl: NemoLibrary, 
        cfg: PipelineInforCOM, 
        logger: Union[logging.Logger, object], 
        fh: ETLFileHandler,
    ) -> None:
        """
        Initialize the InforCOM Extract instance.
        
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
        Execute the main extraction process for InforCOM data.
        
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
            the specific InforCOM system requirements.
        """
        self.logger.info("Extracting all InforCOM objects")

        # extract objects
        odbc = GenericODBCExtract(
            nl=self.nl,
            cfg=self.cfg,
            logger=self.logger,
            fh=self.fh,
            odbc_connstr=self.cfg.extract.odbc_connstr,
            timeout=self.cfg.extract.timeout,
        )
        for table, model in self.cfg.extract.tables.items():
            if model.active is False:
                self.logger.info(f"Skipping inactive table: {table}")
                continue

            self.logger.info(f"Extracting table: {table}")
            odbc.generic_odbc_extract(
                query=f"SELECT * FROM {self.cfg.extract.table_prefix}{table}",
                step=ETLStep.EXTRACT,
                entity=table,
                chunksize=self.cfg.extract.chunk_size if model.big_data else None,
                gzip_enabled=True,
            )
