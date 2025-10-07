from __future__ import annotations
from pathlib import Path
from typing import List, Literal, TYPE_CHECKING

from adaptive_sdk.graphql_client import (
    DatasetCreate,
    Upload,
    LoadDatasetCreateDataset,
    ListDatasetsDatasets,
    DatasetData,
)

from .base_resource import SyncAPIResource, AsyncAPIResource, UseCaseResource

if TYPE_CHECKING:
    from adaptive_sdk.client import Adaptive, AsyncAdaptive


class Datasets(SyncAPIResource, UseCaseResource):  # type: ignore[misc]
    """
    Resource to interact with file datasets.
    """

    def __init__(self, client: Adaptive) -> None:
        SyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)

    def upload(
        self,
        file_path: str,
        dataset_key: str,
        name: str | None = None,
        use_case: str | None = None,
    ) -> LoadDatasetCreateDataset:
        """
         Upload a dataset from a file. File must be jsonl, where each line should match structure in example below.

        Args:
            file_path: Path to jsonl file.
            dataset_key: New dataset key.
            name: Optional name to render in UI; if `None`, defaults to same as `dataset_key`.

        Example:
        ```
        {"messages": [{"role": "system", "content": "<optional system prompt>"}, {"role": "user", "content": "<user content>"}, {"role": "assistant", "content": "<assistant answer>"}], "completion": "hey"}
        ```
        """
        input = DatasetCreate(
            useCase=self.use_case_key(use_case),
            name=name if name else dataset_key,
            key=dataset_key,
        )
        filename = Path(file_path).stem
        with open(file_path, "rb") as f:
            file_upload = Upload(filename=filename, content=f, content_type="application/jsonl")
            return self._gql_client.load_dataset(input=input, file=file_upload).create_dataset

    def list(
        self,
        use_case: str | None = None,
    ) -> List[ListDatasetsDatasets]:
        """
        List previously uploaded datasets.
        """
        return self._gql_client.list_datasets(self.use_case_key(use_case)).datasets

    def get(self, key: str, use_case: str | None = None) -> DatasetData | None:
        """
        Get details for dataset.

        Args:
            key: Dataset key.
        """
        return self._gql_client.describe_dataset(key, self.use_case_key(use_case)).dataset

    def delete(self, key: str, use_case: str | None = None) -> bool:
        """Delete dataset."""
        return self._gql_client.delete_dataset(id_or_key=key, use_case=self.use_case_key(use_case)).delete_dataset


class AsyncDatasets(AsyncAPIResource, UseCaseResource):  # type: ignore[misc]
    def __init__(self, client: AsyncAdaptive) -> None:
        AsyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)

    async def upload(
        self,
        file_path: str,
        dataset_key: str,
        name: str | None = None,
        use_case: str | None = None,
    ) -> LoadDatasetCreateDataset:
        """
        Upload a dataset from a file. File must be jsonl, where each line should match structure in example below.

        Args:
            file_path: Path to jsonl file.
            dataset_key: New dataset key.
            name: Optional name to render in UI; if `None`, defaults to same as `dataset_key`.

        Example:
        ```
        {"messages": [{"role": "system", "content": "<optional system prompt>"}, {"role": "user", "content": "<user content>"}, {"role": "assistant", "content": "<assistant answer>"}], "completion": "hey"}
        ```
        """
        input = DatasetCreate(
            useCase=self.use_case_key(use_case),
            name=name if name else dataset_key,
            key=dataset_key,
        )
        filename = Path(file_path).stem
        with open(file_path, "rb") as f:
            file_upload = Upload(filename=filename, content=f, content_type="application/jsonl")
            upload_result = await self._gql_client.load_dataset(input=input, file=file_upload)
            return upload_result.create_dataset

    async def list(
        self,
        use_case: str | None = None,
    ) -> List[ListDatasetsDatasets]:
        """
        List previously uploaded datasets.
        """
        results = await self._gql_client.list_datasets(self.use_case_key(use_case))
        return results.datasets

    async def get(self, key: str, use_case: str | None = None) -> DatasetData | None:
        """
        Get details for dataset.

        Args:
            key: Dataset key.
        """
        result = await self._gql_client.describe_dataset(key, self.use_case_key(use_case))
        return result.dataset

    async def delete(self, key: str, use_case: str | None = None) -> bool:
        """Delete dataset."""
        return (
            await self._gql_client.delete_dataset(id_or_key=key, use_case=self.use_case_key(use_case))
        ).delete_dataset
