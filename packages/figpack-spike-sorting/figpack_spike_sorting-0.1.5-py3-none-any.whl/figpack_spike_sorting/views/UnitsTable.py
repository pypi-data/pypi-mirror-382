"""
UnitsTable view for figpack - displays a table of units with their properties
"""

from typing import List, Optional
import json

import numpy as np

import figpack
from ..spike_sorting_extension import spike_sorting_extension
from .UnitSimilarityScore import UnitSimilarityScore
from .UnitsTableColumn import UnitsTableColumn
from .UnitsTableRow import UnitsTableRow


class UnitsTable(figpack.ExtensionView):
    """
    A view that displays a table of units with their properties and optional similarity scores
    """

    def __init__(
        self,
        *,
        columns: List[UnitsTableColumn],
        rows: List[UnitsTableRow],
        similarity_scores: Optional[List[UnitSimilarityScore]] = None,
        height: Optional[int] = 600,
    ):
        """
        Initialize a UnitsTable view

        Args:
            columns: List of UnitsTableColumn objects defining the table structure
            rows: List of UnitsTableRow objects containing the data
            similarity_scores: Optional list of UnitSimilarityScore objects
            height: Height of the view in pixels
        """
        super().__init__(
            extension=spike_sorting_extension, view_type="spike_sorting.UnitsTable"
        )
        self.columns = columns
        self.rows = rows
        self.similarity_scores = similarity_scores or []
        self.height = height

    def write_to_zarr_group(self, group: figpack.Group) -> None:
        """
        Write the UnitsTable data to a Zarr group

        Args:
            group: Zarr group to write data into
        """
        super().write_to_zarr_group(group)

        # Set view properties
        if self.height is not None:
            group.attrs["height"] = self.height

        # Store columns metadata
        columns_metadata = [col.to_dict() for col in self.columns]
        group.attrs["columns"] = columns_metadata

        # Store rows data in a zarr array
        rows_data = [row.to_dict() for row in self.rows]
        rows_json = json.dumps(rows_data).encode("utf-8")
        rows_array = np.frombuffer(rows_json, dtype=np.uint8)
        group.create_dataset(
            "rows_data",
            data=rows_array,
        )
        group.attrs["rows_data_size"] = len(rows_json)

        # Store similarity scores in a zarr array
        if self.similarity_scores:
            scores_data = [score.to_dict() for score in self.similarity_scores]
            scores_json = json.dumps(scores_data).encode("utf-8")
            scores_array = np.frombuffer(scores_json, dtype=np.uint8)
            group.create_dataset(
                "similarity_scores_data",
                data=scores_array,
            )
            group.attrs["similarity_scores_data_size"] = len(scores_json)
