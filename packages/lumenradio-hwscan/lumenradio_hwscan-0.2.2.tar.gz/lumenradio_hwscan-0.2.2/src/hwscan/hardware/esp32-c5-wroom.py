# hardware/esp32c5_wroom.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from .util import by_id_links_for_devnode

def detect():
    """
    Detect Espressif USB JTAG/serial debug units exposed by ESP32-C5-WROOM modules.
    Matches VID=303a, PID=1001 and returns a dict keyed by the device SerialNumber
    (often the MAC-like string e.g. '3C:DC:75:81:67:1C').

    Returns:
      {
        "<Serial>": {
          "type": "esp32-c5-wroom",
          "vendor_id": "303a",
          "product_id": "1001",
          "manufacturer": "Espressif",
          "product": "USB JTAG/serial debug unit",
          "usb_path": "3-8.4.4.3",
          "tty": "/dev/ttyACM1",
          "by_id": ["/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_<serial>-if00"]
        },
        ...
      }
    """
    VID = "303a"
    PID = "1001"

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
            if idv.read_text().strip().lower() != VID or idp.read_text().strip().lower() != PID:
                continue

            def rd(name: str) -> str:
                f = dev / name
                return f.read_text().strip() if f.exists() else ""

            serial = rd("serial")
            if not serial:
                # Serial is our dict key; skip if missing
                continue

            product = rd("product") or "USB JTAG/serial debug unit"
            manuf = rd("manufacturer") or "Espressif"

            entry = {
                "type": "esp32-c5-wroom",
                "vendor_id": VID,
                "product_id": PID,
                "manufacturer": manuf,
                "product": product,
                "usb_path": dev.name,  # e.g., "3-8.4.4.3"
            }

            # CDC ACM node (e.g., /dev/ttyACM*)
            tty_node = None
            for p in dev.rglob("ttyACM*"):
                tty_node = f"/dev/{p.name}"
                break
            if tty_node:
                entry["tty"] = tty_node
                by_ids = by_id_links_for_devnode(tty_node)
                if by_ids:
                    entry["by_id"] = by_ids

            results[serial] = entry

        except Exception:
            # Ignore transient/race/permission errors
            continue

    return results
