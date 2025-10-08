// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::num::NonZeroUsize;
use std::path::Path;

use anyhow::{Context, Result};
use ar_row::deserialize::ArRowStruct;
use ar_row::row_iterator::RowIterator;
use ar_row_derive::ArRowDeserialize;
use crossbeam::atomic::AtomicCell;
use dsi_progress_logger::{concurrent_progress_logger, ProgressLog};
use epserde::deser::{Deserialize, Flags};
use epserde::ser::Serialize;
use orc_rust::projection::ProjectionMask;
use orc_rust::ArrowReaderBuilder;
use rayon::prelude::*;
use rdst::RadixSort;
use sux::bits::BitFieldVec;
use sux::func::{VBuilder, VFunc};
use sux::prelude::BitFieldSlice;
use sux::utils::FromIntoIterator;

use crate::table::Table;
use crate::{Sha1, Sha1Git, SHA1_FILENAME, SHA1_GIT_FILENAME, VFUNC_FILENAME};

pub(crate) fn get_dataset_reader_builders<P: AsRef<Path>>(
    dataset_dir: P,
    subdirectory: &str,
) -> Result<Vec<ArrowReaderBuilder<std::fs::File>>> {
    let mut dataset_dir = dataset_dir.as_ref().to_owned();
    dataset_dir.push(subdirectory);
    std::fs::read_dir(&dataset_dir)
        .with_context(|| format!("Could not list {}", dataset_dir.display()))?
        .map(|file_path| {
            let file_path = file_path
                .with_context(|| format!("Failed to list {}", dataset_dir.display()))?
                .path();
            let file = std::fs::File::open(&file_path)
                .with_context(|| format!("Could not open {}", file_path.display()))?;
            let builder = ArrowReaderBuilder::try_new(file)
                .with_context(|| format!("Could not read {}", file_path.display()))?;
            Ok(builder)
        })
        .collect()
}

pub fn build_sha1_git_table<P: AsRef<Path>>(
    orc_dir: P,
    tables_dir: P,
    parallelism: NonZeroUsize,
) -> Result<Table<Sha1Git, impl AsRef<[u8]>>> {
    let tables_dir = tables_dir.as_ref();
    let dataset_reader_builders = get_dataset_reader_builders(orc_dir, "content")?;

    let num_rows = usize::try_from(
        dataset_reader_builders
            .iter()
            .map(|reader_builder| reader_builder.file_metadata().number_of_rows())
            .sum::<u64>(),
    )
    .context("Number of rows overflowed usize")?;
    let mut pl = concurrent_progress_logger! {
        item_name="row",
        display_memory=true,
        expected_updates=Some(num_rows),
    };

    pl.start("Listing keys...");

    let mut sha1_gits = dataset_reader_builders
        .into_par_iter()
        .flat_map_iter(|reader_builder| {
            #[derive(ArRowDeserialize, Clone, Default)]
            struct Row {
                sha1_git: String,
            }

            let mut pl = pl.clone();

            let projection = ProjectionMask::named_roots(
                reader_builder.file_metadata().root_data_type(),
                &Row::columns(),
            );
            let reader = reader_builder.with_projection(projection).build();
            RowIterator::new(reader.map(|batch| batch.unwrap()))
                .expect("Could not create iterator") // TODO: don't panic
                .map(move |Row { sha1_git }| {
                    pl.light_update();
                    Sha1Git::from_hex(sha1_git.as_bytes())
                })
        })
        .collect::<Result<Vec<_>>>()?;

    pl.done();

    log::info!("Sorting keys...");
    sha1_gits.radix_sort_unstable();

    log::info!("Deduplicating sha1_gits...");
    sha1_gits.dedup();
    let num_duplicates = num_rows - sha1_gits.len();
    if num_duplicates > 0 {
        log::warn!("Removed {num_duplicates} duplicates");
    } else {
        log::info!("No duplicates found");
    }

    log::info!("Writing sha1_git table...");
    Table::from_array(tables_dir.join(SHA1_GIT_FILENAME), &sha1_gits, parallelism)
}

