// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use swh_graph::graph_builder::{BuiltGraph, GraphBuilder};
use swh_graph::swhid;

use swh_graph_contributions::impact::*;

#[test]
fn test_parse_iso_date_range() {
    assert!(parse_iso_date_range("".into()).is_err());
    assert!(parse_iso_date_range("2022".into()).is_err());
    assert_eq!(
        parse_iso_date_range("2025-05-27".into()).map_err(|_| ()),
        Ok(Timestamp(1748304000)..Timestamp(1748304000 + 86400))
    );
    assert_eq!(
        parse_iso_date_range("2025-05-27/2025-05-28".into()).map_err(|_| ()),
        Ok(Timestamp(1748304000)..Timestamp(1748304000 + 86400))
    );
    assert!(parse_iso_date_range("2025-05-28/2025-05-27".into()).is_err());
    assert_eq!(
        parse_iso_date_range("2025-05-20/2025-05-28".into()).map_err(|_| ()),
        Ok(Timestamp(1747699200)..Timestamp(1747699200 + 86400 * 8))
    );
}

fn get_graph() -> BuiltGraph {
    let mut builder = GraphBuilder::default();
    let a = builder
        .node(swhid!(swh:1:rev:0000000000000000000000000000000000000010))
        .unwrap()
        .author_timestamp(1000000000, 60)
        .done();
    let b = builder
        .node(swhid!(swh:1:rev:0000000000000000000000000000000000000020))
        .unwrap()
        .committer_timestamp(1100000000, 120)
        .done();
    let c = builder
        .node(swhid!(swh:1:rev:0000000000000000000000000000000000000030))
        .unwrap()
        .author_timestamp(1200000000, 60)
        .committer_timestamp(1300000000, 120)
        .done();
    let d = builder
        .node(swhid!(swh:1:rev:0000000000000000000000000000000000000040))
        .unwrap()
        .done();
    builder.arc(a, b);
    builder.arc(b, c);
    builder.arc(c, d);
    builder.done().unwrap()
}

#[test]
fn test_timestamp_checker_empty() {
    let graph = get_graph();
    let checker = RevrelTimestampChecker {
        include_timestamp_ranges: vec![],
        exclude_timestamp_ranges: vec![],
    };

    assert!(checker.matches(&graph, 0));
    assert!(checker.matches(&graph, 1));
    assert!(checker.matches(&graph, 2));
    assert!(checker.matches(&graph, 3));
}

#[test]
fn test_timestamp_checker_include() {
    let graph = get_graph();
    let checker = RevrelTimestampChecker {
        include_timestamp_ranges: vec![
            Timestamp(1000000000)..Timestamp(1100000000),
            Timestamp(1200000000)..Timestamp(1300000000),
        ],
        exclude_timestamp_ranges: vec![],
    };

    assert!(checker.matches(&graph, 0));
    assert!(!checker.matches(&graph, 1));
    assert!(checker.matches(&graph, 2));
    assert!(!checker.matches(&graph, 3));
}

#[test]
fn test_timestamp_checker_include_exclude() {
    let graph = get_graph();
    let checker = RevrelTimestampChecker {
        include_timestamp_ranges: vec![Timestamp(1000000000)..Timestamp(1300000000)],
        exclude_timestamp_ranges: vec![Timestamp(1200000000)..Timestamp(1300000000)],
    };

    assert!(checker.matches(&graph, 0));
    assert!(checker.matches(&graph, 1));
    assert!(!checker.matches(&graph, 2));
    assert!(!checker.matches(&graph, 3));
}
