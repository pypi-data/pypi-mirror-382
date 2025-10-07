# Copyright © 2025 Oracle and/or its affiliates.
#
# This software is under the Universal Permissive License
# (UPL) 1.0 (LICENSE-UPL or https://oss.oracle.com/licenses/upl) or Apache License
# 2.0 (LICENSE-APACHE or http://www.apache.org/licenses/LICENSE-2.0), at your option.
import json
import logging
from typing import TYPE_CHECKING, Any, AsyncIterable, AsyncIterator, Callable, Dict, List, Optional

from wayflowcore._metadata import MetadataType
from wayflowcore._utils.formatting import stringify
from wayflowcore.messagelist import ImageContent, TextContent
from wayflowcore.tokenusage import TokenUsage
from wayflowcore.tools import ToolRequest

from ..property import Property
from ._requesthelpers import (
    StreamChunkType,
    TaggedMessageChunkTypeWithTokenUsage,
    _RetryStrategy,
    json_iterator_from_stream_of_completion_str,
    request_post_with_retries,
    request_streaming_post_with_retries,
)
from .llmgenerationconfig import LlmGenerationConfig
from .llmmodel import LlmCompletion, LlmModel, Prompt

if TYPE_CHECKING:
    from wayflowcore.messagelist import Message


logger = logging.getLogger(__name__)


