"""Unit tests for config module."""

from pathlib import Path

import pytest
import toml
from pydantic import ValidationError

from src.config import (
    SlurmSettings,
    StageConfig,
    WorkflowConfig,
    load_config,
    substitute_variables,
)


class TestStageConfig:
    """Tests for StageConfig class."""

    def test_stage_config_minimal(self):
        """Test creating minimal stage config."""
        stage = StageConfig(name="opt", simple_keywords=["OPT", "B3LYP"])
        assert stage.name == "opt"
        assert stage.simple_keywords == ["OPT", "B3LYP"]
        assert stage.input_blocks == []
        assert stage.mult is None
        assert stage.charge is None
        assert stage.inherit == []

    def test_stage_config_full(self):
        """Test creating full stage config."""
        stage = StageConfig(
            name="casscf",
            simple_keywords=["CASSCF"],
            input_blocks=["%casscf nroot 2 end"],
            mult=3,
            charge=-1,
            inherit=["*.gbw", "*.xyz"],
        )
        assert stage.name == "casscf"
        assert stage.mult == 3
        assert stage.charge == -1
        assert len(stage.input_blocks) == 1
        assert len(stage.inherit) == 2

    def test_stage_config_strips_name(self):
        """Test that stage name is stripped of whitespace."""
        stage = StageConfig(name="  opt  ", simple_keywords=["OPT"])
        assert stage.name == "opt"

    def test_stage_config_requires_name(self):
        """Test that stage name is required."""
        with pytest.raises(ValidationError):
            StageConfig(simple_keywords=["OPT"])  # type: ignore # missing the name is what we're testing

    def test_stage_config_requires_keywords(self):
        """Test that simple_keywords are required."""
        with pytest.raises(ValidationError):
            StageConfig(name="opt")  # type: ignore # missing the keywords is what we're testing

    def test_stage_config_keywords_not_empty(self):
        """Test that simple_keywords cannot be empty."""
        with pytest.raises(ValidationError):
            StageConfig(name="opt", simple_keywords=[])


class TestWorkflowConfig:
    """Tests for WorkflowConfig class."""

    def test_workflow_config_minimal(self):
        """Test creating minimal workflow config."""
        config = WorkflowConfig(
            stages=[StageConfig(name="opt", simple_keywords=["OPT"])]
        )
        assert len(config.stages) == 1
        assert config.output_dir == Path("output")
        assert config.molecules_dir == Path("molecules")
        assert config.cpus == 1
        assert config.workers == 1

    def test_workflow_config_with_keywords(self):
        """Test workflow config with variable substitution keywords."""
        config = WorkflowConfig(
            keyword_defaults={"basis": "def2-SVP", "method": "B3LYP"},
            stages=[StageConfig(name="opt", simple_keywords=["OPT"])],
        )
        assert config.keyword_defaults["basis"] == "def2-SVP"
        assert config.keyword_defaults["method"] == "B3LYP"

    def test_workflow_config_duplicate_stage_names(self):
        """Test that duplicate stage names are rejected."""
        with pytest.raises(ValidationError, match="Duplicate stage names"):
            WorkflowConfig(
                stages=[
                    StageConfig(name="opt", simple_keywords=["OPT"]),
                    StageConfig(name="opt", simple_keywords=["FREQ"]),
                ]
            )

    def test_workflow_config_slurm_settings(self):
        """Test SLURM settings in workflow config."""
        config = WorkflowConfig(
            stages=[StageConfig(name="opt", simple_keywords=["OPT"])],
            slurm=SlurmSettings(
                nodelist=["node001", "node002"],
                exclude_nodes=["node003"],
                timelimit="24:00:00",
                partition="gpu",
                account="myaccount",
                email="user@example.com",
            ),
        )
        assert config.slurm.nodelist == ["node001", "node002"]
        assert config.slurm.exclude_nodes == ["node003"]
        assert config.slurm.timelimit == "24:00:00"
        assert config.slurm.partition == "gpu"
        assert config.slurm.account == "myaccount"
        assert config.slurm.email == "user@example.com"


