// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::path::PathBuf;

use anyhow::{Context, Result};
use clap::Parser;

use swh_graph::mph::DynMphf;

#[derive(Parser, Debug)]
/// Given a graph and the ORC dataset, produces a table that maps content node ids to their SHA1 hashes.
struct Args {
    #[arg(long)]
    graph: PathBuf,
    #[arg(long)]
    /// Path to the ORC dataset
    ///
    /// It must contain the `content/` subdirectory
    dataset: PathBuf,
    #[arg(long)]
    /// Whether the `skipped_content/` subdirectory should be read, in addition to `content/`.
    include_skipped_contents: bool,
    #[arg(long)]
    /// Where to write the table containing content SHA1 hashes
    node2sha1_out: PathBuf,
}

pub fn main() -> Result<()> {
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();

    let args = Args::parse();

    log::info!("Loading graph");
    let graph = swh_graph::graph::SwhUnidirectionalGraph::new(&args.graph)
        .context("Could not load graph")?
        .init_properties()
        .load_properties(|props| props.load_maps::<DynMphf>())
        .context("Could not load maps")?;

    let node2sha1 = swh_contents::sha1::build::build_sha1_table(
        &graph,
        args.dataset,
        args.include_skipped_contents,
    )
    .context("Could not build SHA1 table")?;

    log::info!("Writing SHA1 table...");
    node2sha1
        .dump(&args.node2sha1_out)
        .context("Could not write SHA1 table")?;
    log::info!("Done.");

    Ok(())
}
