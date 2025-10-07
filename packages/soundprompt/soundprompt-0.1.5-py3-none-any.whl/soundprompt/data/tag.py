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

from dataclasses import dataclass


class Tags:
    """
    Class that manages / represents a list of file tags
    """

    _set: set[str]
    tags: list[str]

    def __init__(self, tags: list[str] | None = None):
        self._set = set()
        self.tags = []
        if tags:
            self.add_many(tags)

    def add(self, tag: str):
        if tag not in self:
            self.tags.append(tag)
            self._set.add(tag)

    def add_many(self, tags: list[str]):
        for tag in tags:
            self.add(tag)

    def __eq__(self, other):
        if not isinstance(other, Tags):
            return NotImplemented

        return self._set == other._set

    def __getitem__(self, index):
        return self.tags[index]

    def __iter__(self):
        return iter(self.tags)

    def __len__(self):
        return len(self.tags)

    def __contains__(self, tag: str):
        return tag in self._set


@dataclass
class TagData:
    """
    Data class containing common tag file info
    """

    file_path: str
    file_name: str
    directory: str | None = None
    tags: Tags | None = None


class TaggedFileMissingError(Exception):
    """
    Exception raised for when a file associated with a tag is missing.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
