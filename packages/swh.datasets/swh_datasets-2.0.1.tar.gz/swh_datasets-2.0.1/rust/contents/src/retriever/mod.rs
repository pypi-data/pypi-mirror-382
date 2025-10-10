// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

//! Provides access to the bytes of a content node from its node id in the graph

use std::error::Error;
use std::future::Future;

use anyhow::Result;
use bytes::Bytes;
use either::Either;
use thiserror::Error;

pub mod http;
pub mod rocksdb;

type NodeId = usize;

/// Interface for a read-only backend that stores contents addressed by node id
pub trait ContentRetriever {
    type GetError: Error + Send + Sync + 'static;

    /// Returns the bytes of the Content identified by the node_id, or `None` if the content
    /// is not found.
    fn get(&self, node_id: NodeId) -> impl Future<Output = Result<Option<Bytes>, Self::GetError>>;

    /// Same as [`Self::get`] but avoids a copy if possible.
    ///
    /// The default implementation is equivalent to [`Self::get`], but some (such as
    /// [`RocksdbContentCache`](rocksdb::RocksdbContentCache) borrow from an in-memory buffer
    /// instead.
    fn get_pinned(
        &self,
        node_id: NodeId,
    ) -> impl Future<Output = Result<Option<impl AsRef<[u8]> + '_>, Self::GetError>> {
        self.get(node_id)
    }
}

/// Interface for a read-write backend that stores contents addressed by node id
///
/// This is a writable subtrait of [`ContentRetriever`].
pub trait ContentCache: ContentRetriever {
    type SetError: Error + Send + Sync + 'static;

    fn set(&self, node_id: NodeId, data: &[u8])
        -> impl Future<Output = Result<(), Self::SetError>>;
}

/// Implementation of [`ContentRetriever`] that wraps two backends of different types;
/// sending requests to primary and falling back to the secondary
///
/// Use [`CachedContentRetriever`] if the primary is a writable cache.
pub struct LayeredContentRetriever<Primary: ContentRetriever, Secondary: ContentRetriever> {
    pub primary: Primary,
    pub secondary: Secondary,
}

#[derive(Error, Debug, PartialEq, Eq)]
/// Error returned by [`LayeredContentRetriever`]
pub enum LayeredError<PrimaryError: Error, SecondaryError: Error> {
    #[error("Could not read from primary backend: {0}")]
    Primary(PrimaryError),
    #[error("Could not read from secondary backend: {0}")]
    Secondary(SecondaryError),
}

macro_rules! LayeredContentRetriever_get {
    ($self:expr, $get:ident, $node_id:expr, $to_primary:expr, $to_secondary:expr) => {{
        match $self.primary.$get($node_id).await {
            Ok(Some(content)) => return Ok(Some($to_primary(content))),
            Ok(None) => (), // not found, fall back to secondary
            Err(e) => {
                let e = anyhow::Error::from(e);
                if let Some(&http::HttpRetrieverError::Zeroed) = e.downcast_ref() {
                    // known issue (https://gitlab.softwareheritage.org/swh/meta/-/issues/5034),
                    // fall back to secondary
                } else {
                    return Err(LayeredError::Primary(
                        e.downcast().expect("could not re-downcast exception"),
                    ));
                }
            }
        }

        $self
            .secondary
            .get($node_id)
            .await
            .map(|opt| opt.map($to_secondary))
            .map_err(LayeredError::Secondary)
    }};
}

impl<Primary: ContentRetriever, Secondary: ContentRetriever> ContentRetriever
    for LayeredContentRetriever<Primary, Secondary>
{
    type GetError = LayeredError<Primary::GetError, Secondary::GetError>;

    async fn get(&self, node_id: NodeId) -> Result<Option<Bytes>, Self::GetError> {
        LayeredContentRetriever_get!(self, get, node_id, |bytes| bytes, |bytes| bytes)
    }

    async fn get_pinned(
        &self,
        node_id: NodeId,
    ) -> Result<Option<impl AsRef<[u8]> + '_>, Self::GetError> {
        LayeredContentRetriever_get!(self, get_pinned, node_id, Either::Left, Either::Right)
    }
}

