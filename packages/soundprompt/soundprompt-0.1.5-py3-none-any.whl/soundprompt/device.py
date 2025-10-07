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

class NoCUDAError(Exception):
    """
    Exception raised when CUDA is requested, but it's unavailable
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def get_device(device: str | None = None) -> str:
    import torch
    cuda_available = torch.cuda.is_available()

    if (
        device is not None and
        device.startswith("cuda") and not cuda_available
    ):
        raise NoCUDAError(
            f"CUDA requested but not available: {device}"
        )

    if device is None and not torch.cuda.is_available():
        return "cpu"

    return device
