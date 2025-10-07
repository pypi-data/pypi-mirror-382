from __future__ import annotations

from dataclasses import asdict
from enum import StrEnum
from typing import TYPE_CHECKING

import yaml

DEFAULT_INDENT_WIDTH = 2


if TYPE_CHECKING:
    from _typeshed import DataclassInstance

# Allows StrEnum to be serialized as a string
yaml.SafeDumper.add_multi_representer(
    StrEnum,
    yaml.representer.SafeRepresenter.represent_str,
)


def to_yaml(obj: DataclassInstance) -> str:
    """Convert an object to yaml."""
    # Remove None values from the dictionary
    obj_dict = asdict(
        obj, dict_factory=lambda d: {key: value for (key, value) in d if value is not None}
    )
    return yaml.safe_dump(obj_dict, indent=DEFAULT_INDENT_WIDTH, sort_keys=False)


def aggregate_yamls(*models: str) -> str:
    """Convert an object to yaml."""
    aggregated_yaml = ""

    for model in models:
        if aggregated_yaml != "" and model != "":
            aggregated_yaml += "\n---\n"
        aggregated_yaml += model
    return aggregated_yaml
