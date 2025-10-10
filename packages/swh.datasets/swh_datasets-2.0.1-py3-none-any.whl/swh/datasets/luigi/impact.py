# Copyright (C) 2025 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

"""
Luigi tasks to measure institutional impact
===========================================

This module contains `Luigi <https://luigi.readthedocs.io/>`_ tasks
computing the impact of an institution across all origins
"""
# WARNING: do not import unnecessary things here to keep cli startup time under
# control
import datetime
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, TypedDict, Union

import luigi

from swh.graph.luigi.compressed_graph import LocalGraph

if TYPE_CHECKING:
    from swh.indexer.storage.model import OriginExtrinsicMetadataRow
    from swh.scheduler.interface import SchedulerInterface

    class ParsedListedOrigin(TypedDict, total=False):
        url: str
        last_update: datetime.datetime
        enabled: bool

else:
    ParsedListedOrigin = dict

logger = logging.getLogger(__name__)


class ComputeRawImpact(luigi.Task):
    """Creates a file that list all origins that contains revrels from a given set
    of persons, as well as the number of revrels and first/latest timestamp for each origin.
    """

    local_graph_path = luigi.PathParameter()
    graph_name = luigi.Parameter(default="graph")
    persons_path = luigi.PathParameter()
    raw_impact_path = luigi.PathParameter()
    output_emails = luigi.BoolParameter(default=False)
    include_ranges = luigi.Parameter(
        default="",
        description="Space-separated list of ISO8601 dates ('YYYY-MM-DD') or "
        "date intervals ('YYYY-MM-DD/YYYY-MM-DD', inclusive/exclusive). "
        "If provided, only revisions and releases with an author *or* committer date in "
        "one of these ranges are considered.",
    )
    exclude_ranges = luigi.Parameter(
        default="",
        description="Space-separated list of ISO8601 dates ('YYYY-MM-DD') or "
        "date intervals ('YYYY-MM-DD/YYYY-MM-DD', inclusive/exclusive). "
        "Author and committer dates in these ranges are not considered for --include-ranges.",
    )

    def requires(self) -> Dict[str, luigi.Task]:
        """Returns an instance of :class:`swh.graph.luigi.compressed_graph.LocalGraph`
        and :class:`swh.graph.luigi.topology.ComputeGenerations`."""

        class PersonsTask(luigi.ExternalTask):
            def output(self2):
                return luigi.LocalTarget(self.persons_path)

        return {
            "graph": LocalGraph(local_graph_path=self.local_graph_path),
            "persons": PersonsTask(),
        }

    def output(self) -> List[luigi.Target]:
        """.csv.zst file that contains the origin_id<->contributor_id map
        and the list of origins"""
        return [
            luigi.LocalTarget(self.raw_impact_path),
        ]

    def run(self) -> None:
        """Runs org.softwareheritage.graph.utils.ListOriginContributors and compresses"""
        import itertools

        from swh.datasets.shell import Rust
        from swh.graph.shell import AtomicFileSink, Command

        # fmt: off
        (
            Command.cat(self.persons_path)
            | Rust(
                "impact",
                self.local_graph_path / self.graph_name,
                *(["--output-emails"] if self.output_emails else []),
                *itertools.chain.from_iterable(
                    ["--include-range", range_]
                    for range_ in self.include_ranges.split()
                ),
                *itertools.chain.from_iterable(
                    ["--exclude-range", range_]
                    for range_ in self.exclude_ranges.split()
                ),
            )
            | Command.zstdmt("-19")
            > AtomicFileSink(self.raw_impact_path)
        ).run()
        # fmt: on


