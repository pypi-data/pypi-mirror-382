// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::ops::Range;
use std::path::PathBuf;

use anyhow::{bail, Context, Result};
use clap::builder::{NonEmptyStringValueParser, TypedValueParser};
use clap::Parser;

use swh_graph::mph::DynMphf;

use swh_graph_contributions::impact::*;

#[derive(Parser, Debug)]
/// given a list of base64-encoded person fullnames on stdin, writes on stdout the list of origins
/// they contributed to and some stats on each origin
struct Args {
    graph_path: PathBuf,
    #[arg(long)]
    output_emails: bool,
    /// "YYYY-MM-DD" or "YYYY-MM-DD/YYYY-MM-DD" (inclusive/exclusive)
    ///
    /// If provided, only revisions and releases with an author *or* committer date in one of these
    /// ranges are considered.
    #[arg(long, value_parser = NonEmptyStringValueParser::new().try_map(parse_iso_date_range))]
    include_range: Vec<Range<Timestamp>>,
    /// "YYYY-MM-DD" or "YYYY-MM-DD/YYYY-MM-DD" (inclusive/exclusive)
    ///
    /// Author and committer dates in these ranges are not considered for --include-ranges.
    #[arg(long, value_parser = NonEmptyStringValueParser::new().try_map(parse_iso_date_range))]
    exclude_range: Vec<Range<Timestamp>>,
}

pub fn main() -> Result<()> {
    let args = Args::parse();

    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();

    log::info!("Loading graph");
    let graph = swh_graph::graph::SwhBidirectionalGraph::new(&args.graph_path)
        .context("Could not load graph")?
        .load_labels()
        .context("Could not load labels")?
        .init_properties()
        .load_properties(|props| props.load_maps::<DynMphf>())
        .context("Could not load maps")?
        .load_properties(|props| props.load_persons())
        .context("Could not load persons")?
        .load_properties(|props| props.load_strings())
        .context("Could not load strings")?
        .load_properties(|props| props.load_timestamps())
        .context("Could not load timestamps")?
        .load_properties(|props| props.load_label_names())
        .context("Could not load label names")?;

    // Compute the ids of people whose contributions we want to measure
    let person_ids =
        get_persons(&args.graph_path, std::io::stdin()).context("Could not compute person ids")?;

    if args.include_range.is_empty() && !args.exclude_range.is_empty() {
        bail!("--exclude-range without --include-range is not implemented yet.");
    }

    // Compute the list of revisions and releases they contributed to
    let revrel_person_checker = RevrelPersonChecker { person_ids };
    let revrels = list_revrels(
        &graph,
        &revrel_person_checker,
        &RevrelTimestampChecker {
            include_timestamp_ranges: args.include_range,
            exclude_timestamp_ranges: args.exclude_range,
        },
    )
    .context("Could not list their revrels")?;
    let RevrelPersonChecker { person_ids } = revrel_person_checker;

    // Traverse the list of revisions and releases in each origin, and count how many are
    // in the list we just computed
    log::info!("Traversing from origins and writing results...");
    let writer = csv::WriterBuilder::new()
        .has_headers(true)
        .terminator(csv::Terminator::CRLF)
        .from_writer(std::io::stdout());
    write_origin_contributors(&graph, writer, &revrels, &person_ids, args.output_emails)
}
