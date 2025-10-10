# Copyright (C) 2025 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from __future__ import annotations

import concurrent
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import boto3
import botocore
from botocore.handlers import disable_signing
import tqdm

if TYPE_CHECKING:
    from types_boto3_s3.service_resource import ObjectSummary


class DatasetDownloader:
    """Utility class to help downloading SWH datasets (ORC exports for instance)
    from S3."""

    def __init__(
        self,
        local_path: Path,
        s3_url: str,
        prefix: str,
        parallelism: int = 5,
    ) -> None:
        if not s3_url.startswith("s3://"):
            raise ValueError("Unsupported S3 URL")

        self.s3 = boto3.resource("s3")
        # don't require credentials to list the bucket
        self.s3.meta.client.meta.events.register("choose-signer.s3.*", disable_signing)
        self.client = boto3.client(
            "s3",
            config=botocore.client.Config(
                # https://github.com/boto/botocore/issues/619
                max_pool_connections=10 * parallelism,
                # don't require credentials to download files
                signature_version=botocore.UNSIGNED,
            ),
        )

        self.local_path = local_path
        self.s3_url = s3_url.rstrip("/")

        s3_dataset_url = self.s3_url + f"/{prefix.strip('/')}/"
        self.bucket_name, self.prefix = s3_dataset_url[len("s3://") :].split("/", 1)
        self.parallelism = parallelism

    def _download_file(
        self, obj: ObjectSummary, prefix: str, local_path: Optional[Path] = None
    ):
        assert obj.key.startswith(prefix)
        if local_path is None:
            relative_path = obj.key.removeprefix(prefix).lstrip("/")
            local_path = self.local_path / relative_path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        self.client.download_file(
            Bucket=self.bucket_name,
            Key=obj.key,
            Filename=str(local_path),
        )

    def download(self):
        bucket = self.s3.Bucket(self.bucket_name)

        # recursively copy local files to S3, and end with compression metadata
        objects = list(bucket.objects.filter(Prefix=self.prefix))
        if not objects:
            raise ValueError(f"No dataset found at URL {self.s3_url}")

        # first download data files, excluding metadata JSON files
        with tqdm.tqdm(total=len(objects), desc="Downloading") as progress:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.parallelism
            ) as executor:
                for _ in concurrent.futures.as_completed(
                    executor.submit(self._download_file, obj, self.prefix)
                    for obj in objects
                    if not obj.key.endswith(".json")
                ):
                    progress.update()

        # download JSON metadata files as stamps after data files
        for obj in bucket.objects.filter(Prefix=self.prefix):
            if obj.key.endswith(".json"):
                self._download_file(obj, self.prefix)

        # also download {s3_url}/meta/ contents if available
        prefix = self.s3_url[len("s3://") :].split("/", 1)[1] + "/meta/"
        for obj in bucket.objects.filter(Prefix=prefix):
            sub_path = obj.key.split("/meta/")[-1]
            self._download_file(obj, prefix, self.local_path / "meta" / sub_path)
