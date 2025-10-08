# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from datetime import datetime
from typing_extensions import Literal

import httpx

from .file import (
    FileResource,
    AsyncFileResource,
    FileResourceWithRawResponse,
    AsyncFileResourceWithRawResponse,
    FileResourceWithStreamingResponse,
    AsyncFileResourceWithStreamingResponse,
)
from ...types import repo_list_params, repo_clone_params, repo_create_params, repo_update_params, repo_retrieve_params
from ..._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.repo_info import RepoInfo
from ...types.repo_metadata import RepoMetadata
from ...types.repo_list_response import RepoListResponse
from ...types.repo_clone_response import RepoCloneResponse
from ...types.repo_retrieve_response import RepoRetrieveResponse

__all__ = ["RepoResource", "AsyncRepoResource"]


class RepoResource(SyncAPIResource):
    @cached_property
    def file(self) -> FileResource:
        return FileResource(self._client)

    @cached_property
    def with_raw_response(self) -> RepoResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/squack-io/relace-python#accessing-raw-response-data-eg-headers
        """
        return RepoResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RepoResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/squack-io/relace-python#with_streaming_response
        """
        return RepoResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        auto_index: bool | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        source: Optional[repo_create_params.Source] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoInfo:
        """
        Create a new repository from the provided template.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/repo",
            body=maybe_transform(
                {
                    "auto_index": auto_index,
                    "metadata": metadata,
                    "source": source,
                },
                repo_create_params.RepoCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RepoInfo,
        )

    def retrieve(
        self,
        repo_id: str,
        *,
        query: str,
        branch: Optional[str] | Omit = omit,
        hash: Optional[str] | Omit = omit,
        include_content: bool | Omit = omit,
        rerank: bool | Omit = omit,
        score_threshold: float | Omit = omit,
        token_limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoRetrieveResponse:
        """
        Retrieve relevant content from a repository based on a query.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_id:
            raise ValueError(f"Expected a non-empty value for `repo_id` but received {repo_id!r}")
        return self._post(
            f"/repo/{repo_id}/retrieve",
            body=maybe_transform(
                {
                    "query": query,
                    "branch": branch,
                    "hash": hash,
                    "include_content": include_content,
                    "rerank": rerank,
                    "score_threshold": score_threshold,
                    "token_limit": token_limit,
                },
                repo_retrieve_params.RepoRetrieveParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RepoRetrieveResponse,
        )

    def update(
        self,
        repo_id: str,
        *,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        source: Optional[repo_update_params.Source] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoInfo:
        """
        Apply repository changes.

        See the model docs for details of each update variant:

        - RepoUpdateFiles - snapshot replacement of tracked files
        - RepoUpdateDiff - explicit write/delete/rename operations
        - RepoUpdateGit - pull & merge from a remote Git repository

        Returns: RepoInfo: Includes the new repo head and, when determinable, a list of
        changed files for convenience.

        Error codes: 400: Invalid request type / diff operation / failed remote merge.
        404: Referenced file for delete/rename does not exist. 423: Repository lock
        contention.

        Args:
          source: Snapshot-style repository update.

              Treat the provided `files` list as the complete authoritative set of tracked
              text files. Any previously tracked file that is not present in the list will be
              deleted. Each listed file is created or overwritten.

              This mirrors the semantics of replacing the working tree with exactly the
              supplied set (excluding ignored/untracked items). Binary files are skipped
              downstream during embedding.

              Attributes: type: Discriminator literal `"files"`. files: List of files that
              should exist after the operation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_id:
            raise ValueError(f"Expected a non-empty value for `repo_id` but received {repo_id!r}")
        return self._post(
            f"/repo/{repo_id}/update",
            body=maybe_transform(
                {
                    "metadata": metadata,
                    "source": source,
                },
                repo_update_params.RepoUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RepoInfo,
        )

    def list(
        self,
        *,
        created_after: Union[str, datetime, None] | Omit = omit,
        created_before: Union[str, datetime, None] | Omit = omit,
        filter_metadata: Optional[str] | Omit = omit,
        order_by: Literal["created_at", "updated_at"] | Omit = omit,
        order_descending: bool | Omit = omit,
        page_size: int | Omit = omit,
        page_start: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoListResponse:
        """
        Get metadata for all repositories owned by the user.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/repo",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "created_after": created_after,
                        "created_before": created_before,
                        "filter_metadata": filter_metadata,
                        "order_by": order_by,
                        "order_descending": order_descending,
                        "page_size": page_size,
                        "page_start": page_start,
                    },
                    repo_list_params.RepoListParams,
                ),
            ),
            cast_to=RepoListResponse,
        )

    def delete(
        self,
        repo_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete a repository and its associated data.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_id:
            raise ValueError(f"Expected a non-empty value for `repo_id` but received {repo_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/repo/{repo_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def clone(
        self,
        repo_id: str,
        *,
        commit: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoCloneResponse:
        """
        Return all readable tracked files in a repository.

        If a `commit` is provided, read file contents from that commit; otherwise read
        from the working directory.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_id:
            raise ValueError(f"Expected a non-empty value for `repo_id` but received {repo_id!r}")
        return self._get(
            f"/repo/{repo_id}/clone",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"commit": commit}, repo_clone_params.RepoCloneParams),
            ),
            cast_to=RepoCloneResponse,
        )

    def get(
        self,
        repo_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoMetadata:
        """
        Get metadata for a single repository.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_id:
            raise ValueError(f"Expected a non-empty value for `repo_id` but received {repo_id!r}")
        return self._get(
            f"/repo/{repo_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RepoMetadata,
        )


class AsyncRepoResource(AsyncAPIResource):
    @cached_property
    def file(self) -> AsyncFileResource:
        return AsyncFileResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncRepoResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/squack-io/relace-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRepoResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRepoResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/squack-io/relace-python#with_streaming_response
        """
        return AsyncRepoResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        auto_index: bool | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        source: Optional[repo_create_params.Source] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoInfo:
        """
        Create a new repository from the provided template.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/repo",
            body=await async_maybe_transform(
                {
                    "auto_index": auto_index,
                    "metadata": metadata,
                    "source": source,
                },
                repo_create_params.RepoCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RepoInfo,
        )

    async def retrieve(
        self,
        repo_id: str,
        *,
        query: str,
        branch: Optional[str] | Omit = omit,
        hash: Optional[str] | Omit = omit,
        include_content: bool | Omit = omit,
        rerank: bool | Omit = omit,
        score_threshold: float | Omit = omit,
        token_limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoRetrieveResponse:
        """
        Retrieve relevant content from a repository based on a query.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_id:
            raise ValueError(f"Expected a non-empty value for `repo_id` but received {repo_id!r}")
        return await self._post(
            f"/repo/{repo_id}/retrieve",
            body=await async_maybe_transform(
                {
                    "query": query,
                    "branch": branch,
                    "hash": hash,
                    "include_content": include_content,
                    "rerank": rerank,
                    "score_threshold": score_threshold,
                    "token_limit": token_limit,
                },
                repo_retrieve_params.RepoRetrieveParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RepoRetrieveResponse,
        )

    async def update(
        self,
        repo_id: str,
        *,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        source: Optional[repo_update_params.Source] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoInfo:
        """
        Apply repository changes.

        See the model docs for details of each update variant:

        - RepoUpdateFiles - snapshot replacement of tracked files
        - RepoUpdateDiff - explicit write/delete/rename operations
        - RepoUpdateGit - pull & merge from a remote Git repository

        Returns: RepoInfo: Includes the new repo head and, when determinable, a list of
        changed files for convenience.

        Error codes: 400: Invalid request type / diff operation / failed remote merge.
        404: Referenced file for delete/rename does not exist. 423: Repository lock
        contention.

        Args:
          source: Snapshot-style repository update.

              Treat the provided `files` list as the complete authoritative set of tracked
              text files. Any previously tracked file that is not present in the list will be
              deleted. Each listed file is created or overwritten.

              This mirrors the semantics of replacing the working tree with exactly the
              supplied set (excluding ignored/untracked items). Binary files are skipped
              downstream during embedding.

              Attributes: type: Discriminator literal `"files"`. files: List of files that
              should exist after the operation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_id:
            raise ValueError(f"Expected a non-empty value for `repo_id` but received {repo_id!r}")
        return await self._post(
            f"/repo/{repo_id}/update",
            body=await async_maybe_transform(
                {
                    "metadata": metadata,
                    "source": source,
                },
                repo_update_params.RepoUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RepoInfo,
        )

    async def list(
        self,
        *,
        created_after: Union[str, datetime, None] | Omit = omit,
        created_before: Union[str, datetime, None] | Omit = omit,
        filter_metadata: Optional[str] | Omit = omit,
        order_by: Literal["created_at", "updated_at"] | Omit = omit,
        order_descending: bool | Omit = omit,
        page_size: int | Omit = omit,
        page_start: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoListResponse:
        """
        Get metadata for all repositories owned by the user.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/repo",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "created_after": created_after,
                        "created_before": created_before,
                        "filter_metadata": filter_metadata,
                        "order_by": order_by,
                        "order_descending": order_descending,
                        "page_size": page_size,
                        "page_start": page_start,
                    },
                    repo_list_params.RepoListParams,
                ),
            ),
            cast_to=RepoListResponse,
        )

    async def delete(
        self,
        repo_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete a repository and its associated data.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_id:
            raise ValueError(f"Expected a non-empty value for `repo_id` but received {repo_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/repo/{repo_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def clone(
        self,
        repo_id: str,
        *,
        commit: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoCloneResponse:
        """
        Return all readable tracked files in a repository.

        If a `commit` is provided, read file contents from that commit; otherwise read
        from the working directory.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_id:
            raise ValueError(f"Expected a non-empty value for `repo_id` but received {repo_id!r}")
        return await self._get(
            f"/repo/{repo_id}/clone",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"commit": commit}, repo_clone_params.RepoCloneParams),
            ),
            cast_to=RepoCloneResponse,
        )

    async def get(
        self,
        repo_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoMetadata:
        """
        Get metadata for a single repository.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_id:
            raise ValueError(f"Expected a non-empty value for `repo_id` but received {repo_id!r}")
        return await self._get(
            f"/repo/{repo_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RepoMetadata,
        )


class RepoResourceWithRawResponse:
    def __init__(self, repo: RepoResource) -> None:
        self._repo = repo

        self.create = to_raw_response_wrapper(
            repo.create,
        )
        self.retrieve = to_raw_response_wrapper(
            repo.retrieve,
        )
        self.update = to_raw_response_wrapper(
            repo.update,
        )
        self.list = to_raw_response_wrapper(
            repo.list,
        )
        self.delete = to_raw_response_wrapper(
            repo.delete,
        )
        self.clone = to_raw_response_wrapper(
            repo.clone,
        )
        self.get = to_raw_response_wrapper(
            repo.get,
        )

    @cached_property
    def file(self) -> FileResourceWithRawResponse:
        return FileResourceWithRawResponse(self._repo.file)


class AsyncRepoResourceWithRawResponse:
    def __init__(self, repo: AsyncRepoResource) -> None:
        self._repo = repo

        self.create = async_to_raw_response_wrapper(
            repo.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            repo.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            repo.update,
        )
        self.list = async_to_raw_response_wrapper(
            repo.list,
        )
        self.delete = async_to_raw_response_wrapper(
            repo.delete,
        )
        self.clone = async_to_raw_response_wrapper(
            repo.clone,
        )
        self.get = async_to_raw_response_wrapper(
            repo.get,
        )

    @cached_property
    def file(self) -> AsyncFileResourceWithRawResponse:
        return AsyncFileResourceWithRawResponse(self._repo.file)


class RepoResourceWithStreamingResponse:
    def __init__(self, repo: RepoResource) -> None:
        self._repo = repo

        self.create = to_streamed_response_wrapper(
            repo.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            repo.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            repo.update,
        )
        self.list = to_streamed_response_wrapper(
            repo.list,
        )
        self.delete = to_streamed_response_wrapper(
            repo.delete,
        )
        self.clone = to_streamed_response_wrapper(
            repo.clone,
        )
        self.get = to_streamed_response_wrapper(
            repo.get,
        )

    @cached_property
    def file(self) -> FileResourceWithStreamingResponse:
        return FileResourceWithStreamingResponse(self._repo.file)


class AsyncRepoResourceWithStreamingResponse:
    def __init__(self, repo: AsyncRepoResource) -> None:
        self._repo = repo

        self.create = async_to_streamed_response_wrapper(
            repo.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            repo.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            repo.update,
        )
        self.list = async_to_streamed_response_wrapper(
            repo.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            repo.delete,
        )
        self.clone = async_to_streamed_response_wrapper(
            repo.clone,
        )
        self.get = async_to_streamed_response_wrapper(
            repo.get,
        )

    @cached_property
    def file(self) -> AsyncFileResourceWithStreamingResponse:
        return AsyncFileResourceWithStreamingResponse(self._repo.file)
