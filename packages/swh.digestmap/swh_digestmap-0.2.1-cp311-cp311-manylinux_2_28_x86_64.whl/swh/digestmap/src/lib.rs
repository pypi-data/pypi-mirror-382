// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::borrow::Cow;
use std::path::PathBuf;

use anyhow::Result;
use pyo3::prelude::*;

#[pymodule]
mod digestmap {
    use pyo3::exceptions::PyValueError;
    use pyo3::intern;
    use swh_digestmap::Sha1Git;

    use super::*;

    #[pyclass]
    struct DigestMap(::swh_digestmap::DigestMap);

    #[pymethods]
    impl DigestMap {
        #[new]
        fn new(path: PathBuf) -> Result<Self> {
            ::swh_digestmap::DigestMap::new(&path).map(Self)
        }

        fn sha1_from_swhid(&self, swhid: &str) -> Result<Option<Cow<'_, [u8]>>> {
            match self.0.sha1_from_string_swhid(swhid) {
                Ok(Some(sha1)) => Ok(Some(Cow::Owned(sha1.0.into()))),
                Ok(None) => Ok(None),
                Err(e) => Err(e),
            }
        }

        #[pyo3(signature = (contents, algo="sha1"))]
        fn content_get<'py>(
            &self,
            py: Python<'py>,
            contents: Vec<Vec<u8>>,
            algo: &str,
        ) -> PyResult<Vec<Option<pyo3::Bound<'py, PyAny>>>> {
            if algo != "sha1_git" {
                return Err(PyValueError::new_err(
                    "This can get content by sha1_git only",
                ));
            }
            let swh_model = PyModule::import(py, "swh.model.model")?;
            let content_class = swh_model.getattr(intern!(py, "Content"))?;
            contents
                .iter()
                .map(|content| {
                    let sha1_git = Sha1Git(content[..20].try_into()?);
                    match self.0.sha1_from_sha1_git(sha1_git) {
                        Ok(Some(sha1)) => Ok(Some(content_class.call1((
                            sha1.0,
                            sha1_git.0,
                            [u8::MIN; 0], // sha256
                            [u8::MIN; 0], // blake2s256
                            0,            // length
                        ))?)),
                        Ok(None) => Ok(None),
                        Err(_) => Ok(None),
                    }
                })
                .collect()
        }
    }

    // workaround for https://github.com/PyO3/pyo3/issues/759
    #[pymodule_init]
    fn init(m: &Bound<'_, PyModule>) -> PyResult<()> {
        Python::with_gil(|py| {
            py.import("sys")?
                .getattr("modules")?
                .set_item("swh.digestmap", m)
        })
    }
}
