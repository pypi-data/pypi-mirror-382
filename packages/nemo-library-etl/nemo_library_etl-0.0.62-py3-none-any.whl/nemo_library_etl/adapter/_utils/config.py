import json
import os
import re
from importlib import import_module
from importlib import resources as importlib_resources
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Type

from platformdirs import PlatformDirs
from pydantic import BaseModel, ConfigDict, Field, ValidationError

# =========================
# Conventions & Derivations
# =========================


def _normalize_adapter(adapter: str) -> str:
    """
    Normalize adapter name into a safe, conventional package/app name.
    Examples:
      "Gedys" -> "gedys"
      "My Adapter" -> "myadapter"
      "foo-bar" -> "foo_bar"
    """
    a = adapter.strip().lower()
    a = re.sub(r"\s+", "", a)  # remove spaces
    return re.sub(r"[^0-9a-z_]", "_", a)  # keep [a-z0-9_]


def _root_pkg() -> str:
    """
    Infer the root package from this module's __name__.
    For 'adapter.utils.config' -> returns 'nemo_library'.
    """
    return __name__.split(".", 1)[0]


def _candidate_base_packages(adapter_norm: str) -> List[str]:
    """
    Candidate base package names in which to look for:
      - config/default_config.json
      - config_models (TABLE_MODEL / PIPELINE_MODEL)
    Order matters; the first that exists wins.
    """
    root = _root_pkg()
    return [
        adapter_norm,  # "gedys" (standalone adapter package)
        f"{adapter_norm}_adapter",  # "gedys_adapter"
        f"{root}.adapter.{adapter_norm}",  # "adapter.gedys"
        f"{root}.{adapter_norm}",  # "gedys"
    ]


def _env_var_name(adapter_norm: str) -> str:
    """
    Build the environment variable name for overrides.
    'gedys' -> 'GEDYS_CONFIG'
    """
    return adapter_norm.upper() + "_CONFIG"


def _candidate_paths(appname: str) -> Dict[str, Path]:
    """
    Canonical config locations using PlatformDirs.
    - site:   system-wide
    - user:   per-user
    - project: ./config/<appname>.json in current working directory
    """
    d = PlatformDirs(appname=appname)
    return {
        "site": Path(d.site_config_dir) / "config.json",
        "user": Path(d.user_config_dir) / "config.json",
        "project": Path.cwd() / "config" / f"{appname}.json",
    }


# ==================
# Minimal Base Schema
# ==================


class _TableBase(BaseModel):
    """Minimum table config across all adapters."""

    active: bool = True


class _ExtractBase(BaseModel):
    tables: Dict[str, _TableBase] = Field(default_factory=dict)


class _PipelineBase(BaseModel):
    """
    Minimal top-level config. We allow extras so adapter-specific keys
    don't break validation if PIPELINE_MODEL is absent.
    """

    config_version: str = "0.0.1"
    etl_directory: str = "./etl/<adapter>"
    extract_active: bool = True
    transform_active: bool = True
    load_active: bool = True
    gzip_enabled: bool = True
    extract: _ExtractBase = Field(default_factory=_ExtractBase)
    transform: Dict[str, Any] = Field(default_factory=dict)
    load: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


# ======================
# Adapter Model Discovery
# ======================


class _AdapterModels(NamedTuple):
    table_model: Optional[Type[BaseModel]] = None
    pipeline_model: Optional[Type[BaseModel]] = None


def _load_adapter_models(adapter_norm: str) -> _AdapterModels:
    """
    Try to import TABLE_MODEL / PIPELINE_MODEL from 'config_models' inside any
    plausible adapter package base (see _candidate_base_packages()).
    """
    for base_pkg in _candidate_base_packages(adapter_norm):
        try:
            m = import_module(f"{base_pkg}.config_models")
            return _AdapterModels(
                table_model=getattr(m, "TABLE_MODEL", None),
                pipeline_model=getattr(m, "PIPELINE_MODEL", None),
            )
        except ModuleNotFoundError:
            continue
    return _AdapterModels()