pub fn build_vfunc(
    keys: &Table<Sha1Git, impl AsRef<[u8]>>,
) -> Result<VFunc<Sha1Git, usize, BitFieldVec>> {
    let num_keys = keys.len();

    let mut pl = concurrent_progress_logger! {
        item_name="key",
        display_memory=true,
        expected_updates=Some(num_keys),
    };
    pl.start("Building VFunc...");
    let builder = VBuilder::<_, BitFieldVec<usize>>::default().expected_num_keys(num_keys);
    let func = builder.try_build_func(
        FromIntoIterator::from(keys.into_iter()),
        FromIntoIterator::from(0..num_keys),
        &mut pl,
    )?;
    pl.done();

    Ok(func)
}

pub fn build_tables<P: AsRef<Path>, D: BitFieldSlice<usize> + Sync>(
    orc_dir: P,
    vfunc: &VFunc<Sha1Git, usize, D>,
    tables_dir: P,
    parallelism: NonZeroUsize,
) -> Result<()> {
    let tables_dir = tables_dir.as_ref();

    let num_keys = vfunc.len();

    log::info!("Allocating arrays...");
    let sha1s: Vec<_> = (0..num_keys)
        .into_par_iter()
        .map(|_| AtomicCell::default())
        .collect();

    let mut pl = concurrent_progress_logger!(
        item_name = "row",
        display_memory = true,
        expected_updates = Some(num_keys),
    );

    pl.start("Building tables...");

    let res = get_dataset_reader_builders(orc_dir, "content")?
        .into_par_iter()
        .try_for_each_with(pl.clone(), |pl, reader_builder| {
            #[derive(ArRowDeserialize, Clone, Default)]
            struct Row {
                sha1: String,
                sha1_git: String,
            }

            let projection = ProjectionMask::named_roots(
                reader_builder.file_metadata().root_data_type(),
                &Row::columns(),
            );
            let reader = reader_builder.with_projection(projection).build();
            for Row { sha1_git, sha1 } in RowIterator::new(reader.map(|batch| batch.unwrap()))
                .context("Could not create iterator")?
            {
                let sha1 = Sha1::from_hex(sha1.as_bytes())?;
                let sha1_git = Sha1Git::from_hex(sha1_git.as_bytes())?;
                let index = vfunc.get(sha1_git);
                sha1s[index].store(sha1);
                pl.light_update();
            }
            Ok(())
        });

    pl.done();

    // Compiled to no-op
    let sha1s: Vec<_> = sha1s.into_iter().map(AtomicCell::into_inner).collect();

    log::info!("Writing sha1 table...");
    Table::from_array(tables_dir.join(SHA1_FILENAME), &sha1s, parallelism)?;

    res
}

pub fn build_digestmap(orc: &Path, dir_out: &Path) -> Result<()> {
    std::fs::create_dir_all(dir_out)
        .with_context(|| format!("Could not create {}", dir_out.display()))?;

    let parallelism = NonZeroUsize::new(8).unwrap(); // TODO: configurable

    let vfunc_path = dir_out.join(VFUNC_FILENAME);
    let load_vfunc = std::fs::exists(&vfunc_path)
        .with_context(|| format!("Could not check if {} exists", vfunc_path.display()))?;
    if load_vfunc {
        log::info!("Load vfunc from {}", vfunc_path.display());
        let vfunc = <VFunc<_>>::mmap(
            &vfunc_path,
            Flags::TRANSPARENT_HUGE_PAGES | Flags::RANDOM_ACCESS,
        )?;
        build_tables(orc, &*vfunc, dir_out, parallelism).context("Could not build tables")?;
    } else {
        let sha1_gits = build_sha1_git_table(orc, dir_out, parallelism)
            .context("Could not build sha1_git table")?;
        let vfunc = build_vfunc(&sha1_gits).context("Could not build VFunc")?;

        log::info!("Writing VFunc...");
        vfunc
            .store(&vfunc_path)
            .with_context(|| format!("Could not save VFunc to {}", vfunc_path.display()))?;
        build_tables(orc, &vfunc, dir_out, parallelism).context("Could not build tables")?;
    };

    Ok(())
}
