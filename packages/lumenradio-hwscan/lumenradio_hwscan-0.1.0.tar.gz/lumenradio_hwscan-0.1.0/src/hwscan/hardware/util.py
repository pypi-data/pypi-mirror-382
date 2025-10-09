#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# file: hardware/util.py
from pathlib import Path
from typing import List

def by_id_links_for_devnode(devnode: str) -> List[str]:
    """
    Return all /dev/serial/by-id/* symlinks that resolve to the given devnode.
    devnode may be like '/dev/ttyUSB0' or '/dev/ttyACM0'.
    """
    links: List[str] = []
    byid = Path("/dev/serial/by-id")
    if not byid.exists():
        return links

    dev_base = Path(devnode).name
    for p in sorted(byid.iterdir()):
        try:
            if not p.is_symlink():
                continue
            target = p.resolve()
            # match by exact realpath or by basename to be robust
            if target.name == dev_base:
                links.append(str(p))
        except Exception:
            continue
    return links
