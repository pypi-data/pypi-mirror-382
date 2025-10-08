"""Command-line interface for Orcastrator."""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click
from jinja2 import Template
from loguru import logger as log

from .config import load_config
from .runner import WorkflowRunner

__version__ = "2.1.0"


def setup_logging(log_file: Path, debug: bool = False) -> None:
    """Configure loguru logging.

    Args:
        log_file: Path to log file
        debug: Enable debug logging
    """
    # Remove default handler
    log.remove()

    # Console handler (INFO or DEBUG)
    log.add(
        sys.stderr,
        format="<level>{level: <8}</level> | <level>{message}</level>",
        level="DEBUG" if debug else "INFO",
        colorize=True,
    )

    # File handler (always DEBUG)
    log.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="DEBUG",
        rotation="10 MB",
    )


@click.group()
@click.version_option(version=__version__, prog_name="orcastrator")
def cli():
    """Orcastrator - ORCA workflow orchestration tool."""
    pass


@cli.command()
@click.argument("config_file", type=click.Path(exists=True, path_type=Path))
@click.option("--debug", is_flag=True, help="Enable debug logging")
def run(config_file: Path, debug: bool):
    """Run ORCA workflow from config file."""
    # Setup logging
    log_file = config_file.with_suffix(".log")
    setup_logging(log_file, debug)

    log.info(f"Orcastrator v{__version__}")
    log.info(f"Config: {config_file}")

    # Load config
    try:
        config = load_config(config_file)
    except Exception as e:
        log.error(f"Failed to load config: {e}")
        sys.exit(1)

    # Override debug setting if CLI flag is set
    if debug:
        config.debug = True

    # Run workflow
    try:
        runner = WorkflowRunner(config)
        results = runner.run()

        # Check for failures
        failed = sum(1 for r in results if not r["success"])
        if failed > 0:
            log.warning(f"{failed} molecules failed")
            sys.exit(1)

    except Exception as e:
        log.exception(f"Workflow failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument("config_file", type=click.Path(exists=True, path_type=Path))
@click.option("--no-submit", is_flag=True, help="Generate script but don't submit")
@click.option("--debug", is_flag=True, help="Enable debug logging")
def slurm(config_file: Path, no_submit: bool, debug: bool):
    """Generate and submit SLURM batch script."""
    # Load config
    try:
        config = load_config(config_file)
    except Exception as e:
        log.error(f"Failed to load config: {e}")
        sys.exit(1)

    # Generate SLURM script from template
    template_str = """#!/bin/bash
#SBATCH --job-name={{ job_name }}
#SBATCH --ntasks={{ ntasks }}
#SBATCH --mem-per-cpu={{ mem_per_cpu }}G
{%- if nodelist %}
#SBATCH --nodelist={{ nodelist }}
{%- endif %}
{%- if exclude %}
#SBATCH --exclude={{ exclude }}
{%- endif %}
{%- if timelimit %}
#SBATCH --time={{ timelimit }}
{%- endif %}
#SBATCH --output={{ job_name }}.slurm.out
#SBATCH --error={{ job_name }}.slurm.err

# Run orcastrator
uvx orcastrator run {{ '--debug' if debug else '' }} {{ config_file }}
"""

    template = Template(template_str)
    script_content = template.render(
        job_name=config_file.stem,
        ntasks=config.cpus,
        mem_per_cpu=config.mem_per_cpu_gb,
        nodelist=",".join(config.nodelist) if config.nodelist else None,
        exclude=",".join(config.exclude_nodes) if config.exclude_nodes else None,
        timelimit=config.timelimit,
        debug=debug,
        config_file=config_file.resolve(),
    )

    # Write script
    slurm_file = config_file.with_suffix(".slurm")
    slurm_file.write_text(script_content)
    log.info(f"Generated SLURM script: {slurm_file}")

    # Submit if requested
    if not no_submit:
        if not shutil.which("sbatch"):
            log.error("sbatch not found in PATH")
            sys.exit(1)

        result = subprocess.run(
            ["sbatch", str(slurm_file)],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            job_id = result.stdout.strip().split()[-1]
            log.info(f"Submitted job: {job_id}")
        else:
            log.error(f"sbatch failed: {result.stderr}")
            sys.exit(1)


@cli.command()
@click.argument("output_file", type=click.Path(path_type=Path), required=False)
@click.option("--slim", "-s", is_flag=True, help="Generate minimal template")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing file")
def init(output_file: Optional[Path] = None, slim: bool = False, force: bool = False):
    """Create a template configuration file."""
    if output_file is None:
        output_file = Path("orcastrator.toml")

    if output_file.exists() and not force:
        log.error(f"File {output_file} already exists (use --force to overwrite)")
        sys.exit(1)

    # Create molecules directory
    mol_dir = output_file.parent / "molecules"
    mol_dir.mkdir(exist_ok=True)

    # Template content
    if slim:
        template = """# Orcastrator Configuration
output_dir = "output"
molecules_dir = "molecules"

cpus = 4
mem_per_cpu_gb = 2
workers = 1

[[stages]]
name = "opt"
keywords = ["D4", "TPSS", "def2-SVP", "OPT"]

[[stages]]
name = "freq"
keywords = ["D4", "TPSS", "def2-SVP", "FREQ"]

[[stages]]
name = "sp"
keywords = ["D4", "TPSSh", "def2-TZVP"]
"""
    else:
        template = f"""# Orcastrator Configuration (v{__version__})

# Core settings (paths relative to this file)
output_dir = "output"
molecules_dir = "molecules"

# Resource settings
cpus = 4
mem_per_cpu_gb = 2
workers = 1
scratch_dir = "/scratch"

# Workflow settings
overwrite = false
debug = false

# Molecule filtering (optional)
# include = ["molecule1", "molecule2"]
# exclude = ["molecule3"]
# rerun_failed = false

# SLURM settings (optional)
# nodelist = ["node001", "node002"]
# exclude_nodes = ["node003"]
# timelimit = "24:00:00"

# Calculation stages (executed in order)
[[stages]]
name = "opt"
keywords = ["D4", "TPSS", "def2-SVP", "OPT"]
# Optional: additional ORCA blocks
# blocks = ["%scf maxiter 150 end"]

[[stages]]
name = "freq"
keywords = ["D4", "TPSS", "def2-SVP", "FREQ"]
# Optional: override multiplicity
# mult = 3
# Optional: copy files from previous stage (e.g., wavefunctions)
# keep = ["*.gbw"]

[[stages]]
name = "sp"
keywords = ["D4", "TPSSh", "def2-TZVP"]
# Optional: copy files from previous stage
# keep = ["*.gbw"]
"""

    output_file.write_text(template)
    log.info(f"Created config template: {output_file}")


if __name__ == "__main__":
    cli()
