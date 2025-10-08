// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::path::PathBuf;

use anyhow::Result;
use clap::Parser;

#[derive(Parser, Debug)]
struct Args {
    /// Path to SWH's ORC export
    #[arg(long)]
    orc: PathBuf,
    #[arg(long)]
    /// Path to a directory where to write the index to
    dir_out: PathBuf,
}

pub fn main() -> Result<()> {
    let args = Args::parse();

    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();

    swh_digestmap::build::build_digestmap(&args.orc, &args.dir_out)
}
