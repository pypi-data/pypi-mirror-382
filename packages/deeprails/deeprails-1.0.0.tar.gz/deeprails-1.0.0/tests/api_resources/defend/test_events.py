# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from deeprails import Deeprails, AsyncDeeprails
from tests.utils import assert_matches_type
from deeprails.types.defend import WorkflowEventResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvents:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_event(self, client: Deeprails) -> None:
        event = client.defend.events.retrieve_event(
            event_id="event_id",
            workflow_id="workflow_id",
        )
        assert_matches_type(WorkflowEventResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_event(self, client: Deeprails) -> None:
        response = client.defend.events.with_raw_response.retrieve_event(
            event_id="event_id",
            workflow_id="workflow_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = response.parse()
        assert_matches_type(WorkflowEventResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_event(self, client: Deeprails) -> None:
        with client.defend.events.with_streaming_response.retrieve_event(
            event_id="event_id",
            workflow_id="workflow_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = response.parse()
            assert_matches_type(WorkflowEventResponse, event, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_event(self, client: Deeprails) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workflow_id` but received ''"):
            client.defend.events.with_raw_response.retrieve_event(
                event_id="event_id",
                workflow_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `event_id` but received ''"):
            client.defend.events.with_raw_response.retrieve_event(
                event_id="",
                workflow_id="workflow_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_submit_event(self, client: Deeprails) -> None:
        event = client.defend.events.submit_event(
            workflow_id="workflow_id",
            model_input={"user_prompt": "user_prompt"},
            model_output="model_output",
            model_used="model_used",
            nametag="nametag",
            run_mode="precision_plus",
        )
        assert_matches_type(WorkflowEventResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_submit_event_with_all_params(self, client: Deeprails) -> None:
        event = client.defend.events.submit_event(
            workflow_id="workflow_id",
            model_input={
                "user_prompt": "user_prompt",
                "context": "context",
            },
            model_output="model_output",
            model_used="model_used",
            nametag="nametag",
            run_mode="precision_plus",
        )
        assert_matches_type(WorkflowEventResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_submit_event(self, client: Deeprails) -> None:
        response = client.defend.events.with_raw_response.submit_event(
            workflow_id="workflow_id",
            model_input={"user_prompt": "user_prompt"},
            model_output="model_output",
            model_used="model_used",
            nametag="nametag",
            run_mode="precision_plus",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = response.parse()
        assert_matches_type(WorkflowEventResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_submit_event(self, client: Deeprails) -> None:
        with client.defend.events.with_streaming_response.submit_event(
            workflow_id="workflow_id",
            model_input={"user_prompt": "user_prompt"},
            model_output="model_output",
            model_used="model_used",
            nametag="nametag",
            run_mode="precision_plus",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = response.parse()
            assert_matches_type(WorkflowEventResponse, event, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_submit_event(self, client: Deeprails) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workflow_id` but received ''"):
            client.defend.events.with_raw_response.submit_event(
                workflow_id="",
                model_input={"user_prompt": "user_prompt"},
                model_output="model_output",
                model_used="model_used",
                nametag="nametag",
                run_mode="precision_plus",
            )


class TestAsyncEvents:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_event(self, async_client: AsyncDeeprails) -> None:
        event = await async_client.defend.events.retrieve_event(
            event_id="event_id",
            workflow_id="workflow_id",
        )
        assert_matches_type(WorkflowEventResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_event(self, async_client: AsyncDeeprails) -> None:
        response = await async_client.defend.events.with_raw_response.retrieve_event(
            event_id="event_id",
            workflow_id="workflow_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = await response.parse()
        assert_matches_type(WorkflowEventResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_event(self, async_client: AsyncDeeprails) -> None:
        async with async_client.defend.events.with_streaming_response.retrieve_event(
            event_id="event_id",
            workflow_id="workflow_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = await response.parse()
            assert_matches_type(WorkflowEventResponse, event, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_event(self, async_client: AsyncDeeprails) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workflow_id` but received ''"):
            await async_client.defend.events.with_raw_response.retrieve_event(
                event_id="event_id",
                workflow_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `event_id` but received ''"):
            await async_client.defend.events.with_raw_response.retrieve_event(
                event_id="",
                workflow_id="workflow_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_submit_event(self, async_client: AsyncDeeprails) -> None:
        event = await async_client.defend.events.submit_event(
            workflow_id="workflow_id",
            model_input={"user_prompt": "user_prompt"},
            model_output="model_output",
            model_used="model_used",
            nametag="nametag",
            run_mode="precision_plus",
        )
        assert_matches_type(WorkflowEventResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_submit_event_with_all_params(self, async_client: AsyncDeeprails) -> None:
        event = await async_client.defend.events.submit_event(
            workflow_id="workflow_id",
            model_input={
                "user_prompt": "user_prompt",
                "context": "context",
            },
            model_output="model_output",
            model_used="model_used",
            nametag="nametag",
            run_mode="precision_plus",
        )
        assert_matches_type(WorkflowEventResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_submit_event(self, async_client: AsyncDeeprails) -> None:
        response = await async_client.defend.events.with_raw_response.submit_event(
            workflow_id="workflow_id",
            model_input={"user_prompt": "user_prompt"},
            model_output="model_output",
            model_used="model_used",
            nametag="nametag",
            run_mode="precision_plus",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = await response.parse()
        assert_matches_type(WorkflowEventResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_submit_event(self, async_client: AsyncDeeprails) -> None:
        async with async_client.defend.events.with_streaming_response.submit_event(
            workflow_id="workflow_id",
            model_input={"user_prompt": "user_prompt"},
            model_output="model_output",
            model_used="model_used",
            nametag="nametag",
            run_mode="precision_plus",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = await response.parse()
            assert_matches_type(WorkflowEventResponse, event, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_submit_event(self, async_client: AsyncDeeprails) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workflow_id` but received ''"):
            await async_client.defend.events.with_raw_response.submit_event(
                workflow_id="",
                model_input={"user_prompt": "user_prompt"},
                model_output="model_output",
                model_used="model_used",
                nametag="nametag",
                run_mode="precision_plus",
            )
