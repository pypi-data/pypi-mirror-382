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

"""
Arguments passed via CLI
Controls behavior and app-specific global settings
"""

from pathlib import Path
from argparse import (
    ArgumentParser,
    Namespace
)

parser = ArgumentParser(
    prog="SoundPrompt",
    description="Your sounds, triggered by AI"
)

parser.add_argument(
    "--config",
    type=Path,
    help="The path to the config.toml file"
)

parser.add_argument(
    "-s",
    "--save",
    type=Path,
    help="Save a sound library"
)

parser.add_argument(
    "--save-filenames",
    action="store_true",
    help="""
    Save filenames as tags. WARNING if you use this:
    ALL your files must be named with real words
    or you'll get unpredictable results
    """
)

parser.add_argument(
    "-l",
    "--load",
    type=Path,
    help="Load a sound library"
)

parser.add_argument(
    "-p",
    "--prompt",
    type=str,
    help="Prompt for what sound to play"
)

parser.add_argument(
    "--db-path",
    type=Path,
    help="Path to database directory"
)

parser.add_argument(
    "--device",
    type=str,
    help="The device to use for AI (e.g. cuda:0 or cpu"
)

parser.add_argument(
    "--debug",
    action="store_true",
    help="Enable debug messages"
)

parser.add_argument(
    "--version",
    action="store_true"
)

parsed_args = parser.parse_args()


def get_args() -> Namespace:
    return parsed_args
