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

from soundprompt.config import args
from typing import Any
import tomllib
from pathlib import Path

args = args.get_args()


def get_config_path():
    return Path(__file__).parent.parent / "config.toml"


def load_config() -> dict[str, Any]:
    """
    Loads the config file, which contains app-specific global settings

    Note: overrides values with CLI args
    """

    config_path = get_config_path()

    if not config_path.exists():
        raise FileNotFoundError(
            f"config.toml missing, needed at {config_path}"
        )

    with open(config_path, "rb") as f:
        cfg = tomllib.load(f)

        if args.save_filenames is True:
            cfg["database"]["save_filenames"] = True

        if args.db_path:
            cfg["database"]["directory"] = args.db_path

        if args.device:
            cfg["general"]["device"] = args.device

        return cfg
