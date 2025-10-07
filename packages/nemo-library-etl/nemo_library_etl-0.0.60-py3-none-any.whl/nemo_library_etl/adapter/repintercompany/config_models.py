"""
RepIntercompany ETL Configuration Models.

This module defines Pydantic models for configuring the RepIntercompany ETL pipeline.
These models provide type safety, validation, and structure for pipeline configuration,
including table-specific settings and overall pipeline control.

The models support:
- Table-level configuration with GUID tracking and activation flags
- Pipeline-wide configuration with phase control (extract/transform/load)
- Flexible configuration with additional fields support
- Version tracking for configuration compatibility
"""

from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class TableRepIntercompany(BaseModel):
    """
    Configuration model for individual RepIntercompany tables.
    
    This model defines the configuration structure for each table in the RepIntercompany
    system that will be processed by the ETL pipeline. Each table configuration
    includes identification and control parameters.
    
    Attributes:
        GUID (str): Unique identifier for the table in the RepIntercompany system.
        active (bool): Flag indicating whether this table should be processed.
                      Defaults to True.
    """
    GUID: str
    active: bool = True


class ExtractRepIntercompany(BaseModel):
    """
    Configuration model for the extraction phase of RepIntercompany ETL.
    
    This model encapsulates all configuration settings related to the data extraction
    phase, including which tables should be processed and their specific settings.
    
    Attributes:
        tables (Dict[str, TableRepIntercompany]): Dictionary mapping table names 
                                                                to their configuration models.
                                                                Defaults to empty dict.
    """
    tables: Dict[str, TableRepIntercompany] = Field(default_factory=dict)


class PipelineRepIntercompany(BaseModel):
    """
    Comprehensive configuration model for the entire RepIntercompany ETL pipeline.
    
    This is the root configuration model that controls all aspects of the ETL pipeline,
    including version tracking, phase activation, and detailed configuration for each
    phase (extract, transform, load).
    
    The model supports:
    - Version tracking for configuration compatibility
    - Individual phase control (enable/disable extract, transform, load)
    - Structured configuration for each phase
    - Additional fields for future extensibility
    
    Attributes:
        config_version (str): Version identifier for configuration compatibility.
                            Defaults to "0.0.1".
        extract_active (bool): Whether the extraction phase should run. Defaults to True.
        transform_active (bool): Whether the transformation phase should run. Defaults to True.
        load_active (bool): Whether the loading phase should run. Defaults to True.
        extract (ExtractRepIntercompany): Configuration for the extraction phase.
        transform (Dict[str, Any]): Configuration for the transformation phase.
                                  Defaults to empty dict.
        load (Dict[str, Any]): Configuration for the loading phase.
                             Defaults to empty dict.
    """
    config_version: str = "0.0.1"
    etl_directory: str = "./etl/repintercompany"
    extract_active : bool = True
    transform_active : bool = True
    load_active : bool = True    
    analyze_table: bool = True
    extract: ExtractRepIntercompany = Field(default_factory=ExtractRepIntercompany)
    transform: Dict[str, Any] = Field(default_factory=dict)
    load: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


# Expose the adapter models for the loader:
# These constants provide easy access to the model classes for dynamic loading
# and configuration validation in the ETL pipeline infrastructure.
TABLE_MODEL = TableRepIntercompany
PIPELINE_MODEL = PipelineRepIntercompany
