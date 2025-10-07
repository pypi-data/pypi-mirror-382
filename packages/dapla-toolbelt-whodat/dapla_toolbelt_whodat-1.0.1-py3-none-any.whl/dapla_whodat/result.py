from typing import Any

from pydantic import BaseModel

from .model import WhodatResponse


class SingleRowInfo(BaseModel):
    """Information about the personal ID search for a single row.

    Attributes:
        index_original_df (int): The index of the row in the original dataframe.
        number_of_found_ids (int): The number of personal IDs found for the row. 1 if unique.
        unique_response_step_number (int): The 1-indexed search algorithm that gave a unique result.
            None if no unique result was found.
    """

    index_fnr_search_df: int
    index_original_df: int | None
    number_of_found_ids: int
    unique_response_step_number: int | None


class Result:
    """Result of a Whodat personal ID search."""

    def __init__(
        self,
        responses: list[WhodatResponse],
        indices: list[int] | None = None,
    ) -> None:
        """Result of a Whodat personal ID search.

        Args:
            responses (list[tuple[WhodatResponse, int]]): List of (responses, index) from Whodat service.
            indices: list[int] | None = None: Original indices from dataframe, if available.
        """
        self.indices_original_df = indices
        self.responses = responses
        self._details: list[dict[str, Any]] = self._generate_details()

    def to_list(self, exclude_nones: bool | None = False) -> list[str | None]:
        """Convert the result to a list of personal IDs. By default, returns None if a unique ID was not found.

        Args:
            exclude_nones (bool, optional): Exclude "None" from requests that did not yield a unique result. Defaults to False.

        Returns:
            list[str | None]: _description_
        """
        result: list[str | None] = []
        for r in self.details:
            if r.get("number_of_found_ids") == 1:
                step_number = (
                    (r["unique_response_step_number"] - 1)
                    if r["unique_response_step_number"] is not None
                    else (len(self.responses) - 1)
                )
                response = self.responses[step_number]
                found_ids = response.found_personal_ids[r["index_fnr_search_df"]]
                result.append(found_ids[0])
            elif not exclude_nones:
                result.append(None)

        return result

    def to_dict_from_original_indices(self) -> dict[int, str]:
        """Convert the result to a dictionary mapping original dataframe indices to personal IDs.

        Only includes entries with a unique personal ID.

        Raises:
            ValueError: If original indices are not available in the DataFrame.

        Returns:
            dict[int, str]: A dictionary mapping original dataframe indices to personal IDs.
        """
        if self.indices_original_df is None:
            raise ValueError(
                "Original indices are not available in DataFrame. If using Polars, include a column named 'index' representing the original indices."
            )

        results = {}
        for r in self.details:
            step_number = (
                (r["unique_response_step_number"] - 1)
                if r["unique_response_step_number"] is not None
                else (len(self.responses) - 1)
            )
            index_fnr_search = r["index_fnr_search_df"]
            index_original_df = r["index_original_df"]
            if r.get("number_of_found_ids") == 1:
                response = self.responses[step_number]
                found_ids = response.found_personal_ids[index_fnr_search]
                results[index_original_df] = found_ids[0]

        return results

    def _generate_details(self) -> list[dict[str, Any]]:
        details: dict[int, dict[str, Any]] = {}
        for step_number, r in enumerate(self.responses, start=1):
            for i, found_personal_ids in enumerate(r.found_personal_ids):
                if (
                    single_row_info := details.get(i)
                ) is not None and single_row_info.get("number_of_found_ids") == 1:
                    continue  # Already have a unique result for this row, skip further processing

                number_of_found_ids = len(found_personal_ids)

                try:
                    index_original_df = (
                        self.indices_original_df[i]
                        if self.indices_original_df is not None
                        else None
                    )
                except IndexError:
                    index_original_df = None

                details[i] = SingleRowInfo(
                    index_fnr_search_df=i,
                    index_original_df=index_original_df,
                    number_of_found_ids=number_of_found_ids,
                    unique_response_step_number=(
                        step_number if number_of_found_ids == 1 else None
                    ),
                ).model_dump()

        return list(details.values())

    @property
    def details(self) -> list[dict[str, Any]]:
        """Return detailed information about the personal ID search for each row.

        Returns:
            list[dict[str, Any]]: A list of dictionaries with information about each row's search result.
        """
        return self._details
