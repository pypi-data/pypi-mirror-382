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

from __future__ import annotations
from soundprompt.config.toml import structure
from soundprompt.data import filesystem
import tomllib
import os
from pathlib import Path
from argparse import Namespace


class ConfigSystem:
    """
    This class loads the program's config

    Requires CLI args to make sure that args
    continue to take precedence

    Responsibilities:
    - Reads user TOML config, converts it to Config()
    """

    _args: Namespace
    config: structure.Config

    def __init__(self, args: Namespace):
        self._args = args

        config_dir = self.get_config_directory()
        config_file = config_dir / "config.toml"

        # Write a default config if one doesn't exist
        if not config_file.exists():
            os.makedirs(config_dir, exist_ok=True)

            self.config = structure.Config()
            self.config.database.directory = str(config_dir)
            self.config.save_toml(str(config_file))

        self.config = self._load_config()

    def get_config_directory(self) -> Path:
        """
        Returns the location for the program's config file

        This will either be specified by CLI arg, or
        an appropriate location based on OS
        """

        if self._args.config:
            filesystem.validate_path(self._args.config)
            return self._args.config

        if os.name == "nt":
            return Path(
                    os.getenv("APPDATA", "")
                ) / "soundprompt"
        else:
            return Path.home() / ".config" / "soundprompt"

    def _load_config(self) -> structure.Config:
        """
        Loads the config file, which contains app-specific global settings

        Note: overrides values with CLI args
        """

        config_dir = self.get_config_directory()
        config_file = config_dir / "config.toml"

        if not config_file.exists():
            raise FileNotFoundError(
                f"config.toml missing, needed at {config_file}"
            )

        with open(config_file, "rb") as f:
            cfg = tomllib.load(f)

            if self._args.save_filenames is True:
                cfg["database"]["save_filenames"] = True

            if self._args.db_path:
                cfg["database"]["directory"] = self._args.db_path

            if self._args.device:
                cfg["general"]["device"] = self._args.device

            return structure.Config.from_dict(cfg)
