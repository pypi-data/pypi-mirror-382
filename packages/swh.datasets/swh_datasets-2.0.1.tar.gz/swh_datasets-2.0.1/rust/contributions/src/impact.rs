// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::collections::{HashMap, HashSet};
use std::io::{BufRead, BufReader};
use std::ops::Range;
use std::path::Path;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Mutex;

use anyhow::{bail, ensure, Context, Result};
use chrono::{NaiveDate, NaiveTime};
use dsi_progress_logger::{concurrent_progress_logger, progress_logger, ProgressLog};
use pthash::Phf;
use rand::seq::SliceRandom;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

use swh_graph::graph::*;
use swh_graph::properties;
use swh_graph::utils::shuffle::par_iter_shuffled_range;
use swh_graph::views::Subgraph;
use swh_graph::{NodeType, SWHID};
use swh_graph_stdlib::collections::{AdaptiveNodeSet, NodeSet, ReadNodeSet};
use swh_graph_stdlib::{find_head_rev_by_refs, find_latest_snp, iter_nodes};

pub type PersonId = u32;

#[derive(Eq, Hash, PartialEq, Ord, PartialOrd, Clone, Copy, Debug)]
pub struct Timestamp(pub i64);

#[derive(Debug, Deserialize)]
pub struct PersonInputRecord {
    fullname_base64: String,
    email_base64: String,
}

#[derive(Debug, Serialize)]
pub struct OriginOutputRecord {
    origin_id: usize,
    origin_url: String,
    num_contributed_revrels: u64,
    num_contributed_revs_in_main_branch: Option<u64>,
    total_revrels: u64,
    total_revs_in_main_branch: Option<u64>,
    first_contributed_revrel: Option<SWHID>,
    first_contributed_revrel_ts: Option<i64>,
    last_contributed_revrel: Option<SWHID>,
    last_contributed_revrel_ts: Option<i64>,
    first_revrel_ts: Option<i64>,
    last_revrel_ts: Option<i64>,
}

#[derive(Debug, Serialize)]
pub struct OriginOutputRecordWithEmails<'a> {
    origin_id: usize,
    origin_url: String,
    num_contributed_revrels: u64,
    num_contributed_revs_in_main_branch: Option<u64>,
    total_revrels: u64,
    total_revs_in_main_branch: Option<u64>,
    first_contributed_revrel: Option<SWHID>,
    first_contributed_revrel_ts: Option<i64>,
    first_contributed_revrel_author: Option<&'a String>,
    first_contributed_revrel_committer: Option<&'a String>,
    last_contributed_revrel: Option<SWHID>,
    last_contributed_revrel_ts: Option<i64>,
    last_contributed_revrel_author: Option<&'a String>,
    last_contributed_revrel_committer: Option<&'a String>,
    first_revrel_ts: Option<i64>,
    last_revrel_ts: Option<i64>,
}

