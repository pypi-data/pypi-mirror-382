.. _swh-digestmap-design:

Design document for a hash conversion service
=============================================

As of March 2025, this has led to a first step using only the MPH step
`swh-digestmap <https://gitlab.softwareheritage.org/swh/devel/swh-digestmap>`__

Introduction
------------

Problem: given a SWHID (eg. from swh-graph), how to get a key that
allows accessing an objstorage (sha1 and/or sha256)

Current solutions:

-  if you have lots of them, join with the ``content`` and
   ``skipped_content`` ORC tables (manually, or using Datafusion or
   Spark-SQL) -> takes tenth of minutes to answer and lots of CPU, no
   matter the query size
-  if you have few of them, query swh-storage -> not public, has latency

Proposal: a service that answers these queries efficiently

Use cases
---------

Please describe here the envisioned deployment conditions, access
patterns and volumes.

-  repository mining / empirical software engineering (MSR/EMSE) by
   researchers

   -  the typical usage pattern for this is: (1) use swh-graph heavily
      to identify contents you care about (graph leaves), (2) retrieve
      all the contents from some object storage (usually S3)
   -  problem: from the graph leaves you have SWHIDs/sha1_git, not the
      actual keys used by the object storages
   -  having a service and/or a local map that can be used for
      translation would address this

-  ``swh-fuse``\ @CodeCommons

   -  We’ll have a fairly independent deployment
      `@CINES <https://www.cines.fr/calcul/adastra/>`__: a local graph
      instance, but also a datacenter-local ``storage`` and
      ``objstorage``.
   -  We’d like to run
      `ScanCode <https://scancode-toolkit.readthedocs.io>`__ on the
      whole archive :ship:

      -  although they implement some heuristic to avoid traversing some
         subtrees, we can expect ScanCode to open and read *every* file
         in each directory we’ll provide (not sure we’ll run it on every
         rev of every origin, though).
      -  so far we need to make the hash conversion before each
         ``open``. Maybe we’ll implement pre-loading, ie. pre-fetching
         all hashes/blobs contained in a directory.

-  one day, we should be able to materialize all hashes in objstorages

   -  also in mirrors, they might have the same problem - and they’ll
      have to download it

-  Cassandra is very often (too much) called to check if an object is
   archived or not
-  maybe we’ll have SWHIDv2, so we might have to be able to match other
   hashes in the future

Discussion
----------

-  [name=david]: we already have a service for this (the public API),
   for the “few of them” case at least

   -  [name=david]: to be discussed, we need to specify what is “high
      latency” etc in this context I suppose
   -  [name=Thomas]: +1 for specifying “high latency” and maybe a
      benchmark of the API endpoint before optimizing.

-  [name=anlambert]: fyi, ``storage.content_get_data`` method will fetch
   missing hashes before querying the object storage `thanks to the
   wrapper <https://gitlab.softwareheritage.org/swh/devel/swh-storage/-/blob/c2fd0f01a15da3972b6b15fc9f7eaf39e67bffa4/swh/storage/objstorage.py#L67-79>`__
   it uses under the hood

-  [name=martin] how does the proposed design differ with the addition
   of 3 hashes to the graph’s properties?

   -  `name=vlorentz <but%20it%20has%20high%20latency,%20doesn't%20it?%20that's%20the%20reason%20we%20are%20exploring%20swh-graph%20as%20a%20replacement%20backend%20for%20swh-fuse>`__
      It allows converting other hashes to SWHID, supports SWHID
      collisions, and does not need to be distributed as part of the
      graph (which would double the size of the graph). It’s also
      smaller for users who don’t need the graph itself.
   -  [name=martin] deploying that service would double the space
      consumption anyway. On the other hand, adding 3 properties would
      be *much* simpler to use/deploy. And the MPH will be the one
      mapping to graph nodes, right ?

