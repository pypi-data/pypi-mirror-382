// Copyright (C) 2023-2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

//! Reads ORC files to build a [`Sha1Table`] mapping [`swh-graph`](::swh_graph) node ids to SHA1 hashes

use std::fs::{DirEntry, File};
use std::path::Path;

use anyhow::{Context, Result};
use ar_row::deserialize::{ArRowDeserialize, ArRowStruct};
use ar_row::{
    arrow::array::RecordBatch, arrow::datatypes::DataType, arrow::record_batch::RecordBatchReader,
};
use ar_row_derive::ArRowDeserialize;
use crossbeam::atomic::AtomicCell;
use dsi_progress_logger::{concurrent_progress_logger, ProgressLog};
use orc_rust::arrow_reader::ArrowReaderBuilder;
use orc_rust::projection::ProjectionMask;
use orc_rust::reader::ChunkReader;
use rayon::prelude::*;
use swh_graph::graph::{SwhGraph, SwhGraphWithProperties};
use swh_graph::properties;
use swh_graph::views::Subgraph;
use swh_graph::{NodeType, SWHID};

use super::{Sha1Table, SHA1_SIZE};

const ORC_BATCH_SIZE: usize = 1024;

fn list_orc_files(dir: impl AsRef<Path>) -> Result<Vec<DirEntry>> {
    let dir = dir.as_ref();
    log::info!("Listing .orc files");
    std::fs::read_dir(dir)
        .with_context(|| format!("Could not stat directory {}", dir.display()))?
        .map(|entry| Ok(entry?))
        .collect::<Result<_>>()
        .with_context(|| format!("Could not stat {} entry", dir.display()))
}

fn open_orc_files(dir: impl AsRef<Path>) -> Result<Vec<ArrowReaderBuilder<File>>> {
    let dir = dir.as_ref();
    let paths = list_orc_files(dir).with_context(|| format!("Could not list {}", dir.display()))?;
    log::info!("Opening ORC files");
    paths
        .into_par_iter()
        .map(|entry| {
            let path = entry.path();
            let file =
                File::open(&path).with_context(|| format!("Could not open {}", path.display()))?;
            let builder = ArrowReaderBuilder::try_new(file)
                .with_context(|| format!("Could not read {}", path.display()))?;
            Ok(builder)
        })
        .collect()
}

pub fn iter_arrow<R: ChunkReader, T, U, F>(
    reader_builder: ArrowReaderBuilder<R>,
    mut f: F,
) -> impl Iterator<Item = U>
where
    F: FnMut(T) -> U,
    T: ArRowDeserialize + ArRowStruct,
{
    let field_names = <T>::columns();
    let projection = ProjectionMask::named_roots(
        reader_builder.file_metadata().root_data_type(),
        field_names.as_slice(),
    );
    let reader_builder = reader_builder
        .with_projection(projection.clone())
        .with_batch_size(ORC_BATCH_SIZE);

    let reader = reader_builder.build();

    T::check_datatype(&DataType::Struct(reader.schema().fields().clone()))
        .expect("Invalid data type in ORC file");

    reader.flat_map(move |chunk| {
        let chunk: RecordBatch = chunk.unwrap_or_else(|e| panic!("Could not read chunk: {e}"));
        let items: Vec<T> = T::from_record_batch(chunk).expect("Could not deserialize from arrow");
        items.into_iter().map(&mut f).collect::<Vec<_>>()
    })
}

pub fn build_sha1_table<G: SwhGraphWithProperties<Maps: properties::Maps> + Sync>(
    graph: G,
    dataset: impl AsRef<Path>,
    include_skipped_contents: bool,
) -> Result<Sha1Table<Box<[u8]>>> {
    let dataset = dataset.as_ref();
    let mut reader_builders =
        open_orc_files(dataset.join("content")).context("Could not open content/ ORC files")?;
    if include_skipped_contents {
        reader_builders.extend(
            open_orc_files(dataset.join("skipped_content"))
                .context("Could not open skipped_content/ ORC files")?,
        );
    }

    #[derive(ArRowDeserialize, Default, Clone)]
    struct Content {
        sha1: Option<String>,
        sha1_git: Option<String>,
    }

    let num_nodes = graph.num_nodes();

    log::info!("Initializing table...");
    let sha1s: Vec<_> = (0..num_nodes)
        .into_par_iter()
        .map(|_| AtomicCell::new([0; SHA1_SIZE]))
        .collect();

    let mut pl = concurrent_progress_logger!(
        display_memory = true,
        item_name = "node",
        local_speed = true,
        expected_updates = Some(
            Subgraph::with_node_constraint(&graph, "cnt".parse().unwrap())
                .actual_num_nodes()
                .unwrap_or(graph.num_nodes())
        ),
    );
    pl.start("Reading ORC dataset and building sha1 table");

    // not using reader_builders.into_par_iter() because Rayon does not give work to some threads
    // (it probably does not divide the small iterator into one-item chunks for each thread)
    std::thread::scope(|s| {
        reader_builders
            .into_iter()
            .map(|reader_builder| -> std::thread::ScopedJoinHandle<_> {
                let mut pl = pl.clone();
                let graph = &graph;
                let sha1s = &sha1s;
                s.spawn(move || -> Result<()> {
                    iter_arrow(reader_builder, |cnt: Content| {
                        pl.light_update();
                        if let Some(sha1_git) = cnt.sha1_git {
                            if let Some(sha1) = cnt.sha1 {
                                let mut buf = [0u8; SHA1_SIZE];

                                faster_hex::hex_decode(sha1_git.as_bytes(), &mut buf)
                                    .with_context(|| {
                                        format!("Invalid hex string as sha1_git: {sha1_git}")
                                    })?;
                                let sha1_git = buf;

                                faster_hex::hex_decode(sha1.as_bytes(), &mut buf).with_context(
                                    || format!("Invalid hex string as sha1_git: {sha1}"),
                                )?;
                                let sha1 = buf;

                                let swhid = SWHID {
                                    namespace_version: 1,
                                    node_type: NodeType::Content,
                                    hash: sha1_git,
                                };
                                let node =
                                    graph.properties().node_id(swhid).with_context(|| {
                                        format!("{swhid} is in an ORC file but not in the graph")
                                    })?;
                                sha1s[node].store(sha1);
                            }
                        }
                        Ok(())
                    })
                    .collect::<Result<()>>()
                })
            })
            .collect::<Vec<_>>() // spawn all the threads
            .into_iter() // then wait for them
            .try_for_each(|thread| thread.join().expect("Could not join thread"))
    })?;

    pl.done();

    // Compiled to a no-op
    let sha1s = sha1s
        .into_iter()
        .map(|sha1: AtomicCell<[u8; SHA1_SIZE]>| sha1.into_inner())
        .collect();

    Ok(Sha1Table {
        num_nodes,
        data: bytemuck::allocation::cast_slice_box(sha1s),
    })
}
