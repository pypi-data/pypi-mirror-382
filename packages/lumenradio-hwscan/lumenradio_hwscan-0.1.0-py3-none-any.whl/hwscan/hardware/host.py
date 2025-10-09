#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# file: hardware/host.py

import subprocess

def get_system_uuid():
    """Return the system UUID from dmidecode, or None if unavailable."""
    try:
        result = subprocess.run(
            ["sudo", "dmidecode", "-s", "system-uuid"],
            capture_output=True, text=True, check=True
        )
        uuid = result.stdout.strip()
        if uuid and uuid.lower() != "unknown":
            return uuid
    except Exception:
        pass
    return None


def get_model_name():
    """Return the system model name from dmidecode, or None if unavailable."""
    try:
        result = subprocess.run(
            ["sudo", "dmidecode", "-s", "system-product-name"],
            capture_output=True, text=True, check=True
        )
        model = result.stdout.strip()
        if model and model.lower() != "unknown":
            return model
    except Exception:
        pass
    return None

def get_hostname():
    """Return the current hostname."""
    try:
        result = subprocess.run(
            ["hostname"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except Exception:
        return "unknown-host"

def detect():
    """Detect host system information."""
    return {
        get_system_uuid(): {
            "type": "ubuntu-host",
            "model": get_model_name(),
            "hostname": get_hostname(),
        }       
    }

