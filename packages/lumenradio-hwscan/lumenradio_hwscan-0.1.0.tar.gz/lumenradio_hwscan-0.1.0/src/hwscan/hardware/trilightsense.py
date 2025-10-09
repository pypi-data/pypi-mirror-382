# hardware/trilightsense.py
from pathlib import Path
from .util import by_id_links_for_devnode

def detect():
    VID = "0403"
    PID = "6015"
    PRODUCT = "TriLightSense"

    results = {}
    for tty in Path("/sys/bus/usb-serial/devices").glob("ttyUSB*"):
        try:
            iface = tty.resolve()
            p = iface
            usb_dev = None
            while p != p.parent:
                if (p / "idVendor").exists() and (p / "idProduct").exists():
                    usb_dev = p
                    break
                p = p.parent
            if not usb_dev:
                continue

            def rd(name):
                f = usb_dev / name
                return f.read_text().strip() if f.exists() else ""

            if rd("idVendor").lower() == VID and rd("idProduct").lower() == PID and rd("product") == PRODUCT:
                serial = rd("serial")
                if not serial:
                    continue
                devnode = f"/dev/{tty.name}"
                entry = {
                    "type": "tri-light-sense",
                    "devnode": devnode,
                    "vendor_id": VID,
                    "product_id": PID,
                }
                by_ids = by_id_links_for_devnode(devnode)
                if by_ids:
                    entry["by_id"] = by_ids  # list of /dev/serial/by-id/... links

                results[serial] = entry
        except Exception:
            continue
    return results
