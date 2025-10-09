import json
from importlib import resources
from typing import List

_data = json.loads(resources.files(__package__).joinpath("regions.json").read_text())


class Regions:
    @staticmethod
    def lookup(name: str) -> str:
        try:
            return _data[name]
        except KeyError as e:
            raise ValueError(f"unknown region {name}") from e

    @staticmethod
    def list() -> List[str]:
        return list(_data.keys())