class ComputeIndexedImpact(luigi.Task):
    """Removes forks from :class:`ComputeRawImpact`'s output, unless they contain more
    revrels (or older/newer ones) than the upstream origin."""

    indexer_storage_url = luigi.Parameter(significant=False)
    swh_scheduler_url = luigi.Parameter(significant=False)

    FORK_FILTERS = [
        "all",
        "none",
        "without-upstream-contribution",
        "with-original-content",
    ]

    local_graph_path = luigi.PathParameter()
    graph_name = luigi.Parameter(default="graph")
    persons_path = luigi.PathParameter()
    raw_impact_path = luigi.PathParameter()
    output_emails = luigi.BoolParameter(default=False)
    indexed_impact_path = luigi.PathParameter()
    fork_filter = luigi.ChoiceParameter(
        choices=FORK_FILTERS,
        default="with-original-content",
        description="'all' includes all forks. 'none' excludes all forks. "
        "'without-known-upstream' excludes forks of an upstream that does not have "
        "original content from one of the persons."
        "'with-original-content' extends this to include forks that have more commits "
        "from the persons than the upstream origin.",
    )

    def requires(self) -> Dict[str, luigi.Task]:
        """Returns an instance of :class:`swh.graph.luigi.compressed_graph.LocalGraph`
        and :class:`swh.graph.luigi.topology.ComputeGenerations`."""
        return {
            "graph": LocalGraph(local_graph_path=self.local_graph_path),
            "raw_impact": ComputeRawImpact(
                local_graph_path=self.local_graph_path,
                graph_name=self.graph_name,
                persons_path=self.persons_path,
                raw_impact_path=self.raw_impact_path,
                output_emails=self.output_emails,
            ),
        }

    def output(self) -> List[luigi.Target]:
        """.csv.zst file that contains the origin_id<->contributor_id map
        and the list of origins"""
        return [
            luigi.LocalTarget(self.indexed_impact_path),
        ]

    def run(self) -> None:
        """Runs org.softwareheritage.graph.utils.ListOriginContributors and compresses"""
        import csv
        import os

        import pyzstd
        import tqdm

        def opt_int(s: str) -> Optional[int]:
            if s == "":
                return None
            else:
                return int(s)

        with open(self.raw_impact_path, "rb") as in_fd:
            with pyzstd.open(in_fd, "rt") as f:
                reader = csv.reader(f)
                header = next(reader)
                origins: Union[
                    Dict[
                        str,
                        Tuple[
                            str,  # origin_id
                            int,  # num_contributed_revrels
                            Optional[int],  # num_contributed_revs_in_main_branch
                            int,  # total_revrels
                            Optional[int],  # total_revs_in_main_branch
                            str,  # first_contributed_revrel
                            Optional[int],  # first_contributed_revrel_ts
                            str,  # first_contributed_revrel_author
                            str,  # first_contributed_revrel_committer
                            str,  # last_contributed_revrel
                            Optional[int],  # last_contributed_revrel_ts
                            str,  # last_contributed_revrel_author
                            str,  # last_contributed_revrel_committer
                            Optional[int],  # first_revrel_ts
                            Optional[int],  # last_revrel_ts
                        ],
                    ],
                    Dict[
                        str,
                        Tuple[
                            str,  # origin_id
                            int,  # num_contributed_revrels
                            Optional[int],  # num_contributed_revs_in_main_branch
                            int,  # total_revrels
                            Optional[int],  # total_revs_in_main_branch
                            str,  # first_contributed_revrel
                            Optional[int],  # first_contributed_revrel_ts
                            None,  # first_contributed_revrel_author
                            None,  # first_contributed_revrel_committer
                            str,  # last_contributed_revrel
                            Optional[int],  # last_contributed_revrel_ts
                            None,  # last_contributed_revrel_author
                            None,  # last_contributed_revrel_committer
                            Optional[int],  # first_revrel_ts
                            Optional[int],  # last_revrel_ts
                        ],
                    ],
                ]
                if self.output_emails:
                    assert header == [
                        "origin_id",
                        "origin_url",
                        "num_contributed_revrels",
                        "num_contributed_revs_in_main_branch",
                        "total_revrels",
                        "total_revs_in_main_branch",
                        "first_contributed_revrel",
                        "first_contributed_revrel_ts",
                        "first_contributed_revrel_author",
                        "first_contributed_revrel_committer",
                        "last_contributed_revrel",
                        "last_contributed_revrel_ts",
                        "last_contributed_revrel_author",
                        "last_contributed_revrel_committer",
                        "first_revrel_ts",
                        "last_revrel_ts",
                    ], f"Unexpected header: {header}"
                    origins = {
                        origin_url: (
                            origin_id,
                            int(num_contributed_revrels),
                            opt_int(num_contributed_revs_in_main_branch),
                            int(total_revrels),
                            opt_int(total_revs_in_main_branch),
                            first_contributed_revrel,
                            opt_int(first_contributed_revrel_ts),
                            first_contributed_revrel_author,
                            first_contributed_revrel_committer,
                            last_contributed_revrel,
                            opt_int(last_contributed_revrel_ts),
                            last_contributed_revrel_author,
                            last_contributed_revrel_committer,
                            opt_int(first_revrel_ts),
                            opt_int(last_revrel_ts),
                        )
                        for (
                            origin_id,
                            origin_url,
                            num_contributed_revrels,
                            num_contributed_revs_in_main_branch,
                            total_revrels,
                            total_revs_in_main_branch,
                            first_contributed_revrel,
                            first_contributed_revrel_ts,
                            first_contributed_revrel_author,
                            first_contributed_revrel_committer,
                            last_contributed_revrel,
                            last_contributed_revrel_ts,
                            last_contributed_revrel_author,
                            last_contributed_revrel_committer,
                            first_revrel_ts,
                            last_revrel_ts,
                        ) in tqdm.tqdm(reader, desc="Reading raw origin stats")
                    }
                else:
                    assert header == [
                        "origin_id",
                        "origin_url",
                        "num_contributed_revrels",
                        "num_contributed_revs_in_main_branch",
                        "total_revrels",
                        "total_revs_in_main_branch",
                        "first_contributed_revrel",
                        "first_contributed_revrel_ts",
                        "last_contributed_revrel",
                        "last_contributed_revrel_ts",
                        "first_revrel_ts",
                        "last_revrel_ts",
                    ], f"Unexpected header: {header}"
                    origins = {
                        origin_url: (
                            origin_id,
                            int(num_contributed_revrels),
                            opt_int(num_contributed_revs_in_main_branch),
                            int(total_revrels),
                            opt_int(total_revs_in_main_branch),
                            first_contributed_revrel,
                            opt_int(first_contributed_revrel_ts),
                            None,  # first_contributed_revrel_author
                            None,  # first_contributed_revrel_committer
                            last_contributed_revrel,
                            opt_int(last_contributed_revrel_ts),
                            None,  # last_contributed_revrel_author
                            None,  # last_contributed_revrel_committer
                            opt_int(first_revrel_ts),
                            opt_int(last_revrel_ts),
                        )
                        for (
                            origin_id,
                            origin_url,
                            num_contributed_revrels,
                            num_contributed_revs_in_main_branch,
                            total_revrels,
                            total_revs_in_main_branch,
                            first_contributed_revrel,
                            first_contributed_revrel_ts,
                            last_contributed_revrel,
                            last_contributed_revrel_ts,
                            first_revrel_ts,
                            last_revrel_ts,
                        ) in tqdm.tqdm(reader, desc="Reading raw origin stats")
                    }

        origins_metadata = self._get_origins_metadata(list(origins))

        listed_origins = self._get_listed_origins(list(origins))

        tmp_path = f"{self.indexed_impact_path}.tmp"
        with open(tmp_path, "wb") as out_fd:
            with pyzstd.open(out_fd, "wt") as f:
                writer = csv.writer(f)
                writer.writerow(
                    (
                        *header,
                        "last_visit_ts",
                        "visits_enabled",
                        "num_forks",
                        "num_stars",
                        "num_followers",
                        "forked_from",
                    )
                )
                for origin_url in tqdm.tqdm(
                    origins,
                    desc=(
                        "Writing"
                        if self.fork_filter == "all"
                        else "Filtering out uninteresting forks and writing"
                    ),
                ):

                    origin_metadata = origins_metadata.get(origin_url)
                    if origin_metadata is None:
                        upstream_origin_url = None
                        num_forks = num_likes = num_followers = 0
                    else:
                        (upstream_origin_url, num_forks, num_likes, num_followers) = (
                            self._parse_origin_metadata(
                                origin_url, origin_metadata.metadata
                            )
                        )

                    (
                        origin_id,
                        num_contributed_revrels,
                        num_contributed_revs_in_main_branch,
                        total_revrels,
                        total_revs_in_main_branch,
                        first_contributed_revrel,
                        first_contributed_revrel_ts,
                        first_contributed_revrel_author,
                        first_contributed_revrel_committer,
                        last_contributed_revrel,
                        last_contributed_revrel_ts,
                        last_contributed_revrel_author,
                        last_contributed_revrel_committer,
                        first_revrel_ts,
                        last_revrel_ts,
                    ) = origins[origin_url]
                    listed_origin: ParsedListedOrigin = listed_origins.get(
                        origin_url, {}
                    )

                    if upstream_origin_url is None:
                        pass  # not a fork, we keep it
                    elif self.fork_filter == "none":
                        continue  # exclude all forks
                    elif self.fork_filter == "all":
                        pass  # include all forks
                    elif self.fork_filter == "without-upstream-contribution":
                        if upstream_origin_url in origins:
                            continue  # upstream has contributions
                        else:
                            pass  # upstream does not
                    else:
                        # check for new content
                        try:
                            (
                                _origin_id,
                                num_upstream_revrels,
                                _num_contributed_revs_in_main_branch,
                                _total_revrels,
                                _total_revs_in_main_branch,
                                _first_contributed_revrel,
                                first_upstream_revrel_ts,
                                _first_upstream_contributed_revrel_author,
                                _first_upstream_contributed_revrel_committer,
                                _last_upstream_contributed_revrel,
                                last_upstream_contributed_revrel_ts,
                                _last_upstream_contributed_revrel_author,
                                _last_upstream_contributed_revrel_committer,
                                _first_revrel_ts,
                                _last_revrel_ts,
                            ) = origins[upstream_origin_url]
                        except KeyError:
                            pass  # unknown upstream, so let's keep the fork
                        else:
                            if (
                                # the fork does not have more revrels
                                num_contributed_revrels <= num_upstream_revrels
                                and (
                                    (
                                        # the fork does not have a newer revrel
                                        last_contributed_revrel_ts is not None
                                        and last_upstream_contributed_revrel_ts
                                        is not None
                                        and last_contributed_revrel_ts
                                        <= last_upstream_contributed_revrel_ts
                                    )
                                    or (
                                        # the fork has no timestamped revrel, but upstream does
                                        last_contributed_revrel_ts is None
                                        and last_upstream_contributed_revrel_ts
                                        is not None
                                    )
                                )
                                and num_likes <= 1
                                and num_followers <= 1
                            ):
                                # uninteresting fork
                                continue
                    if self.output_emails:
                        writer.writerow(
                            (
                                origin_id,
                                origin_url,
                                num_contributed_revrels,
                                num_contributed_revs_in_main_branch,
                                total_revrels,
                                total_revs_in_main_branch,
                                first_contributed_revrel,
                                first_contributed_revrel_ts,
                                first_contributed_revrel_author,
                                first_contributed_revrel_committer,
                                last_contributed_revrel,
                                last_contributed_revrel_ts,
                                last_contributed_revrel_author,
                                last_contributed_revrel_committer,
                                first_revrel_ts,
                                last_revrel_ts,
                                listed_origin.get("last_update", ""),
                                listed_origin.get("enabled", ""),
                                num_forks,
                                num_likes,
                                num_followers,
                                upstream_origin_url or "",
                            )
                        )
                    else:
                        writer.writerow(
                            (
                                origin_id,
                                origin_url,
                                num_contributed_revrels,
                                num_contributed_revs_in_main_branch,
                                total_revrels,
                                total_revs_in_main_branch,
                                first_contributed_revrel,
                                first_contributed_revrel_ts,
                                last_contributed_revrel,
                                last_contributed_revrel_ts,
                                first_revrel_ts,
                                last_revrel_ts,
                                listed_origin.get("last_update", ""),
                                listed_origin.get("enabled", ""),
                                num_forks,
                                num_likes,
                                num_followers,
                                upstream_origin_url or "",
                            )
                        )

        os.rename(tmp_path, self.indexed_impact_path)  # atomic write

    def _parse_origin_metadata(
        self, origin_url, json_ld
    ) -> Tuple[Optional[str], int, int, int]:
        import json

        import rdflib

        from swh.indexer.codemeta import expand
        from swh.indexer.namespaces import ACTIVITYSTREAMS, FORGEFED

        origin = rdflib.term.URIRef(origin_url)

        g: Any = rdflib.Graph().parse(
            data=json.dumps(expand(json_ld)),
            format="json-ld",
            # replace invalid URIs with blank node ids, instead of discarding
            # whole nodes:
            generalized_rdf=True,
        )
        for _, _, forked_from in g.triples((origin, FORGEFED.forkedFrom, None)):
            upstream_origin_url = str(forked_from)
            break
        else:
            # not a fork, as far as we know
            upstream_origin_url = None

        num_forks = 0
        for _, _, forks in g.triples((origin, FORGEFED.forks, None)):
            for _, _, total_items in g.triples(
                (forks, ACTIVITYSTREAMS.totalItems, None)
            ):
                num_forks = total_items.value

        num_likes = 0
        for _, _, likes in g.triples((origin, ACTIVITYSTREAMS.likes, None)):
            for _, _, total_items in g.triples(
                (likes, ACTIVITYSTREAMS.totalItems, None)
            ):
                num_likes = total_items.value

        num_followers = 0
        for _, _, followers in g.triples((origin, ACTIVITYSTREAMS.followers, None)):
            for _, _, total_items in g.triples(
                (followers, ACTIVITYSTREAMS.totalItems, None)
            ):
                num_followers = total_items.value
        return (upstream_origin_url, num_forks, num_likes, num_followers)

    def _get_origins_metadata(
        self, origins: List[str]
    ) -> Dict[str, "OriginExtrinsicMetadataRow"]:
        import itertools
        import math
        import multiprocessing.dummy

        import tqdm

        from swh.core.utils import grouper
        from swh.indexer.storage import get_indexer_storage

        idx_storage = get_indexer_storage("remote", url=self.indexer_storage_url)

        num_concurrent_requests = 10
        num_origins_per_request = 100
        with multiprocessing.dummy.Pool(num_concurrent_requests) as p:
            return {
                row.id: row
                for row in itertools.chain.from_iterable(
                    tqdm.tqdm(
                        p.imap_unordered(
                            idx_storage.origin_extrinsic_metadata_get,
                            grouper(origins, num_origins_per_request),
                        ),
                        desc="Fetching origin metadata",
                        total=math.ceil(len(origins) / num_origins_per_request),
                    ),
                )
            }

    def _get_listed_origins(self, origins: List[str]) -> Dict[str, ParsedListedOrigin]:
        import functools
        import itertools
        import math
        import multiprocessing.dummy

        import tqdm

        from swh.core.utils import grouper
        from swh.scheduler import get_scheduler

        scheduler = get_scheduler("remote", url=self.swh_scheduler_url)

        num_concurrent_requests = 10
        num_origins_per_request = 100
        with multiprocessing.dummy.Pool(num_concurrent_requests) as p:
            return {
                listed_origin["url"]: listed_origin
                for listed_origin in itertools.chain.from_iterable(
                    tqdm.tqdm(
                        p.imap_unordered(
                            functools.partial(
                                self._get_listed_origins_group, scheduler=scheduler
                            ),
                            grouper(origins, num_origins_per_request),
                        ),
                        desc="Fetching scheduler info",
                        total=math.ceil(len(origins) / num_origins_per_request),
                    ),
                )
            }

    def _get_listed_origins_group(
        self, origins: List[str], scheduler: "SchedulerInterface"
    ) -> List[ParsedListedOrigin]:
        import datetime

        from swh.core.api.classes import stream_results

        results: Dict[str, ParsedListedOrigin] = {}
        for listed_origin in stream_results(scheduler.get_listed_origins, urls=origins):
            origin_result = results.setdefault(
                listed_origin.url,
                {
                    "url": listed_origin.url,
                    "last_update": datetime.datetime.max.replace(
                        tzinfo=datetime.timezone.utc
                    ),
                    "enabled": False,
                },
            )
            if listed_origin.last_update:
                origin_result["last_update"] = min(
                    origin_result["last_update"], listed_origin.last_update
                )
            origin_result["enabled"] = origin_result["enabled"] or listed_origin.enabled

        return list(results.values())
