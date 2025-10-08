# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from relace import Relace, AsyncRelace
from tests.utils import assert_matches_type
from relace.types import RepoInfo

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFile:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Relace) -> None:
        file = client.repo.file.delete(
            file_path="file_path",
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(RepoInfo, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Relace) -> None:
        response = client.repo.file.with_raw_response.delete(
            file_path="file_path",
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(RepoInfo, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Relace) -> None:
        with client.repo.file.with_streaming_response.delete(
            file_path="file_path",
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(RepoInfo, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Relace) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_id` but received ''"):
            client.repo.file.with_raw_response.delete(
                file_path="file_path",
                repo_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_path` but received ''"):
            client.repo.file.with_raw_response.delete(
                file_path="",
                repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_download(self, client: Relace) -> None:
        file = client.repo.file.download(
            file_path="file_path",
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_download(self, client: Relace) -> None:
        response = client.repo.file.with_raw_response.download(
            file_path="file_path",
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_download(self, client: Relace) -> None:
        with client.repo.file.with_streaming_response.download(
            file_path="file_path",
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(object, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_download(self, client: Relace) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_id` but received ''"):
            client.repo.file.with_raw_response.download(
                file_path="file_path",
                repo_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_path` but received ''"):
            client.repo.file.with_raw_response.download(
                file_path="",
                repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload(self, client: Relace) -> None:
        file = client.repo.file.upload(
            file_path="file_path",
            body=b"raw file contents",
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(RepoInfo, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_upload(self, client: Relace) -> None:
        response = client.repo.file.with_raw_response.upload(
            file_path="file_path",
            body=b"raw file contents",
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(RepoInfo, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_upload(self, client: Relace) -> None:
        with client.repo.file.with_streaming_response.upload(
            file_path="file_path",
            body=b"raw file contents",
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(RepoInfo, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_upload(self, client: Relace) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_id` but received ''"):
            client.repo.file.with_raw_response.upload(
                file_path="file_path",
                body=b"raw file contents",
                repo_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_path` but received ''"):
            client.repo.file.with_raw_response.upload(
                file_path="",
                body=b"raw file contents",
                repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )


class TestAsyncFile:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncRelace) -> None:
        file = await async_client.repo.file.delete(
            file_path="file_path",
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(RepoInfo, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncRelace) -> None:
        response = await async_client.repo.file.with_raw_response.delete(
            file_path="file_path",
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(RepoInfo, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncRelace) -> None:
        async with async_client.repo.file.with_streaming_response.delete(
            file_path="file_path",
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(RepoInfo, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncRelace) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_id` but received ''"):
            await async_client.repo.file.with_raw_response.delete(
                file_path="file_path",
                repo_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_path` but received ''"):
            await async_client.repo.file.with_raw_response.delete(
                file_path="",
                repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_download(self, async_client: AsyncRelace) -> None:
        file = await async_client.repo.file.download(
            file_path="file_path",
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_download(self, async_client: AsyncRelace) -> None:
        response = await async_client.repo.file.with_raw_response.download(
            file_path="file_path",
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_download(self, async_client: AsyncRelace) -> None:
        async with async_client.repo.file.with_streaming_response.download(
            file_path="file_path",
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(object, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_download(self, async_client: AsyncRelace) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_id` but received ''"):
            await async_client.repo.file.with_raw_response.download(
                file_path="file_path",
                repo_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_path` but received ''"):
            await async_client.repo.file.with_raw_response.download(
                file_path="",
                repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload(self, async_client: AsyncRelace) -> None:
        file = await async_client.repo.file.upload(
            file_path="file_path",
            body=b"raw file contents",
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(RepoInfo, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_upload(self, async_client: AsyncRelace) -> None:
        response = await async_client.repo.file.with_raw_response.upload(
            file_path="file_path",
            body=b"raw file contents",
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(RepoInfo, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_upload(self, async_client: AsyncRelace) -> None:
        async with async_client.repo.file.with_streaming_response.upload(
            file_path="file_path",
            body=b"raw file contents",
            repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(RepoInfo, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_upload(self, async_client: AsyncRelace) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_id` but received ''"):
            await async_client.repo.file.with_raw_response.upload(
                file_path="file_path",
                body=b"raw file contents",
                repo_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_path` but received ''"):
            await async_client.repo.file.with_raw_response.upload(
                file_path="",
                body=b"raw file contents",
                repo_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )
