// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::path::PathBuf;
use std::time::Duration;

use anyhow::{bail, Context, Result};
use clap::Parser;
use dsi_progress_logger::{concurrent_progress_logger, ProgressLog};
use futures::{FutureExt, StreamExt, TryFutureExt, TryStreamExt};
use rayon::prelude::*;
use rdst::RadixSort;
use sux::dict::elias_fano::{EfDict, EliasFanoConcurrentBuilder};
use sux::traits::IndexedDict;
use swh_graph::graph::{SwhBidirectionalGraph, SwhGraph};
use swh_graph::mph::DynMphf;
use swh_graph::SWHID;

use swh_contents::retriever::rocksdb::{GraphWithFilenames, RocksdbContentCache};
use swh_contents::retriever::*;
use swh_contents::sha1::Sha1Table;

#[derive(Parser, Debug)]
/// Reads SWHIDs from stdin (one per line) and downloads corresponding contents to a local cache
struct Args {
    #[arg(long)]
    graph: PathBuf,
    #[arg(long)]
    /// Map from node ids to SHA1 hash, as produced by `build-sha1-table`
    node2sha1: PathBuf,
    #[arg(long)]
    /// Must start with either `plain:` or `gzip:` and contain `{sha1}` (which will be substituted
    /// by each content's SHA1 hash).
    url: Vec<String>,
    #[arg(long)]
    /// What rocksdb database to write to
    db: PathBuf,
    #[arg(long, default_value_t = 100)]
    /// Maximum number of concurrent downloads
    concurrent_downloads: usize,
    #[arg(long)]
    /// .csv.zst file (or directories of such files) containing lists of SWHIDs.
    /// Defaults to stdin if not provided
    swhids: Vec<PathBuf>,
}

#[tokio::main(flavor = "multi_thread")]
async fn main() -> Result<()> {
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

    let client = reqwest::Client::builder()
        .user_agent(format!(
            "{}/{} (download-contents.rs)",
            env!("CARGO_PKG_NAME"),
            env!("CARGO_PKG_VERSION"),
        ))
        .build()
        .context("Could not build HTTP client")?;

    // Wrap client in retry middleware
    let retry_policy =
        reqwest_retry::policies::ExponentialBackoff::builder().build_with_max_retries(10);
    let client = reqwest_middleware::ClientBuilder::new(client)
        .with(http::Http429Middleware)
        .with(reqwest_retry::RetryTransientMiddleware::new_with_policy(
            retry_policy,
        ))
        .build();

    log::info!("Loading SHA1 table...");
    let node2sha1 = Sha1Table::mmap(graph.num_nodes(), &args.node2sha1)
        .with_context(|| format!("Could not mmap {}", args.node2sha1.display()))?;

    log::info!("Initializing HTTP backends...");
    let http_backends = args
        .url
        .into_iter()
        .map(|url| {
            let (compression, url_pattern) = url.split_once(':').with_context(|| {
                format!("Missing URL prefix in {url}. Each URL must start with plain: or gzip:")
            })?;
            let compression = match compression {
                "plain" => http::Compression::None,
                "gzip" => http::Compression::Gzip,
                _ => bail!("Unsupported compression algorithm {compression}"),
            };
            http::HttpContentRetriever::new(
                &node2sha1,
                client.clone(),
                url_pattern.to_owned(),
                compression,
            )
            .with_context(|| format!("Could not build HttpContentRetriever for {url}"))
        })
        .collect::<Result<_>>()?;

    let content_retriever = NLayeredContentRetriever {
        backends: http_backends,
    };

    log::info!("Opening cache...");
    let cache = RocksdbContentCache::new_without_durable_writes(&graph, &args.db)
        .context("Could not load Rocksdb cache")?;

    let cache_cache = compute_cache_cache(&graph, &cache)
        .context("Could not load set of already cached contents")?;

    let thread_pl = thread_local::ThreadLocal::new();
    if args.swhids.is_empty() {
        let mut pl = concurrent_progress_logger!(
            display_memory = true,
            item_name = "content",
            local_speed = true,
        );
        pl.threshold(1000);
        pl.start("Downloading contents...");

        {
            let pl = &pl;
            futures::stream::iter(std::io::stdin().lines())
                .map(|line| line.context("Could not read line"))
                .try_for_each_concurrent(args.concurrent_downloads, |line| {
                    std::future::ready(
                        line.parse()
                            .with_context(|| format!("Invalid SWHID: {line}")),
                    )
                    .and_then(|swhid| {
                        download_swhid(&graph, &content_retriever, &cache, &cache_cache, swhid)
                            .inspect(|_| {
                                thread_pl
                                    .get_or(move || std::cell::RefCell::new(pl.clone()))
                                    .borrow_mut()
                                    .light_update()
                            })
                    })
                })
                .await?;
        }

        pl.done();
    } else {
        let file_paths: Vec<_> = args
            .swhids
            .iter()
            .map(|dir| {
                std::fs::read_dir(dir)
                    .with_context(|| format!("Could not list {}", dir.display()))?
                    .map(|dir_entry| {
                        Ok(dir_entry
                            .with_context(|| {
                                format!("Could not read dir entry in {}", dir.display())
                            })?
                            .path()
                            .to_owned())
                    })
                    .collect::<Result<Vec<_>>>()
            })
            .collect::<Result<Vec<_>>>()?
            .into_iter()
            .flatten()
            .collect();

        #[derive(serde::Deserialize)]
        #[allow(non_snake_case)]
        struct Row {
            SWHID: SWHID,
        }

        let get_readers = || {
            file_paths
                .iter()
                .map(|path| {
                    let file = std::fs::File::open(path)
                        .with_context(|| format!("Could not open {}", path.display()))?;
                    let decoder = zstd::stream::read::Decoder::new(file).with_context(|| {
                        format!("Could not read {} as zstd file", path.display())
                    })?;
                    Ok(csv::ReaderBuilder::new()
                        .has_headers(true)
                        .from_reader(decoder)
                        .into_deserialize()
                        .map(|row: Result<Row, _>| {
                            row.with_context(|| {
                                format!("Could not read row from {}", path.display())
                            })
                        }))
                })
                .collect::<Result<Vec<_>>>()
        };

        let mut pl = concurrent_progress_logger!(
            display_memory = true,
            item_name = "row",
            local_speed = true,
        );
        pl.threshold(1000);
        pl.start("Counting rows...");
        let num_lines = get_readers()?.into_iter().map(|file| file.count()).sum();
        pl.done();

        let mut pl = concurrent_progress_logger!(
            display_memory = true,
            item_name = "content",
            local_speed = true,
            expected_updates = Some(num_lines),
        );
        pl.threshold(1000);
        pl.start("Downloading contents...");

        {
            let pl = &pl;
            futures::stream::iter(get_readers()?.into_iter())
                .flat_map_unordered(None, futures::stream::iter) // interleave files
                .inspect(|_row: &Result<Row>| ()) // prevent unwieldy type errors
                .try_for_each_concurrent(args.concurrent_downloads, |Row { SWHID: swhid }| {
                    download_swhid(&graph, &content_retriever, &cache, &cache_cache, swhid).inspect(
                        |_| {
                            thread_pl
                                .get_or(move || std::cell::RefCell::new(pl.clone()))
                                .borrow_mut()
                                .light_update()
                        },
                    )
                })
                .await?;
        }
        pl.done();
    }

    Ok(())
}

