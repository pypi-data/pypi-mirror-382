.. _swh-digestmap:

.. include:: README.rst

.. toctree::
   :hidden:

   design


Direct use
----------

::

  from swh.digestmap import DigestMap
  digestmap = DigestMap("dest_folder")
  digestmap.sha1_from_swhid("swh:1:cnt:0000000000000000000000000000000000000004")

  found = digestmap.content_get([b"0000000000000000000000000000000000000004"], algo="sha1_git")
  if found and found[0]:
      hashes_dict = found[0].hashes()

Use as a Software Heritage storage backend
------------------------------------------

The Python package will register ``digestmap`` as a
:ref:`Software Heritage storage backend <swh-storage>`.
However it only partially implements
:py:func:`swh.storage.interface.StorageInterface.content_get`:
returned content objects should only be used to fetch ``.hashes()`` as in the example above.
Note that the returned dict will only contain hashes known to the digestmap,
``sha1`` and ``sha1_git``.
If you are not bothered by these limitations (for example, you're using
:ref:`swh-fuse <swh-fuse>`
)
It can be configured as such::

  storage:
    cls: digestmap
    path: "/path/to/digestmap/folder"

Publicly-available digestmaps
-----------------------------

Some digestmaps matching :ref:`some graph exports <swh-export-list>`
are available online.
Those can be downloaded with:

::

  aws s3 cp --no-sign-request --recursive [PATH] .

.. list-table:: Available digestmaps
   :header-rows: 1

   * - Graph class
     - Graph name
     - Path
     - Size
   * - Full
     - 2025-05-18
     - s3://softwareheritage/derived_datasets/2025-05-18/digestmap
     - 1.1TB
   * - Teaser
     - 2025-05-18-popular-1k
     - s3://softwareheritage/derived_datasets/2025-05-18-popular-1k/digestmap/
     - 4.8GB
   * - Teaser
     - 2023-09-06-popular-1k
     - s3://softwareheritage/derived_datasets/2023-09-06-popular-1k/digestmap/
     - 2.6GB
   * - Full
     - 2024-12-06
     - s3://softwareheritage/derived_datasets/2024-12-06/digestmap/
     - 917GB

Develop
-------

::

  pip install -r requirements-swh.txt
  pip install -r requirements-test.txt
  pip install .
  pytest

We test via ``pytest`` because the ``DigestMap`` binding needs a Python able to import
``swh.model.model``.

Package with ``cibuildwheel .`` from the repository's root.
