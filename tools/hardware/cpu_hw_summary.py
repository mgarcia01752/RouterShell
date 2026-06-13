#!/usr/bin/env python3
"""Print a concise CPU hardware summary."""

from __future__ import annotations

import json
import subprocess

from tabulate import tabulate


def extract_field(data: list[dict[str, str]], field_name: str) -> str:
    """Return a named field from lscpu JSON output."""
    for item in data:
        if item["field"] == field_name:
            return item["data"]
    return "N/A"


def create_tabulated_summary() -> str:
    """Create a tabulated CPU summary from lscpu output."""
    try:
        result = subprocess.run(["lscpu", "-J"], capture_output=True, text=True, check=True)
        lscpu_json = result.stdout

        data = json.loads(lscpu_json)["lscpu"]

        architecture = extract_field(data, "Architecture:")
        cpu_count = extract_field(data, "CPU(s):")
        vendor_id = extract_field(data, "Vendor ID:")

        model_name = extract_field(data, "Model name:")
        cpu_family = extract_field(data, "CPU family:")
        model = extract_field(data, "Model:")
        thread_per_core = extract_field(data, "Thread(s) per core:")
        core_per_socket = extract_field(data, "Core(s) per socket:")
        socket_count = extract_field(data, "Socket(s):")
        cpu_max_mhz = extract_field(data, "CPU max MHz:")
        cpu_min_mhz = extract_field(data, "CPU min MHz:")
        bogo_mips = extract_field(data, "BogoMIPS:")

        virtualization = extract_field(data, "Virtualization:")

        table = [
            ["Model Name", model_name],
            ["Vendor ID", vendor_id],
            ["Model", model],
            ["Architecture", architecture],
            ["CPU(s)", cpu_count],
            ["CPU Family", cpu_family],
            ["Thread(s) per Core", thread_per_core],
            ["Core(s) per Socket", core_per_socket],
            ["Socket(s)", socket_count],
            ["CPU Min/Max MHz", f"{cpu_min_mhz}/{cpu_max_mhz}"],
            ["BogoMIPS", bogo_mips],
            ["Virtualization", virtualization],
        ]

        return tabulate(table, headers=["CPU", "Info"], tablefmt="simple")
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        return f"Error: {exc}"


if __name__ == "__main__":
    print(create_tabulated_summary())
