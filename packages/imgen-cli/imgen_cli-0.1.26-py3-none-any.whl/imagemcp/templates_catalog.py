from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List

from importlib import resources

from .data import PLACEMENT_CATALOG_FILENAME

TemplateDict = Dict[str, object]


@lru_cache(maxsize=1)
def load_default_placement_templates() -> List[TemplateDict]:
    """Load the packaged placement template catalog as dictionaries."""
    with resources.files("imagemcp.data").joinpath(PLACEMENT_CATALOG_FILENAME).open(
        "r", encoding="utf-8"
    ) as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("Placement catalog JSON must be a list of template objects")
    return data


def seed_default_placement_templates(templates_root: Path) -> List[Path]:
    """Ensure packaged placement templates exist under the project templates directory.

    Returns a list of files that were written during this call.
    """
    placements_dir = templates_root / "placements"
    placements_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []
    for template in load_default_placement_templates():
        template_id = template.get("template_id")
        if not template_id:
            continue
        destination = placements_dir / f"{template_id}.json"
        if destination.exists():
            continue
        with destination.open("w", encoding="utf-8") as fh:
            json.dump(template, fh, indent=2)
            fh.write("\n")
        written.append(destination)
    return written


__all__ = [
    "load_default_placement_templates",
    "seed_default_placement_templates",
]
