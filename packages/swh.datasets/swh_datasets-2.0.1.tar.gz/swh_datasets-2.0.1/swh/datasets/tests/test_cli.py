# Copyright (C) 2019-2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os
from tempfile import TemporaryDirectory

import boto3
from click.testing import CliRunner
from moto import mock_aws
import pytest

from swh.datasets.cli import datasets_cli_group
import swh.graph


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.mark.parametrize("exit_code", [0, 1])
def test_luigi(mocker, tmpdir, exit_code, cli_runner):
    """calls Luigi with the given configuration"""
    # bare bone configuration, to allow testing the compression pipeline
    # with minimum RAM requirements on trivial graphs

    subprocess_run = mocker.patch("subprocess.run")
    subprocess_run.return_value.returncode = exit_code

    with TemporaryDirectory(suffix=".swh-datasets-test") as tmpdir:
        result = cli_runner.invoke(
            datasets_cli_group,
            [
                "luigi",
                "--base-directory",
                f"{tmpdir}/base_dir",
                "--dataset-name",
                "2022-12-07",
                "--",
                "foo",
                "bar",
                "--baz",
                "qux",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == exit_code, result.output

    luigi_config_path = subprocess_run.mock_calls[0][2]["env"]["LUIGI_CONFIG_PATH"]
    subprocess_run.assert_called_once_with(
        [
            "luigi",
            "--module",
            "swh.export.luigi",
            "--module",
            "swh.graph.luigi",
            "--module",
            "swh.datasets.luigi",
            "foo",
            "bar",
            "--baz",
            "qux",
        ],
        env={"LUIGI_CONFIG_PATH": luigi_config_path, **os.environ},
    )


def add_example_dataset_to_s3_bucket(bucket, prefix, name):
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=bucket)
    datasets_path = os.path.join(os.path.dirname(swh.graph.__file__), "example_dataset")
    for root, _, files in os.walk(datasets_path):
        for f in files:
            path = os.path.join(root, f)
            relative_path = path.replace(datasets_path + "/", "")
            key = os.path.join(prefix, name, relative_path)
            if relative_path.startswith(("orc/", "compressed/", "meta/")):
                s3.upload_file(
                    Filename=path,
                    Bucket=bucket,
                    Key=key,
                    ExtraArgs={
                        "ACL": "public-read",
                    },
                )
    s3.put_object(
        ACL="public-read",
        Body=b"{}",
        Bucket=bucket,
        Key=os.path.join(prefix, name, "compressed/meta/compression.json"),
    )
    s3.put_object(
        ACL="public-read",
        Body=b"{}",
        Bucket=bucket,
        Key=os.path.join(prefix, name, "meta/foo/bar.json"),
    )


@pytest.fixture
def bucket_name():
    return "softwareheritage"


@pytest.fixture
def dataset_path_prefix():
    return "graph"


@pytest.fixture
def dataset_name():
    return "example"


@mock_aws
def test_download_graph(cli_runner, bucket_name, dataset_path_prefix, dataset_name):
    add_example_dataset_to_s3_bucket(bucket_name, dataset_path_prefix, dataset_name)
    with TemporaryDirectory(suffix=".swh-datasets-test") as tmpdir:
        result = cli_runner.invoke(
            datasets_cli_group,
            [
                "download-graph",
                "--name",
                dataset_name,
                tmpdir,
            ],
        )
        assert result.exit_code == 0, result.output
        assert os.path.exists(os.path.join(tmpdir, "example.graph"))
        assert os.path.exists(os.path.join(tmpdir, "meta/compression.json"))


@mock_aws
def test_download_export(cli_runner, bucket_name, dataset_path_prefix, dataset_name):
    add_example_dataset_to_s3_bucket(bucket_name, dataset_path_prefix, dataset_name)
    with TemporaryDirectory(suffix=".swh-datasets-test") as tmpdir:
        result = cli_runner.invoke(
            datasets_cli_group,
            [
                "download-export",
                "--name",
                dataset_name,
                tmpdir,
            ],
        )
        assert result.exit_code == 0, result.output
        assert os.path.exists(os.path.join(tmpdir, "content/content-all.orc"))
        assert os.path.exists(os.path.join(tmpdir, "meta/export.json"))
        assert os.path.exists(os.path.join(tmpdir, "meta/foo/bar.json"))