class TestLegacyConfigNormalization:
    """Tests for legacy config format normalization."""

    def test_legacy_main_section(self):
        """Test normalizing legacy 'main' section."""
        raw_config = {
            "main": {
                "output_dir": "results",
                "cpus": 8,
                "workers": 2,
            },
            "stages": [{"name": "opt", "simple_keywords": ["OPT"]}],
        }
        config = WorkflowConfig(**raw_config)
        assert config.output_dir == Path("results")
        assert config.cpus == 8
        assert config.workers == 2

    def test_legacy_molecules_section(self):
        """Test normalizing legacy 'molecules' section."""
        raw_config = {
            "molecules": {
                "directory": "xyz_files",
                "include": ["mol1", "mol2"],
                "exclude": ["mol3"],
            },
            "stages": [{"name": "opt", "simple_keywords": ["OPT"]}],
        }
        config = WorkflowConfig(**raw_config)
        assert config.molecules_dir == Path("xyz_files")
        assert config.include == ["mol1", "mol2"]
        assert config.exclude == ["mol3"]

    def test_legacy_step_to_stages(self):
        """Test normalizing legacy 'step' to 'stages'."""
        raw_config = {
            "step": [{"name": "opt", "simple_keywords": ["OPT"]}],
        }
        config = WorkflowConfig(**raw_config)  # type: ignore # no way to check the expansion satifies the types
        assert len(config.stages) == 1
        assert config.stages[0].name == "opt"

    def test_legacy_keywords_to_simple_keywords(self):
        """Test normalizing legacy 'keywords' to 'simple_keywords' in stages."""
        raw_config = {
            "stages": [{"name": "opt", "keywords": ["OPT", "B3LYP"]}],
        }
        config = WorkflowConfig(**raw_config)  # type: ignore # no way to check the expansion satifies the types
        assert config.stages[0].simple_keywords == ["OPT", "B3LYP"]

    def test_legacy_keywords_not_overwrite_simple_keywords(self):
        """Test that simple_keywords takes precedence over keywords."""
        raw_config = {
            "stages": [
                {
                    "name": "opt",
                    "keywords": ["OPT"],
                    "simple_keywords": ["FREQ"],
                }
            ],
        }
        config = WorkflowConfig(**raw_config)  # type: ignore # no way to check the expansion satifies the types
        # simple_keywords should be preserved
        assert config.stages[0].simple_keywords == ["FREQ"]


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_basic(self, tmp_path):
        """Test loading a basic config file."""
        config_file = tmp_path / "config.toml"
        config_data = {
            "output_dir": "output",
            "molecules_dir": "molecules",
            "cpus": 4,
            "stages": [{"name": "opt", "simple_keywords": ["OPT"]}],
        }
        config_file.write_text(toml.dumps(config_data))

        config = load_config(config_file)
        assert config.cpus == 4
        assert len(config.stages) == 1

    def test_load_config_with_relative_paths(self, tmp_path):
        """Test that relative paths are resolved relative to config file."""
        subdir = tmp_path / "configs"
        subdir.mkdir()
        config_file = subdir / "config.toml"

        config_data = {
            "output_dir": "../output",
            "molecules_dir": "../molecules",
            "stages": [{"name": "opt", "simple_keywords": ["OPT"]}],
        }
        config_file.write_text(toml.dumps(config_data))

        config = load_config(config_file)
        # Paths should be resolved relative to config file location
        assert config.output_dir == (tmp_path / "output").resolve()
        assert config.molecules_dir == (tmp_path / "molecules").resolve()

    def test_load_config_with_absolute_paths(self, tmp_path):
        """Test that absolute paths are preserved."""
        config_file = tmp_path / "config.toml"

        config_data = {
            "output_dir": "/absolute/output",
            "molecules_dir": "/absolute/molecules",
            "stages": [{"name": "opt", "simple_keywords": ["OPT"]}],
        }
        config_file.write_text(toml.dumps(config_data))

        config = load_config(config_file)
        assert config.output_dir == Path("/absolute/output")
        assert config.molecules_dir == Path("/absolute/molecules")

    def test_load_config_invalid_toml(self, tmp_path):
        """Test loading invalid TOML raises error."""
        config_file = tmp_path / "config.toml"
        config_file.write_text("this is not valid toml [[[]")

        with pytest.raises(Exception):  # toml.TomlDecodeError
            load_config(config_file)

    def test_load_config_invalid_schema(self, tmp_path):
        """Test loading config with invalid schema raises error."""
        config_file = tmp_path / "config.toml"
        config_data = {
            "output_dir": "output",
            # Missing required 'stages' field
        }
        config_file.write_text(toml.dumps(config_data))

        with pytest.raises(ValidationError):
            load_config(config_file)


class TestSubstituteVariables:
    """Tests for substitute_variables function (already covered in test_variable_substitution.py)."""

    def test_substitute_basic(self):
        """Test basic variable substitution."""
        template = "Hello {name}"
        result = substitute_variables(template, {"name": "World"}, {})
        assert result == "Hello World"

    def test_substitute_from_global(self):
        """Test substitution from global keywords."""
        template = "Method: {method}"
        result = substitute_variables(template, {}, {"method": "B3LYP"})
        assert result == "Method: B3LYP"

    def test_substitute_molecule_overrides_global(self):
        """Test that molecule metadata overrides global keywords."""
        template = "{value}"
        result = substitute_variables(
            template, {"value": "molecule"}, {"value": "global"}
        )
        assert result == "molecule"

    def test_substitute_variable_not_found(self):
        """Test that missing variable raises KeyError."""
        template = "Missing {var}"
        with pytest.raises(KeyError, match="not found"):
            substitute_variables(template, {}, {})

    def test_substitute_no_variables(self):
        """Test that strings without variables are unchanged."""
        template = "No variables here"
        result = substitute_variables(template, {}, {})
        assert result == template

    def test_substitute_multiple_same_variable(self):
        """Test substituting the same variable multiple times."""
        template = "{x} + {x} = {x}"
        result = substitute_variables(template, {"x": 5}, {})
        assert result == "5 + 5 = 5"
