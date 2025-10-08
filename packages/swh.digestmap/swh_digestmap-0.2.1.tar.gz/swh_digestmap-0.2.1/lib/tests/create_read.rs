// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::fs::{copy, DirBuilder, File};
use std::path::Path;
use tempfile::TempDir;

use anyhow::{Context, Result};
use arrow_array::record_batch;
use orc_rust::arrow_writer::ArrowWriterBuilder;

use swh_digestmap::build::build_digestmap;
use swh_digestmap::{DigestMap, Sha1, Sha1Git, SHA1_FILENAME, SHA1_GIT_FILENAME, VFUNC_FILENAME};

pub struct TestsRootFolder {
    pub dir: TempDir,
}

impl TestsRootFolder {
    pub fn new() -> Result<Self> {
        let root_dir = tempfile::tempdir().context("Could not create temporary directory")?;
        let root = root_dir.path();

        let batch = record_batch!(
            (
                "sha1",
                Utf8,
                [
                    "1123456789012345678901234567890123456789",
                    "2223456789012345678901234567890123456789",
                    "3333456789012345678901234567890123456789"
                ]
            ),
            (
                "sha1_git",
                Utf8,
                [
                    "9876543210987654321098765432109876543211",
                    "9876543210987654321098765432109876543222",
                    "9876543210987654321098765432109876543333"
                ]
            )
        )
        .unwrap();

        let content_folder = root.join("content");
        DirBuilder::new().create(&content_folder).unwrap();
        let orc_input = content_folder.join("input.orc");
        let file = File::create(&orc_input).unwrap();
        let mut writer = ArrowWriterBuilder::new(file, batch.schema())
            .try_build()
            .unwrap();
        writer.write(&batch).unwrap();
        writer.close().unwrap();

        build_digestmap(root, root).expect("error while building test digestmap");

        // this may be used to generate tests/assets on the pyo3 side
        let target = option_env!("COPY_TEST_DIGESTMAP_TO");
        if let Some(dirname) = target {
            let target = Path::new(dirname);
            assert!(
                target.is_dir(),
                "provided path COPY_TEST_DIGESTMAP_TO does not point to an existing directory"
            );
            copy(root.join(SHA1_FILENAME), target.join(SHA1_FILENAME))?;
            copy(root.join(SHA1_GIT_FILENAME), target.join(SHA1_GIT_FILENAME))?;
            copy(root.join(VFUNC_FILENAME), target.join(VFUNC_FILENAME))?;
        }

        Ok(TestsRootFolder { dir: root_dir })
    }
}

#[test]
fn test_create_read_digestmap() {
    let root_folder = TestsRootFolder::new().unwrap();
    let root = root_folder.dir.path();

    let digestmap = DigestMap::new(root).unwrap();

    let found = digestmap
        .sha1_from_sha1_git(Sha1Git([
            0x98, 0x76, 0x54, 0x32, 0x10, 0x98, 0x76, 0x54, 0x32, 0x10, 0x98, 0x76, 0x54, 0x32,
            0x10, 0x98, 0x76, 0x54, 0x33, 0x33,
        ]))
        .unwrap();
    match found {
        Some(Sha1(h)) => assert_eq!(
            h,
            [
                0x33, 0x33, 0x45, 0x67, 0x89, 0x01, 0x23, 0x45, 0x67, 0x89, 0x01, 0x23, 0x45, 0x67,
                0x89, 0x01, 0x23, 0x45, 0x67, 0x89
            ]
        ),
        None => panic!("sha1 should be found"),
    }

    let not_found = digestmap
        .sha1_from_sha1_git(Sha1Git([
            0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
            0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
        ]))
        .unwrap();
    if let Some(Sha1(_h)) = not_found {
        panic!("that sha1_git does not exists")
    }

    let found = digestmap
        .sha1_from_string_swhid("swh:1:cnt:9876543210987654321098765432109876543211")
        .unwrap();
    match found {
        Some(Sha1(h)) => assert_eq!(
            h,
            [
                0x11, 0x23, 0x45, 0x67, 0x89, 0x01, 0x23, 0x45, 0x67, 0x89, 0x01, 0x23, 0x45, 0x67,
                0x89, 0x01, 0x23, 0x45, 0x67, 0x89
            ]
        ),
        None => panic!("sha1 should be found"),
    }

    let not_found = digestmap
        .sha1_from_string_swhid("swh:1:cnt:1524365476223125614543654654365460001234")
        .unwrap();
    if let Some(Sha1(_h)) = not_found {
        panic!("that sha1_git does not exists")
    }
}