// Builds an efficient of files that were already downloaded. It's faster to read the whole DB
// once here than to do random reads later.
fn compute_cache_cache<G: GraphWithFilenames + Send + Sync>(
    graph: G,
    cache: &RocksdbContentCache<G>,
) -> Result<EfDict> {
    let mut pl = concurrent_progress_logger!(
        log_target = "download_contents::compute_cache_cache",
        display_memory = true,
        item_name = "content",
        local_speed = true,
        expected_updates = Some(
            cache
                .estimate_num_cached_contents()
                .context("Could not estimate cache size")?
        ),
    );
    pl.start("Scanning already-downloaded contents...");

    let mut node_ids: Vec<_> = rocksdb_rayon::ParallelRocksdbKeyIterator::new(cache.db())
        .try_fold(
            || (pl.clone(), Vec::new()),
            |(mut pl, mut nodes), key| {
                let (_filename, node_id) = cache
                    .parse_key(&key)
                    .with_context(|| format!("Could not parse key {:?}", key))?;
                nodes.push(node_id);
                pl.light_update();
                Ok((pl, nodes))
            },
        )
        .map(|item: Result<_>| item.map(|(_pl, nodes)| nodes))
        .try_reduce(Vec::new, |mut nodes1, mut nodes2| {
            if nodes1.len() < nodes2.len() {
                (nodes1, nodes2) = (nodes2, nodes1);
            }
            nodes1.extend(nodes2);
            Ok(nodes1)
        })?
        .into_par_iter()
        .collect();
    pl.done();

    log::info!("Sorting node ids...");
    node_ids.radix_sort_unstable();

    log::info!("Building EliasFano...");
    let efb = EliasFanoConcurrentBuilder::new(node_ids.len(), graph.num_nodes());
    node_ids
        .into_par_iter()
        .enumerate()
        .for_each(|(index, node)| unsafe { efb.set(index, node) });

    Ok(efb.build_with_dict())
}

async fn download_swhid<G: GraphWithFilenames>(
    graph: &G,
    content_retriever: &impl ContentRetriever,
    cache: &RocksdbContentCache<impl GraphWithFilenames>,
    cache_cache: &EfDict,
    swhid: SWHID,
) -> Result<()> {
    // In a block_in_place block because this is a bottleneck causing the whole process
    // to be effectively single-threaded if the on-disk permutation is slow to access
    // (eg. FS-level compression) *and* the work is read-heavy (most contents are
    // already downloaded).
    let node_id = tokio::task::block_in_place(|| {
        graph
            .properties()
            .node_id(swhid)
            .with_context(|| format!("Unknown SWHID: {swhid}"))
    })?;

    if cache_cache.contains(node_id) {
        // already downloaded (faster than the check below because it fits in memory)
        return Ok(());
    }

    if cache
        .get(node_id)
        .await
        .with_context(|| format!("Could not check where {swhid} is in the cache"))?
        .is_some()
    {
        // already downloaded
        return Ok(());
    }

    let mut last_error = None;
    for _ in 0..10 {
        match content_retriever
            .get(node_id)
            .await
            .with_context(|| format!("Could not get {swhid}"))
        {
            Ok(Some(bytes)) => {
                cache
                    .set(node_id, &bytes)
                    .await
                    .with_context(|| format!("Could not write {swhid} to cache"))?;

                return Ok(());
            }
            Ok(None) => {
                if let Some(filename) = swh_contents::utils::get_sample_filename(graph, node_id) {
                    log::warn!(
                        "{swhid} ({}) is not in any backend",
                        String::from_utf8_lossy(&filename)
                    );
                } else {
                    log::warn!("{swhid} is not in any backend");
                }
                return Ok(());
            }
            Err(e) => {
                log::error!("Could not get {swhid}: {e:#}");
                tokio::time::sleep(Duration::from_secs(10)).await;
                last_error = Some(e);
            }
        }
    }
    log::error!(
        "Giving up download of {swhid}. Last error: {}",
        last_error.unwrap()
    );
    Ok(())
}
