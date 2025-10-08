# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

if grep alpine /etc/os-release; then
    # install build dependencies for musllinux wheels
    apk add cargo rust clang clang-libclang
else
    # install build dependencies for manylinux wheels
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs -o /tmp/rustup-init.sh
    chmod +x /tmp/rustup-init.sh
    /tmp/rustup-init.sh -y --profile minimal
    rm /tmp/rustup-init.sh

    yum install -y clang
fi
