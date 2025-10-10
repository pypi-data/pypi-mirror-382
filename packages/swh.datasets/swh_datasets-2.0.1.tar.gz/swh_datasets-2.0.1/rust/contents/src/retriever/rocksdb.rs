// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

//! Implementation of [`ContentRetriever`] that fetches from (and writes to) a local
//! [RocksDB](https://rocksdb.org/) cache

use std::path::Path;

use ::rocksdb::*;
use anyhow::{anyhow, ensure, Context, Result};
use bytes::Bytes;
use swh_graph::graph::{SwhGraphWithProperties, SwhLabeledBackwardGraph};
use swh_graph::properties;

use super::*;

fn get_options() -> Options {
    let mut options = Options::default();
    options.create_if_missing(true);
    options.optimize_for_point_lookup(100);

    // defaults to 2, which is not enough given the high compression level below.
    // Compaction is our bottleneck and RocksDB allocates half its background threads
    // to it, so we need twice as many background threads as CPU threads to use them
    // optimally.
    options.set_max_background_jobs((num_cpus::get() * 2).max(4) as i32);

    // See https://github.com/facebook/rocksdb/blob/b9957c991cae44959f96888369caf1b145398132/include/rocksdb/compression_type.h#L169
    // for the meaning of each compression setting.

    // Setting max_dict_bytes and zstd_max_train_bytes according to
    // https://rocksdb.org/blog/2021/05/31/dictionary-compression.html#user-api
    options.set_compression_type(DBCompressionType::Zstd);
    options.set_compression_options(
        0,      // window_bits, used only by zlib
        1,      // level
        0,      // strategy, used only by zlib
        16_000, // max_dict_bytes
    );
    options.set_zstd_max_train_bytes(16_000 * 100);

    // compress the bottommost level with better (and slower) compression
    options.set_bottommost_compression_type(DBCompressionType::Zstd); // redundant?
    options.set_bottommost_compression_options(
        0,       // window_bits, used only by zlib
        19,      // level
        0,       // strategy, used only by zlib
        512_000, // max_dict_bytes
        true,    // enabled
    );
    options.set_bottommost_zstd_max_train_bytes(
        512_000 * 100,
        true, // enabled
    );

    //  options.set_allow_mmap_reads(true);
    //  options.set_allow_mmap_writes(true);

    options
}

/// Shorthand for [`SwhLabeledBackwardGraph`]
/// + [`SwhGraphWithProperties`]`<Maps: properties::Maps, LabelNames: properties::LabelNames>`
pub trait GraphWithFilenames:
    SwhLabeledBackwardGraph
    + SwhGraphWithProperties<Maps: properties::Maps, LabelNames: properties::LabelNames>
{
}

impl<
        G: SwhLabeledBackwardGraph
            + SwhGraphWithProperties<Maps: properties::Maps, LabelNames: properties::LabelNames>,
    > GraphWithFilenames for G
{
}

/// Implementation of [`ContentRetriever`] that fetches from a local [RocksDB](https://rocksdb.org/) cache
/// but does not write to it.
///
/// See [`RocksdbContentCache`] for a read-write implementation and an example of how to initialize
/// it.
pub struct ReadonlyRocksdbContentCache<G: GraphWithFilenames> {
    graph: G,
    db: DBWithThreadMode<MultiThreaded>,
}

impl<G: GraphWithFilenames> ReadonlyRocksdbContentCache<G> {
    pub fn new(graph: G, path: impl AsRef<Path>) -> Result<Self> {
        let path = path.as_ref();
        let options = get_options();
        let db = DBWithThreadMode::open_cf_with_opts_for_read_only(
            &options.clone(),
            path,
            [("default", options)], // column family options
            false,                  // error_if_log_file_exist
        )
        .with_context(|| format!("Could not open {}", path.display()))?;

        Ok(Self { graph, db })
    }

    /// Returns if the node_id may be in the database
    ///
    /// `true` means the node_id may be in the database, `false` means it is not
    pub fn may_have(&self, node_id: NodeId) -> bool {
        tokio::task::block_in_place(|| self.db.key_may_exist(self.compute_key(node_id)))
    }

    pub fn db(&self) -> &::rocksdb::DBWithThreadMode<impl ::rocksdb::ThreadMode> {
        &self.db
    }

