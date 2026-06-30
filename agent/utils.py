from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List

from agent.models import NetworkMetrics


def ensure_output_path(path: str) -> Path:
    """Create parent directories for the output file if needed."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def write_metrics(metrics: NetworkMetrics, output_file: str) -> None:
    """Persist metrics to a JSON file."""

    output_path = ensure_output_path(output_file)
    existing: List[Dict[str, Any]] = []
    if output_path.exists():
        with output_path.open("r", encoding="utf-8") as handle:
            try:
                existing = json.load(handle)
            except json.JSONDecodeError:
                existing = []

    if not isinstance(existing, list):
        existing = []

    existing.append(metrics.to_payload())
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(existing, handle, indent=2)


def is_command_available(command: str) -> bool:
    """Return True when a binary is available in the shell path."""

    return shutil.which(command) is not None
