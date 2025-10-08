# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from pathlib import Path

from swh.digestmap import DigestMap


def test_digestmap():
    assets = Path(__file__).parent / "assets"
    testmap = DigestMap(assets)
    assert testmap.sha1_from_swhid(
        "swh:1:cnt:9876543210987654321098765432109876543222"
    ) == bytes.fromhex("2223456789012345678901234567890123456789")

    found = testmap.content_get(
        [
            bytes.fromhex("9876543210987654321098765432109876543222"),
            bytes.fromhex("9876543210987654321098765432109876543333"),
            bytes.fromhex("9876543210987654321098765432109876543211"),
        ],
        algo="sha1_git",
    )
    assert len(found) == 3
    h2 = found[2].hashes()
    assert h2["sha1"] == bytes.fromhex("1123456789012345678901234567890123456789")