-  [name=Thomas] : why not a good old database of
   swhid/sha1_git/sha1/sha256 ?

   -  `name=vlorentz <but%20it%20has%20high%20latency,%20doesn't%20it?%20that's%20the%20reason%20we%20are%20exploring%20swh-graph%20as%20a%20replacement%20backend%20for%20swh-fuse>`__
      that’s what swh-storage does, and I have been told repeatedly it
      is too slow
   -  [name=zack] also, it’s not publicly accessible; as such, it would
      fail meeting the requirements of the MSR/EMSE use cases

Design
------

1. From the ORC tables, build four files, that contain (in the same
   order) the sha1/sha1_git/sha256/blake2s256 hashes of each file. Let’s
   call this the “rainbow table” for lack of a better word.
2. For each hashing algo:

   1. the **MPH**: build a MPH mapping a hash ``h`` to a unique number
      ``i``
   2. the **“index”**: build an array of integers, storing the set of
      row numbers in the rainbow table that each ``h`` occurs in; in the
      same order as ``i``
   3. the **“offsets”**: build an Elias-Fano sequence that maps for each
      ``i`` the offset of the end of its sequence in the “index”

So for example, if we have this “rainbow table”:

======== ======== ========
sha1_git sha1     sha256
======== ======== ========
00000000 11111111 22222222
33333333 44444444 55555555
88888888 99999999 77777777
33333333 66666666 77777777
======== ======== ========

and assuming the MPH for sha1_git is: - 00000000 → 0 - 33333333 → 1 -
88888888 → 2

Then the “index” for sha1_git would be:

===== =============================
index (comment)
===== =============================
0     only occurrence of 00000000
1     first occurrence of 33333333
3     second occurrence of 33333333
2     only occurrence of 88888888
===== =============================

and the offsets for sha1_git would be:

====== =============================================
offset (comment)
====== =============================================
1      end of the sequence “0”
3      end of the sequence “1 3”
4      end of the sequence “2” (and end of the file)
====== =============================================

3. Deployment:

   -  expose this with a gRPC or our own RPC framework
   -  distribute with swh-graph datasets, together with Rust API

Rationale
---------

This is similar to what we do in swh-graph. It works well because:

1. everything but the MPH can be mmapped and accessed in constant time
   (I estimate about 1ms per query when done in-process, excluding
   networking)
2. the “rainbow table” is as small as it can be (the only redundant
   information is duplicate hashes), which is a few terabytes
3. the MPH for each algorithm will be about 1GB (and needs to be loaded
   in memory)
4. the “index”’s size for each algorithm is ``N * log(N)`` bits where
   ``N`` is the number of contents (``N``\ =23 billion in practice, so
   69GB)
5. the “offsets”’ size for each algorithm will be a few gigabytes

Downsides
---------

1. It’s going to lag behind the archive, like the graph does.

   -  We can fallback to swh-storage/the web UI for recent contents
   -  It’s not a big deal if we got the SWHIDs from the graph anyway

Dismissed alternatives
----------------------

Additional node property file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What if we distribute, aside the compressed graph, an optional
additional property file ? It would be able to attach ``sha256``,
``sha1``, ``blake`` as content nodes’ properties.

The downside is that property file are indexed by node id, but not all
nodes are content: it would have many holes, which is not efficiently
stored by the current format.

RocksDB
~~~~~~~

for CodeCommons@CINES, the GitHub catchup also needs a service that can
tell quickly if a hash is already archived or not. In their
documentation it is the “known object index” (as in: all archive
objects, not only contents) is a RocksDB where SWHID are primary keys,
and values are empty. Its is filled from graph exports (ORC files) in a
“few” hours-days, as implemented in
`github-ingestion <https://gitlab.softwareheritage.org/teams/codecommons/github-ingestion/-/tree/master/deduplicator/indexmanager>`__.
currently weights 600GB. Note that it uses another lib (from the PPC
objstorage project),
`rocksdb-py <https://pypi.org/project/rocksdb-py/>`__, because that one
could be installed on CINES machines.

Could RocksDB be a Storage backend ? It can be accessed concurrently for
reading. Maybe a “partial” Storage backend, ie. it would not cover the
complete API ?
