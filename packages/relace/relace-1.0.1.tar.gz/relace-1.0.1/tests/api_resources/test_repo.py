# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from relace import Relace, AsyncRelace
from tests.utils import assert_matches_type
from relace.types import (
    RepoInfo,
    RepoMetadata,
    RepoListResponse,
    RepoCloneResponse,
    RepoRetrieveResponse,
)
from relace._utils import parse_datetime

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRepo:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Relace) -> None:
        repo = client.repo.create()
        assert_matches_type(RepoInfo, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Relace) -> None:
        repo = client.repo.create(
            auto_index=True,
            metadata={"foo": "string"},
            source={
                "type": "git",
                "url": "https://example.com",
                "branch": "branch",
                "hash": "hash",
            },
        )
        assert_matches_type(RepoInfo, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Relace) -> None:
        response = client.repo.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = response.parse()
        assert_matches_type(RepoInfo, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Relace) -> None:
        with client.repo.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = response.parse()
            assert_matches_type(RepoInfo, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Relace) -> None:
        repo = client.repo.retrieve(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            query="x",
        )
        assert_matches_type(RepoRetrieveResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Relace) -> None:
        repo = client.repo.retrieve(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            query="x",
            branch="branch",
            hash="hash",
            include_content=True,
            rerank=True,
            score_threshold=0,
            token_limit=0,
        )
        assert_matches_type(RepoRetrieveResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Relace) -> None:
        response = client.repo.with_raw_response.retrieve(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            query="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = response.parse()
        assert_matches_type(RepoRetrieveResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Relace) -> None:
        with client.repo.with_streaming_response.retrieve(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            query="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = response.parse()
            assert_matches_type(RepoRetrieveResponse, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Relace) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_id` but received ''"):
            client.repo.with_raw_response.retrieve(
                repo_id="",
                query="x",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Relace) -> None:
        repo = client.repo.update(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(RepoInfo, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Relace) -> None:
        repo = client.repo.update(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            metadata={"foo": "string"},
            source={
                "files": [
                    {
                        "content": "content",
                        "filename": "filename",
                    }
                ],
                "type": "files",
            },
        )
        assert_matches_type(RepoInfo, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Relace) -> None:
        response = client.repo.with_raw_response.update(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = response.parse()
        assert_matches_type(RepoInfo, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Relace) -> None:
        with client.repo.with_streaming_response.update(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = response.parse()
            assert_matches_type(RepoInfo, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Relace) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_id` but received ''"):
            client.repo.with_raw_response.update(
                repo_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Relace) -> None:
        repo = client.repo.list()
        assert_matches_type(RepoListResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Relace) -> None:
        repo = client.repo.list(
            created_after=parse_datetime("2019-12-27T18:11:19.117Z"),
            created_before=parse_datetime("2019-12-27T18:11:19.117Z"),
            filter_metadata="filter_metadata",
            order_by="created_at",
            order_descending=True,
            page_size=1,
            page_start=0,
        )
        assert_matches_type(RepoListResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Relace) -> None:
        response = client.repo.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = response.parse()
        assert_matches_type(RepoListResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Relace) -> None:
        with client.repo.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = response.parse()
            assert_matches_type(RepoListResponse, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Relace) -> None:
        repo = client.repo.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert repo is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Relace) -> None:
        response = client.repo.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = response.parse()
        assert repo is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Relace) -> None:
        with client.repo.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = response.parse()
            assert repo is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Relace) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_id` but received ''"):
            client.repo.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_clone(self, client: Relace) -> None:
        repo = client.repo.clone(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(RepoCloneResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_clone_with_all_params(self, client: Relace) -> None:
        repo = client.repo.clone(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            commit="commit",
        )
        assert_matches_type(RepoCloneResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_clone(self, client: Relace) -> None:
        response = client.repo.with_raw_response.clone(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = response.parse()
        assert_matches_type(RepoCloneResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_clone(self, client: Relace) -> None:
        with client.repo.with_streaming_response.clone(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = response.parse()
            assert_matches_type(RepoCloneResponse, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_clone(self, client: Relace) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_id` but received ''"):
            client.repo.with_raw_response.clone(
                repo_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Relace) -> None:
        repo = client.repo.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(RepoMetadata, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Relace) -> None:
        response = client.repo.with_raw_response.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = response.parse()
        assert_matches_type(RepoMetadata, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Relace) -> None:
        with client.repo.with_streaming_response.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = response.parse()
            assert_matches_type(RepoMetadata, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Relace) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_id` but received ''"):
            client.repo.with_raw_response.get(
                "",
            )


class TestAsyncRepo:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncRelace) -> None:
        repo = await async_client.repo.create()
        assert_matches_type(RepoInfo, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncRelace) -> None:
        repo = await async_client.repo.create(
            auto_index=True,
            metadata={"foo": "string"},
            source={
                "type": "git",
                "url": "https://example.com",
                "branch": "branch",
                "hash": "hash",
            },
        )
        assert_matches_type(RepoInfo, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncRelace) -> None:
        response = await async_client.repo.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = await response.parse()
        assert_matches_type(RepoInfo, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncRelace) -> None:
        async with async_client.repo.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = await response.parse()
            assert_matches_type(RepoInfo, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncRelace) -> None:
        repo = await async_client.repo.retrieve(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            query="x",
        )
        assert_matches_type(RepoRetrieveResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncRelace) -> None:
        repo = await async_client.repo.retrieve(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            query="x",
            branch="branch",
            hash="hash",
            include_content=True,
            rerank=True,
            score_threshold=0,
            token_limit=0,
        )
        assert_matches_type(RepoRetrieveResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncRelace) -> None:
        response = await async_client.repo.with_raw_response.retrieve(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            query="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = await response.parse()
        assert_matches_type(RepoRetrieveResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncRelace) -> None:
        async with async_client.repo.with_streaming_response.retrieve(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            query="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = await response.parse()
            assert_matches_type(RepoRetrieveResponse, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncRelace) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_id` but received ''"):
            await async_client.repo.with_raw_response.retrieve(
                repo_id="",
                query="x",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncRelace) -> None:
        repo = await async_client.repo.update(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(RepoInfo, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncRelace) -> None:
        repo = await async_client.repo.update(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            metadata={"foo": "string"},
            source={
                "files": [
                    {
                        "content": "content",
                        "filename": "filename",
                    }
                ],
                "type": "files",
            },
        )
        assert_matches_type(RepoInfo, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncRelace) -> None:
        response = await async_client.repo.with_raw_response.update(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = await response.parse()
        assert_matches_type(RepoInfo, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncRelace) -> None:
        async with async_client.repo.with_streaming_response.update(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = await response.parse()
            assert_matches_type(RepoInfo, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncRelace) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_id` but received ''"):
            await async_client.repo.with_raw_response.update(
                repo_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncRelace) -> None:
        repo = await async_client.repo.list()
        assert_matches_type(RepoListResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncRelace) -> None:
        repo = await async_client.repo.list(
            created_after=parse_datetime("2019-12-27T18:11:19.117Z"),
            created_before=parse_datetime("2019-12-27T18:11:19.117Z"),
            filter_metadata="filter_metadata",
            order_by="created_at",
            order_descending=True,
            page_size=1,
            page_start=0,
        )
        assert_matches_type(RepoListResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncRelace) -> None:
        response = await async_client.repo.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = await response.parse()
        assert_matches_type(RepoListResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncRelace) -> None:
        async with async_client.repo.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = await response.parse()
            assert_matches_type(RepoListResponse, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncRelace) -> None:
        repo = await async_client.repo.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert repo is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncRelace) -> None:
        response = await async_client.repo.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = await response.parse()
        assert repo is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncRelace) -> None:
        async with async_client.repo.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = await response.parse()
            assert repo is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncRelace) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_id` but received ''"):
            await async_client.repo.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_clone(self, async_client: AsyncRelace) -> None:
        repo = await async_client.repo.clone(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(RepoCloneResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_clone_with_all_params(self, async_client: AsyncRelace) -> None:
        repo = await async_client.repo.clone(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            commit="commit",
        )
        assert_matches_type(RepoCloneResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_clone(self, async_client: AsyncRelace) -> None:
        response = await async_client.repo.with_raw_response.clone(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = await response.parse()
        assert_matches_type(RepoCloneResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_clone(self, async_client: AsyncRelace) -> None:
        async with async_client.repo.with_streaming_response.clone(
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = await response.parse()
            assert_matches_type(RepoCloneResponse, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_clone(self, async_client: AsyncRelace) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_id` but received ''"):
            await async_client.repo.with_raw_response.clone(
                repo_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncRelace) -> None:
        repo = await async_client.repo.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(RepoMetadata, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncRelace) -> None:
        response = await async_client.repo.with_raw_response.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = await response.parse()
        assert_matches_type(RepoMetadata, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncRelace) -> None:
        async with async_client.repo.with_streaming_response.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = await response.parse()
            assert_matches_type(RepoMetadata, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncRelace) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_id` but received ''"):
            await async_client.repo.with_raw_response.get(
                "",
            )
