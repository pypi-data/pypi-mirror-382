# LICENSE HEADER MANAGED BY add-license-header
#
# Copyright (C) 2025 Ethorbit
#
# This file is part of SoundPrompt.
#
# SoundPrompt is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# SoundPrompt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the
# GNU General Public License along with SoundPrompt.
# If not, see <https://www.gnu.org/licenses/>.
#

import tomli_w
import json
from dataclasses import dataclass, field, asdict


@dataclass
class General:
    # TODO: raranker_model = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    """
    This class represents the [general] section
    of the configuration

    Attributes:
    model_name: the Text Semantic Search model name from Hugging Face
    device: the Torch device to use for AI. "cuda" for fast GPU, or "cpu"
    """

    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    device: str = "cpu"


@dataclass
class Hotkeys:
    """
    This class represents the [hotkeys] section
    of the configuration

    Attributes use the pynput hotkey syntax
    https://pynput.readthedocs.io/en/latest/keyboard.html

    Attributes:
    stop_sound: hotkey to quickly stop a playing sound
    """

    stop_sound: str = "<shift>+<esc>"


@dataclass
class Database:
    """
    This class represents the [database] section
    of the configuration

    Attributes:
    directory: directory where the database files are stored at

    save_filenames:
    saves filenames into the database as valid tags

    This can rapidly skew the database with unpredictable results
    if the filenames are not real English words or irrelevant to the sounds
    """

    directory: str = "output"
    save_filenames: bool = False


@dataclass
class Config:
    """
    This class represents a template which can be used to
    form a configuration for this program
    """
    general: General = field(default_factory=General)
    hotkeys: Hotkeys = field(default_factory=Hotkeys)
    database: Database = field(default_factory=Database)

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """
        This returns a Config, made from a dict
        """
        return cls(
            general=General(**data.get("general", {})),
            hotkeys=Hotkeys(**data.get("hotkeys", {})),
            database=Database(**data.get("database", {}))
        )

    def to_dict(self) -> dict:
        """
        This gets the Config as a dict
        """
        return asdict(self)

    @classmethod
    def from_json(cls, json_data: str):
        """
        Create a Config instance from a JSON string.
        """
        data = json.loads(json_data)
        return cls.from_dict(data)

    def to_json(self, *, indent: int = 4) -> str:
        """
        Serialize this Config instance to a JSON string.

        Args:
            indent: number of spaces to use for pretty-printing (default 4)

        Returns:
            A JSON string representation of this Config.
        """
        return json.dumps(asdict(self), indent=indent)

    def to_toml(self) -> str:
        """
        Converts the Config into a TOML string
        """
        return tomli_w.dumps(asdict(self))

    def save_toml(self, path: str):
        """
        Writes the Config as a TOML file to the given path
        """
        with open(path, "wb") as f:
            f.write(tomli_w.dumps(asdict(self)).encode("utf-8"))
