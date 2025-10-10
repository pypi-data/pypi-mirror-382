// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

//! Implementation of [`ContentRetriever`] that queries contents by HTTP

use std::io::Read;
use std::time::{Duration, SystemTime};

use anyhow::{Context, Result};
use bytes::Bytes;
use thiserror::Error;

use super::*;
use crate::sha1::Sha1Table;

#[derive(Clone, Copy, Debug)]
pub enum Compression {
    None,
    Gzip,
}

#[derive(Error, Debug)]
pub enum HttpRetrieverError {
    #[error("{0}")]
    Reqwest(#[from] reqwest::Error),
    #[error("{0}")]
    ReqwestMiddleware(#[from] reqwest_middleware::Error),
    #[error("Could not decompress content: {0}")]
    Decompression(anyhow::Error),
    #[error("Retrieved an entirely zeroed file, which not valid gzipped content.")]
    Zeroed,
}

/// Implementation of [`ContentRetriever`] that queries contents by HTTP
///
/// `url_pattern` must be a URL with `{sha1}` placeholder.
///
/// We recommend you initialize its client this way:
///
/// ```
/// let client = reqwest::Client::builder()
///     .user_agent(format!(
///         "{}/{}",
///         env!("CARGO_PKG_NAME"),
///         env!("CARGO_PKG_VERSION"),
///     ))
///     .build()
///     .expect("Could not build HTTP client");
///
/// // Wrap client in retry middleware
/// let retry_policy =
///     reqwest_retry::policies::ExponentialBackoff::builder().build_with_max_retries(10);
/// let client = reqwest_middleware::ClientBuilder::new(client)
///     .with(swh_contents::retriever::http::Http429Middleware)
///     .with(reqwest_retry::RetryTransientMiddleware::new_with_policy(
///         retry_policy,
///     ))
///     .build();
/// ```
pub struct HttpContentRetriever<'a, D: AsRef<[u8]>> {
    node2sha1: &'a Sha1Table<D>,
    client: reqwest_middleware::ClientWithMiddleware,
    url_pattern: String,
    compression: Compression,
    authorization_string: Option<reqwest::header::HeaderValue>,
}

impl<'a, D: AsRef<[u8]>> HttpContentRetriever<'a, D> {
    pub fn new(
        node2sha1: &'a Sha1Table<D>,
        client: reqwest_middleware::ClientWithMiddleware,
        url_pattern: String,
        compression: Compression,
    ) -> Result<Self> {
        let authorization_string =
            if url_pattern.starts_with("https://archive.softwareheritage.org/") {
                std::env::var("SWH_AUTH_TOKEN")
                    .map(|auth_token| {
                        log::info!("Using $SWH_AUTH_TOKEN");
                        format!("Bearer {auth_token}")
                            .try_into()
                            .expect("Could not build Authorization header")
                    })
                    .ok()
            } else {
                None
            };
        Ok(Self {
            node2sha1,
            client,
            url_pattern,
            compression,
            authorization_string,
        })
    }
}

impl<D: AsRef<[u8]>> ContentRetriever for HttpContentRetriever<'_, D> {
    type GetError = HttpRetrieverError;

    async fn get(&self, node_id: NodeId) -> Result<Option<Bytes>, Self::GetError> {
        let Some(sha1) = self.node2sha1.get(node_id) else {
            return Ok(None);
        };
        let url = self.url_pattern.replace("{sha1}", &sha1.hex_string());
        let mut request = self
            .client
            .get(&url)
            .build()
            .expect("Could not build request");
        if let Some(authorization_string) = &self.authorization_string {
            request
                .headers_mut()
                .insert("Authorization", authorization_string.clone());
        }
        let response = self.client.execute(request).await?;
        if response.status() == reqwest::StatusCode::NOT_FOUND {
            return Ok(None);
        }
        let response = response.error_for_status()?;
        assert!(
            response.status().is_success(),
            "HTTP response is neither error nor success: {:?}",
            response
        );
        let mut bytes = response.bytes().await?;
        match self.compression {
            Compression::None => (),
            Compression::Gzip => {
                let mut decompressed_bytes = Vec::with_capacity(bytes.len());
                let mut decoder = flate2::read::GzDecoder::new(std::io::Cursor::new(&bytes));
                decoder.read_to_end(&mut decompressed_bytes).map_err(|e| {
                    if bytes.iter().all(|&byte| byte == 0) {
                        // https://gitlab.softwareheritage.org/swh/meta/-/issues/5034
                        log::warn!("{url} is {} null bytes", bytes.len());
                        HttpRetrieverError::Zeroed
                    } else {
                        HttpRetrieverError::Decompression(
                            Err::<(), _>(e)
                                .with_context(|| format!("Could not decompress {url} as gzip"))
                                .unwrap_err(),
                        )
                    }
                })?;
                bytes = decompressed_bytes.into_boxed_slice().into();
            }
        }

        Ok(Some(bytes))
    }
}

/// On 429 response, pauses download for the duration implied by `X-RateLimit-Reset`.
pub struct Http429Middleware;

#[async_trait::async_trait]
impl reqwest_middleware::Middleware for Http429Middleware {
    async fn handle(
        &self,
        req: reqwest::Request,
        extensions: &mut ::http::Extensions,
        next: reqwest_middleware::Next<'_>,
    ) -> Result<reqwest::Response, reqwest_middleware::Error> {
        loop {
            let response = {
                let Some(req) = req.try_clone() else {
                    log::warn!("Could not clone 'req'. 429 retry disabled.");
                    return next.run(req, extensions).await;
                };
                next.clone().run(req, extensions).await?
            };

            if response.status() == reqwest::StatusCode::TOO_MANY_REQUESTS {
                let Some(ratelimit_reset_at) = response.headers().get("X-RateLimit-Reset") else {
                    // missing header
                    return Ok(response);
                };
                let ratelimit_reset_at = ratelimit_reset_at.to_str().with_context(|| {
                    format!("Non-UTF8 X-RateLimit-Reset value: {ratelimit_reset_at:?}")
                })?;
                let ratelimit_reset_at = ratelimit_reset_at.parse().with_context(|| {
                    format!("Invalid X-RateLimit-Reset value: {ratelimit_reset_at}")
                })?;
                let sleep_duration = Duration::from_secs(ratelimit_reset_at)
                    .saturating_sub(
                        SystemTime::now()
                            .duration_since(SystemTime::UNIX_EPOCH)
                            .unwrap(),
                    )
                    .max(Duration::from_secs(0)); // avoid negative sleep

                // avoid busy wait in case of desynchronised clocks
                let sleep_duration = sleep_duration + Duration::from_secs(1);

                log::info!(
                    "Got 429 on {}, sleeping for {:?}",
                    req.url(),
                    sleep_duration
                );
                tokio::time::sleep(sleep_duration).await;
            } else {
                return Ok(response);
            }
        }
    }
}
