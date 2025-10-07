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

import asyncio
from signal import signal, SIGINT, SIG_IGN
from soundprompt.event import Event
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.patch_stdout import patch_stdout


class CommandQueue:
    """
    Handles processing of commands asynchronously
    """

    _running: bool
    _queue: asyncio.Queue[str]
    event: Event

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._queue = asyncio.Queue()
        self.event = Event()

    async def run(self) -> None:
        self._running = True

        while self._running:
            try:
                cmd = await self._queue.get()
            except asyncio.CancelledError:
                break

            try:
                await self.event.notify_async(cmd)
            finally:
                self._queue.task_done()

    def stop(self):
        self._running = False

    async def submit(self, cmd: str) -> None:
        await self._queue.put(cmd)

    def submit_threadsafe(self, cmd: str) -> None:
        loop = asyncio.get_event_loop()

        asyncio.run_coroutine_threadsafe(
            self.submit(cmd),
            loop
        )


class Console:
    """
    Class for CLI console
    """

    commandQueue: CommandQueue
    history: InMemoryHistory
    _prompt_session: PromptSession
    _running: bool

    def __init__(self, commandQueue: CommandQueue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commandQueue = commandQueue
        history = InMemoryHistory()
        self.history = history
        self._prompt_session = PromptSession(
            message="> ",
            auto_suggest=False,
            history=history,
            enable_suspend=False,
            enable_open_in_editor=False,
            enable_system_prompt=False,
            mouse_support=False,
            validate_while_typing=False,
            complete_while_typing=False,
            reserve_space_for_menu=0
        )

    async def send_command(self, command: str) -> None:
        await self.commandQueue.submit(command)

    async def run(self) -> None:
        self._running = True

        with patch_stdout():
            while self._running:
                try:
                    cmd = await self._prompt_session.prompt_async()
                    cmd = cmd .strip().lower()

                    if not cmd:
                        continue

                    await self.send_command(cmd)
                except (
                    asyncio.exceptions.CancelledError,
                    KeyboardInterrupt,
                    EOFError
                ):
                    print("\nInterrupted. Exiting...")

                    signal(SIGINT, SIG_IGN)

                    break

    def stop(self):
        self._running = False
