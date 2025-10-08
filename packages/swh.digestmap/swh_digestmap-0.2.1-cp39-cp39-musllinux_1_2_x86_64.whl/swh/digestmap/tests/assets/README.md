This folder contains a pre-generated digestmap.
Update these files by running the main library's tests with the `COPY_TEST_DIGESTMAP_TO`
environment variable:

    COPY_TEST_DIGESTMAP_TO=$HOME/swh-environment/swh-digestmap/pyo3/test_assets cargo test --all-features
