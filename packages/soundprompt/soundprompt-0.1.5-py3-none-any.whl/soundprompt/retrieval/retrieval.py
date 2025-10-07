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
import numpy as np
from sentence_transformers import util
from collections import defaultdict
if TYPE_CHECKING:
    from torch import Tensor
    from chromadb import Collection, QueryResult

def get_top_results(
    collection: Collection,
    embedding: Tensor,
    limit: int = 5
) -> QueryResult:
    # TODO: add Reranking & Rerank model
    # (OPTIONAL)
    return collection.query(
        query_embeddings=[embedding],
        n_results=limit
    )


def deduplicate_results(result: QueryResult) -> QueryResult:
    """
    Keep only the first tag of an item
    """
    unique_metadatas = []
    unique_distances = []
    seen_items = set()

    for result_id, metadata, distance in zip(
        result["ids"][0],
        result["metadatas"][0],
        result["distances"][0]
    ):
        if result_id not in seen_items:
            seen_items.add(result_id)
            unique_metadatas.append(metadata)
            unique_distances.append(distance)

    return {
        "metadatas": [unique_metadatas],
        "distances": [unique_distances]
    }


def get_cumulative_file_scores(
    collection: Collection,
    embedding: Tensor,
    result: QueryResult
) -> dict[str]:
    """
    Scores simularity of each result file
    by comparing each of its tags
    to the provided embeddings

    Returns the cumulative scores
    """

    file_scores = defaultdict(float)
    tag_counts = defaultdict(int)

    for meta in result["metadatas"][0]:
        tag_results = collection.get(
            where={"tag_file": meta["tag_file"]},
            include=["embeddings", "metadatas"]
        )

        for tag_metadata, tag_embedding in zip(
            tag_results["metadatas"],
            np.array(tag_results["embeddings"], dtype=np.float32)
        ):
            # Get tag's simularity to prompt, save as score
            score = util.cos_sim(
                embedding,
                tag_embedding
            ).item()

            key = tag_metadata["audio_file"]
            file_scores[key] += score
            tag_counts[key] += 1

    # Normalize by actual number of tags summed
    for key in file_scores:
        file_scores[key] /= tag_counts[key]

    return file_scores


def get_highest_scored_file(file_scores: dict[str]) -> str:
    """
    Returns the file with the highest score
    """
    return max(file_scores, key=file_scores.get)
