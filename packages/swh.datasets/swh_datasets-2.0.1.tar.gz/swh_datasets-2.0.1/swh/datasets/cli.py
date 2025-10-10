# Copyright (C) 2019-2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

# WARNING: do not import unnecessary things here to keep cli startup time under
# control
import click

from swh.core.cli import CONTEXT_SETTINGS, AliasedGroup
from swh.core.cli import swh as swh_cli_group

if TYPE_CHECKING:
    from swh.graph.webgraph import CompressionStep  # noqa

logger = logging.getLogger(__name__)


class PathlibPath(click.Path):
    """A Click path argument that returns a pathlib Path, not a string"""

    def convert(self, value, param, ctx):
        return Path(super().convert(value, param, ctx))


DEFAULT_CONFIG: Dict[str, Tuple[str, Any]] = {
    "graph": ("dict", {"cls": "local", "grpc_server": {}})
}


@swh_cli_group.group(
    name="datasets", context_settings=CONTEXT_SETTINGS, cls=AliasedGroup
)
@click.option(
    "--config-file",
    "-C",
    default=None,
    type=click.Path(
        exists=True,
        dir_okay=False,
    ),
    help="YAML configuration file",
)
@click.pass_context
def datasets_cli_group(ctx, config_file):
    """Software Heritage datasets tools."""
    from swh.core import config

    ctx.ensure_object(dict)
    conf = config.read(config_file, DEFAULT_CONFIG)
    if "graph" not in conf:
        raise ValueError(
            'no "graph" stanza found in configuration file %s' % config_file
        )
    ctx.obj["config"] = conf


@datasets_cli_group.command(name="list")
@click.option(
    "--s3-bucket",
    default="softwareheritage",
    help="S3 bucket name containing Software Heritage datasets. "
    "Defaults to 'sotwareheritage'",
)
@click.pass_context
def list_datasets(
    ctx,
    s3_bucket: str,
):
    """List datasets available for download.

    Print the names of the Software Heritage datasets (exports or compressed
    graphs) that can be downloaded with the following commands:

    $ swh datasets download-graph --name <dataset_name> <target_directory>
    $ swh datasets download-export --name <dataset_name> <target_directory>

    The list may contain datasets that are not suitable for production, or not yet
    fully available. See
    https://docs.softwareheritage.org/devel/swh-export/graph/dataset.html
    for the official list of datasets, along with release notes.
    """
    import boto3
    from botocore import UNSIGNED
    from botocore.client import Config

    click.echo(
        "The following list is automatically generated from Software Heritage's "
        "S3 bucket.",
        err=True,
    )
    click.echo(
        "It may contain datasets that are not suitable for production, or not yet "
        "fully available.",
        err=True,
    )
    click.echo(
        "See https://docs.softwareheritage.org/devel/swh-export/graph/dataset.html "
        "for the official list of datasets, along with release notes.",
        err=True,
    )

    s3_client = boto3.client("s3", config=Config(signature_version=UNSIGNED))
    paginator = s3_client.get_paginator("list_objects_v2")

    for dataset_prefix in [
        prefix["Prefix"]
        for page in paginator.paginate(Bucket=s3_bucket, Prefix="graph/", Delimiter="/")
        for prefix in page["CommonPrefixes"]
    ]:
        if "Contents" in s3_client.list_objects_v2(
            Bucket=s3_bucket,
            Prefix=dataset_prefix + "compressed/",
            Delimiter="/",
        ):
            click.echo(dataset_prefix.split("/")[1])


def _download_options(function):
    function = click.option(
        "--s3-prefix",
        default="s3://softwareheritage/graph/",
        help="Base directory of Software Heritage's graphs on S3",
    )(function)
    function = click.option(
        "--name",
        required=True,
        help="Name of the dataset to download. This is an ISO8601 date, optionally with a "
        "suffix. See https://docs.softwareheritage.org/devel/swh-export/graph/dataset.html",
    )(function)
    function = click.option(
        "--parallelism",
        "-j",
        default=5,
        help="Number of threads used to download/decompress files.",
    )(function)
    function = click.argument(
        "target-dir",
        type=click.Path(
            file_okay=False,
            writable=True,
            path_type=Path,
        ),
    )(function)
    return function