    pub fn estimate_num_cached_contents(&self) -> Result<usize> {
        self.db
            .property_value(::rocksdb::properties::ESTIMATE_NUM_KEYS)
            .context("Could not get ESTIMATE_NUM_KEYS")?
            .ok_or(anyhow!("ESTIMATE_NUM_KEYS property does not exist"))?
            .parse()
            .context("ESTIMATE_NUM_KEYS value is not an integer")
    }

    /// Given a NodeId, returns its key in the database.
    ///
    /// This is implemented as the concatenation of the reversed file name of the node_id
    /// followed by the node_id in big endian.
    ///
    /// The rationale for this key is:
    ///
    /// 1. [Boffa et al. 2025](https://www.sciencedirect.com/science/article/pii/S0164121225000974)
    ///    tell us that clustering by reversed "most popular file name" produces excellent
    ///    compression ratios.
    ///    Here we use only one file name (and pick it deterministically), because it would
    ///    be expensive in I/O and compute to exhaustively list the file names for very
    ///    littly gain as very few files have more than one name.
    /// 2. Using big-endian so the lexicographic order of bytes matches the numeric order.
    ///    As LLP orders graph-wise similar nodes next to each other, this should
    ///    increase compression ratio by clustering content-wise similar nodes together.
    pub fn compute_key(&self, node_id: NodeId) -> Box<[u8]> {
        let encoded_node_id = node_id.to_be_bytes();

        match crate::utils::get_sample_filename(&self.graph, node_id) {
            Some(file_name) => {
                let mut file_name = Vec::from(file_name);
                file_name.reverse();
                file_name.push(0);
                file_name.extend(encoded_node_id);
                file_name.into()
            }
            None => encoded_node_id.into(),
        }
    }

    /// The opposite of [`compute_key`](Self::compute_key): returns the node id
    /// and **reversed** filename in a key
    pub fn parse_key<'a>(&self, key: &'a [u8]) -> Result<(&'a [u8], NodeId)> {
        let end = key.len();
        let node_id = NodeId::from_be_bytes(
            key[end - 8..]
                .try_into()
                .context("Malformed key: too short")?,
        );
        ensure!(
            key[end - 8] == 0,
            "Malformed key: no null byte before the node id"
        );
        let filename = &key[0..end - 8];
        Ok((filename, node_id))
    }
}

impl<G: GraphWithFilenames> ContentRetriever for ReadonlyRocksdbContentCache<G> {
    type GetError = ::rocksdb::Error;

    async fn get(&self, node_id: NodeId) -> Result<Option<Bytes>, Self::GetError> {
        tokio::task::block_in_place(|| {
            self.db
                .get(self.compute_key(node_id))
                .map(|bytes| bytes.map(Into::into))
        })
    }

    async fn get_pinned(
        &self,
        node_id: NodeId,
    ) -> Result<Option<impl AsRef<[u8]> + '_>, Self::GetError> {
        tokio::task::block_in_place(|| self.db.get_pinned(self.compute_key(node_id)))
    }
}

/// Implementation of [`ContentRetriever`] that fetches from (and writes to) a local
/// [RocksDB](https://rocksdb.org/) cache.
///
/// See [`ReadonlyRocksdbContentCache`] for a read-only implementation.
///
/// # Example
///
/// ```
/// use anyhow::Context;
/// use swh_contents::retriever::rocksdb::RocksdbContentCache;
/// use crate::swh_contents::retriever::{ContentCache, ContentRetriever};
/// use swh_graph::graph::SwhBidirectionalGraph;
/// use swh_graph::mph::DynMphf;
/// # use swh_graph::swhid;
///
/// # #[tokio::main]
/// # async fn f() -> Result<(), anyhow::Error> {
///
/// # let graph_path = std::path::PathBuf::from(".");
/// # || Ok::<(), anyhow::Error>({
/// let graph = SwhBidirectionalGraph::new(&graph_path)
///     .context("Could not load graph")?
///     .load_labels()
///     .context("Could not load graph labels")?
///     .init_properties()
///     .load_properties(|properties| properties.load_maps::<DynMphf>())
///     .context("Could not load maps")?
///     .load_properties(|properties| properties.load_label_names())
///     .context("Could not load label names")?;
/// # });
/// # let mut builder = swh_graph::graph_builder::GraphBuilder::default();
/// # builder.node(swhid!(swh:1:cnt:0000000000000000000000000000000000000001)).unwrap().done();
/// # builder.node(swhid!(swh:1:cnt:0000000000000000000000000000000000000002)).unwrap().done();
/// # builder.node(swhid!(swh:1:cnt:0000000000000000000000000000000000000003)).unwrap().done();
/// # builder.node(swhid!(swh:1:cnt:0000000000000000000000000000000000000004)).unwrap().done();
/// # builder.arc(0, 1);
/// # builder.arc(2, 3);
/// # let graph = builder.done().unwrap();
///
/// let db_dir = tempfile::tempdir().unwrap();
/// let cache = RocksdbContentCache::new_without_durable_writes(&graph, db_dir.path())
///     .context("Could not load Rocksdb cache")?;
///
/// assert_eq!(cache.get(2).await, Ok(None));
/// cache.set(2, b"content bytes").await.context("Could not add content to cache")?;
/// assert_eq!(cache.get(2).await, Ok(Some(b"content bytes".as_ref().into())));
///
/// Ok(())
///
/// # }
/// # f().unwrap();
/// ```
pub struct RocksdbContentCache<G: GraphWithFilenames> {
    inner: ReadonlyRocksdbContentCache<G>,
    write_options: ::rocksdb::WriteOptions,
}