/// Implementation of [`ContentRetriever`] that wraps multiple backends of the same type;
/// sending requests in order.
///
/// Use [`CachedContentRetriever`] if the primary is a writable cache.
pub struct NLayeredContentRetriever<Backend: ContentRetriever> {
    pub backends: Vec<Backend>,
}

macro_rules! NLayeredContentRetriever_get {
    ($self:expr, $get:ident, $node_id:expr) => {{
        for backend in &$self.backends {
            match backend.$get($node_id).await {
                Ok(Some(content)) => return Ok(Some(content)),
                Ok(None) => (), // not found, fall back to next backend
                Err(e) => {
                    let e = anyhow::Error::from(e);
                    if let Some(&http::HttpRetrieverError::Zeroed) = e.downcast_ref() {
                        // known issue (https://gitlab.softwareheritage.org/swh/meta/-/issues/5034),
                        // fall back to next backend
                    } else {
                        return Err(e.downcast().expect("could not re-downcast exception"));
                    }
                }
            }
        }
        Ok(None)
    }};
}

impl<Backend: ContentRetriever> ContentRetriever for NLayeredContentRetriever<Backend> {
    type GetError = Backend::GetError;

    async fn get(&self, node_id: NodeId) -> Result<Option<Bytes>, Self::GetError> {
        NLayeredContentRetriever_get!(self, get, node_id)
    }

    async fn get_pinned(
        &self,
        node_id: NodeId,
    ) -> Result<Option<impl AsRef<[u8]> + '_>, Self::GetError> {
        NLayeredContentRetriever_get!(self, get_pinned, node_id)
    }
}

/// Implementation of [`ContentRetriever`] that can store data in a cache.
///
/// Use [`LayeredContentRetriever`] instead if the cache is ready-only.
pub struct CachedContentRetriever<Cache: ContentRetriever, Backend: ContentRetriever> {
    cache: Cache,
    backend: Backend,
}

#[derive(Error, Debug, PartialEq, Eq)]
/// Error returned by [`CachedContentRetriever`]
pub enum CacheError<GetCacheError: Error, SetCacheError: Error, GetBackendError: Error> {
    #[error("Could not read cache: {0}")]
    GetCache(GetCacheError),
    #[error("Could not write cache: {0}")]
    SetCache(SetCacheError),
    #[error("Could not read backend : {0}")]
    GetBackend(GetBackendError),
}

impl<Cache: ContentCache, Backend: ContentRetriever> CachedContentRetriever<Cache, Backend> {
    pub fn new(cache: Cache, backend: Backend) -> Result<Self> {
        Ok(Self { cache, backend })
    }
}

macro_rules! CachedContentRetriever_get {
    ($self:expr, $get:ident, $node_id:expr, $to_primary:expr, $to_secondary:expr) => {{
        if let Some(content) = $self
            .cache
            .$get($node_id)
            .await
            .map_err(CacheError::GetCache)?
        {
            return Ok(Some($to_primary(content)));
        }

        let Some(content) = $self
            .backend
            .$get($node_id)
            .await
            .map_err(CacheError::GetBackend)?
        else {
            return Ok(None);
        };
        $self
            .cache
            .set($node_id, content.as_ref())
            .await
            .map_err(CacheError::SetCache)?;
        Ok(Some($to_secondary(content)))
    }};
}

impl<Cache: ContentCache, Backend: ContentRetriever> ContentRetriever
    for CachedContentRetriever<Cache, Backend>
{
    type GetError = CacheError<Cache::GetError, Cache::SetError, Backend::GetError>;

    async fn get(&self, node_id: NodeId) -> Result<Option<Bytes>, Self::GetError> {
        CachedContentRetriever_get!(self, get, node_id, |bytes| bytes, |bytes| bytes)
    }

    async fn get_pinned(
        &self,
        node_id: NodeId,
    ) -> Result<Option<impl AsRef<[u8]> + '_>, Self::GetError> {
        CachedContentRetriever_get!(self, get_pinned, node_id, Either::Left, Either::Right)
    }
}