@datasets_cli_group.command(name="download-graph")
@_download_options
@click.pass_context
def download_graph(
    ctx,
    s3_prefix: str,
    name: Optional[str],
    parallelism: int,
    target_dir: Path,
):
    """Downloads a compressed SWH graph to the given target directory"""
    from swh.graph.download import GraphDownloader

    s3_url = f"{s3_prefix.rstrip('/')}/{name}/compressed/"

    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        GraphDownloader(
            local_graph_path=target_dir,
            s3_graph_path=s3_url,
            parallelism=parallelism,
        ).download_graph(
            progress_percent_cb=lambda _: None,
            progress_status_cb=lambda _: None,
        )
    except Exception as e:
        raise click.ClickException(str(e))


@datasets_cli_group.command(name="download-export")
@_download_options
@click.pass_context
def download_export(
    ctx,
    s3_prefix: str,
    name: Optional[str],
    parallelism: int,
    target_dir: Path,
):
    """Downloads a SWH ORC dataset to the given target directory"""
    from swh.datasets.download import DatasetDownloader

    s3_url = f"{s3_prefix.rstrip('/')}/{name}/"

    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        DatasetDownloader(
            local_path=target_dir,
            s3_url=s3_url,
            prefix="orc",
            parallelism=parallelism,
        ).download()
    except Exception as e:
        raise click.ClickException(str(e))


def get_all_subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses


@datasets_cli_group.command()
@click.option(
    "--base-directory",
    required=True,
    type=PathlibPath(),
    help="""The base directory where all datasets and compressed graphs are.
    Its subdirectories should be named after a date (and optional flavor).
    For example: ``/poolswh/softwareheritage/``.""",
)
@click.option(
    "--base-sensitive-directory",
    required=False,
    type=PathlibPath(),
    help="""The base directory for any data that should not be publicly available
    (eg. because it contains people's names).
    For example: ``/poolswh/softwareheritage/``.""",
)
@click.option(
    "--athena-prefix",
    required=False,
    type=str,
    help="""A prefix for the Athena Database that will be created and/or used.
    For example: ``swh``.""",
)
@click.option(
    "--s3-prefix",
    required=False,
    type=str,
    help="""The base S3 "directory" where all datasets and compressed graphs are.
    Its subdirectories should be named after a date (and optional flavor).
    For example: ``s3://softwareheritage/graph/``.""",
)
@click.option(
    "--max-ram",
    help="""Maximum RAM that some scripts will try not to exceed""",
)
@click.option(
    "--batch-size",
    type=int,
    help="""Default value for compression tasks handling objects in batch""",
)
@click.option(
    "--grpc-api", help="""Default value for the <hostname>:<port> of the gRPC server"""
)
@click.option(
    "--s3-athena-output-location",
    required=False,
    type=str,
    help="""The base S3 "directory" where all datasets and compressed graphs are.
    Its subdirectories should be named after a date (and optional flavor).
    For example: ``s3://softwareheritage/graph/``.""",
)
@click.option(
    "--graph-base-directory",
    required=False,
    type=PathlibPath(),
    help="""Overrides the path of the graph to use. Defaults to the value of
    ``{base_directory}/{dataset_name}/{compressed}/``.
    For example: ``/dev/shm/swh-graph/default/``.""",
)
@click.option(
    "--export-base-directory",
    required=False,
    type=PathlibPath(),
    help="""Overrides the path of the export to use. Defaults to the value of
    ``--base-directory``.""",
)
@click.option(
    "--dataset-name",
    required=True,
    type=str,
    help="""Should be a date and optionally a flavor, which will be used
    as directory name. For example: ``2022-04-25`` or ``2022-11-12_staging``.""",
)
@click.option(
    "--parent-dataset-name",
    required=False,
    type=str,
    help="""When generating a subdataset (eg. ``2024-08-23-python3k``), this is the name
    of a full export (eg. ``2024-08-23``) the subdataset should be built from.""",
)
@click.option(
    "--export-name",
    required=False,
    type=str,
    help="""Should be a date and optionally a flavor, which will be used
    as directory name for the export (not the compressed graph).
    For example: ``2022-04-25`` or ``2022-11-12_staging``.
    Defaults to the value of --dataset-name""",
)
@click.option(
    "--parent-export-name",
    required=False,
    type=str,
    help="""When generating a subdataset (eg. ``2024-08-23-python3k``), this is the name
    of a full export (eg. ``2024-08-23``) the subdataset should be built from.
    Defaults to the value of --parent-dataset-name""",
)
@click.option(
    "--previous-dataset-name",
    required=False,
    type=str,
    help="""When regenerating a derived dataset, this can be set to the name of
    a previous dataset the derived dataset was generated for.
    Some results from the previous generated dataset will be reused to speed-up
    regeneration.""",
)
@click.option(
    "--base-rust-executable-dir",
    required=False,
    type=str,
    help="""Where to search for Rust executables that are not in $PATH""",
)
@click.option(
    "--luigi-config",
    type=PathlibPath(),
    help="""Extra options to add to ``luigi.cfg``, following the same format.
    This overrides any option that would be other set automatically.""",
)
@click.option(
    "--retry-luigi-delay",
    type=int,
    default=10,
    help="""Time to wait before re-running Luigi, if some tasks are pending
    but stuck.""",
)
@click.argument("luigi_param", nargs=-1)
@click.pass_context
def luigi(
    ctx,
    base_directory: Path,
    graph_base_directory: Optional[Path],
    export_base_directory: Optional[Path],
    base_sensitive_directory: Optional[Path],
    s3_prefix: Optional[str],
    athena_prefix: Optional[str],
    max_ram: Optional[str],
    batch_size: Optional[int],
    grpc_api: Optional[str],
    s3_athena_output_location: Optional[str],
    dataset_name: str,
    parent_dataset_name: Optional[str],
    parent_export_name: Optional[str],
    export_name: Optional[str],
    previous_dataset_name: Optional[str],
    retry_luigi_delay: int,
    base_rust_executable_dir: str,
    luigi_config: Optional[Path],
    luigi_param: List[str],
):
    r"""
    Calls Luigi with the given task and params, and automatically
    configures paths based on --base-directory and --dataset-name.

    The list of Luigi params should be prefixed with ``--`` so they are not interpreted
    by the ``swh`` CLI. For example::

        swh graph luigi \
                --base-directory ~/tmp/ \
                --dataset-name 2022-12-05_test ListOriginContributors \
                -- \
                RunAll \
                --local-scheduler

    to pass ``RunAll --local-scheduler`` as Luigi params

    Or, to compute a derived dataset::

        swh graph luigi \
                --graph-base-directory /dev/shm/swh-graph/default/ \
                --base-directory /poolswh/softwareheritage/vlorentz/ \
                --athena-prefix swh \
                --dataset-name 2022-04-25 \
                --s3-athena-output-location s3://some-bucket/tmp/athena \
                -- \
                --log-level INFO \
                FindEarliestRevisions \
                --scheduler-url http://localhost:50092/ \
                --blob-filter citation
    """
    import configparser
    import os
    import socket
    import subprocess
    import tempfile
    import time

    import luigi
    import psutil

    # Popular the list of subclasses of luigi.Task
    import swh.datasets.luigi  # noqa
    import swh.export.luigi  # noqa
    import swh.graph.luigi  # noqa
    import swh.provenance.luigi  # noqa

    config = configparser.ConfigParser()

    # By default, Luigi always returns code 0.
    # See https://luigi.readthedocs.io/en/stable/configuration.html#retcode
    config["retcode"] = {
        "already_running": "128",
        "missing_data": "129",
        "not_run": "130",
        "task_failed": "131",
        "scheduling_error": "132",
        "unhandled_exception": "133",
    }

    if max_ram:
        if max_ram.endswith("G"):
            max_ram_mb = int(max_ram[:-1]) * 1024
        elif max_ram.endswith("M"):
            max_ram_mb = int(max_ram[:-1])
        else:
            raise click.ClickException(
                "--max-ram must be an integer followed by M or G"
            )
    else:
        max_ram_mb = psutil.virtual_memory().total // (1024 * 1024)

    # Only used by the local scheduler; otherwise it needs to be configured
    # in luigid.cfg
    hostname = socket.getfqdn()
    config["resources"] = {
        f"{hostname}_ram_mb": str(max_ram_mb),
    }

    export_name = export_name or dataset_name
    parent_export_name = parent_export_name or parent_dataset_name

    export_path = (export_base_directory or base_directory) / export_name
    dataset_path = base_directory / dataset_name

    default_values = dict(
        local_export_path=export_path,
        local_graph_path=dataset_path / "compressed",
        derived_datasets_path=dataset_path,
        topological_order_dir=dataset_path / "topology/",
        aggregate_datasets_path=dataset_path / "aggregate/",
        popular_content_names_path=dataset_path / "popular-content-names/",
        provenance_dir=dataset_path / "provenance",
        origin_contributors_path=dataset_path / "contribution_graph.csv.zst",
        origin_urls_path=dataset_path / "origin_urls.csv.zst",
        export_name=export_name,
        dataset_name=dataset_name,
        previous_dataset_name=previous_dataset_name,
    )

    if graph_base_directory:
        default_values["local_graph_path"] = graph_base_directory

    if s3_prefix:
        default_values["s3_export_path"] = f"{s3_prefix.rstrip('/')}/{export_name}"
        default_values["s3_graph_path"] = (
            f"{s3_prefix.rstrip('/')}/{dataset_name}/compressed"
        )
        if parent_dataset_name:
            default_values["s3_parent_export_path"] = (
                f"{s3_prefix.rstrip('/')}/{parent_export_name}"
            )
            default_values["s3_parent_graph_path"] = (
                f"{s3_prefix.rstrip('/')}/{parent_dataset_name}/compressed"
            )

    if s3_athena_output_location:
        default_values["s3_athena_output_location"] = s3_athena_output_location

    if max_ram:
        default_values["max_ram_mb"] = max_ram_mb

    if batch_size:
        default_values["batch_size"] = batch_size

    if grpc_api:
        default_values["grpc_api"] = grpc_api

    if base_sensitive_directory:
        sensitive_path = base_sensitive_directory / dataset_name
        sensitive_export_path = base_sensitive_directory / export_name
        sensitive_graph_path = base_sensitive_directory / export_name / "compressed"
        default_values["local_sensitive_export_path"] = sensitive_export_path
        default_values["local_sensitive_graph_path"] = sensitive_graph_path
        default_values["deanonymized_origin_contributors_path"] = (
            sensitive_path / "contributors_deanonymized.csv.zst"
        )
        default_values["deanonymization_table_path"] = (
            sensitive_path / "persons_sha256_to_name.csv.zst"
        )
    else:
        default_values["local_sensitive_export_path"] = None
        default_values["local_sensitive_graph_path"] = None

    if previous_dataset_name:
        default_values["previous_derived_datasets_path"] = (
            base_directory / previous_dataset_name
        )

    if athena_prefix:
        default_values["athena_db_name"] = (
            f"{athena_prefix}_{dataset_name.replace('-', '')}"
        )
        if parent_dataset_name:
            default_values["athena_parent_db_name"] = (
                f"{athena_prefix}_{parent_dataset_name.replace('-', '')}"
            )

    for task_cls in get_all_subclasses(luigi.Task):
        task_name = task_cls.__name__
        # If the task has an argument with one of the known name, add the default value
        # to its config.
        task_config = {
            arg_name: str(arg_value)
            for arg_name, arg_value in default_values.items()
            if hasattr(task_cls, arg_name)
        }
        if task_config:
            config[task_name] = task_config

    # If any config is provided, add it.
    # This may override default arguments configured above.
    if os.environ.get("LUIGI_CONFIG_PATH"):
        config.read(os.environ["LUIGI_CONFIG_PATH"])
    if luigi_config is not None:
        config.read(luigi_config)

    with tempfile.NamedTemporaryFile(mode="w+t", prefix="luigi_", suffix=".cfg") as fd:
        config.write(fd)
        fd.flush()

        while True:
            start_time = time.time()
            proc = subprocess.run(
                [
                    "luigi",
                    "--module",
                    "swh.export.luigi",
                    "--module",
                    "swh.graph.luigi",
                    "--module",
                    "swh.datasets.luigi",
                    *luigi_param,
                ],
                env={
                    **os.environ,
                    "LUIGI_CONFIG_PATH": fd.name,
                },
            )

            # If all tasks are stuck, run another loop to wait for them to be unstuck.
            # The normal way to do this would be to set config["worker"]["keep_alive"]
            # to True, but we do it this way to force Luigi to recompute resources
            # because most tasks in compressed_graph.py can only know their resource
            # usage after ExtractNodes and ExtractPersons ran.
            if proc.returncode != int(config["retcode"]["not_run"]):
                break

            # wait a few seconds between loops to avoid wasting CPU
            time.sleep(max(0, retry_luigi_delay - (time.time() - start_time)))
        exit(proc.returncode)


def main():
    return datasets_cli_group(auto_envvar_prefix="SWH_GRAPH")


if __name__ == "__main__":
    main()