impl<G: GraphWithFilenames> RocksdbContentCache<G> {
    pub fn new(graph: G, path: impl AsRef<Path>) -> Result<Self> {
        let path = path.as_ref();
        let options = get_options();
        let db = DBWithThreadMode::open_cf_with_opts(
            &options.clone(),
            path,
            [("default", options)], // column family options
        )
        .with_context(|| format!("Could not open {}", path.display()))?;
        let mut write_options = ::rocksdb::WriteOptions::default();
        write_options.set_sync(true);
        write_options.disable_wal(false);

        Ok(Self {
            inner: ReadonlyRocksdbContentCache { graph, db },
            write_options,
        })
    }

    /// Makes writes faster than [`new`](Self::new), but they may be lost in case
    /// of system crash or power outage
    pub fn new_without_durable_writes(graph: G, path: impl AsRef<Path>) -> Result<Self> {
        let path = path.as_ref();
        let mut options = get_options();
        options.set_manual_wal_flush(true);

        let db = DBWithThreadMode::open_cf_with_opts(
            &options.clone(),
            path,
            [("default", options)], // column family options
        )
        .with_context(|| format!("Could not open {}", path.display()))?;

        let mut write_options = ::rocksdb::WriteOptions::default();
        write_options.set_sync(false);
        write_options.disable_wal(true);

        Ok(Self {
            inner: ReadonlyRocksdbContentCache { graph, db },
            write_options,
        })
    }

    /// Returns if the node_id may be in the database
    ///
    /// `true` means the node_id may be in the database, `false` means it is not
    #[inline(always)]
    pub fn may_have(&self, node_id: NodeId) -> bool {
        self.inner.may_have(node_id)
    }

    pub fn db(&self) -> &::rocksdb::DBWithThreadMode<impl ::rocksdb::ThreadMode> {
        self.inner.db()
    }

    /// See [`ReadonlyRocksdbContentCache::compute_key`]
    pub fn compute_key(&self, node_id: NodeId) -> Box<[u8]> {
        self.inner.compute_key(node_id)
    }

    /// See [`ReadonlyRocksdbContentCache::parse_key`]
    pub fn parse_key<'a>(&self, key: &'a [u8]) -> Result<(&'a [u8], NodeId)> {
        self.inner.parse_key(key)
    }

    /// See [`ReadonlyRocksdbContentCache::estimate_num_cached_contents`]
    pub fn estimate_num_cached_contents(&self) -> Result<usize> {
        self.inner.estimate_num_cached_contents()
    }
}

impl<G: GraphWithFilenames> ContentRetriever for RocksdbContentCache<G> {
    type GetError = ::rocksdb::Error;

    #[inline(always)]
    async fn get(&self, node_id: NodeId) -> Result<Option<Bytes>, Self::GetError> {
        self.inner.get(node_id).await
    }

    #[inline(always)]
    async fn get_pinned(
        &self,
        node_id: NodeId,
    ) -> Result<Option<impl AsRef<[u8]> + '_>, Self::GetError> {
        self.inner.get_pinned(node_id).await
    }
}
impl<G: GraphWithFilenames> ContentCache for RocksdbContentCache<G> {
    type SetError = ::rocksdb::Error;
    async fn set(&self, node_id: NodeId, bytes: &[u8]) -> Result<(), Self::GetError> {
        tokio::task::block_in_place(|| {
            self.inner
                .db
                .put_opt(self.inner.compute_key(node_id), bytes, &self.write_options)
        })
    }
}
