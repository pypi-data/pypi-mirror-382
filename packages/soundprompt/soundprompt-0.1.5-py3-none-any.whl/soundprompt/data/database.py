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
import logging
import re
import chromadb
import os
from soundprompt.config.toml.structure import Config
from soundprompt.data.tag import (
    TaggedFileMissingError,
    TagData,
    Tags
)
from soundprompt.data import filesystem
from sentence_transformers import SentenceTransformer


# TODO: add progress bar or loading animation
# 100 files takes ~5 seconds to save
# massive libraries could take minutes
class Data:
    """
    Manages a sound library with tag-based metadata and AI embeddings.

    Responsibilities:
    - Validate and manage the data and library directories.
    - Iterate and process tag files and associated audio files.
    - Store metadata in a database (e.g., SQLite or ChromaDB).
    - Encode tags using a SentenceTransformer and manage embeddings.
    - Provide retrieval of data.

    Notes:
    - Tag files must exactly match the associated audio file name
    with a '.txt' suffix.
    - Audio file extensions and tag normalization are handled
    internally.
    - Designed to handle large libraries efficiently
    (hundreds of thousands of files).
    """

    config: Config
    logger: logging.Logger
    client: chromadb.PersistentClient
    model: SentenceTransformer
    directory: str
    library_directory: str
    collection_name: str

    def __init__(
        self,
        config: Config,
        model: SentenceTransformer,
        library_directory: str,
        debug: bool = False
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)

        self.config = config
        self.model = model

        data_directory = config.database.directory
        for d in [data_directory, library_directory]:
            filesystem.validate_directory(d)

        self.directory = data_directory
        self.library_directory = library_directory
        self.set_collection_name(library_directory)
        self.client = chromadb.PersistentClient(
            path=data_directory,
            settings=chromadb.Settings(
                anonymized_telemetry=False
            )
        )

    def set_collection_name(self, value: str) -> None:
        """
        Sanitizes a string to be a valid ChromaDB Collection name
        - Replaces symbols and whitespaces with an underscore
        """
        pattern = re.compile(r"(\s|\W)")
        self.collection_name = re.sub(pattern, "_", str(value))

    def create_key(self, *parts: str) -> str:
        """
        Standardized format for collection key
        Should always be used when saving entries
        """

        return "::".join(str(p) for p in parts if p)

    def collection_update_config(
        self,
        collection: chromadb.Collection
    ) -> None:
        """
        Saves the config's settings to the database collection
        """

        config_json = self.config.to_json()

        collection.upsert(
            ids=[self.create_key(
                self.library_directory,
                "settings",
            )],
            documents=[config_json]
        )

        self.logger.debug(f"Updating settings: {config_json}")

    def collection_get_config(
        self,
        collection: chromadb.Collection
    ) -> Config:
        item = collection.get(
            ids=[self.create_key(
                self.library_directory,
                "settings"
            )],
            include=["documents"]
        )

        documents = item.get("documents", [])
        config = Config()

        if documents:
            try:
                config = Config.from_json(documents[0])
            except Exception as e:
                self.logger.error(f"Failed to parse config - {e}")
            else:
                if item["ids"]:
                    return config
        else:
            self.logger.debug(
                "No saved config for this library."
                " Is this the first time saving?"
            )

        return config

    def collection_get_file_tags(
        self,
        collection: chromadb.Collection,
        tag_data: TagData
    ) -> Tags:
        with open(
            tag_data.file_path,
            mode="r",
            encoding="utf-8"
        ) as f:
            tags = Tags([
                tag.strip()
                for tag in f.read().lower().split(",")
            ])

            if self.config.database.save_filenames:
                file_name, _ = filesystem.split_extension(tag_data.file_name)
                tags.add(file_name.lower())

            return tags

    def collection_update_file(
        self,
        collection: chromadb.Collection,
        tag_data: TagData,
        audio_file_path: str
    ) -> None:
        """
        Saves a file to a database collection
        - Adds the tag file path
        - Adds the audio file path
        - AI Encodes each of its tags
        """

        # First remove the file's entry
        # (we have to calculate all tags anyway)
        # + this fixes tags not being removed
        self.collection_remove_file(
            collection,
            audio_file_path=audio_file_path
        )

        if tag_data.tags is None:
            tag_data.tags = self.collection_get_file_tags(
                collection,
                TagData(
                    file_name=tag_data.file_name,
                    file_path=tag_data.file_path
                )
            )

        for tag in tag_data.tags:
            collection.upsert(
                ids=[
                    self.create_key(
                        self.library_directory,
                        tag_data.file_name,
                        tag
                    )
                ],
                embeddings=[
                    self.model.encode(tag, show_progress_bar=False)
                ],
                metadatas=[{
                    "tag_file": tag_data.file_path,
                    "audio_file": audio_file_path,
                    "tag": tag
                }]
            )

    def collection_remove_file(
        self,
        collection: chromadb.Collection,
        audio_file_path
    ) -> None:
        collection.delete(
            where={"audio_file": audio_file_path}
        )

    def update(self) -> None:
        """
        Updates the library in the database
        - Iterates all the files
        - Add missing entries to collection
        """

        collection = self.get_collection(True)

        force_file_update = False

        # Force an update if crucial settings have changed
        collection_config = self.collection_get_config(collection)
        if collection_config:
            if (
                self.config.database.save_filenames
                != collection_config.database.save_filenames
            ) or (
                # Models change embeddings entirely
                self.config.general.model_name
                != collection_config.general.model_name
            ):
                force_file_update = True

        file_entries = filesystem.RecursiveScanDir(
            self.library_directory,
            extensions="txt",
            only_files=True
        )

        for file_entry, file_stem, file_ext in file_entries:
            tags_file_path = file_entry.path
            tag_data = TagData(
                file_name=file_stem,
                file_path=tags_file_path,
                directory=os.path.dirname(tags_file_path)
            )

            audio_file_path = os.path.join(tag_data.directory, file_stem)
            self.logger.debug(
                f"Combining directory {tag_data.directory} "
                f"and file stem: {file_stem} "
                f"result: {audio_file_path}"
            )

            try:
                filesystem.validate_file(audio_file_path)
            except FileExistsError:
                raise TaggedFileMissingError(
                    f"Your tag {tags_file_path} was made "
                    f"for an audio file that doesn't exist: "
                    f"{audio_file_path}\n"
                    f"Make sure the tag's filename is "
                    f"EXACTLY the same as the sound's "
                    f"with .txt appended at the end. "
                    f"e.g.: awesome-explosion.mp3.txt"
                )
            finally:
                tag_data.tags = self.collection_get_file_tags(
                    collection,
                    tag_data=tag_data
                )

                existing_item = force_file_update or collection.get(
                    where={
                        "tag_file": tag_data.file_path,
                    }
                )

                if force_file_update or not existing_item["ids"]:
                    self.collection_update_file(
                        collection=collection,
                        tag_data=tag_data,
                        audio_file_path=audio_file_path
                    )
                else:
                    # Update on tag mismatch
                    db_tags = Tags([
                        db_entry["tag"]
                        for db_entry in existing_item["metadatas"]
                    ])

                    if db_tags != tag_data.tags:
                        self.collection_update_file(
                            collection=collection,
                            tag_data=tag_data,
                            audio_file_path=audio_file_path
                        )

                        self.logger.info(f"Updated {tags_file_path}")

        self.collection_update_config(collection)

        # Remove database files if invalid on system
        checked_files = set()
        results = collection.get(
            include=["metadatas"]
        )

        for result in results["metadatas"]:
            if not result:
                continue

            result_audio_file = result["audio_file"]

            if result_audio_file in checked_files:
                continue

            checked_files.add(result_audio_file)

            try:
                filesystem.validate_file(result_audio_file)
            except FileExistsError:
                self.logger.error(
                    (
                        "Removing entry for missing audio file:"
                        f" {result_audio_file}"
                    )
                )
                self.collection_remove_file(
                    collection,
                    result_audio_file
                )

    def get_collection(self, create: bool = False) -> chromadb.Collection:
        return (
            create and
            self.client.get_or_create_collection(self.collection_name)
            or self.client.get_collection(self.collection_name)
        )
