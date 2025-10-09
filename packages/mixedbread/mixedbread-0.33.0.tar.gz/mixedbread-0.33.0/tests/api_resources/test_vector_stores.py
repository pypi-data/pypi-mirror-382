# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from mixedbread import Mixedbread, AsyncMixedbread
from tests.utils import assert_matches_type
from mixedbread.types import (
    VectorStore,
    VectorStoreDeleteResponse,
    VectorStoreSearchResponse,
    VectorStoreQuestionAnsweringResponse,
)
from mixedbread.pagination import SyncCursor, AsyncCursor

# pyright: reportDeprecated=false

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestVectorStores:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = client.vector_stores.create()

        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = client.vector_stores.create(
                name="Technical Documentation",
                description="Contains technical specifications and guides",
                is_public=False,
                expires_after={
                    "anchor": "last_active_at",
                    "days": 0,
                },
                metadata={},
                file_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            )

        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.vector_stores.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = response.parse()
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            with client.vector_stores.with_streaming_response.create() as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                vector_store = response.parse()
                assert_matches_type(VectorStore, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = client.vector_stores.retrieve(
                "vector_store_identifier",
            )

        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.vector_stores.with_raw_response.retrieve(
                "vector_store_identifier",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = response.parse()
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            with client.vector_stores.with_streaming_response.retrieve(
                "vector_store_identifier",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                vector_store = response.parse()
                assert_matches_type(VectorStore, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(
                ValueError, match=r"Expected a non-empty value for `vector_store_identifier` but received ''"
            ):
                client.vector_stores.with_raw_response.retrieve(
                    "",
                )

    @parametrize
    def test_method_update(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = client.vector_stores.update(
                vector_store_identifier="vector_store_identifier",
            )

        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = client.vector_stores.update(
                vector_store_identifier="vector_store_identifier",
                name="x",
                description="description",
                is_public=True,
                expires_after={
                    "anchor": "last_active_at",
                    "days": 0,
                },
                metadata={},
            )

        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.vector_stores.with_raw_response.update(
                vector_store_identifier="vector_store_identifier",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = response.parse()
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            with client.vector_stores.with_streaming_response.update(
                vector_store_identifier="vector_store_identifier",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                vector_store = response.parse()
                assert_matches_type(VectorStore, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(
                ValueError, match=r"Expected a non-empty value for `vector_store_identifier` but received ''"
            ):
                client.vector_stores.with_raw_response.update(
                    vector_store_identifier="",
                )

    @parametrize
    def test_method_list(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = client.vector_stores.list()

        assert_matches_type(SyncCursor[VectorStore], vector_store, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = client.vector_stores.list(
                limit=10,
                after="eyJjcmVhdGVkX2F0IjoiMjAyNC0xMi0zMVQyMzo1OTo1OS4wMDBaIiwiaWQiOiJhYmMxMjMifQ==",
                before="eyJjcmVhdGVkX2F0IjoiMjAyNC0xMi0zMVQyMzo1OTo1OS4wMDBaIiwiaWQiOiJhYmMxMjMifQ==",
                include_total=False,
                q="x",
            )

        assert_matches_type(SyncCursor[VectorStore], vector_store, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.vector_stores.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = response.parse()
        assert_matches_type(SyncCursor[VectorStore], vector_store, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            with client.vector_stores.with_streaming_response.list() as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                vector_store = response.parse()
                assert_matches_type(SyncCursor[VectorStore], vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = client.vector_stores.delete(
                "vector_store_identifier",
            )

        assert_matches_type(VectorStoreDeleteResponse, vector_store, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.vector_stores.with_raw_response.delete(
                "vector_store_identifier",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = response.parse()
        assert_matches_type(VectorStoreDeleteResponse, vector_store, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            with client.vector_stores.with_streaming_response.delete(
                "vector_store_identifier",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                vector_store = response.parse()
                assert_matches_type(VectorStoreDeleteResponse, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(
                ValueError, match=r"Expected a non-empty value for `vector_store_identifier` but received ''"
            ):
                client.vector_stores.with_raw_response.delete(
                    "",
                )

    @parametrize
    def test_method_question_answering(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = client.vector_stores.question_answering(
                vector_store_identifiers=["string"],
            )

        assert_matches_type(VectorStoreQuestionAnsweringResponse, vector_store, path=["response"])

    @parametrize
    def test_method_question_answering_with_all_params(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = client.vector_stores.question_answering(
                query="x",
                vector_store_identifiers=["string"],
                top_k=1,
                filters={
                    "all": [
                        {
                            "key": "price",
                            "value": "100",
                            "operator": "gt",
                        },
                        {
                            "key": "color",
                            "value": "red",
                            "operator": "eq",
                        },
                    ],
                    "any": [
                        {
                            "key": "price",
                            "value": "100",
                            "operator": "gt",
                        },
                        {
                            "key": "color",
                            "value": "red",
                            "operator": "eq",
                        },
                    ],
                    "none": [
                        {
                            "key": "price",
                            "value": "100",
                            "operator": "gt",
                        },
                        {
                            "key": "color",
                            "value": "red",
                            "operator": "eq",
                        },
                    ],
                },
                file_ids=["123e4567-e89b-12d3-a456-426614174000", "123e4567-e89b-12d3-a456-426614174001"],
                search_options={
                    "score_threshold": 0,
                    "rewrite_query": True,
                    "rerank": True,
                    "return_metadata": True,
                    "apply_search_rules": True,
                },
                stream=True,
                qa_options={
                    "cite": True,
                    "multimodal": True,
                },
            )

        assert_matches_type(VectorStoreQuestionAnsweringResponse, vector_store, path=["response"])

    @parametrize
    def test_raw_response_question_answering(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.vector_stores.with_raw_response.question_answering(
                vector_store_identifiers=["string"],
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = response.parse()
        assert_matches_type(VectorStoreQuestionAnsweringResponse, vector_store, path=["response"])

    @parametrize
    def test_streaming_response_question_answering(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            with client.vector_stores.with_streaming_response.question_answering(
                vector_store_identifiers=["string"],
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                vector_store = response.parse()
                assert_matches_type(VectorStoreQuestionAnsweringResponse, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_search(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = client.vector_stores.search(
                query="how to configure SSL",
                vector_store_identifiers=["string"],
            )

        assert_matches_type(VectorStoreSearchResponse, vector_store, path=["response"])

    @parametrize
    def test_method_search_with_all_params(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = client.vector_stores.search(
                query="how to configure SSL",
                vector_store_identifiers=["string"],
                top_k=1,
                filters={
                    "all": [
                        {
                            "key": "price",
                            "value": "100",
                            "operator": "gt",
                        },
                        {
                            "key": "color",
                            "value": "red",
                            "operator": "eq",
                        },
                    ],
                    "any": [
                        {
                            "key": "price",
                            "value": "100",
                            "operator": "gt",
                        },
                        {
                            "key": "color",
                            "value": "red",
                            "operator": "eq",
                        },
                    ],
                    "none": [
                        {
                            "key": "price",
                            "value": "100",
                            "operator": "gt",
                        },
                        {
                            "key": "color",
                            "value": "red",
                            "operator": "eq",
                        },
                    ],
                },
                file_ids=["123e4567-e89b-12d3-a456-426614174000", "123e4567-e89b-12d3-a456-426614174001"],
                search_options={
                    "score_threshold": 0,
                    "rewrite_query": True,
                    "rerank": True,
                    "return_metadata": True,
                    "apply_search_rules": True,
                },
            )

        assert_matches_type(VectorStoreSearchResponse, vector_store, path=["response"])

    @parametrize
    def test_raw_response_search(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.vector_stores.with_raw_response.search(
                query="how to configure SSL",
                vector_store_identifiers=["string"],
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = response.parse()
        assert_matches_type(VectorStoreSearchResponse, vector_store, path=["response"])

    @parametrize
    def test_streaming_response_search(self, client: Mixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            with client.vector_stores.with_streaming_response.search(
                query="how to configure SSL",
                vector_store_identifiers=["string"],
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                vector_store = response.parse()
                assert_matches_type(VectorStoreSearchResponse, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncVectorStores:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = await async_client.vector_stores.create()

        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = await async_client.vector_stores.create(
                name="Technical Documentation",
                description="Contains technical specifications and guides",
                is_public=False,
                expires_after={
                    "anchor": "last_active_at",
                    "days": 0,
                },
                metadata={},
                file_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            )

        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.vector_stores.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = await response.parse()
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.vector_stores.with_streaming_response.create() as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                vector_store = await response.parse()
                assert_matches_type(VectorStore, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = await async_client.vector_stores.retrieve(
                "vector_store_identifier",
            )

        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.vector_stores.with_raw_response.retrieve(
                "vector_store_identifier",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = await response.parse()
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.vector_stores.with_streaming_response.retrieve(
                "vector_store_identifier",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                vector_store = await response.parse()
                assert_matches_type(VectorStore, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(
                ValueError, match=r"Expected a non-empty value for `vector_store_identifier` but received ''"
            ):
                await async_client.vector_stores.with_raw_response.retrieve(
                    "",
                )

    @parametrize
    async def test_method_update(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = await async_client.vector_stores.update(
                vector_store_identifier="vector_store_identifier",
            )

        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = await async_client.vector_stores.update(
                vector_store_identifier="vector_store_identifier",
                name="x",
                description="description",
                is_public=True,
                expires_after={
                    "anchor": "last_active_at",
                    "days": 0,
                },
                metadata={},
            )

        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.vector_stores.with_raw_response.update(
                vector_store_identifier="vector_store_identifier",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = await response.parse()
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.vector_stores.with_streaming_response.update(
                vector_store_identifier="vector_store_identifier",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                vector_store = await response.parse()
                assert_matches_type(VectorStore, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(
                ValueError, match=r"Expected a non-empty value for `vector_store_identifier` but received ''"
            ):
                await async_client.vector_stores.with_raw_response.update(
                    vector_store_identifier="",
                )

    @parametrize
    async def test_method_list(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = await async_client.vector_stores.list()

        assert_matches_type(AsyncCursor[VectorStore], vector_store, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = await async_client.vector_stores.list(
                limit=10,
                after="eyJjcmVhdGVkX2F0IjoiMjAyNC0xMi0zMVQyMzo1OTo1OS4wMDBaIiwiaWQiOiJhYmMxMjMifQ==",
                before="eyJjcmVhdGVkX2F0IjoiMjAyNC0xMi0zMVQyMzo1OTo1OS4wMDBaIiwiaWQiOiJhYmMxMjMifQ==",
                include_total=False,
                q="x",
            )

        assert_matches_type(AsyncCursor[VectorStore], vector_store, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.vector_stores.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = await response.parse()
        assert_matches_type(AsyncCursor[VectorStore], vector_store, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.vector_stores.with_streaming_response.list() as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                vector_store = await response.parse()
                assert_matches_type(AsyncCursor[VectorStore], vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = await async_client.vector_stores.delete(
                "vector_store_identifier",
            )

        assert_matches_type(VectorStoreDeleteResponse, vector_store, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.vector_stores.with_raw_response.delete(
                "vector_store_identifier",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = await response.parse()
        assert_matches_type(VectorStoreDeleteResponse, vector_store, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.vector_stores.with_streaming_response.delete(
                "vector_store_identifier",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                vector_store = await response.parse()
                assert_matches_type(VectorStoreDeleteResponse, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(
                ValueError, match=r"Expected a non-empty value for `vector_store_identifier` but received ''"
            ):
                await async_client.vector_stores.with_raw_response.delete(
                    "",
                )

    @parametrize
    async def test_method_question_answering(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = await async_client.vector_stores.question_answering(
                vector_store_identifiers=["string"],
            )

        assert_matches_type(VectorStoreQuestionAnsweringResponse, vector_store, path=["response"])

    @parametrize
    async def test_method_question_answering_with_all_params(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = await async_client.vector_stores.question_answering(
                query="x",
                vector_store_identifiers=["string"],
                top_k=1,
                filters={
                    "all": [
                        {
                            "key": "price",
                            "value": "100",
                            "operator": "gt",
                        },
                        {
                            "key": "color",
                            "value": "red",
                            "operator": "eq",
                        },
                    ],
                    "any": [
                        {
                            "key": "price",
                            "value": "100",
                            "operator": "gt",
                        },
                        {
                            "key": "color",
                            "value": "red",
                            "operator": "eq",
                        },
                    ],
                    "none": [
                        {
                            "key": "price",
                            "value": "100",
                            "operator": "gt",
                        },
                        {
                            "key": "color",
                            "value": "red",
                            "operator": "eq",
                        },
                    ],
                },
                file_ids=["123e4567-e89b-12d3-a456-426614174000", "123e4567-e89b-12d3-a456-426614174001"],
                search_options={
                    "score_threshold": 0,
                    "rewrite_query": True,
                    "rerank": True,
                    "return_metadata": True,
                    "apply_search_rules": True,
                },
                stream=True,
                qa_options={
                    "cite": True,
                    "multimodal": True,
                },
            )

        assert_matches_type(VectorStoreQuestionAnsweringResponse, vector_store, path=["response"])

    @parametrize
    async def test_raw_response_question_answering(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.vector_stores.with_raw_response.question_answering(
                vector_store_identifiers=["string"],
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = await response.parse()
        assert_matches_type(VectorStoreQuestionAnsweringResponse, vector_store, path=["response"])

    @parametrize
    async def test_streaming_response_question_answering(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.vector_stores.with_streaming_response.question_answering(
                vector_store_identifiers=["string"],
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                vector_store = await response.parse()
                assert_matches_type(VectorStoreQuestionAnsweringResponse, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_search(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = await async_client.vector_stores.search(
                query="how to configure SSL",
                vector_store_identifiers=["string"],
            )

        assert_matches_type(VectorStoreSearchResponse, vector_store, path=["response"])

    @parametrize
    async def test_method_search_with_all_params(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            vector_store = await async_client.vector_stores.search(
                query="how to configure SSL",
                vector_store_identifiers=["string"],
                top_k=1,
                filters={
                    "all": [
                        {
                            "key": "price",
                            "value": "100",
                            "operator": "gt",
                        },
                        {
                            "key": "color",
                            "value": "red",
                            "operator": "eq",
                        },
                    ],
                    "any": [
                        {
                            "key": "price",
                            "value": "100",
                            "operator": "gt",
                        },
                        {
                            "key": "color",
                            "value": "red",
                            "operator": "eq",
                        },
                    ],
                    "none": [
                        {
                            "key": "price",
                            "value": "100",
                            "operator": "gt",
                        },
                        {
                            "key": "color",
                            "value": "red",
                            "operator": "eq",
                        },
                    ],
                },
                file_ids=["123e4567-e89b-12d3-a456-426614174000", "123e4567-e89b-12d3-a456-426614174001"],
                search_options={
                    "score_threshold": 0,
                    "rewrite_query": True,
                    "rerank": True,
                    "return_metadata": True,
                    "apply_search_rules": True,
                },
            )

        assert_matches_type(VectorStoreSearchResponse, vector_store, path=["response"])

    @parametrize
    async def test_raw_response_search(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.vector_stores.with_raw_response.search(
                query="how to configure SSL",
                vector_store_identifiers=["string"],
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = await response.parse()
        assert_matches_type(VectorStoreSearchResponse, vector_store, path=["response"])

    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncMixedbread) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.vector_stores.with_streaming_response.search(
                query="how to configure SSL",
                vector_store_identifiers=["string"],
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                vector_store = await response.parse()
                assert_matches_type(VectorStoreSearchResponse, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True
