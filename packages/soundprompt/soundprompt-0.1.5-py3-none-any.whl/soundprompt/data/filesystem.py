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

import os
from typing import Generator


def split_extension(path: str) -> tuple[str, str]:
    return os.path.splitext(path)


class RecursiveScanDir:
    """
    Recursively scan a directory very quickly,
    optionally filter files and extensions.
    """

    path: str
    only_files: bool

    def __init__(
        self,
        path: str,
        extensions: str | list[str] | None = None,
        only_files: bool = False
    ):
        self.path = path
        if extensions is not None:
            if isinstance(extensions, str):
                extensions = [extensions]

            # Extensions: normalize lowercase & dot
            self.extensions = {
                ext.lower()
                if ext.startswith(".") else f".{ext.lower()}"
                for ext in extensions
            }
        self.only_files = only_files

    def __iter__(self) -> Generator[
            tuple[os.DirEntry, str | None, str | None],
            None,
            None]:
        yield from self._scan(self.path)

    def _scan(self, path: str) -> Generator[
            tuple[os.DirEntry, str | None, str | None],
            None,
            None]:
        for entry in os.scandir(path):
            is_dir = entry.is_dir(follow_symlinks=False)

            if is_dir:  # recursive, add subdir's contents
                yield from self._scan(entry.path)
            else:
                if self.extensions is not None:
                    stem, ext = split_extension(entry.name)

                    if ext.lower() in self.extensions:
                        # (we pass the stem & ext so they
                        # won't have to splitext a sec time)
                        yield entry, stem, ext
                else:
                    yield entry, None, None

            # Add the dir itself too if allowed
            if not self.only_files and is_dir:
                yield entry, None, None


"""
Validation for working with essential files
"""


def validate_path(path: str):
    if not os.path.exists(path):
        raise FileExistsError(f"{path} doesn't exist.")


def validate_directory(directory: str):
    validate_path(directory)

    if not os.path.isdir(directory):
        raise NotADirectoryError(f"{directory} is not a directory.")


def validate_file(file: str):
    validate_path(file)

    if not os.path.isfile(file):
        raise FileNotFoundError(f"{file} is not a file.")