class OpenAICompatibleModel(LlmModel):
    def __init__(
        self,
        model_id: str,
        base_url: str,
        proxy: Optional[str] = None,
        api_key: Optional[str] = None,
        generation_config: Optional[LlmGenerationConfig] = None,
        supports_structured_generation: Optional[bool] = True,
        supports_tool_calling: Optional[bool] = True,
        __metadata_info__: Optional[MetadataType] = None,
        id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        Model to use remote LLM endpoints that use OpenAI-compatible chat APIs.

        Parameters
        ----------
        model_id:
            Name of the model to use
        base_url:
            Hostname and port of the vllm server where the model is hosted. If you specify a url
            ending with `/completions` it will be used as-is, otherwise the url path
            `v1/chat/completions` will be appended to the base url.
        proxy:
            Proxy to use to connect to the remote LLM endpoint
        api_key:
            API key to use for the request if needed. It will be formatted in the OpenAI format
            (as "Bearer API_KEY" in the request header)
        generation_config:
            default parameters for text generation with this model
        supports_structured_generation:
            Whether the model supports structured generation or not. When set to `None`,
            the model will be prompted with a response format and it will check it can use
            structured generation.
        supports_tool_calling:
            Whether the model supports tool calling or not. When set to `None`,
            the model will be prompted with a tool and it will check it can use
            the tool.
        id:
            ID of the component.
        name:
            Name of the component.
        description:
            Description of the component.

        Examples
        --------
        >>> from wayflowcore.models import OpenAICompatibleModel
        >>> llm = OpenAICompatibleModel(
        ...     model_id="<MODEL_NAME>",
        ...     base_url="<ENDPOINT_URL>",
        ...     api_key="<API_KEY_FOR_REMOTE_ENDPOINT>",
        ... )

        """
        self.base_url = _add_leading_http_if_needed(base_url)
        self.proxy = proxy
        self.api_key = api_key
        self._retry_strategy = _RetryStrategy()
        super().__init__(
            model_id=model_id,
            generation_config=generation_config,
            supports_structured_generation=supports_structured_generation,
            supports_tool_calling=supports_tool_calling,
            __metadata_info__=__metadata_info__,
            id=id,
            name=name,
            description=description,
        )

    def _generate_request_params(self, prompt: "Prompt") -> Dict[str, Any]:
        url = (
            self.base_url
            if self.base_url.endswith("/completions")
            else f"{self.base_url}/v1/chat/completions"
        )
        return dict(
            url=url,
            headers=self._get_headers(),
            json={
                "model": self.model_id,
                **self._convert_prompt(prompt),
                **self._convert_generation_params(prompt.generation_config),
            },
        )

    async def _generate_impl(
        self,
        prompt: "Prompt",
    ) -> LlmCompletion:
        p = self._generate_request_params(prompt)
        response_data = await self._post(
            request_params=p, retry_strategy=self._retry_strategy, proxy=self.proxy
        )
        logger.debug(f"Raw LLM answer: %s", response_data)
        message = _convert_openai_completion_into_message(response_data)
        message = self._post_process(message)
        message = prompt.parse_output(message)
        return LlmCompletion(
            message=message,
            token_usage=(
                _extract_usage(response_data["usage"]) if "usage" in response_data else None
            ),
        )

    async def _stream_generate_impl(
        self, prompt: "Prompt"
    ) -> AsyncIterable[TaggedMessageChunkTypeWithTokenUsage]:
        request_args = self._generate_request_params(prompt)
        # needed for openai streaming endpoint
        request_args["json"]["stream_options"] = dict(include_usage=True)
        request_args["json"]["stream"] = True

        def final_message_post_processing(message: "Message") -> "Message":
            return prompt.parse_output(self._post_process(message))

        json_stream = self._post_stream(
            request_args,
            retry_strategy=self._retry_strategy,
            proxy=self.proxy,
        )

        async for chunk in _tagged_chunk_iterator_from_stream_of_openai_compatible_json(
            json_object_iterable=json_stream,
            post_processing=final_message_post_processing,
        ):
            yield chunk

    def _pre_process(self, prompt: "Prompt") -> "Prompt":
        return prompt

    def _post_process(self, message: "Message") -> "Message":
        return message

    def _convert_prompt(self, prompt: "Prompt") -> Dict[str, Any]:
        prompt = self._pre_process(prompt)
        return _convert_prompt_into_openai_compatible_request(prompt)

    def _convert_generation_params(self, config: Optional[LlmGenerationConfig]) -> Dict[str, Any]:
        return _convert_generation_config_into_openai_arguments(config)

    def _get_headers(self) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key is not None:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    @staticmethod
    async def _post(
        request_params: Dict[str, Any], retry_strategy: _RetryStrategy, proxy: Optional[str]
    ) -> Dict[str, Any]:
        logger.debug(f"Request to remote endpoint: {request_params}")
        response = await request_post_with_retries(request_params, retry_strategy, proxy)
        logger.debug(f"Raw remote endpoint response: {response}")
        return response

    @staticmethod
    async def _post_stream(
        request_params: Dict[str, Any],
        retry_strategy: _RetryStrategy,
        proxy: Optional[str],
    ) -> AsyncIterator[Dict[str, Any]]:
        logger.debug(f"Streaming request to remote endpoint: {request_params}")
        line_iterator = request_streaming_post_with_retries(
            request_params, retry_strategy=retry_strategy, proxy=proxy
        )
        async for chunk in json_iterator_from_stream_of_completion_str(line_iterator):
            yield chunk

    @property
    def config(self) -> Dict[str, Any]:
        if self.api_key is not None:
            logger.warning(
                f"API was configured on {self} but it will not be serialized in the config"
            )
        return {
            "model_type": "openaicompatible",
            "model_id": self.model_id,
            "base_url": self.base_url,
            "proxy": self.proxy,
            "supports_structured_generation": self.supports_structured_generation,
            "supports_tool_calling": self.supports_tool_calling,
            "generation_config": (
                self.generation_config.to_dict() if self.generation_config is not None else None
            ),
        }


def _add_leading_http_if_needed(url: str) -> str:
    """
    Ensures URLs have http:// if missing
    """
    if "://" in url:
        return url

    return f"http://{url}"


async def _tagged_chunk_iterator_from_stream_of_openai_compatible_json(
    json_object_iterable: AsyncIterable[Any],
    post_processing: Optional[Callable[["Message"], "Message"]] = None,
) -> AsyncIterable[TaggedMessageChunkTypeWithTokenUsage]:
    """Using API: https://platform.openai.com/docs/api-reference/chat-streaming/streaming"""
    from wayflowcore.messagelist import Message, MessageType

    # start the stream
    yield StreamChunkType.START_CHUNK, Message(content="", message_type=MessageType.AGENT), None

    text = ""
    tool_deltas = []
    token_usage: Optional[TokenUsage] = None
    async for json_object in json_object_iterable:
        text_delta = ""
        for chunk in json_object["choices"]:
            delta = chunk["delta"]
            if "tool_calls" in delta:
                tool_deltas.extend(delta["tool_calls"])
            if "content" in delta and delta["content"] is not None:
                text_delta = delta["content"]
                text += text_delta

        if "usage" in json_object and json_object["usage"] is not None:
            raw_usage = json_object["usage"]
            token_usage = _extract_usage(raw_usage)
        yield StreamChunkType.TEXT_CHUNK, Message(
            content=text_delta, message_type=MessageType.AGENT
        ), None

    if len(tool_deltas) > 0:
        message_type = MessageType.TOOL_REQUEST
        tool_calls = _convert_tool_deltas_into_tool_requests(tool_deltas)
    else:
        message_type = MessageType.AGENT
        tool_calls = None

    message = Message(content=text, message_type=message_type, tool_requests=tool_calls)
    if post_processing is not None:
        message = post_processing(message)
    yield StreamChunkType.END_CHUNK, message, token_usage


def _convert_tool_deltas_into_tool_requests(tool_deltas: List[Any]) -> List[ToolRequest]:
    """Gets tool deltas and return list of proper tool calls"""
    tool_requests_dict = {}
    for delta in tool_deltas:
        index = delta["index"]
        if index not in tool_requests_dict:
            tool_requests_dict[index] = {"name": "", "arguments": ""}
        if "id" in delta:
            tool_requests_dict[index]["tool_request_id"] = delta["id"]
        if "function" in delta:
            func = delta["function"]
            if "name" in func:
                tool_requests_dict[index]["name"] += func["name"]
            if "arguments" in func:
                tool_requests_dict[index]["arguments"] += func["arguments"]
    return [
        ToolRequest(
            name=s["name"],
            tool_request_id=s["tool_request_id"],
            args=json.loads(s["arguments"]),
        )
        for s in tool_requests_dict.values()
    ]


def _convert_message_into_openai_message_dict(m: "Message") -> List[Dict[str, Any]]:
    if m.tool_requests:
        if any([not isinstance(content, TextContent) for content in m.contents]):
            raise ValueError(
                "Invalid tool request. A tool request message should only contain text contents"
            )
        return [
            {
                "content": m.content,
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": tc.tool_request_id,
                        "type": "function",
                        "function": {"name": tc.name, "arguments": json.dumps(tc.args)},
                    }
                    for tc in (m.tool_requests or [])
                ],
            }
        ]
    elif m.tool_result:
        if len(m.contents):
            raise ValueError(
                "Invalid tool result. Tool results should not contain any message content"
            )

        return [
            {
                "role": "tool",
                "tool_call_id": m.tool_result.tool_request_id,
                "content": stringify(m.tool_result.content),
            }
        ]
    else:
        role = m.role
        all_contents = []

        for content in m.contents:
            if isinstance(content, ImageContent):
                all_contents.append(
                    {"type": "image_url", "image_url": {"url": content.base64_content}}
                )
            elif isinstance(content, TextContent):
                all_contents.append({"type": "text", "text": content.content})
            else:
                raise RuntimeError(f"Unsupported content type: {content.__class__.__name__}")

    return [{"role": role, "content": all_contents if len(all_contents) else ""}]


