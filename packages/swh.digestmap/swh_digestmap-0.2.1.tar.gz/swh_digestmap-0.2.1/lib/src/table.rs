// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::fs::File;
use std::marker::PhantomData;
use std::mem::size_of;
use std::num::NonZeroUsize;
use std::os::unix::fs::FileExt;
use std::path::Path;

use anyhow::{ensure, Context, Result};
use bytemuck::Pod;
use dsi_progress_logger::{concurrent_progress_logger, ProgressLog};
use mmap_rs::{Mmap, MmapFlags, MmapMut};
use thiserror::Error;

#[derive(Error, Debug, PartialEq, Eq, Hash, Clone)]
#[error("Accessed table index {index} out of {len}")]
pub struct OutOfBoundError {
    pub index: usize,
    pub len: usize,
}

pub struct Table<Item: Pod, B> {
    data: B,
    marker: PhantomData<Item>,
}

impl<Item: Pod> Table<Item, MmapMut> {
    /// Creates a new `.bin` file of the needed size
    pub fn new<P: AsRef<Path>>(path: P, num_nodes: usize) -> Result<Self> {
        let path = path.as_ref();

        let (file, file_len) = allocate_file(
            path,
            u64::try_from(num_nodes * size_of::<Item>()).context("File size overflowed u64")?,
        )?;

        let data = unsafe {
            mmap_rs::MmapOptions::new(file_len as _)
                .context("Could not initialize mmap")?
                .with_flags(MmapFlags::TRANSPARENT_HUGE_PAGES | MmapFlags::SHARED)
                .with_file(&file, 0)
                .map_mut()
                .with_context(|| format!("Could not mmap {}", path.display()))?
        };

        Ok(Self {
            data,
            marker: PhantomData,
        })
    }
}

impl<Item: Pod> Table<Item, Mmap> {
    /// Load a `.bin` file
    pub fn load<P: AsRef<Path>>(path: P) -> Result<Self> {
        let path = path.as_ref();
        let file_len = path
            .metadata()
            .with_context(|| format!("Could not stat {}", path.display()))?
            .len();
        let item_size = size_of::<Item>();
        ensure!(
            file_len % (item_size as u64) == 0,
            "Expected {} length to be a multiple of {}, but it is {}",
            path.display(),
            item_size,
            file_len
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
        Ok(Self {
            data,
            marker: PhantomData,
        })
    }

    /// Writes a new `.bin` using an array already in memory
    pub fn from_array<P: AsRef<Path>>(
        path: P,
        values: &[Item],
        parallelism: NonZeroUsize,
    ) -> Result<Self> {
        let path = path.as_ref();

        // So we can use chunks whose size is a power of two,
        // instead of rounding up/down to Item's size
        let values: &[u8] = bytemuck::cast_slice(values);

        let (file, _file_len) = allocate_file(
            path,
            u64::try_from(values.len()).context("File size overflowed u64")?,
        )?;

        let slice_len = values.len().div_ceil(parallelism.into());
        let slices: Vec<_> = values.chunks(slice_len).collect();

        let mut pl = concurrent_progress_logger!(
            display_memory = true,
            item_name = "byte",
            local_speed = true,
            expected_updates = Some(values.len()),
        );
        pl.start("Writing table");

        let chunk_len = 1 << 26; // 64 MiB, somewhat arbitrary power of two
        std::thread::scope(|s| -> Result<_> {
            let file = &file;
            let thread_handles: Vec<_> = slices
                .into_iter()
                .enumerate()
                .map(|(slice_id, slice)| {
                    let mut thread_pl = pl.clone();
                    s.spawn(move || -> Result<_> {
                        for (chunk_id, chunk) in slice.chunks(chunk_len).enumerate() {
                            let offset = u64::try_from(slice_id * slice_len + chunk_id * chunk_len)
                                .context("File offset overflowed u64")?;
                            file.write_all_at(chunk, offset)?;
                            thread_pl.update_with_count(chunk.len());
                        }

                        Ok(())
                    })
                })
                .collect();

            for handle in thread_handles {
                handle.join().expect("Cannot join thread")?;
            }

            Ok(())
        })?;

        pl.done();

        Self::load(path)
    }
}
impl<Item: Pod, B: AsRef<[u8]>> Table<Item, B> {
    /// Convert a node_id to a SWHID
    #[inline]
    pub fn get(&self, index: usize) -> Result<Item, OutOfBoundError> {
        let item_size = size_of::<Item>();
        let offset = index * item_size;
        let bytes = self
            .data
            .as_ref()
            .get(offset..offset + item_size)
            .ok_or(OutOfBoundError {
                index,
                len: self.data.as_ref().len() / item_size,
            })?;

        Ok(*bytemuck::from_bytes(bytes))
    }

    /// Return how many node_ids are in this map
    #[allow(clippy::len_without_is_empty)] // rationale: we don't care about empty maps
    #[inline]
    pub fn len(&self) -> usize {
        self.data.as_ref().len() / size_of::<Item>()
    }
}

impl<'a, Item: Pod, B: AsRef<[u8]>> IntoIterator for &'a Table<Item, B> {
    type Item = Item;
    type IntoIter = std::iter::Copied<std::slice::Iter<'a, Item>>;

    fn into_iter(self) -> Self::IntoIter {
        bytemuck::cast_slice(self.data.as_ref()).iter().copied()
    }
}

impl<Item: Pod, B: AsMut<[u8]> + AsRef<[u8]>> Table<Item, B> {
    /// Set an item at the given position
    #[inline]
    pub fn set(&mut self, index: usize, item: Item) {
        let item_size = size_of::<Item>();
        let offset = index * item_size;
        self.data
            .as_mut()
            .get_mut(offset..offset + item_size)
            .expect("Tried to write past the end of table")
            .copy_from_slice(bytemuck::bytes_of(&item));
    }
}

fn allocate_file(path: &Path, file_len: u64) -> Result<(File, u64)> {
    let file = std::fs::File::options()
        .read(true)
        .write(true)
        .create_new(true)
        .open(path)
        .with_context(|| format!("Could not create {}", path.display()))?;

    // fallocate the file with zeros so we can fill it without ever resizing it
    file.set_len(file_len)
        .with_context(|| format!("Could not fallocate {} with zeros", path.display()))?;

    Ok((file, file_len))
}
