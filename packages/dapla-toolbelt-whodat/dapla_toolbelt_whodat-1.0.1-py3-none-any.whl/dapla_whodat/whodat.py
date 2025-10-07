import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import pandas as pd
import polars as pl

from .client.client import _client
from .model import WhodatModifiers
from .model import WhodatRequest
from .model import WhodatVariables
from .result import Result
from .utils import running_asyncio_loop


class Whodat:
    """Main class for performing Whodat personal ID searches."""

    @staticmethod
    def from_pandas(dataframe: pd.DataFrame) -> "Whodat._MethodSelector":
        """Initiate a Whodat search from a Pandas DataFrame.

        Args:
            dataframe (pd.DataFrame): Pandas DataFrame containing the data to search.

        Returns:
            Whodat._MethodSelector: Intermediate class for choosing search method.
        """
        dataframe.index.name = "index"  # Ensure index has a name for later retrieval
        return Whodat._MethodSelector(pl.from_pandas(dataframe, include_index=True))

    @staticmethod
    def from_polars(dataframe: pl.DataFrame) -> "Whodat._MethodSelector":
        """Initiate a Whodat search from a Polars DataFrame.

        Args:
            dataframe (pl.DataFrame): Polars DataFrame containing the data to search.

        Returns:
            Whodat._MethodSelector: Intermediate class for choosing search method.
        """
        return Whodat._MethodSelector(dataframe)

    class _MethodSelector:
        def __init__(self, dataframe: pl.DataFrame) -> None:
            self.dataframe: pl.DataFrame = dataframe

        def search_fnr(self) -> "Whodat._VariableSelector":
            return Whodat._VariableSelector(self.dataframe)

    class _VariableSelector:
        def __init__(
            self,
            dataframe: pl.DataFrame,
        ) -> None:
            self.dataframe: pl.DataFrame = dataframe
            self.all_variables: list[list[str]] = []
            self.all_modifiers: list[WhodatModifiers] = []

        def with_search_strategy(
            self,
            variables: list[str],
            inkluder_oppholdsadresse: bool | None = None,
            soek_fonetisk: bool | None = None,
            inkluder_doede: bool | None = None,
            opplysningsgrunnlag: str | None = None,
        ) -> "Whodat._VariableSelector":
            self.all_variables.append(variables)
            self.all_modifiers.append(
                WhodatModifiers(
                    inkluderOppholdsadresse=inkluder_oppholdsadresse,
                    soekFonetisk=soek_fonetisk,
                    inkluderDoede=inkluder_doede,
                    opplysningsgrunnlag=opplysningsgrunnlag,
                )
            )

            return self

        def run(self) -> Result:
            def index_column_to_dict(
                variables: list[str], row: dict[str, Any]
            ) -> dict[str, Any]:
                if not all(var in row for var in variables):
                    raise ValueError(
                        f"Not all variables {variables} are were found in the dataframe columns {row.keys()}"
                    )

                return {var: row[var] for var in variables}

            requests: list[WhodatRequest] = []
            for variables, modifiers in zip(
                self.all_variables, self.all_modifiers, strict=True
            ):
                variables_for_row: list[WhodatVariables] = [
                    WhodatVariables.model_validate(index_column_to_dict(variables, row))
                    for row in self.dataframe.iter_rows(named=True)
                ]
                requests.append(
                    WhodatRequest(
                        whodat_variables=variables_for_row,
                        whodat_modifiers=modifiers,
                    )
                )

            whodat_client = _client()
            if running_asyncio_loop() is not None:
                with ThreadPoolExecutor(
                    1
                ) as pool:  # Run new event loop in a second worker thread if an event loop is already running
                    responses = pool.submit(
                        lambda: asyncio.run(
                            whodat_client.post_to_field_endpoint(
                                path="search",
                                timeout=600,
                                whodat_requests=requests,
                            )
                        )
                    ).result()
            else:
                responses = asyncio.run(
                    whodat_client.post_to_field_endpoint(
                        path="search",
                        timeout=600,
                        whodat_requests=requests,
                    )
                )

            if "index" in self.dataframe.columns:
                indices_original_df = self.dataframe.get_column("index").to_list()
            else:
                indices_original_df = None

            return Result(responses, indices_original_df)