def _convert_generation_config_into_openai_arguments(
    generation_config: Optional[LlmGenerationConfig],
) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {}
    if generation_config is None:
        return kwargs
    if generation_config.top_p is not None:
        kwargs["top_p"] = generation_config.top_p
    if generation_config.temperature is not None:
        kwargs["temperature"] = generation_config.temperature
    if generation_config.max_tokens is not None:
        kwargs["max_completion_tokens"] = generation_config.max_tokens
    if generation_config.stop is not None:
        kwargs["stop"] = generation_config.stop
    if generation_config.frequency_penalty is not None:
        kwargs["frequency_penalty"] = generation_config.frequency_penalty
    if generation_config.extra_args:
        kwargs.update(generation_config.extra_args)
    return kwargs


def _convert_prompt_into_openai_compatible_request(prompt: "Prompt") -> Dict[str, Any]:
    payload_arguments: Dict[str, Any] = {
        "messages": [
            m
            for message in prompt.messages
            for m in _convert_message_into_openai_message_dict(message)
        ],
    }
    if prompt.tools is not None:
        payload_arguments["tools"] = [t.to_openai_format() for t in prompt.tools]
    if prompt.response_format is not None:
        payload_arguments["response_format"] = {
            "type": "json_schema",
            "json_schema": _prepare_openai_compatible_json_schema(prompt.response_format),
        }
    return payload_arguments


def _prepare_openai_compatible_json_schema(response_format: Property) -> Dict[str, Any]:
    return {
        "name": response_format.name,
        "strict": True,
        "schema": _property_to_openai_schema(response_format),
    }


def _logs_about_default_values_not_used(schema: Dict[str, Any]) -> None:
    for property_name, property_ in schema["properties"].items():
        if "default" in property_:
            logger.info(
                "The LLM cannot access the default value of the property `%s=%s`. "
                "If you need to preserve this behavior, define the property as a union "
                "with `NullProperty` and handle the default manually.",
                property_name,
                property_["default"],
            )


def _property_to_openai_schema(property_: Property) -> Dict[str, Any]:
    schema = dict(property_.to_json_schema())
    if "properties" in schema and isinstance(schema["properties"], dict):
        # openai requires all properties to be marked required
        # https://platform.openai.com/docs/guides/structured-outputs#all-fields-must-be-required,
        schema["required"] = list(schema["properties"].keys())
        # logs a message for each default value to indicate to the user that it will not be used
        _logs_about_default_values_not_used(schema)
    if "additionalProperties" not in schema:
        # openai requires to always pass additionalProperties
        schema["additionalProperties"] = False
    return schema


def _extract_usage(response: Dict[str, Any]) -> TokenUsage:
    cached_tokens = 0
    if "prompt_tokens_details" in response and "cached_tokens" in (
        response["prompt_tokens_details"] or []
    ):
        cached_tokens = response["prompt_tokens_details"]["cached_tokens"]
    return TokenUsage(
        input_tokens=response["prompt_tokens"],
        output_tokens=response["completion_tokens"],
        total_tokens=response["total_tokens"],
        cached_tokens=cached_tokens,
        exact_count=True,
    )


def _convert_openai_completion_into_message(response: Any) -> "Message":
    from wayflowcore.messagelist import Message

    extracted_message = response["choices"][0]["message"]
    if len(extracted_message.get("tool_calls") or []) > 0:
        message = Message(
            tool_requests=[
                ToolRequest(
                    name=tc["function"]["name"],
                    args=json.loads(tc["function"]["arguments"]),
                    tool_request_id=tc["id"],
                )
                for tc in extracted_message["tool_calls"]
            ],
            role="assistant",
        )
    else:
        message = Message(role="assistant", contents=[TextContent(extracted_message["content"])])
    return message