/// Parses a string in the format YYYY-MM-DD/YYYY-MM-DD (inclusive/exclusive)
pub fn parse_iso_date_range(value: String) -> Result<Range<Timestamp>> {
    let splits: Vec<_> = value.split('/').collect();
    let (from, to) = match splits[..] {
        [date_str] => {
            let date: NaiveDate = date_str.parse()?;
            (
                date,
                date.succ_opt().context("Date is too far in the future")?,
            )
        }
        [from_str, to_str] => {
            let from = from_str.parse()?;
            let to = to_str.parse()?;
            ensure!(
                from < to,
                "Second date in the time interval ({to_str}) is not strictly greater than the first one ({from_str})");
            (from, to)
        }
        _ => bail!(
            "must be a date (YYYY-MM-DD) or a range of dates (YYYY-MM-DD/YYYY-MM-DD), not {value}"
        ),
    };

    let midnight = NaiveTime::MIN;
    let at_midnight = |date: NaiveDate| Timestamp(date.and_time(midnight).and_utc().timestamp());
    Ok(at_midnight(from)..at_midnight(to))
}
pub fn get_persons<R: std::io::Read>(
    graph_path: &Path,
    needles_file: R,
) -> Result<HashMap<PersonId, String>> {
    log::info!("Reading persons MPHF...");
    let mphf_path = graph_path.with_extension("persons.pthash");
    let mphf = swh_graph::compress::persons::PersonMphf::load(&mphf_path)
        .with_context(|| format!("Could not load persons MPHF from {}", mphf_path.display()))?;

    let mut pl = concurrent_progress_logger! {
        item_name="person",
        display_memory=true,
    };
    pl.start("Loading all persons from graph...");
    let haystack_sha256_path = graph_path.with_extension("persons.csv.zst");
    let haystack_sha256_file = std::fs::File::open(&haystack_sha256_path).with_context(|| {
        format!(
            "Could not open list of person sha256 from {}",
            haystack_sha256_path.display()
        )
    })?;
    let haystack_sha256_decoder = zstd::stream::read::Decoder::new(haystack_sha256_file)
        .with_context(|| {
            format!(
                "{} is not a valid ZSTD file",
                haystack_sha256_path.display()
            )
        })?;
    let base64 = base64_simd::STANDARD;
    let haystack_sha256: Vec<Box<[u8]>> = BufReader::new(haystack_sha256_decoder)
        .lines()
        .par_bridge()
        .map_init(
            || pl.clone(),
            |pl, line| {
                pl.light_update();
                let line = line?;
                let line = line.trim_end();
                Ok(base64
                    .decode_to_vec(line)
                    .with_context(|| {
                        format!(
                            "Could not base64-decode haystack line {:?} from {}",
                            line,
                            haystack_sha256_path.display()
                        )
                    })?
                    .into())
            },
        )
        .collect::<Result<_>>()?;
    let haystack_sha256_set: HashSet<_> = haystack_sha256.iter().cloned().collect();

    let mut pl = progress_logger! {
        item_name="person",
        display_memory=true,
    };

    pl.start("Listing persons...");

    let num_lines = AtomicUsize::new(0);

    let mut reader = csv::Reader::from_reader(needles_file);
    let persons: HashMap<_, _> = reader
        .deserialize()
        .filter_map(|line| {
            num_lines.fetch_add(1, Ordering::Relaxed);
            let PersonInputRecord {
                fullname_base64,
                email_base64,
            } = match line {
                Ok(line) => line,
                Err(e) => return Some(Err(e.into())),
            };
            let needle = match base64.decode_to_vec(&fullname_base64).with_context(|| {
                format!("Could not base64-decode needle fullname {fullname_base64:?} from stdin")
            }) {
                Ok(needle) => needle,
                Err(e) => return Some(Err(e)),
            };
            let mut hasher = Sha256::new();
            hasher.update(&needle);
            let needle_sha256 = hasher.finalize();
            pl.light_update();
            if haystack_sha256_set.contains(&*needle_sha256) {
                match PersonId::try_from(
                    mphf.hash(base64.encode_to_string(needle_sha256).as_bytes()),
                )
                .context("Person id overflowed")
                {
                    Ok(id) => {
                        let email = match base64.decode_to_vec(&email_base64).with_context(|| {
                            format!(
                                "Could not base64-decode needle email {email_base64:?} from stdin"
                            )
                        }) {
                            Ok(needle) => needle,
                            Err(e) => return Some(Err(e)),
                        };
                        Some(Ok((id, String::from_utf8_lossy(&email).into_owned())))
                    }
                    Err(e) => Some(Err(e)),
                }
            } else {
                log::debug!("Unknown person name: {}", String::from_utf8_lossy(&needle));
                None
            }
        })
        .collect::<Result<_>>()?;

    log::info!(
        "{} known needles out of {}",
        persons.len(),
        num_lines.into_inner()
    );

    pl.done();

    Ok(persons)
}

pub struct RevrelTimestampChecker {
    pub include_timestamp_ranges: Vec<Range<Timestamp>>,
    pub exclude_timestamp_ranges: Vec<Range<Timestamp>>,
}

