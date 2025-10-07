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
from typing import TYPE_CHECKING
from soundprompt.retrieval import retrieval
if TYPE_CHECKING:
    import chromadb
    from sentence_transformers import SentenceTransformer


class Prompter:
    """
    Class to send prompts and receive responses
    """

    model: SentenceTransformer
    collection: chromadb.Collection

    def __init__(
        self,
        model: SentenceTransformer,
        collection: chromadb.Collection
    ):
        self.model = model
        self.collection = collection

    def prompt(self, prompt: str) -> str:
        prompt_embedding = self.model.encode(
            prompt.lower(),
            show_progress_bar=False
        )

        top_results = retrieval.get_top_results(
            self.collection,
            embedding=prompt_embedding,
            limit=10
        )

        deduplicated_top_results = retrieval.deduplicate_results(
            top_results
        )

        scored_files = retrieval.get_cumulative_file_scores(
            self.collection,
            embedding=prompt_embedding,
            result=deduplicated_top_results
        )

        return retrieval.get_highest_scored_file(scored_files)
