#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import importlib
import pkgutil
from types import ModuleType
from typing import Dict, Tuple

def run_all_detectors() -> Tuple[Dict[str, dict], Dict[str, str]]:
    """
    Imports every module in the 'hwscan.hardware' package and calls its detect().
    Returns:
      results: { "<ID>": {...device data...} }
      errors:  { "<module_name>": "error text" }
    """
    # Always absolute import inside the installed package
    from hwscan import hardware as detectors_pkg

    results: Dict[str, dict] = {}
    errors: Dict[str, str] = {}

    for modinfo in pkgutil.iter_modules(detectors_pkg.__path__, detectors_pkg.__name__ + "."):
        try:
            mod: ModuleType = importlib.import_module(modinfo.name)
            detect = getattr(mod, "detect", None)
            if not callable(detect):
                continue
            devices = detect() or {}
            for hw_id, data in devices.items():
                if not hw_id:
                    continue
                results[hw_id] = data
        except Exception as e:
            errors[modinfo.name] = f"{type(e).__name__}: {e}"

    return results, errors
