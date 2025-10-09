# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import Body, Query, Headers, NotGiven, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ....types.v1 import pdf_generator_create_params
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v1.pdf_generator.pdf_response import PdfResponse
from ....types.v1.pdf_generator_create_response import PdfGeneratorCreateResponse
from ....types.v1.pdf_generator_delete_response import PdfGeneratorDeleteResponse
from ....types.v1.pdf_generator_get_all_response import PdfGeneratorGetAllResponse

__all__ = ["PdfGeneratorResource", "AsyncPdfGeneratorResource"]


class PdfGeneratorResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PdfGeneratorResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return PdfGeneratorResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PdfGeneratorResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return PdfGeneratorResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        locale: str,
        number_of_slides: float,
        topic: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PdfGeneratorCreateResponse:
        """
        Generate a new PDF presentation

        Args:
          locale: Locale/language for the presentation (e.g., en-US, es-ES, fr-FR)

          number_of_slides: Number of slides to generate

          topic: The topic for the PDF presentation

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/pdf-generator/create",
            body=maybe_transform(
                {
                    "locale": locale,
                    "number_of_slides": number_of_slides,
                    "topic": topic,
                },
                pdf_generator_create_params.PdfGeneratorCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PdfGeneratorCreateResponse,
        )

    def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PdfGeneratorDeleteResponse:
        """
        Delete a PDF presentation by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/api/v1/pdf-generator/delete/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PdfGeneratorDeleteResponse,
        )

    def get_all(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PdfGeneratorGetAllResponse:
        """Get all PDF presentations"""
        return self._get(
            "/api/v1/pdf-generator/get",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PdfGeneratorGetAllResponse,
        )

    def get_by_id(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PdfResponse:
        """
        Get a PDF presentation by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/api/v1/pdf-generator/get/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PdfResponse,
        )


class AsyncPdfGeneratorResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPdfGeneratorResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPdfGeneratorResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPdfGeneratorResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncPdfGeneratorResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        locale: str,
        number_of_slides: float,
        topic: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PdfGeneratorCreateResponse:
        """
        Generate a new PDF presentation

        Args:
          locale: Locale/language for the presentation (e.g., en-US, es-ES, fr-FR)

          number_of_slides: Number of slides to generate

          topic: The topic for the PDF presentation

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/pdf-generator/create",
            body=await async_maybe_transform(
                {
                    "locale": locale,
                    "number_of_slides": number_of_slides,
                    "topic": topic,
                },
                pdf_generator_create_params.PdfGeneratorCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PdfGeneratorCreateResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PdfGeneratorDeleteResponse:
        """
        Delete a PDF presentation by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/api/v1/pdf-generator/delete/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PdfGeneratorDeleteResponse,
        )

    async def get_all(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PdfGeneratorGetAllResponse:
        """Get all PDF presentations"""
        return await self._get(
            "/api/v1/pdf-generator/get",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PdfGeneratorGetAllResponse,
        )

    async def get_by_id(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PdfResponse:
        """
        Get a PDF presentation by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/api/v1/pdf-generator/get/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PdfResponse,
        )


class PdfGeneratorResourceWithRawResponse:
    def __init__(self, pdf_generator: PdfGeneratorResource) -> None:
        self._pdf_generator = pdf_generator

        self.create = to_raw_response_wrapper(
            pdf_generator.create,
        )
        self.delete = to_raw_response_wrapper(
            pdf_generator.delete,
        )
        self.get_all = to_raw_response_wrapper(
            pdf_generator.get_all,
        )
        self.get_by_id = to_raw_response_wrapper(
            pdf_generator.get_by_id,
        )


class AsyncPdfGeneratorResourceWithRawResponse:
    def __init__(self, pdf_generator: AsyncPdfGeneratorResource) -> None:
        self._pdf_generator = pdf_generator

        self.create = async_to_raw_response_wrapper(
            pdf_generator.create,
        )
        self.delete = async_to_raw_response_wrapper(
            pdf_generator.delete,
        )
        self.get_all = async_to_raw_response_wrapper(
            pdf_generator.get_all,
        )
        self.get_by_id = async_to_raw_response_wrapper(
            pdf_generator.get_by_id,
        )


class PdfGeneratorResourceWithStreamingResponse:
    def __init__(self, pdf_generator: PdfGeneratorResource) -> None:
        self._pdf_generator = pdf_generator

        self.create = to_streamed_response_wrapper(
            pdf_generator.create,
        )
        self.delete = to_streamed_response_wrapper(
            pdf_generator.delete,
        )
        self.get_all = to_streamed_response_wrapper(
            pdf_generator.get_all,
        )
        self.get_by_id = to_streamed_response_wrapper(
            pdf_generator.get_by_id,
        )


class AsyncPdfGeneratorResourceWithStreamingResponse:
    def __init__(self, pdf_generator: AsyncPdfGeneratorResource) -> None:
        self._pdf_generator = pdf_generator

        self.create = async_to_streamed_response_wrapper(
            pdf_generator.create,
        )
        self.delete = async_to_streamed_response_wrapper(
            pdf_generator.delete,
        )
        self.get_all = async_to_streamed_response_wrapper(
            pdf_generator.get_all,
        )
        self.get_by_id = async_to_streamed_response_wrapper(
            pdf_generator.get_by_id,
        )
