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

from threading import Thread, Event
from abc import ABC, abstractmethod


class Worker(Thread, ABC):
    """
    Base class for threaded workers.
    """

    _stop_event: Event

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = Event()

    @abstractmethod
    def run(self) -> None:
        """
        Subclasses must implement this method
        Should check self.is_stopped
        """

        pass

    def stop(self) -> None:
        """
        Signal the thread to stop.
        """

        self._stop_event.set()

    def is_stopped(self) -> bool:
        return self._stop_event.is_set()
