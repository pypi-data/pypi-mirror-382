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
# If not, see <https://www.gnu.org/licenses/>.

# TODO: add VTT

def main():
    import logging
    from soundprompt.config import args
    from soundprompt.config.config import load_config
    args = args.get_args()                   # noqa: E402
    cfg = load_config()                      # noqa: E402
    logging.basicConfig(level=logging.INFO)  # noqa: E402
    logger = logging.getLogger(__name__)     # noqa: E402
    logger.info("Loading model..")  # noqa: E402 sentence_transformers: ~7s delay

    from soundprompt.sound import SoundPlayer
    from soundprompt.device import get_device
    from soundprompt.console import Console, CommandLoop
    from soundprompt.retrieval.prompter import Prompter
    from soundprompt.data import database
    from sentence_transformers import SentenceTransformer
    from pynput import keyboard

    device = get_device(cfg["general"]["device"])
    logger.info(f"Requested device: {device}")

    model_name = cfg["general"]["model_name"]
    model = SentenceTransformer(model_name, device=device)
    logger.info("Model ready!")

    if args.save or args.load:
        logger.info("Loading database...")
        data = database.Data(
            config=cfg,
            model=model,
            library_directory=(args.save or args.load)
        )
        logger.info("Database ready!")

    if args.save:
        logger.info("Saving..")

        try:
            data.update()
        except Exception as e:
            logger.error(f"Failed to save - {e}")
        finally:
            logger.info("Saved")

    if args.load:
        collection = data.get_collection()
        prompter = Prompter(model=model, collection=collection)
        sound_player = SoundPlayer()

        def enter_prompt(prompt: str):
            file = prompter.prompt(prompt)

            try:
                sound_player.play(file)
            except Exception as e:
                logger.error(
                    f"Failed to play sound - {e}"
                )

        if args.prompt:
            enter_prompt(args.prompt)
        else:
            keyboard.GlobalHotKeys({
                cfg["hotkeys"]["stop_sound"]:
                    lambda: sound_player.stop()
            }).start()

            command_loop = CommandLoop()
            command_loop.event.subscribe(
                lambda cmd: enter_prompt(cmd)
            )
            console = Console(command_loop)
            command_loop.start()
            console.start()
            console.join()
            command_loop.stop()


if __name__ == "__main__":
    main()
