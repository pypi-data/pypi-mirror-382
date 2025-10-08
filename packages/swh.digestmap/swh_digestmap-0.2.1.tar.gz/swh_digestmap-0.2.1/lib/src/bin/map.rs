// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::path::PathBuf;

use anyhow::{Context, Result};
use clap::Parser;

use swh_digestmap::DigestMap;

#[derive(Parser, Debug)]
struct Args {
    /// Path to a directory where tables and .vfunc files are available
    dir: PathBuf,
    /// A SWHID to map to other hashes
    #[arg(long)]
    swhid: Option<String>,
}

pub fn main() -> Result<()> {
    let args = Args::parse();

    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();

    let digest_map = DigestMap::new(&args.dir).context("Could not load digestmap")?;

    match args.swhid {
        Some(swhid) => match digest_map.sha1_from_string_swhid(&swhid)? {
            Some(sha1) => println!("{}", faster_hex::hex_string(&sha1.0)),
            None => println!("Unknown SWHID: {swhid}"),
        },
        None => unimplemented!("missing --swhid"),
    }

    Ok(())
}