# =============
# I/O Utilities
# =============


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge override into base. Lists are replaced (not extended).
    This is conventional for configs, where a later layer fully overrides a list.
    """
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k] = _deep_merge(dict(base[k]), v)
        else:
            base[k] = v
    return base


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _default_config_dict(adapter_norm: str) -> Dict[str, Any]:
    """
    Locate and load 'config/default_config.json' from the first adapter package
    that provides it, following _candidate_base_packages().
    """
    for base_pkg in _candidate_base_packages(adapter_norm):
        try:
            files = importlib_resources.files(base_pkg)
            path = files.joinpath("config/default_config.json")
            if path.is_file():
                with path.open("r", encoding="utf-8") as f:
                    return json.load(f)
        except (ModuleNotFoundError, FileNotFoundError):
            continue
    return {}  # No defaults found; higher layers may still provide everything


# =============
# Public API
# =============


def load_pipeline_config(
    adapter: str,
    config_file: Optional[Path] = None,
) -> BaseModel:
    """
    Convention-over-Configuration loader.

    You only pass the adapter name (e.g., "Gedys").
    The loader will:
      - normalize it to 'gedys'
      - look for defaults in one of:
          1) gedys
          2) gedys_adapter
          3) <root>.adapter.gedys         (e.g., adapter.gedys)
          5) <root>.gedys
        under 'config/default_config.json'
      - merge layers in precedence:
          default < site < user < project < ENV < CLI
        where ENV var is '<ADAPTER>_CONFIG', e.g. 'GEDYS_CONFIG'
      - validate minimally using _PipelineBase
      - if available, validate per-table with adapter's TABLE_MODEL
      - if available, validate full config with adapter's PIPELINE_MODEL
      - return the adapter pipeline model instance if provided, else _PipelineBase

    Parameters
    ----------
    adapter : str
        Human-friendly adapter name, e.g., "Gedys".
    config_file : Optional[Path], optional
        Optional path to a JSON config file to override all other layers,
        by default None
    Returns
    -------
    BaseModel
        Pydantic model instance: adapter pipeline model if available, else _PipelineBase.
    """
    adapter_norm = _normalize_adapter(adapter)
    appname = adapter_norm
    env_var = _env_var_name(adapter_norm)

    # 1) defaults
    cfg: Dict[str, Any] = _default_config_dict(adapter_norm)

    # 2) layered files: site, user, project
    paths = _candidate_paths(appname)
    for key in ("site", "user", "project"):
        cfg = _deep_merge(cfg, _load_json(paths[key]))

    # 3) ENV: file path or inline JSON
    env_val = os.getenv(env_var)
    if env_val:
        p = Path(env_val)
        if p.exists():
            cfg = _deep_merge(cfg, _load_json(p))
        else:
            try:
                cfg = _deep_merge(cfg, json.loads(env_val))
            except json.JSONDecodeError:
                raise RuntimeError(
                    f"{env_var} must be a file path or JSON string (got: {env_val})"
                )

    # 4) config_json argument
    if config_file:
        p = Path(config_file)
        if not p.exists():
            raise RuntimeError(f"Config file not found: {p}")
        cfg = _deep_merge(cfg, _load_json(p))

    # --- minimal validation ---
    try:
        base_obj = _PipelineBase.model_validate(cfg)
    except ValidationError as e:
        raise RuntimeError(f"Invalid base configuration: {e}") from e

    # --- adapter-specific validation (optional) ---
    models = _load_adapter_models(adapter_norm)

    # per-table validation, if TABLE_MODEL is present
    if models.table_model:
        tables = cfg.get("extract", {}).get("tables", {})
        if not isinstance(tables, dict):
            raise RuntimeError(
                "extract.tables must be an object mapping table name -> table config"
            )
        validated_tables: Dict[str, Dict[str, Any]] = {}
        for name, tdict in tables.items():
            if not isinstance(tdict, dict):
                raise RuntimeError(f"Table '{name}' must be an object")
            validated_tables[name] = models.table_model.model_validate(
                tdict
            ).model_dump()
        # Put validated tables back for possible pipeline-level validation
        cfg = dict(cfg)
        cfg.setdefault("extract", {})
        cfg["extract"] = dict(cfg["extract"])
        cfg["extract"]["tables"] = validated_tables

    # full pipeline validation, if PIPELINE_MODEL is present
    if models.pipeline_model:
        try:
            return models.pipeline_model.model_validate(cfg)
        except ValidationError as e:
            raise RuntimeError(f"Invalid adapter configuration: {e}") from e

    # otherwise return minimal model
    return base_obj
