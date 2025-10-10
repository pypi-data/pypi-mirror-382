// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

//! Allows getting the SHA1 of a node given its node id
//!
//! This allows fetching content bytes from SWH's object storages.

use std::borrow::Borrow;
use std::io::Write;
use std::path::Path;

use anyhow::{ensure, Context, Result};
use bytemuck::TransparentWrapper;
use mmap_rs::{Mmap, MmapFlags};

#[cfg(feature = "build")]
pub mod build;

/// Number of bytes in a SHA1 digest
pub const SHA1_SIZE: usize = 20;

#[derive(Copy, Clone, Debug, Eq, PartialEq, Ord, PartialOrd, TransparentWrapper)]
/// A single SHA1 digest
#[repr(transparent)]
pub struct Sha1(pub [u8; SHA1_SIZE]);

impl TryFrom<&[u8]> for Sha1 {
    type Error = std::array::TryFromSliceError;

    fn try_from(v: &[u8]) -> Result<Self, Self::Error> {
        v.try_into().map(Sha1)
    }
}

impl From<[u8; SHA1_SIZE]> for Sha1 {
    fn from(v: [u8; SHA1_SIZE]) -> Self {
        Sha1(v)
    }
}

impl From<Sha1> for [u8; SHA1_SIZE] {
    fn from(v: Sha1) -> Self {
        v.0
    }
}

impl Borrow<[u8; SHA1_SIZE]> for Sha1 {
    fn borrow(&self) -> &[u8; SHA1_SIZE] {
        &self.0
    }
}

impl Borrow<[u8]> for Sha1 {
    fn borrow(&self) -> &[u8] {
        &self.0
    }
}

impl Sha1 {
    pub fn hex_string(&self) -> String {
        faster_hex::hex_string(&self.0)
    }
}

#[derive(Clone, Debug)]
/// Maps [`swh-graph`](::swh_graph) node ids to SHA1 hashes
pub struct Sha1Table<D: AsRef<[u8]>> {
    num_nodes: usize,
    data: D,
}

impl Sha1Table<Mmap> {
    pub fn mmap(num_nodes: usize, path: impl AsRef<Path>) -> Result<Self> {
        let path = path.as_ref();
        let file_len = path
            .metadata()
            .with_context(|| format!("Could not stat {}", path.display()))?
            .len();
        ensure!(
            u64::try_from(num_nodes * SHA1_SIZE).expect("num_nodes overflowed u64") == file_len,
            "Unexpected file length ({file_len}) for Sha1Table with {num_nodes} nodes"
        );
        let file = std::fs::File::open(path)
            .with_context(|| format!("Could not open {}", path.display()))?;
        let data = unsafe {
            mmap_rs::MmapOptions::new(file_len as _)
                .context("Could not initialize mmap")?
                .with_flags(MmapFlags::TRANSPARENT_HUGE_PAGES | MmapFlags::RANDOM_ACCESS)
                .with_file(&file, 0)
                .map()
                .with_context(|| format!("Could not mmap {}", path.display()))?
        };

        Ok(Sha1Table { num_nodes, data })
    }
}

impl<D: AsRef<[u8]>> Sha1Table<D> {
    /// Returns the SHA1 associated with the given node id, or `None` if the node
    /// does not exist, is not a content node, or does not have a known SHA1
    pub fn get(&self, node_id: usize) -> Option<Sha1> {
        if node_id >= self.num_nodes {
            return None;
        }
        let sha1 = self.data.as_ref()[node_id * SHA1_SIZE..(node_id + 1) * SHA1_SIZE]
            .try_into()
            .expect("Sha1 does not have length SHA1_SIZE");
        if sha1 == [0u8; SHA1_SIZE] {
            None
        } else {
            Some(Sha1(sha1))
        }
    }

    pub fn dump(&self, path: impl AsRef<Path>) -> Result<()> {
        let path = path.as_ref();

        let mut file = std::fs::File::create(path)
            .with_context(|| format!("Could not create {}", path.display()))?;
        file.write_all(self.data.as_ref())
            .with_context(|| format!("Could not write to {}", path.display()))?;

        Ok(())
    }
}
