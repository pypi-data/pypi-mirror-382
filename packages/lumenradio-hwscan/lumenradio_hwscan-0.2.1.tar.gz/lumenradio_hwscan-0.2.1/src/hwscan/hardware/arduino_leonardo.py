# hardware/arduino_leonardo.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from hashlib import sha1
from .util import by_id_links_for_devnode

def detect():
    """
    Detect Arduino Leonardo (CDC ACM, HID).
    Matches VID=2341, PID=8036 and returns a dict keyed by a stable serial-like ID.

    Returns:
      {
        "<serial_like_id>": {
          "type": "Arduino Leonardo",
          "vendor_id": "2341",
          "product_id": "8036",
          "manufacturer": "Arduino LLC",
          "product": "Arduino Leonardo",
          "usb_path": "1-3",
          "tty": "/dev/ttyACM0",
          "by_id": ["/dev/serial/by-id/usb-Arduino_LLC_Arduino_Leonardo-if00"]
        }
      }
    """
    VIDS = {"2341", "2a03"}  # Arduino SA & Arduino.org
    PIDS = {"8036"}          # Leonardo
    TYPE = "Arduino Leonardo"

    results = {}
    root = Path("/sys/bus/usb/devices")
    if not root.exists():
        return results

    for dev in root.iterdir():
        try:
            idv = dev / "idVendor"
            idp = dev / "idProduct"
            if not (idv.exists() and idp.exists()):
                continue

            vid = idv.read_text().strip().lower()
            pid = idp.read_text().strip().lower()
            if vid not in VIDS or pid not in PIDS:
                continue

            def rd(name: str) -> str:
                f = dev / name
                return f.read_text().strip() if f.exists() else ""

            product = rd("product") or TYPE
            manufacturer = rd("manufacturer") or "Arduino"
            serial = rd("serial") or ""  # usually empty
            usb_path = dev.name

            entry = {
                "type": TYPE,
                "vendor_id": vid,
                "product_id": pid,
                "manufacturer": manufacturer,
                "product": product,
                "usb_path": usb_path,
            }

            # Detect /dev/ttyACM* node
            tty_node = None
            for p in dev.rglob("ttyACM*"):
                tty_node = f"/dev/{p.name}"
                break
            if tty_node:
                entry["tty"] = tty_node
                links = by_id_links_for_devnode(tty_node)
                if links:
                    entry["by_id"] = links

            # --- determine stable key ---
            if serial:
                key = serial
            else:
                # prefer by-id symlink target for determinism
                seed = None
                if "by_id" in entry:
                    seed = entry["by_id"][0]
                else:
                    seed = usb_path
                # Hash to short serial-like format (8 hex chars)
                key = "ARDU-" + sha1(seed.encode()).hexdigest()[:8].upper()

            results[key] = entry

        except Exception:
            continue

    return results
