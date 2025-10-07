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

import sounddevice
import numpy as np
from pydub import AudioSegment


class SoundPlayer:
    def __init__(self):
        pass

    def play(self, file: str) -> None:
        segment = AudioSegment.from_file(file)
        sample_rate = segment.frame_rate
        byte_data = segment.raw_data
        dtype_map = {1: np.int8, 2: np.int16, 4: np.int32}
        samples = np.frombuffer(
            byte_data,
            dtype=dtype_map[segment.sample_width]
        )

        if segment.channels > 1:
            samples = samples.reshape((-1, segment.channels))

        sounddevice.play(
            samples,
            samplerate=sample_rate
        )

    def wait(self) -> None:
        sounddevice.wait()

    def stop(self) -> None:
        sounddevice.stop()
