# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK
from studyfetch_sdk.types.v1 import (
    PdfGeneratorCreateResponse,
    PdfGeneratorDeleteResponse,
    PdfGeneratorGetAllResponse,
)
from studyfetch_sdk.types.v1.pdf_generator import PdfResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPdfGenerator:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: StudyfetchSDK) -> None:
        pdf_generator = client.v1.pdf_generator.create(
            locale="locale",
            number_of_slides=1,
            topic="topic",
        )
        assert_matches_type(PdfGeneratorCreateResponse, pdf_generator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: StudyfetchSDK) -> None:
        response = client.v1.pdf_generator.with_raw_response.create(
            locale="locale",
            number_of_slides=1,
            topic="topic",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pdf_generator = response.parse()
        assert_matches_type(PdfGeneratorCreateResponse, pdf_generator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: StudyfetchSDK) -> None:
        with client.v1.pdf_generator.with_streaming_response.create(
            locale="locale",
            number_of_slides=1,
            topic="topic",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pdf_generator = response.parse()
            assert_matches_type(PdfGeneratorCreateResponse, pdf_generator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: StudyfetchSDK) -> None:
        pdf_generator = client.v1.pdf_generator.delete(
            "id",
        )
        assert_matches_type(PdfGeneratorDeleteResponse, pdf_generator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: StudyfetchSDK) -> None:
        response = client.v1.pdf_generator.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pdf_generator = response.parse()
        assert_matches_type(PdfGeneratorDeleteResponse, pdf_generator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: StudyfetchSDK) -> None:
        with client.v1.pdf_generator.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pdf_generator = response.parse()
            assert_matches_type(PdfGeneratorDeleteResponse, pdf_generator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.pdf_generator.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_all(self, client: StudyfetchSDK) -> None:
        pdf_generator = client.v1.pdf_generator.get_all()
        assert_matches_type(PdfGeneratorGetAllResponse, pdf_generator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_all(self, client: StudyfetchSDK) -> None:
        response = client.v1.pdf_generator.with_raw_response.get_all()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pdf_generator = response.parse()
        assert_matches_type(PdfGeneratorGetAllResponse, pdf_generator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_all(self, client: StudyfetchSDK) -> None:
        with client.v1.pdf_generator.with_streaming_response.get_all() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pdf_generator = response.parse()
            assert_matches_type(PdfGeneratorGetAllResponse, pdf_generator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_by_id(self, client: StudyfetchSDK) -> None:
        pdf_generator = client.v1.pdf_generator.get_by_id(
            "id",
        )
        assert_matches_type(PdfResponse, pdf_generator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_by_id(self, client: StudyfetchSDK) -> None:
        response = client.v1.pdf_generator.with_raw_response.get_by_id(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pdf_generator = response.parse()
        assert_matches_type(PdfResponse, pdf_generator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_by_id(self, client: StudyfetchSDK) -> None:
        with client.v1.pdf_generator.with_streaming_response.get_by_id(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pdf_generator = response.parse()
            assert_matches_type(PdfResponse, pdf_generator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_by_id(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.pdf_generator.with_raw_response.get_by_id(
                "",
            )


class TestAsyncPdfGenerator:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncStudyfetchSDK) -> None:
        pdf_generator = await async_client.v1.pdf_generator.create(
            locale="locale",
            number_of_slides=1,
            topic="topic",
        )
        assert_matches_type(PdfGeneratorCreateResponse, pdf_generator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.pdf_generator.with_raw_response.create(
            locale="locale",
            number_of_slides=1,
            topic="topic",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pdf_generator = await response.parse()
        assert_matches_type(PdfGeneratorCreateResponse, pdf_generator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.pdf_generator.with_streaming_response.create(
            locale="locale",
            number_of_slides=1,
            topic="topic",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pdf_generator = await response.parse()
            assert_matches_type(PdfGeneratorCreateResponse, pdf_generator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        pdf_generator = await async_client.v1.pdf_generator.delete(
            "id",
        )
        assert_matches_type(PdfGeneratorDeleteResponse, pdf_generator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.pdf_generator.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pdf_generator = await response.parse()
        assert_matches_type(PdfGeneratorDeleteResponse, pdf_generator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.pdf_generator.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pdf_generator = await response.parse()
            assert_matches_type(PdfGeneratorDeleteResponse, pdf_generator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.pdf_generator.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_all(self, async_client: AsyncStudyfetchSDK) -> None:
        pdf_generator = await async_client.v1.pdf_generator.get_all()
        assert_matches_type(PdfGeneratorGetAllResponse, pdf_generator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_all(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.pdf_generator.with_raw_response.get_all()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pdf_generator = await response.parse()
        assert_matches_type(PdfGeneratorGetAllResponse, pdf_generator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_all(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.pdf_generator.with_streaming_response.get_all() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pdf_generator = await response.parse()
            assert_matches_type(PdfGeneratorGetAllResponse, pdf_generator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_by_id(self, async_client: AsyncStudyfetchSDK) -> None:
        pdf_generator = await async_client.v1.pdf_generator.get_by_id(
            "id",
        )
        assert_matches_type(PdfResponse, pdf_generator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_by_id(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.pdf_generator.with_raw_response.get_by_id(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pdf_generator = await response.parse()
        assert_matches_type(PdfResponse, pdf_generator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_by_id(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.pdf_generator.with_streaming_response.get_by_id(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pdf_generator = await response.parse()
            assert_matches_type(PdfResponse, pdf_generator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_by_id(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.pdf_generator.with_raw_response.get_by_id(
                "",
            )
