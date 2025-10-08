# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from pathlib import Path
from typing import List, Optional

from swh.model.model import Content

class DigestMap:
    def __init__(self, path: Path): ...
    def sha1_from_swhid(self, swhid: str) -> bytes: ...
    def content_get(
        self, sha1_gits: List[bytes], algo: str
    ) -> List[Optional[Content]]: ...
