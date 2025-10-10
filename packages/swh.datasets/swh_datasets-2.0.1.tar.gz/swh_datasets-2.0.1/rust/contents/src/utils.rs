// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use swh_graph::graph::{SwhGraphWithProperties, SwhLabeledBackwardGraph};
use swh_graph::labels::DirEntry;
use swh_graph::properties;

pub fn get_sample_filename<
    G: SwhLabeledBackwardGraph
        + SwhGraphWithProperties<Maps: properties::Maps, LabelNames: properties::LabelNames>,
>(
    graph: G,
    node: usize,
) -> Option<Box<[u8]>> {
    graph
        .untyped_labeled_predecessors(node)
        .into_iter()
        .flat_map(|(_succ, labels)| labels.into_iter())
        .next() // pick the smallest label of the smallest successor with a label
        .and_then(|label| {
            graph
                .properties()
                .try_label_name(DirEntry::from(label).label_name_id())
                .ok()
        })
        .map(Vec::into_boxed_slice)
}
