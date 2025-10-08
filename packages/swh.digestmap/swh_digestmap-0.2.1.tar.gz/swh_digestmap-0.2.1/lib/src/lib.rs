// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

#![doc = include_str!("../README.md")]

use std::{borrow::Borrow, path::Path};

use anyhow::{bail, Context, Result};
use bytemuck::{Pod, Zeroable};
use epserde::{
    deser::{Deserialize, Flags, MemCase},
    Epserde,
};
use mmap_rs::Mmap;
use sux::{bits::BitFieldVec, func::VFunc, utils::sig_store::ToSig};
use xxhash_rust::xxh3;

#[cfg(any(test, feature = "build"))]
pub mod build;

pub mod table;
use table::Table;

const SWHID_PREFIX: &str = "swh:1:cnt:";
pub const VFUNC_FILENAME: &str = "sha1_git.vfunc";
pub const SHA1_FILENAME: &str = "sha1.bin";
pub const SHA1_GIT_FILENAME: &str = "sha1_git.bin";

pub const SHA1_BYTES: usize = 20;

#[derive(Clone, Copy, Default, Debug, PartialEq, Eq, Pod, Zeroable)]
#[repr(transparent)]
pub struct Sha1(pub [u8; SHA1_BYTES]);

impl Sha1 {
    pub fn from_hex(hex: &[u8]) -> Result<Self> {
        let mut buf = [0u8; SHA1_BYTES];
        faster_hex::hex_decode(hex, &mut buf)
            .with_context(|| format!("Could not decode {hex:?}"))?;
        Ok(Self(buf))
    }
}

pub const SHA1_GIT_BYTES: usize = 20;
#[derive(Clone, Copy, Default, Debug, PartialEq, Eq, Epserde, Pod, Zeroable)]
#[repr(transparent)]
pub struct Sha1Git(pub [u8; SHA1_GIT_BYTES]);

impl Sha1Git {
    pub fn from_hex(hex: &[u8]) -> Result<Self> {
        let mut buf = [0u8; SHA1_GIT_BYTES];
        faster_hex::hex_decode(hex, &mut buf)
            .with_context(|| format!("Could not decode {hex:?}"))?;
        Ok(Self(buf))
    }
}

impl ToSig<[u64; 2]> for &Sha1Git {
    fn to_sig(key: impl Borrow<Self>, seed: u64) -> [u64; 2] {
        let Sha1Git(as_bytes) = key.borrow();
        let hash128 = xxh3::xxh3_128_with_seed(as_bytes, seed);
        [(hash128 >> 64) as u64, hash128 as u64]
    }
}
impl ToSig<[u64; 2]> for Sha1Git {
    fn to_sig(key: impl Borrow<Self>, seed: u64) -> [u64; 2] {
        let Sha1Git(as_bytes) = key.borrow();
        let hash128 = xxh3::xxh3_128_with_seed(as_bytes, seed);
        [(hash128 >> 64) as u64, hash128 as u64]
    }
}

impl rdst::RadixKey for Sha1Git {
    const LEVELS: usize = SHA1_GIT_BYTES;

    fn get_level(&self, level: usize) -> u8 {
        self.0[level]
    }
}

pub struct DigestMap {
    #[allow(clippy::type_complexity)]
    vfunc: MemCase<VFunc<Sha1Git, usize, BitFieldVec<usize, &'static [usize]>>>,
    sha1_table: Table<Sha1, Mmap>,
    sha1_git_table: Table<Sha1Git, Mmap>,
}

impl DigestMap {
    pub fn new(path: &Path) -> Result<Self> {
        let vfunc_path = path.join(VFUNC_FILENAME);
        let vfunc = <VFunc<Sha1Git, usize, BitFieldVec<usize, Vec<usize>>>>::mmap(
            &vfunc_path,
            Flags::TRANSPARENT_HUGE_PAGES | Flags::RANDOM_ACCESS,
        )
        .with_context(|| format!("could not mmap {}", vfunc_path.display()))?;
        let sha1_table_path = path.join(SHA1_FILENAME);
        let sha1_table = Table::load(&sha1_table_path).with_context(|| {
            format!("could not load digests table {}", sha1_table_path.display())
        })?;
        let sha1_git_table_path = path.join(SHA1_GIT_FILENAME);
        let sha1_git_table = Table::load(&sha1_git_table_path).with_context(|| {
            format!(
                "could not load digests table {}",
                sha1_git_table_path.display()
            )
        })?;
        Ok(DigestMap {
            vfunc,
            sha1_table,
            sha1_git_table,
        })
    }

    pub fn sha1_from_string_swhid(&self, swhid: &str) -> Result<Option<Sha1>> {
        let Some(sha1_git) = swhid.strip_prefix(SWHID_PREFIX) else {
            bail!("SWHID must start with {}", SWHID_PREFIX);
        };
        let sha1_git = Sha1Git::from_hex(sha1_git.as_bytes()).context("Could not parse SWHID")?;

        self.sha1_from_sha1_git(sha1_git)
    }

    pub fn sha1_from_sha1_git(&self, sha1_git: Sha1Git) -> Result<Option<Sha1>> {
        let index = self.vfunc.get(sha1_git);
        let sha1_git2 = self.sha1_git_table.get(index);

        // If we're out of bound of if they are not equal, that means
        // one of them is not in the static function's known keys.
        // By construction, we know that sha1_git2 is.
        if sha1_git2.is_err() {
            return Ok(None);
        }
        let sha1_git2 = sha1_git2.unwrap();
        if sha1_git != sha1_git2 {
            // Unknown SWHID
            return Ok(None);
        }

        let sha1 = self
            .sha1_table
            .get(index)
            .context("hash overflowed sha1 table size")?;
        Ok(Some(sha1))
    }
}
