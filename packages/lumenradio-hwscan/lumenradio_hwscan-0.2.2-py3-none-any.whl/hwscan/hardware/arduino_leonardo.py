# hardware/arduino_leonardo.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from hashlib import sha1
from .util import by_id_links_for_devnode

def _read(dev: Path, name: str) -> str:
    f = dev / name
    return f.read_text().strip() if f.exists() else ""

def _first_tty_acm(dev: Path):
    for p in dev.rglob("ttyACM*"):
        return f"/dev/{p.name}"
    return None

def _serial_like(seed: str, prefix: str = "ARDU-") -> str:
    return prefix + sha1(seed.encode()).hexdigest()[:8].upper()

def detect():
    """
    Detect Arduino/Leonardo-class CDC-ACM boards, including LattePanda-branded variants.
    Primary matches:
      VIDs: 2341 (Arduino SA), 2a03 (Arduino.org), 3343 (LattePanda)
      PIDs: 8036, 803a
    Fallback match:
      product string contains "leonardo" AND has a ttyACM* under the same USB device.
    Returns a dict keyed by a real serial (if present) or a stable serial-like ID.
    """
    VIDS = {"2341", "2a03", "3343"}
    PIDS = {"8036", "803a"}
    TYPE = "Arduino Leonardo"

    results = {}
    root = Path("/sys/bus/usb/devices")
    if not root.exists():
        return results

    for dev in root.iterdir():
        try:
            idv_p = dev / "idVendor"
            idp_p = dev / "idProduct"
            if not (idv_p.exists() and idp_p.exists()):
                continue

            vid = _read(dev, "idVendor").lower()
            pid = _read(dev, "idProduct").lower()
            product = _read(dev, "product")
            manufacturer = _read(dev, "manufacturer")
            serial = _read(dev, "serial")  # often empty on Leonardo
            usb_path = dev.name

            # Primary rule: known VID/PID pairs
            primary_match = (vid in VIDS and pid in PIDS)

            # Fallback rule: product string contains "Leonardo" and there is a ttyACM*
            fallback_match = ("leonardo" in product.lower()) if product else False

            if not primary_match and not fallback_match:
                continue

            tty_node = _first_tty_acm(dev)
            if not tty_node:
                # Leonardo is CDC-ACM; if no ttyACM* under this USB dev, skip
                continue

            entry = {
                "type": TYPE,
                "vendor_id": vid,
                "product_id": pid,
                "manufacturer": manufacturer or "Arduino/Compatible",
                "product": product or TYPE,
                "usb_path": usb_path,
                "tty": tty_node,
            }

            links = by_id_links_for_devnode(tty_node)
            if links:
                entry["by_id"] = links

            # Key selection: real serial first; else deterministic serial-like from by-id or usb path
            if serial:
                key = serial
            elif links:
                key = _serial_like(links[0])
            else:
                key = _serial_like(usb_path)

            results[key] = entry

        except Exception:
            continue

    return results
