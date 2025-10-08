# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._files import read_file_content, async_read_file_content
from ..._types import Body, Query, Headers, NotGiven, FileContent, not_given
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

__all__ = ["FileResource", "AsyncFileResource"]


class FileResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FileResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/squack-io/relace-python#accessing-raw-response-data-eg-headers
        """
        return FileResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FileResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/squack-io/relace-python#with_streaming_response
        """
        return FileResourceWithStreamingResponse(self)

    def delete(
        self,
        file_path: str,
        *,
        repo_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoInfo:
        """
        Delete a file from a repository.

        Automatically commits the change and returns the repo info with the updated
        head.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_id:
            raise ValueError(f"Expected a non-empty value for `repo_id` but received {repo_id!r}")
        if not file_path:
            raise ValueError(f"Expected a non-empty value for `file_path` but received {file_path!r}")
        return self._delete(
            f"/repo/{repo_id}/file/{file_path}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RepoInfo,
        )

    def download(
        self,
        file_path: str,
        *,
        repo_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Read a file from a repository.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_id:
            raise ValueError(f"Expected a non-empty value for `repo_id` but received {repo_id!r}")
        if not file_path:
            raise ValueError(f"Expected a non-empty value for `file_path` but received {file_path!r}")
        return self._get(
            f"/repo/{repo_id}/file/{file_path}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def upload(
        self,
        file_path: str,
        body: FileContent,
        *,
        repo_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoInfo:
        """
        Write a file to a repository.

        Automatically commits the change and returns the repo info with the updated
        head.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_id:
            raise ValueError(f"Expected a non-empty value for `repo_id` but received {repo_id!r}")
        if not file_path:
            raise ValueError(f"Expected a non-empty value for `file_path` but received {file_path!r}")
        extra_headers = {"Content-Type": "application/octet-stream", **(extra_headers or {})}
        return self._put(
            f"/repo/{repo_id}/file/{file_path}",
            body=read_file_content(body),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RepoInfo,
        )


class AsyncFileResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFileResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/squack-io/relace-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFileResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFileResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/squack-io/relace-python#with_streaming_response
        """
        return AsyncFileResourceWithStreamingResponse(self)

    async def delete(
        self,
        file_path: str,
        *,
        repo_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoInfo:
        """
        Delete a file from a repository.

        Automatically commits the change and returns the repo info with the updated
        head.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_id:
            raise ValueError(f"Expected a non-empty value for `repo_id` but received {repo_id!r}")
        if not file_path:
            raise ValueError(f"Expected a non-empty value for `file_path` but received {file_path!r}")
        return await self._delete(
            f"/repo/{repo_id}/file/{file_path}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RepoInfo,
        )

    async def download(
        self,
        file_path: str,
        *,
        repo_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Read a file from a repository.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_id:
            raise ValueError(f"Expected a non-empty value for `repo_id` but received {repo_id!r}")
        if not file_path:
            raise ValueError(f"Expected a non-empty value for `file_path` but received {file_path!r}")
        return await self._get(
            f"/repo/{repo_id}/file/{file_path}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def upload(
        self,
        file_path: str,
        body: FileContent,
        *,
        repo_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoInfo:
        """
        Write a file to a repository.

        Automatically commits the change and returns the repo info with the updated
        head.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_id:
            raise ValueError(f"Expected a non-empty value for `repo_id` but received {repo_id!r}")
        if not file_path:
            raise ValueError(f"Expected a non-empty value for `file_path` but received {file_path!r}")
        extra_headers = {"Content-Type": "application/octet-stream", **(extra_headers or {})}
        return await self._put(
            f"/repo/{repo_id}/file/{file_path}",
            body=await async_read_file_content(body),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RepoInfo,
        )


class FileResourceWithRawResponse:
    def __init__(self, file: FileResource) -> None:
        self._file = file

        self.delete = to_raw_response_wrapper(
            file.delete,
        )
        self.download = to_raw_response_wrapper(
            file.download,
        )
        self.upload = to_raw_response_wrapper(
            file.upload,
        )


class AsyncFileResourceWithRawResponse:
    def __init__(self, file: AsyncFileResource) -> None:
        self._file = file

        self.delete = async_to_raw_response_wrapper(
            file.delete,
        )
        self.download = async_to_raw_response_wrapper(
            file.download,
        )
        self.upload = async_to_raw_response_wrapper(
            file.upload,
        )


class FileResourceWithStreamingResponse:
    def __init__(self, file: FileResource) -> None:
        self._file = file

        self.delete = to_streamed_response_wrapper(
            file.delete,
        )
        self.download = to_streamed_response_wrapper(
            file.download,
        )
        self.upload = to_streamed_response_wrapper(
            file.upload,
        )


class AsyncFileResourceWithStreamingResponse:
    def __init__(self, file: AsyncFileResource) -> None:
        self._file = file

        self.delete = async_to_streamed_response_wrapper(
            file.delete,
        )
        self.download = async_to_streamed_response_wrapper(
            file.download,
        )
        self.upload = async_to_streamed_response_wrapper(
            file.upload,
        )
