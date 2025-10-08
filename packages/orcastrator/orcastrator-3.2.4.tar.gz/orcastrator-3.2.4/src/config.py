"""Configuration models for Orcastrator using Pydantic."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import toml
from loguru import logger as log
from pydantic import BaseModel, Field, field_validator, model_validator


class GlobalConfig(BaseModel):
    """Global user configuration from ~/.orcastrator_config."""

    orca_path: Optional[Path] = Field(
        default=None, description="Path to ORCA executable"
    )
    openmpi_path: Optional[Path] = Field(
        default=None, description="Path to OpenMPI installation directory"
    )
    scratch_dir: Optional[Path] = Field(
        default=None, description="Default scratch directory"
    )

    @field_validator("orca_path", "openmpi_path", "scratch_dir", mode="before")
    def _expand_paths(cls, v):
        if v is None:
            return None
        return Path(v).expanduser().resolve()


def load_global_config() -> GlobalConfig:
    """Load global user configuration from ~/.orcastrator_config.

    Returns:
        GlobalConfig instance (possibly with all None values if file doesn't exist)
    """
    config_file = Path.home() / ".orcastrator_config"

    if not config_file.exists():
        log.debug(f"Global config not found at {config_file}, using defaults")
        return GlobalConfig()

    try:
        raw = toml.loads(config_file.read_text())
        log.debug(f"Loaded global config from {config_file}")
        return GlobalConfig(**raw)
    except Exception as e:
        log.warning(f"Failed to load global config from {config_file}: {e}")
        return GlobalConfig()


class StageConfig(BaseModel):
    """Configuration for a single calculation stage."""

    name: str = Field(..., description="Stage name (e.g., 'opt', 'freq', 'sp')")
    simple_keywords: List[str] = Field(
        ..., min_length=1, description="ORCA keywords (simple input line)"
    )
    blocks: List[str] = Field(
        default_factory=list, description="Additional ORCA % blocks"
    )
    mult: Optional[int] = Field(
        default=None, description="Override multiplicity for this stage"
    )
    charge: Optional[int] = Field(
        default=None, description="Override charge for this stage"
    )
    keep: List[str] = Field(
        default_factory=list,
        description="File patterns to copy from previous stage (e.g., ['*.gbw'])",
    )

    @field_validator("name")
    def _strip_name(cls, v: str) -> str:
        return v.strip()


class WorkflowConfig(BaseModel):
    """Main workflow configuration."""

    # Core settings
    output_dir: Path = Field(default=Path("output"), description="Output directory")
    molecules_dir: Path = Field(
        default=Path("molecules"), description="Directory containing .xyz files"
    )

    # Variable substitution defaults
    keywords: Dict[str, Any] = Field(
        default_factory=dict,
        description="Global default values for keyword substitution in stages",
    )

    # Resource settings
    cpus: int = Field(default=1, ge=1, description="Total CPU cores available")
    mem_per_cpu_gb: int = Field(default=1, ge=1, description="Memory per CPU in GB")
    workers: int = Field(default=1, ge=1, description="Number of parallel workers")
    scratch_dir: Path = Field(
        default=Path("/scratch"), description="Scratch directory for calculations"
    )

    # Workflow settings
    stages: List[StageConfig] = Field(
        ..., min_length=1, description="Calculation stages"
    )
    overwrite: bool = Field(
        default=False, description="Overwrite existing calculations"
    )

    # Filtering
    include: List[str] = Field(
        default_factory=list, description="Include only these molecules"
    )
    exclude: List[str] = Field(
        default_factory=list, description="Exclude these molecules"
    )
    rerun_failed: bool = Field(
        default=False, description="Only rerun previously failed molecules"
    )

    # SLURM settings (optional)
    nodelist: List[str] = Field(default_factory=list, description="SLURM node list")
    exclude_nodes: List[str] = Field(
        default_factory=list, description="SLURM nodes to exclude"
    )
    timelimit: Optional[str] = Field(
        default=None, description="SLURM time limit (HH:MM:SS)"
    )
    partition: str = Field(default="normal", description="SLURM partition")
    account: Optional[str] = Field(default=None, description="SLURM account")
    email: Optional[str] = Field(
        default=None, description="Email for SLURM notifications"
    )
    orca_install_dir: str = Field(
        default="/soft/orca/orca_6_0_1_linux_x86-64_shared_openmpi416_avx2",
        description="ORCA installation directory",
    )
    openmpi_install_dir: str = Field(
        default="/soft/openmpi/openmpi-4.1.6",
        description="OpenMPI installation directory",
    )

    # Other
    debug: bool = Field(default=False, description="Enable debug logging")

    # Internal: store config file path for relative path resolution
    _config_file_path: Optional[Path] = None

    @model_validator(mode="before")
    def _normalize_legacy_config(cls, values):
        """Support legacy config format from old orcastrator."""
        if not isinstance(values, dict):
            return values

        # Handle legacy 'main' section
        if "main" in values:
            main = values.pop("main")
            values["output_dir"] = main.get("output_dir", "output")
            values["overwrite"] = main.get("overwrite", False)
            values["debug"] = main.get("debug", False)
            values["cpus"] = main.get("cpus", 1)
            values["mem_per_cpu_gb"] = main.get("mem_per_cpu_gb", 1)
            values["workers"] = main.get("workers", 1)
            values["scratch_dir"] = main.get("scratch_dir", "/scratch")
            values["nodelist"] = main.get("nodelist", [])
            values["exclude_nodes"] = main.get("exclude", [])
            values["timelimit"] = main.get("timelimit")

        # Handle legacy 'molecules' section
        if "molecules" in values:
            mol = values.pop("molecules")
            values["molecules_dir"] = mol.get("directory", "molecules")
            values["include"] = mol.get("include", [])
            values["exclude"] = mol.get("exclude", [])
            values["rerun_failed"] = mol.get("rerun_failed", False)

        # Handle legacy 'dataset' section
        if "dataset" in values:
            dataset = values.pop("dataset")
            values["molecules_dir"] = dataset.get("directory", "molecules")
            values["include"] = dataset.get("include", [])
            values["exclude"] = dataset.get("exclude", [])
            values["rerun_failed"] = dataset.get("rerun_failed", False)

        # Handle legacy 'resources' section
        if "resources" in values:
            res = values.pop("resources")
            values["cpus"] = res.get("cpus", 1)
            values["mem_per_cpu_gb"] = res.get("mem_per_cpu_gb", 1)
            values["workers"] = res.get("workers", 1)
            values["scratch_dir"] = res.get("scratch_dir", "/scratch")

        # Handle legacy 'slurm' section
        if "slurm" in values:
            slurm = values.pop("slurm")
            values["nodelist"] = slurm.get("nodelist", [])
            values["exclude_nodes"] = slurm.get("exclude", [])
            values["timelimit"] = slurm.get("timelimit")

        # Handle legacy 'step' instead of 'stages'
        if "step" in values and "stages" not in values:
            values["stages"] = values.pop("step")

        # Handle legacy 'keywords' instead of 'simple_keywords' in stages
        if "stages" in values:
            for stage in values["stages"]:
                if (
                    isinstance(stage, dict)
                    and "keywords" in stage
                    and "simple_keywords" not in stage
                ):
                    stage["simple_keywords"] = stage.pop("keywords")

        return values

    def _resolve_path(self, path: Path) -> Path:
        """Resolve path relative to config file location."""
        if path.is_absolute():
            return path.expanduser().resolve()

        # Resolve relative to config file if available
        if self._config_file_path:
            base_dir = self._config_file_path.parent
            return (base_dir / path).resolve()

        # Fallback to cwd
        return (Path.cwd() / path).resolve()

    @field_validator("output_dir", "molecules_dir", "scratch_dir", mode="before")
    def _resolve_paths(cls, v: str) -> Path:
        """Store path as-is for now, will resolve after config_file_path is set."""
        return Path(v)

    @field_validator("stages")
    def _unique_stage_names(cls, v: List[StageConfig]) -> List[StageConfig]:
        names = [s.name for s in v]
        duplicates = {n for n in names if names.count(n) > 1}
        if duplicates:
            raise ValueError(f"Duplicate stage names found: {duplicates}")
        return v

    def resolve_paths(self, config_file: Path) -> None:
        """Resolve all paths relative to the config file.

        This must be called after loading the config.
        """
        self._config_file_path = config_file.resolve()
        self.output_dir = self._resolve_path(self.output_dir)
        self.molecules_dir = self._resolve_path(self.molecules_dir)
        # Don't resolve scratch_dir - it's usually an absolute system path
        self.scratch_dir = self.scratch_dir.expanduser().resolve()


def substitute_variables(
    template: str, molecule_metadata: Dict[str, Any], global_keywords: Dict[str, Any]
) -> str:
    """Substitute variables in template string using molecule metadata and global keywords.

    Variables are specified using {variable_name} syntax. Resolution order:
    1. Molecule-specific metadata (from XYZ file JSON)
    2. Global keywords (from config [keywords] section)
    3. Error if not found

    Args:
        template: String containing variables like "nroot {casscf_roots}"
        molecule_metadata: Molecule-specific metadata from XYZ file
        global_keywords: Global default keywords from config

    Returns:
        String with all variables substituted

    Raises:
        KeyError: If a variable is not found in either metadata or global keywords
    """
    import re

    pattern = r"\{(\w+)\}"

    def replacer(match):
        var_name = match.group(1)
        # Try molecule metadata first, then global keywords
        if var_name in molecule_metadata:
            return str(molecule_metadata[var_name])
        elif var_name in global_keywords:
            return str(global_keywords[var_name])
        else:
            raise KeyError(
                f"Variable '{var_name}' not found in molecule metadata or global keywords"
            )

    return re.sub(pattern, replacer, template)


def load_config(config_file: Path) -> WorkflowConfig:
    """Load and validate workflow configuration from a TOML file.

    Args:
        config_file: Path to the TOML configuration file

    Returns:
        Validated WorkflowConfig instance

    Raises:
        toml.TomlDecodeError: if the TOML is invalid
        pydantic.ValidationError: if the config does not match the schema
    """
    raw = toml.loads(config_file.read_text())
    config = WorkflowConfig(**raw)
    config.resolve_paths(config_file)
    return config