impl RevrelTimestampChecker {
    /// Returns whether whether either timestamp of the revision matches the requirements
    ///
    /// for each timestamp of the revision (author or committer), if it is in
    /// `include_timestamp_ranges` but not in `exclude_timestamp_ranges`, returns true.
    /// Otherwise, returns false
    pub fn matches<G>(&self, graph: &G, revrel: NodeId) -> bool
    where
        G: SwhGraphWithProperties,
        <G as SwhGraphWithProperties>::Timestamps: properties::Timestamps,
    {
        if self.include_timestamp_ranges.is_empty() {
            true
        } else {
            let author_ts = graph.properties().author_timestamp(revrel);
            let committer_ts = graph.properties().committer_timestamp(revrel);
            for ts in [author_ts, committer_ts]
                .into_iter()
                .flatten()
                .map(Timestamp)
            {
                if self
                    .exclude_timestamp_ranges
                    .iter()
                    .any(|range| range.contains(&ts))
                {
                    // don't even consider timestamp for include_timestamp_ranges
                    continue;
                }
                if self
                    .include_timestamp_ranges
                    .iter()
                    .any(|range| range.contains(&ts))
                {
                    return true;
                }
            }
            false
        }
    }
}

pub struct RevrelPersonChecker {
    pub person_ids: HashMap<PersonId, String>,
}

impl RevrelPersonChecker {
    /// Returns whether the author or the committer is in the `person_ids`
    pub fn matches<G>(&self, graph: G, revrel: NodeId) -> bool
    where
        G: SwhGraphWithProperties,
        <G as SwhGraphWithProperties>::Persons: properties::Persons,
    {
        if let Some(author_id) = graph.properties().author_id(revrel) {
            if self.person_ids.contains_key(&author_id) {
                return true;
            }
        }
        if let Some(committer_id) = graph.properties().committer_id(revrel) {
            if self.person_ids.contains_key(&committer_id) {
                return true;
            }
        }
        false
    }
}

pub fn list_revrels<G>(
    graph: &G,
    revrel_person_checker: &RevrelPersonChecker,
    revrel_timestamp_checker: &RevrelTimestampChecker,
) -> Result<HashSet<NodeId>>
where
    G: SwhForwardGraph + SwhBackwardGraph + SwhGraphWithProperties + Sync + Send,
    <G as SwhGraphWithProperties>::Maps: properties::Maps,
    <G as SwhGraphWithProperties>::Persons: properties::Persons,
    <G as SwhGraphWithProperties>::Timestamps: properties::Timestamps,
{
    let mut pl = concurrent_progress_logger! {
        item_name="node",
        display_memory=true,
        expected_updates=Some(graph.num_nodes()),
    };
    pl.start("Listing revrels they contributed to...");

    let (revrels, _pl) = par_iter_shuffled_range(0..graph.num_nodes())
        .fold(
            || (HashSet::new(), pl.clone()),
            |(mut revrels, mut pl), node| {
                let is_revrel = match graph.properties().node_type(node) {
                    NodeType::Origin
                    | NodeType::Snapshot
                    | NodeType::Content
                    | NodeType::Directory => false,
                    NodeType::Release | NodeType::Revision => true,
                };
                if is_revrel
                    && revrel_timestamp_checker.matches(graph, node)
                    && revrel_person_checker.matches(graph, node)
                {
                    revrels.insert(node);
                }

                pl.light_update();
                (revrels, pl)
            },
        )
        .reduce(
            || (HashSet::new(), pl.clone()),
            |(mut revrels1, pl1), (mut revrels2, _pl2)| {
                if revrels1.len() > revrels2.len() {
                    (revrels1, revrels2) = (revrels2, revrels1)
                }
                for revrel in revrels2 {
                    revrels1.insert(revrel);
                }
                (revrels1, pl1)
            },
        );

    pl.done();

    log::info!("Found {} revrels", revrels.len());

    Ok(revrels)
}

