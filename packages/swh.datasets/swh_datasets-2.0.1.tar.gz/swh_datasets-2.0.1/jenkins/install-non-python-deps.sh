# Installs executable dependencies on the CI before running tests.

cargo install --debug --locked swh_graph_topology --version 6.7.5

cargo install --debug --locked swh-provenance-db-build --git https://gitlab.softwareheritage.org/swh/devel/swh-provenance.git --rev 8539e9c9ac1ad864b4aed3fca6999ae14fdd36df
