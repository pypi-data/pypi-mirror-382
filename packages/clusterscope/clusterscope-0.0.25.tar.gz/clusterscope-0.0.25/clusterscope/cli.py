#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
import json
from typing import Any, Dict, Optional

import click
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup

from clusterscope.cluster_info import AWSClusterInfo, UnifiedInfo
from clusterscope.validate import job_gen_task_slurm_validator


def format_dict(data: Dict[str, Any]) -> str:
    """Format a dictionary for display."""
    return json.dumps(data, indent=2)


@click.group()
def cli():
    """Command-line tool to query Slurm cluster information."""
    pass


@cli.command()
def version():
    """Show the version of clusterscope."""
    try:
        from importlib.metadata import version as get_version

        pkg_version = get_version("clusterscope")
    except Exception:
        # Fallback to the version in __init__.py if setuptools-scm isn't available
        import clusterscope

        pkg_version = clusterscope.__version__
    click.echo(f"clusterscope version {pkg_version}")


@cli.command()
@click.option(
    "--partition",
    type=str,
    default=None,
    help="Slurm partition name to filter queries (optional)",
)
def info(partition: str):
    """Show basic cluster information."""
    unified_info = UnifiedInfo(partition=partition)
    cluster_name = unified_info.get_cluster_name()
    slurm_version = unified_info.get_slurm_version()
    click.echo(f"Cluster Name: {cluster_name}")
    click.echo(f"Slurm Version: {slurm_version}")


@cli.command()
@click.option(
    "--partition",
    type=str,
    default=None,
    help="Slurm partition name to filter queries (optional)",
)
def cpus(partition: str):
    """Show CPU counts per node."""
    unified_info = UnifiedInfo(partition=partition)
    cpus_per_node = unified_info.get_cpus_per_node()
    click.echo("CPU counts per node:")
    click.echo(cpus_per_node)


@cli.command()
@click.option(
    "--partition",
    type=str,
    default=None,
    help="Slurm partition name to filter queries (optional)",
)
def mem(partition: str):
    """Show memory information per node."""
    unified_info = UnifiedInfo(partition=partition)
    mem_per_node = unified_info.get_mem_per_node_MB()
    click.echo("Mem per node MB:")
    click.echo(mem_per_node)


@cli.command()
@click.option(
    "--partition",
    type=str,
    default=None,
    help="Slurm partition name to filter queries (optional)",
)
@click.option("--generations", is_flag=True, help="Show only GPU generations")
@click.option("--counts", is_flag=True, help="Show only GPU counts by type")
@click.option("--vendor", is_flag=True, help="Show GPU vendor information")
def gpus(partition: str, generations: bool, counts: bool, vendor: bool):
    """Show GPU information."""
    unified_info = UnifiedInfo(partition=partition)

    if vendor:
        vendor_info = unified_info.get_gpu_vendor()
        click.echo(f"Primary GPU vendor: {vendor_info}")
    elif counts:
        gpu_counts = unified_info.get_gpu_generation_and_count()
        if gpu_counts:
            click.echo("GPU counts by type:")
            for gpu_type, count in sorted(gpu_counts.items()):
                click.echo(f"  {gpu_type}: {count}")
        else:
            click.echo("No GPUs found")
    elif generations:
        gpu_counts = unified_info.get_gpu_generation_and_count()
        if gpu_counts:
            click.echo("GPU generations available:")
            for gen in sorted(gpu_counts.keys()):
                click.echo(f"- {gen}")
        else:
            click.echo("No GPUs found")
    else:
        # Default: show both vendor and detailed info
        vendor_info = unified_info.get_gpu_vendor()
        gpu_counts = unified_info.get_gpu_generation_and_count()

        click.echo(f"GPU vendor: {vendor_info}")
        if gpu_counts:
            click.echo("GPU information:")
            for gpu_type, count in sorted(gpu_counts.items()):
                click.echo(f"  {gpu_type}: {count}")
        else:
            click.echo("No GPUs found")


@cli.command(name="check-gpu")
@click.argument("gpu_type")
@click.option(
    "--partition",
    type=str,
    default=None,
    help="Slurm partition name to filter queries (optional)",
)
def check_gpu(gpu_type: str, partition: str):
    """Check if a specific GPU type exists.

    GPU_TYPE: GPU type to check for (e.g., A100, MI300X)
    """
    unified_info = UnifiedInfo(partition=partition)
    has_gpu = unified_info.has_gpu_type(gpu_type)
    if has_gpu:
        click.echo(f"GPU type {gpu_type} is available in the cluster.")
    else:
        click.echo(f"GPU type {gpu_type} is NOT available in the cluster.")


@cli.command()
def aws():
    """Check if running on AWS and show NCCL settings."""
    aws_cluster_info = AWSClusterInfo()
    is_aws = aws_cluster_info.is_aws_cluster()
    if is_aws:
        click.echo("This is an AWS cluster.")
        nccl_settings = aws_cluster_info.get_aws_nccl_settings()
        click.echo("\nRecommended NCCL settings:")
        click.echo(format_dict(nccl_settings))
    else:
        click.echo("This is NOT an AWS cluster.")


@cli.group(name="job-gen")
def job_gen():
    """Generate job requirements for different job types."""
    pass


@job_gen.group(name="task")
def task():
    """Generate job requirements for a task of a job."""
    pass


@task.command()  # type: ignore[arg-type]
@click.option("--partition", type=str, required=True, help="Partition to query")
@click.option(
    "--tasks-per-node",
    type=int,
    default=1,
    help="Number of tasks per node to request",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "sbatch", "srun", "submitit", "salloc"]),
    default="json",
    help="Format to output the job requirements in",
)
@optgroup.group(
    "GPU or CPU Job Request",
    cls=RequiredMutuallyExclusiveOptionGroup,
    help="Only one of --gpus-per-task or --cpus-per-task can be specified. For GPU requests, use --gpus-per-task and cpus-per-task will be generated automatically. For CPU requests, use --cpus-per-task.",
)
@optgroup.option(
    "--gpus-per-task",
    default=None,
    type=click.IntRange(min=1),
    help="Number of GPUs per task to request",
)
@optgroup.option(  # type: ignore[arg-type]
    "--cpus-per-task",
    default=None,
    type=click.IntRange(min=1),
    help="Number of CPUs per task to request",
)
def slurm(
    tasks_per_node: int,
    output_format: str,
    partition: str,
    gpus_per_task: Optional[int],
    cpus_per_task: Optional[int],
):
    """Generate job requirements for a task of a Slurm job based on GPU or CPU per task requirements."""
    job_gen_task_slurm_validator(
        partition=partition,
        gpus_per_task=gpus_per_task,
        cpus_per_task=cpus_per_task,
        tasks_per_node=tasks_per_node,
        exit_on_error=True,
    )

    unified_info = UnifiedInfo(partition=partition)
    job_requirements = unified_info.get_task_resource_requirements(
        partition=partition,
        cpus_per_task=cpus_per_task,
        gpus_per_task=gpus_per_task,
        tasks_per_node=tasks_per_node,
    )

    # Route to the correct format method based on CLI option
    format_methods = {
        "json": job_requirements.to_json,
        "sbatch": job_requirements.to_sbatch,
        "srun": job_requirements.to_srun,
        "submitit": job_requirements.to_submitit,
        "salloc": job_requirements.to_salloc,
    }
    click.echo(format_methods[output_format]())


def main():
    """Main entry point for the Slurm information CLI."""
    cli()


if __name__ == "__main__":
    main()
