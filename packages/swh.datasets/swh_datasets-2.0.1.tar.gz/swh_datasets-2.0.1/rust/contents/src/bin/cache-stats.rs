// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::path::PathBuf;

use anyhow::{Context, Result};
use clap::Parser;
use dsi_progress_logger::{concurrent_progress_logger, ProgressLog};
use rayon::prelude::*;
use swh_graph::graph::SwhBidirectionalGraph;
use swh_graph::mph::DynMphf;

use swh_contents::retriever::rocksdb::ReadonlyRocksdbContentCache;

#[derive(Parser, Debug)]
/// Computes and prints some statistics about the content cache
struct Args {
    #[arg(long)]
    graph: PathBuf,
    #[arg(long)]
    /// What rocksdb database to write to
    db: PathBuf,
}

fn main() -> Result<()> {
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();

    let args = Args::parse();

    log::info!("Loading graph...");
    let graph = SwhBidirectionalGraph::new(&args.graph)
        .context("Could not load graph")?
        .load_labels()
        .context("Could not load graph labels")?
        .init_properties()
        .load_properties(|properties| properties.load_maps::<DynMphf>())
        .context("Could not load maps")?
        .load_properties(|properties| properties.load_label_names())
        .context("Could not load label names")?;

    log::info!("Opening cache...");
    let cache = ReadonlyRocksdbContentCache::new(&graph, &args.db)
        .context("Could not load Rocksdb cache")?;

    let mut pl = concurrent_progress_logger!(
        display_memory = true,
        item_name = "content",
        local_speed = true,
        expected_updates = Some(
            cache
                .estimate_num_cached_contents()
                .context("Could not estimate cache size")?
        ),
    );
    pl.start("Scanning contents...");
    let stats = rocksdb_rayon::ParallelRocksdbItemIterator::new(cache.db())
        .map_with(pl.clone(), |pl, (key, value)| {
            pl.light_update();
            Stats {
                count: 1,
                total_keys_len: key.len() as u64,
                total_values_len: value.len() as u64,
            }
        })
        .reduce(Stats::default, |stats1, stats2| stats1 + stats2);
    pl.done();

    println!("{stats:#?}");

    Ok(())
}

#[derive(Debug, Default, derive_more::Add)]
struct Stats {
    count: usize,
    total_keys_len: u64,
    total_values_len: u64,
}