pub fn write_origin_contributors<G, W: std::io::Write + Send>(
    graph: &G,
    mut writer: csv::Writer<W>,
    revrels: &HashSet<NodeId>,
    persons: &HashMap<PersonId, String>,
    output_emails: bool,
) -> Result<()>
where
    G: SwhLabeledForwardGraph + SwhBackwardGraph + SwhGraphWithProperties + Send + Sync,
    <G as SwhGraphWithProperties>::Maps: properties::Maps,
    <G as SwhGraphWithProperties>::Persons: properties::Persons,
    <G as SwhGraphWithProperties>::Strings: properties::Strings,
    <G as SwhGraphWithProperties>::Timestamps: properties::Timestamps,
    <G as SwhGraphWithProperties>::LabelNames: properties::LabelNames,
{
    let writer = Mutex::new(&mut writer);
    let graph =
        Subgraph::with_node_filter(graph, |node| match graph.properties().node_type(node) {
            NodeType::Origin | NodeType::Snapshot | NodeType::Release | NodeType::Revision => true,
            NodeType::Content | NodeType::Directory => false,
        });

    let head_ref_name_ids: Vec<_> = ["refs/heads/main", "refs/heads/master"]
        .into_iter()
        .filter_map(|name| graph.properties().label_name_id(name.as_bytes()).ok())
        .collect();

    let mut origins: Vec<_> = (0..graph.num_nodes())
        .into_par_iter()
        .filter(|&node| graph.properties().node_type(node) == NodeType::Origin)
        .collect();
    origins.shuffle(&mut rand::rng());

    let mut pl = concurrent_progress_logger! {
        item_name="origin",
        //display_memory=true, // deadlocks
        display_memory=false,
        expected_updates=Some(origins.len()),
    };
    pl.threshold(1 << 10);

    pl.start("Listing revrels in each origin...");

    origins
        .into_par_iter()
        .try_for_each_init(
            || pl.clone(),
            |pl, origin| -> Result<()> {
                pl.light_update();
                let mut to_visit = vec![origin];
                let mut seen = AdaptiveNodeSet::new(graph.num_nodes());
                let mut first_revrel_ts = None;
                let mut last_revrel_ts = None;
                let mut num_contributed_revrels = 0u64;
                let mut total_revrels = 0u64;
                let mut first_contributed_revrel = None;
                let mut last_contributed_revrel = None;
                let mut first_contributed_revrel_ts = None;
                let mut last_contributed_revrel_ts = None;

                while let Some(node) = to_visit.pop() {
                    match graph.properties().node_type(node) {
                        NodeType::Revision | NodeType::Release => {
                            total_revrels = total_revrels.saturating_add(1);

                            let ts = graph
                                .properties()
                                .author_timestamp(node)
                                .or_else(|| graph.properties().committer_timestamp(node));
                            if let Some(ts) = ts {
                                first_revrel_ts = Some(first_revrel_ts.unwrap_or(i64::MAX).min(ts));
                                last_revrel_ts = Some(last_revrel_ts.unwrap_or(i64::MIN).max(ts));
                            }

                            // If the revrel was computed by a person in the small set
                            if revrels.contains(&node) {
                                num_contributed_revrels = num_contributed_revrels.saturating_add(1);
                                if let Some(ts) = ts {
                                    if ts < first_contributed_revrel_ts.unwrap_or(i64::MAX) {
                                        first_contributed_revrel_ts = Some(ts);
                                        first_contributed_revrel = Some(node);
                                    }
                                    if ts > last_contributed_revrel_ts.unwrap_or(i64::MIN) {
                                        last_contributed_revrel_ts = Some(ts);
                                        last_contributed_revrel = Some(node);
                                    }
                                }
                            }
                        }
                        _ => (),
                    };
                    for succ in graph.successors(node) {
                        if !seen.contains(succ) {
                            to_visit.push(succ);
                            seen.insert(succ);
                        }
                    }
                }

                if num_contributed_revrels > 0 {
                    let head_rev = find_latest_snp(&graph, origin)
                        .context("Could not get latest snapshot")?
                        .and_then(|(snp, _name_id)| {
                            find_head_rev_by_refs(&graph, snp, &head_ref_name_ids).transpose()
                        })
                        .transpose()
                        .context("Could not get head rev")?;

                    let (num_contributed_revs_in_main_branch, total_revs_in_main_branch) =
                        match head_rev {
                            None => (None, None),
                            Some(head_rev) => {
                                let mut total_revs_in_main_branch = 0u64;
                                let mut num_contributed_revs_in_main_branch = 0u64;
                                for node in iter_nodes(&graph, [head_rev]) {
                                    if graph.properties().node_type(node) == NodeType::Revision {
                                        total_revs_in_main_branch =
                                            total_revs_in_main_branch.saturating_add(1);
                                        if revrels.contains(&node) {
                                            num_contributed_revs_in_main_branch =
                                                num_contributed_revs_in_main_branch
                                                    .saturating_add(1);
                                        }
                                    }
                                }
                                (
                                    Some(num_contributed_revs_in_main_branch),
                                    Some(total_revs_in_main_branch),
                                )
                            }
                        };

                    let origin_url = graph
                        .properties()
                        .message(origin)
                        .map(|url| String::from_utf8_lossy(&url).into())
                        .unwrap_or_else(|| "".to_owned());
                    if output_emails {
                        writer
                            .lock()
                            .unwrap()
                            .serialize(OriginOutputRecordWithEmails {
                                origin_id: origin,
                                origin_url,
                                num_contributed_revrels,
                                num_contributed_revs_in_main_branch,
                                total_revrels,
                                total_revs_in_main_branch,
                                first_contributed_revrel: first_contributed_revrel
                                    .map(|revrel| graph.properties().swhid(revrel)),
                                first_contributed_revrel_ts,
                                first_contributed_revrel_author: first_contributed_revrel
                                    .and_then(|first_contributed_revrel| {
                                        graph.properties().author_id(first_contributed_revrel)
                                    })
                                    .and_then(|person_id| persons.get(&person_id)),
                                first_contributed_revrel_committer: first_contributed_revrel
                                    .and_then(|first_contributed_revrel| {
                                        graph.properties().committer_id(first_contributed_revrel)
                                    })
                                    .and_then(|person_id| persons.get(&person_id)),

                                last_contributed_revrel: last_contributed_revrel
                                    .map(|revrel| graph.properties().swhid(revrel)),
                                last_contributed_revrel_ts,
                                last_contributed_revrel_author: last_contributed_revrel
                                    .and_then(|last_contributed_revrel| {
                                        graph.properties().author_id(last_contributed_revrel)
                                    })
                                    .and_then(|person_id| persons.get(&person_id)),
                                last_contributed_revrel_committer: last_contributed_revrel
                                    .and_then(|last_contributed_revrel| {
                                        graph.properties().committer_id(last_contributed_revrel)
                                    })
                                    .and_then(|person_id| persons.get(&person_id)),

                                first_revrel_ts,
                                last_revrel_ts,
                            })
                            .context("could not write to CSV")?;
                    } else {
                        writer
                            .lock()
                            .unwrap()
                            .serialize(OriginOutputRecord {
                                origin_id: origin,
                                origin_url,
                                num_contributed_revrels,
                                num_contributed_revs_in_main_branch,
                                total_revrels,
                                total_revs_in_main_branch,
                                first_contributed_revrel: first_contributed_revrel
                                    .map(|revrel| graph.properties().swhid(revrel)),
                                first_contributed_revrel_ts,
                                last_contributed_revrel: last_contributed_revrel
                                    .map(|revrel| graph.properties().swhid(revrel)),
                                last_contributed_revrel_ts,
                                first_revrel_ts,
                                last_revrel_ts,
                            })
                            .context("could not write to CSV")?;
                    }
                }

                Ok(())
            },
        )
        .context("Could not write origin stats")?;

    pl.done();

    writer
        .into_inner()
        .unwrap()
        .flush()
        .context("could not flush CSV writer")?;

    Ok(())
}
