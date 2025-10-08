"""
InforCOM ETL Transform Module.

This module handles the transformation phase of the InforCOM ETL pipeline.
It processes the extracted data, applies business rules, data cleaning, and formatting
to prepare the data for loading into the target system.

The transformation process typically includes:
1. Data validation and quality checks
2. Data type conversions and formatting
3. Business rule application
4. Data enrichment and calculated fields
5. Data structure normalization
6. Comprehensive logging throughout the process

Classes:
    InforCOMTransform: Main class handling InforCOM data transformation.
"""

from importlib import resources
import logging
from typing import Union
from nemo_library_etl.adapter._utils.db_handler import ETLDuckDBHandler
from nemo_library_etl.adapter.inforcom.config_models import PipelineInforCOM
from nemo_library_etl.adapter._utils.enums import ETLAdapter, ETLStep
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library import NemoLibrary

from nemo_library_etl.adapter.inforcom.enums import InforComTransformStep


class InforCOMTransform:
    """
    Handles transformation of extracted InforCOM data.
    
    This class manages the transformation phase of the InforCOM ETL pipeline,
    providing methods to process, clean, and format the extracted data for loading
    into the target system.
    
    The transformer:
    - Uses NemoLibrary for core functionality and configuration
    - Integrates with Prefect logging for pipeline visibility
    - Applies business rules and data validation
    - Handles data type conversions and formatting
    - Provides data enrichment and calculated fields
    - Ensures data quality and consistency
    
    Attributes:
        nl (NemoLibrary): Core Nemo library instance for system integration.
        config: Configuration object from the Nemo library.
        logger: Prefect logger for pipeline execution tracking.
        cfg (PipelineInforCOM): Pipeline configuration with transformation settings.
    """
    
    def __init__(
        self, 
        nl: NemoLibrary, 
        cfg: PipelineInforCOM, 
        logger: Union[logging.Logger, object], 
        fh: ETLFileHandler,
    ) -> None:
        """
        Initialize the InforCOM Transform instance.

        Sets up the transformer with the necessary library instances, configuration,
        and logging capabilities for the transformation process.

        Args:
            nl (NemoLibrary): Core Nemo library instance for system integration.
            cfg (PipelineInforCOM): Pipeline configuration object containing
                                                          transformation settings and rules.
            logger (Union[logging.Logger, object]): Logger instance for recording execution details.
                                                   Can be a standard Python logger or Prefect logger.
        """
        self.nl = nl
        self.cfg = cfg
        self.logger = logger
        self.fh = fh

        super().__init__()           

    def transform(self) -> None:
        """
        Execute the main transformation process for InforCOM data.
        
        This method orchestrates the complete transformation process by:
        1. Loading extracted data from the previous ETL phase
        2. Applying data validation and quality checks
        3. Performing data type conversions and formatting
        4. Applying business rules and logic
        5. Creating calculated fields and data enrichment
        6. Ensuring data consistency and integrity
        7. Preparing data for the loading phase
        
        The method provides detailed logging for monitoring and debugging purposes
        and handles errors gracefully to ensure pipeline stability.
        
        Note:
            The actual transformation logic needs to be implemented based on
            the specific InforCOM system requirements and business rules.
        """
        self.logger.info("Transforming all InforCOM objects")

        # transform objects
                
        with ETLDuckDBHandler(
            nl=self.nl,
            cfg=self.cfg,
            logger=self.logger,
            step=ETLStep.TRANSFORM,
            database=self.cfg.transform_database,
        ) as self.db:

            # load all extracted data into duckdb
            self.load_local_database()

            # perform joins
            self.joins()

    def load_local_database(self) -> None:
        self.logger.info("Loading all InforCOM objects into local database")

        if not self.db:
            raise ValueError("Database handler is not initialized")

        # load all extracted data into duckdb
        for table, model in self.cfg.extract.tables.items():
            if model.active is False:
                self.logger.info(f"Skipping inactive table: {table}")
                continue

            self.logger.info(f"Loading table: {table}")

            self.db.ingest_jsonl(
                step=ETLStep.EXTRACT,
                entity=table,
                ignore_nonexistent=True,
                create_mode="replace",  # or "append"
                table_name=str(table),  # keep your original table name
                add_metadata=True,  # adds _source_path & _ingested_at
            )

    def joins(self) -> None:
        """
        Execute join operations as defined in the configuration.

        This method processes join operations specified in the configuration,
        executing SQL queries to combine data from multiple tables based on
        defined relationships. The results are then saved for further processing
        or loading into the target system.

        The method provides detailed logging for monitoring and debugging purposes
        and handles errors gracefully to ensure pipeline stability.

        Note:
            The actual join logic needs to be implemented based on
            the specific InforCOM system requirements and business rules.
        """
        self.logger.info("Executing configured joins for InforCOM data")

        for join_name, join_cfg in self.cfg.transform.joins.items():
            if not join_cfg.active:
                self.logger.info(f"Skipping inactive join: {join_name}")
                continue

            self.logger.info(f"Processing join: {join_name}")

            try:
                if not self.db:
                    raise ValueError("Database handler is not initialized")

                # load the JOIN SQL from the config
                file = (
                    resources.files("nemo_library_etl")
                    / "adapter"
                    / ETLAdapter.INFORCOM.value
                    / "config"
                    / join_cfg.file
                )
                with resources.as_file(file) as sql_file:
                    query = sql_file.read_text(encoding="utf-8")

                if not query:
                    raise ValueError(f"Join SQL file is empty: {join_cfg.file}")

                query = query.replace("INFOR.", "")  # adjust schema if needed

                # Execute the join query
                join_result = self.db.query(query).fetch_arrow_table().to_pylist()

                # Save the result to a JSONL file
                out_path = self.fh.writeJSONL(
                    step=ETLStep.TRANSFORM,
                    entity=join_name,
                    data=join_result,
                    gzip_enabled=False,
                    substep=InforComTransformStep.JOINS,
                )
                self.logger.info(
                    f"Join result saved: {out_path} ({len(join_result)} rows)"
                )

            except Exception as e:
                raise ValueError(f"Error processing join {join_name}: {e}")
