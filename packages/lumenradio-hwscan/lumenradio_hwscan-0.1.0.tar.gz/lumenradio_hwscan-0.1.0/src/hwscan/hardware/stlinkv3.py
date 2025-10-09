# hardware/stlinkv3.py
from pathlib import Path
from .util import by_id_links_for_devnode

def detect():
    VID = "0483"
    PID = "374e"

    results = {}
    root = Path("/sys/bus/usb/devices")
    if not root.exists():
        return results

    for dev in root.iterdir():
        try:
            idv = (dev / "idVendor")
            idp = (dev / "idProduct")
            if not (idv.exists() and idp.exists()):
                continue
            if idv.read_text().strip().lower() != VID or idp.read_text().strip().lower() != PID:
                continue

            def rd(name):
                f = dev / name
                return f.read_text().strip() if f.exists() else ""

            serial = rd("serial")
            if not serial:
                continue
            product = rd("product") or "STLINK-V3"
            manuf = rd("manufacturer")

            entry = {
                "type": "stlink-v3",
                "vendor_id": VID,
                "product_id": PID,
                "manufacturer": manuf,
                "product": product,
                "usb_path": dev.name,
            }

            # CDC ACM node (e.g., /dev/ttyACM0)
            tty_node = None
            for p in dev.rglob("ttyACM*"):
                tty_node = f"/dev/{p.name}"
                break
            if tty_node:
                entry["tty"] = tty_node
                by_ids = by_id_links_for_devnode(tty_node)
                if by_ids:
                    entry["by_id"] = by_ids  # list of /dev/serial/by-id/... links

            # Optional: mass-storage nodes
            blocks = []
            for blk in dev.rglob("block/sd*"):
                name = blk.name
                if len(name) >= 3 and name.startswith("sd") and name[2].isalpha():
                    blocks.append(f"/dev/{name}")
            if blocks:
                seen, uniq = set(), []
                for b in blocks:
                    if b not in seen:
                        seen.add(b)
                        uniq.append(b)
                entry["storage"] = uniq

            results[serial] = entry
        except Exception:
            continue

    return results
