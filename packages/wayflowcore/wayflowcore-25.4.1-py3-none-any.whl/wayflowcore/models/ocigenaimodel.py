# Copyright © 2025 Oracle and/or its affiliates.
#
# This software is under the Universal Permissive License
# (UPL) 1.0 (LICENSE-UPL or https://oss.oracle.com/licenses/upl) or Apache License
# 2.0 (LICENSE-APACHE or http://www.apache.org/licenses/LICENSE-2.0), at your option.
import json
import logging
import uuid
import warnings
from abc import ABC, abstractmethod
from copy import deepcopy
from enum import Enum
from typing import TYPE_CHECKING, Any, AsyncIterable, Callable, Dict, Iterator, List, Optional, cast

from wayflowcore._metadata import MetadataType
from wayflowcore._utils.async_helpers import run_sync_in_thread, sync_to_async_iterator
from wayflowcore._utils.formatting import stringify
from wayflowcore.messagelist import ImageContent, MessageType, TextContent
from wayflowcore.tokenusage import TokenUsage
from wayflowcore.tools import Tool, ToolRequest

from ._requesthelpers import StreamChunkType, TaggedMessageChunkTypeWithTokenUsage
from .llmgenerationconfig import LlmGenerationConfig
from .llmmodel import LlmCompletion, LlmModel, Prompt
from .ociclientconfig import (
    OCIClientConfig,
    _client_config_to_oci_client_kwargs,
    _convert_arguments_into_client_config,
)
from .openaicompatiblemodel import _property_to_openai_schema

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from wayflowcore.messagelist import Message
    from wayflowcore.templates import PromptTemplate


class ServingMode(str, Enum):
    """
    The serving mode in which the model is hosted
    """

    ON_DEMAND = "ON_DEMAND"
    DEDICATED = "DEDICATED"


def _detect_serving_mode_from_model_id(model_id: str) -> ServingMode:
    # dedicated model_ids have some specific shape
    if "generativeaimodel" in model_id:
        return ServingMode.DEDICATED
    return ServingMode.ON_DEMAND


class ModelProvider(str, Enum):
    """
    Provider of the model. It is used to ensure the requests to this model respect
    the format expected by the provider.
    """

    META = "META"
    GROK = "GROK"
    COHERE = "COHERE"
    OTHER = "OTHER"


def _detect_provider_from_model_id(model_id: str) -> ModelProvider:
    if "." not in model_id:
        return ModelProvider.OTHER

    # in on_demand mode, model_id contains the name of the provider
    provider_name, model_name = model_id.split(".", maxsplit=1)
    if "cohere" in provider_name.lower():
        return ModelProvider.COHERE
    elif "meta" in provider_name.lower():
        return ModelProvider.META
    else:
        return ModelProvider.OTHER


class OCIGenAIModel(LlmModel):
    def __init__(
        self,
        *,
        model_id: str,
        compartment_id: Optional[str] = None,
        client_config: Optional[OCIClientConfig] = None,
        serving_mode: Optional[ServingMode] = None,
        provider: Optional[ModelProvider] = None,
        generation_config: Optional[LlmGenerationConfig] = None,
        id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        __metadata_info__: Optional[MetadataType] = None,
        # deprecated
        service_endpoint: Optional[str] = None,
        auth_type: Optional[str] = None,
        auth_profile: Optional[str] = "DEFAULT",
    ) -> None:
        """
        Model powered by OCIGenAI.

        Parameters
        ----------
        model_id:
            Name of the model to use.
        compartment_id:
            The compartment OCID. Can be also configured in the `OCI_GENAI_COMPARTMENT` env variable.
        client_config:
            OCI client config to authenticate the OCI service.
        serving_mode:
            OCI serving mode for the model. Either ``ServingMode.ON_DEMAND`` or ``ServingMode.DEDICATED``.
            When set to None, it will be auto-detected based on the ``model_id``.
        provider:
            Name of the provider of the underlying model, to adapt the request.
            Needs to be specified in ``ServingMode.DEDICATED``. Is auto-detected when in ``ServingMode.ON_DEMAND``
            based on the ``model_id``.
        generation_config:
            default parameters for text generation with this model
        id:
            ID of the component.
        name:
            Name of the component.
        description:
            Description of the component.

        Examples
        --------
        >>> from wayflowcore.models.ocigenaimodel import OCIGenAIModel
        >>> from wayflowcore.models.ociclientconfig import (
        ...     OCIClientConfigWithInstancePrincipal,
        ...     OCIClientConfigWithApiKey,
        ... )
        >>> ## Example 1. Instance Principal
        >>> client_config = OCIClientConfigWithInstancePrincipal(
        ...     service_endpoint="my_service_endpoint",
        ... )
        >>> ## Example 2. API Key from a config file (~/.oci/config)
        >>> client_config = OCIClientConfigWithApiKey(
        ...     service_endpoint="my_service_endpoint",
        ...     auth_profile="DEFAULT",
        ...     _auth_file_location="~/.oci/config"
        ... )
        >>> llm = OCIGenAIModel(
        ...     model_id="xai.grok-4",
        ...     client_config=client_config,
        ...     compartment_id="my_compartment_id",
        ... )  # doctest: +SKIP

        Notes
        -----
        When running under Oracle VPN, the connection to the OCIGenAI service requires to run the model without any proxy.
        Therefore, make sure not to have any of `http_proxy` or `HTTP_PROXY` environment variables setup, or unset them with `unset http_proxy HTTP_PROXY`

        Warning
        -------
        If when using ``INSTANCE_PRINCIPAL`` authentication, the response of the model returns a ``404`` error, please check if the machine is listed in the dynamic group and has the right privileges. Otherwise, please ask someone with administrative privileges.
        To grant an OCI Compute instance the ability to authenticate as an Instance Principal, one needs to define a Dynamic Group that includes the instance and create a policy that allows this dynamic group to manage OCI GenAI services.
        """
        if client_config is None:
            warnings.warn(
                "Passing authentication config parameters individually (e.g. service_endpoint, "
                "compartment_id, etc.) to this class is deprecated. "
                "Please provide one of the subclasses of OCIClientConfig using the `client_config` "
                "argument instead.",
                DeprecationWarning,
            )
            client_config = _convert_arguments_into_client_config(
                compartment_id=compartment_id,
                service_endpoint=service_endpoint,
                auth_type=auth_type,
                auth_profile=auth_profile,
            )
        self.client_config = client_config

        if compartment_id is None and client_config.compartment_id is not None:
            warnings.warn(
                "Passing `compartment_id` to the client config is deprecated. "
                "Please pass the id to the `OCIGenAIModel` instead.",
                DeprecationWarning,
            )
            compartment_id = client_config.compartment_id
        if compartment_id is None:
            raise ValueError("`compartment_id` should not be `None`.")
        self.compartment_id = compartment_id

        if serving_mode is None:
            serving_mode = _detect_serving_mode_from_model_id(model_id)
            logger.info(
                "OCI model with model_id=%s was resolved to use serving_mode=%s",
                model_id,
                serving_mode,
            )
        self.serving_mode = serving_mode

        if self.serving_mode == ServingMode.DEDICATED:
            if provider is None:
                raise ValueError(
                    "When using dedicated mode, please pass the provider of your dedicated model"
                    " with the ``provider`` argument."
                )
        elif provider is None:
            # model_id in serving_mode=on_demand should contain enough information to detect the provider
            provider = _detect_provider_from_model_id(model_id)
        self.provider = provider

        self._client = None
        self._oci_serving_mode = None

        if (
            provider == ModelProvider.COHERE
            and generation_config is not None
            and generation_config.frequency_penalty is not None
        ):
            if generation_config.frequency_penalty < 0:
                raise ValueError("Cohere Models do not support negative frequency penalties")
            generation_config.frequency_penalty = generation_config.frequency_penalty / 2
            logger.info("rescaled frequency penalty to [0,1] range for Cohere compatibility")
            generation_config = deepcopy(generation_config)

        super().__init__(
            model_id=model_id,
            id=id,
            name=name,
            description=description,
            generation_config=generation_config,
            supports_structured_generation=True,
            supports_tool_calling=True,
            __metadata_info__=__metadata_info__,
        )

    def _init_client(self) -> None:
        import oci  # type: ignore

        self._client = oci.generative_ai_inference.GenerativeAiInferenceClient(
            **_client_config_to_oci_client_kwargs(self.client_config)
        )

        if self.serving_mode == ServingMode.ON_DEMAND:
            self._oci_serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
                model_id=self.model_id
            )
        elif self.serving_mode == ServingMode.DEDICATED:
            self._oci_serving_mode = oci.generative_ai_inference.models.DedicatedServingMode(
                endpoint_id=self.model_id
            )
        else:
            raise ValueError(
                f"Invalid serving_mode specified for OciGenAIModel. Valid options are {ServingMode.ON_DEMAND, ServingMode.DEDICATED} but got {self.serving_mode} instead."
            )

    def _init_client_if_needed(self) -> None:
        if self._client is None or self._oci_serving_mode is None:
            try:
                self._init_client()
            except ImportError:
                raise ImportError(
                    "Optional dependency `oci` not found. Please install `wayflowcore[oci]` to be able to use `OciGenAIModel`"
                )

    async def _generate_impl(
        self, prompt: Prompt, generation_config: Optional[LlmGenerationConfig] = None
    ) -> "LlmCompletion":

        provider = _MODEL_PROVIDER_TO_FORMATTER[self.provider]

        response = await run_sync_in_thread(self._post_with_retry, provider, prompt)
        logger.debug(f"Raw remote oci genai response: {response.data}")

        response_message = provider.convert_completion_into_message(response)
        response_message = prompt.parse_output(response_message)
        return LlmCompletion(message=response_message, token_usage=provider.extract_usage(response))

    def _post_with_retry(self, provider: "_OciApiFormatter", prompt: Prompt) -> Any:
        import oci

        max_attempts = 3
        for i in range(max_attempts):
            try:
                return self._post(provider=provider, prompt=prompt)
            except oci.exceptions.ServiceError as e:
                error_message = e.message
                if any(pattern in error_message for pattern in _UNSUPPORTED_ARGUMENT_PATTERNS):
                    old_generation_config = prompt.generation_config
                    if old_generation_config is None or i == max_attempts - 1:
                        # either no parameter config to change or it last the last try
                        raise e

                    new_config = _adapt_generation_config_with_error_message(
                        generation_config=old_generation_config, error_message=error_message
                    )
                    prompt = prompt.copy(generation_config=new_config)
                else:
                    raise e

    def _post(self, provider: "_OciApiFormatter", prompt: Prompt) -> Any:
        import oci

        self._init_client_if_needed()
        if self._client is None or self._oci_serving_mode is None:
            raise ValueError("Could not initialize the OCI client")

        request = provider.convert_prompt_into_request(prompt, self.model_id)
        logger.debug(f"Request to remote oci genai endpoint: {json.loads(str(request))}")

        chat_details = oci.generative_ai_inference.models.ChatDetails(
            compartment_id=self.compartment_id,
            serving_mode=self._oci_serving_mode,
            chat_request=request,
        )

        return self._client.chat(chat_details=chat_details)

    async def _stream_generate_impl(
        self,
        prompt: Prompt,
    ) -> AsyncIterable[TaggedMessageChunkTypeWithTokenUsage]:
        import oci

        self._init_client_if_needed()
        if self._client is None or self._oci_serving_mode is None:
            raise ValueError("Could not initialize the OCI client")

        provider = _MODEL_PROVIDER_TO_FORMATTER[self.provider]

        request = provider.convert_prompt_into_request(prompt, self.model_id)
        logger.debug(f"Streaming request to remote oci genai endpoint: {json.loads(str(request))}")
        request.is_stream = True
        response = self._client.chat(
            chat_details=oci.generative_ai_inference.models.ChatDetails(
                compartment_id=self.compartment_id,
                serving_mode=self._oci_serving_mode,
                chat_request=request,
            ),
        )
        async for chunk in sync_to_async_iterator(
            provider.convert_oci_chunk_iterator_into_tagged_chunk_iterator(
                iterator=response.data.events(), post_processing=prompt.parse_output
            )
        ):
            yield chunk

    @property
    def config(self) -> Dict[str, Any]:
        return {
            "model_type": "ocigenai",
            "model_id": self.model_id,
            "generation_config": (
                self.generation_config.to_dict() if self.generation_config is not None else None
            ),
            "client_config": self.client_config.to_dict(),
            "serving_mode": self.serving_mode.value,
            "compartment_id": self.compartment_id,
            "provider": self.provider.value,
        }

    @property
    def default_chat_template(self) -> "PromptTemplate":
        from wayflowcore.templates import LLAMA_CHAT_TEMPLATE, NATIVE_CHAT_TEMPLATE

        if self.provider == ModelProvider.COHERE:
            return NATIVE_CHAT_TEMPLATE
        if self.provider == ModelProvider.META and "3." in self.model_id:
            # meta llama3.x works better with custom template
            return LLAMA_CHAT_TEMPLATE
        return NATIVE_CHAT_TEMPLATE

    @property
    def default_agent_template(self) -> "PromptTemplate":
        from wayflowcore.templates import LLAMA_AGENT_TEMPLATE, NATIVE_AGENT_TEMPLATE

        if self.provider == ModelProvider.COHERE:
            return NATIVE_AGENT_TEMPLATE
        if self.provider == ModelProvider.META and "3." in self.model_id:
            # llama3.x works better with custom template
            return LLAMA_AGENT_TEMPLATE
        return NATIVE_AGENT_TEMPLATE


class _OciApiFormatter(ABC):
    @classmethod
    @abstractmethod
    def convert_prompt_into_request(cls, prompt: "Prompt", model_id: str) -> Any: ...

    @staticmethod
    @abstractmethod
    def extract_usage(response: Dict[str, Any]) -> Optional[TokenUsage]: ...

    @staticmethod
    @abstractmethod
    def convert_completion_into_message(response: Dict[str, Any]) -> "Message": ...

    @staticmethod
    @abstractmethod
    def convert_oci_chunk_iterator_into_tagged_chunk_iterator(
        iterator: Iterator[Any],
        post_processing: Optional[Callable[["Message"], "Message"]] = None,
    ) -> Iterator[TaggedMessageChunkTypeWithTokenUsage]: ...


class _GenericOciApiFormatter(_OciApiFormatter):

    @classmethod
    def convert_prompt_into_request(cls, prompt: "Prompt", model_id: str) -> Any:
        import oci

        response_format = None
        if prompt.response_format is not None:
            json_schema = _property_to_openai_schema(prompt.response_format)
            response_format = oci.generative_ai_inference.models.JsonSchemaResponseFormat(
                json_schema=oci.generative_ai_inference.models.ResponseJsonSchema(
                    name=prompt.response_format.name, is_strict=True, schema=json_schema
                )
            )

        return oci.generative_ai_inference.models.GenericChatRequest(
            messages=[_message_to_generic_oci_message(m) for m in prompt.messages],
            tools=(
                [_tools_to_oci_generic_tools(t) for t in prompt.tools]
                if prompt.tools is not None
                else None
            ),
            response_format=response_format,
            **cls._generation_config_to_oci_parameter(prompt.generation_config),
        )

    @staticmethod
    def _generation_config_to_oci_parameter(
        generation_config: Optional[LlmGenerationConfig],
    ) -> Any:
        return _generation_config_to_generic_oci_parameters(generation_config, False)

    @staticmethod
    def extract_usage(response: Dict[str, Any]) -> Optional[TokenUsage]:
        # OCI doesnt use tokens, but rather characters to bill
        return None

    @staticmethod
    def convert_completion_into_message(response: Dict[str, Any]) -> "Message":
        from wayflowcore.messagelist import Message

        completion_choices = response.data.chat_response.choices  # type: ignore
        if len(completion_choices) > 1:
            raise NotImplementedError("Provider does not support multiple completions")

        completion_message = completion_choices[0].message
        text_content, tool_requests = "", None
        if completion_message.content is not None:
            text_content = "".join(t.text for t in completion_message.content if t.type == "TEXT")
        if completion_message.tool_calls is not None and len(completion_message.tool_calls) > 0:
            tool_requests = [
                ToolRequest(
                    name=tc.name,
                    args=json.loads(tc.arguments),
                    tool_request_id=tc.id,
                )
                for tc in completion_message.tool_calls
            ]
        return Message(
            content=text_content,
            tool_requests=tool_requests,
            role="assistant",
        )

    @staticmethod
    def convert_oci_chunk_iterator_into_tagged_chunk_iterator(
        iterator: Iterator[Any],
        post_processing: Optional[Callable[["Message"], "Message"]] = None,
    ) -> Iterator[TaggedMessageChunkTypeWithTokenUsage]:
        from wayflowcore.messagelist import Message, MessageType

        # start the stream
        yield StreamChunkType.START_CHUNK, Message(content="", message_type=MessageType.AGENT), None

        accumulated_text = ""
        tool_deltas = []
        for raw_chunk in iterator:
            chunk = json.loads(raw_chunk.data)
            text_delta, tool_requests = "", None

            if "message" not in chunk:
                delta = {}
            else:
                delta = chunk["message"]

            if "tool_calls" in delta:
                tool_deltas.extend(delta["tool_calls"])
            if "toolCalls" in delta:
                tool_deltas.extend(delta["toolCalls"])

            if "content" in delta and delta["content"] is not None:
                text_delta = "".join(t["text"] for t in delta["content"] if t["type"] == "TEXT")
                accumulated_text += text_delta

            if text_delta != "":
                yield StreamChunkType.TEXT_CHUNK, Message(
                    contents=[TextContent(text_delta)], message_type=MessageType.AGENT
                ), None

        message_has_tool_calls = len(tool_deltas) > 0
        if message_has_tool_calls:
            tool_calls = _convert_tool_deltas_into_tool_requests(tool_deltas)
        else:
            tool_calls = None
        message = Message(
            content=accumulated_text,
            tool_requests=tool_calls,
            role="assistant",
        )
        if post_processing is not None:
            message = post_processing(message)
        yield StreamChunkType.END_CHUNK, message, None  # oci doesn't have token counts


class _MetaOciApiFormatter(_GenericOciApiFormatter):
    @staticmethod
    def _generation_config_to_oci_parameter(
        generation_config: Optional[LlmGenerationConfig],
    ) -> Any:
        return _generation_config_to_generic_oci_parameters(generation_config, True)


def _generation_config_to_generic_oci_parameters(
    generation_config: Optional[LlmGenerationConfig], meta_model: bool
) -> Dict[str, Any]:
    if generation_config is None:
        return {}

    kwargs: Dict[str, Any] = {}
    if generation_config.top_p is not None:
        kwargs["top_p"] = generation_config.top_p
    if generation_config.temperature is not None:
        kwargs["temperature"] = generation_config.temperature
    if generation_config.max_tokens is not None:
        if meta_model:
            kwargs["max_tokens"] = generation_config.max_tokens
        else:
            # recent providers use this new name
            kwargs["max_completion_tokens"] = generation_config.max_tokens
    if generation_config.stop is not None:
        kwargs["stop"] = generation_config.stop
    if generation_config.frequency_penalty is not None and meta_model:
        # only meta models support frequency penalty
        kwargs["frequency_penalty"] = generation_config.frequency_penalty
    if generation_config.extra_args:
        kwargs.update(generation_config.extra_args)

    return kwargs


def _tools_to_oci_generic_tools(tool: Tool) -> Any:
    import oci

    return oci.generative_ai_inference.models.FunctionDefinition(
        name=tool.name,
        description=tool.description,
        parameters=tool.to_openai_format()["function"]["parameters"],
    )


def _message_to_generic_oci_message(m: "Message") -> Any:
    import oci

    if m.tool_requests is not None:
        return oci.generative_ai_inference.models.AssistantMessage(
            tool_calls=(
                [
                    oci.generative_ai_inference.models.FunctionCall(
                        id=tool_call.tool_request_id,
                        name=tool_call.name,
                        arguments=json.dumps(tool_call.args),
                    )
                    for tool_call in m.tool_requests
                ]
                if m.tool_requests is not None
                else None
            ),
            content=(
                [oci.generative_ai_inference.models.TextContent(text=m.content)]
                if m.content != ""
                else []
            ),
        )
    elif m.tool_result:
        return oci.generative_ai_inference.models.ToolMessage(
            content=[
                oci.generative_ai_inference.models.TextContent(
                    text=stringify(m.tool_result.content)
                )
            ],
            tool_call_id=m.tool_result.tool_request_id,
        )
    contents = []
    for content in m.contents:
        if isinstance(content, TextContent):
            contents.append(oci.generative_ai_inference.models.TextContent(text=content.content))
        elif isinstance(content, ImageContent):
            contents.append(
                oci.generative_ai_inference.models.ImageContent(
                    type="IMAGE",
                    image_url=oci.generative_ai_inference.models.ImageUrl(
                        url=content.base64_content
                    ),
                )
            )
        else:
            raise RuntimeError(f"Unsupported content of type {content.__class__.__name__}")
    role = m.role
    if role == "user":
        return oci.generative_ai_inference.models.UserMessage(content=contents)
    elif role == "system":
        return oci.generative_ai_inference.models.SystemMessage(content=contents)
    else:
        return oci.generative_ai_inference.models.AssistantMessage(content=contents)


def _convert_tool_deltas_into_tool_requests(tool_deltas: List[Any]) -> List[ToolRequest]:
    tool_calls = []
    current_tool_call: Dict[str, Any] = {}
    for chunk in tool_deltas:
        if "id" in chunk:
            if "id" in current_tool_call:
                tool_calls.append(current_tool_call)
            current_tool_call = {
                "type": "FUNCTION",
                "id": chunk["id"],
                "name": "",
                "arguments": "",
            }
        if "name" in chunk:
            current_tool_call["name"] += chunk["name"]
        if "arguments" in chunk:
            current_tool_call["arguments"] += chunk["arguments"]
    if "id" in current_tool_call:
        tool_calls.append(current_tool_call)
    return [
        ToolRequest(name=tc["name"], args=json.loads(tc["arguments"]), tool_request_id=tc["id"])
        for i, tc in enumerate(tool_calls)
    ]


class _CohereOciApiFormatter(_OciApiFormatter):
    @classmethod
    def convert_prompt_into_request(cls, prompt: "Prompt", model_id: str) -> Any:
        import oci

        cohere_response_format = None
        if prompt.response_format is not None:
            json_schema = _property_to_openai_schema(prompt.response_format)
            cohere_response_format = oci.generative_ai_inference.models.CohereResponseJsonFormat(
                schema=json_schema
            )

        ids_to_tool_requests = {
            tc.tool_request_id: tc
            for message in prompt.messages
            for tc in (message.tool_requests or [])
        }

        message: str = ""
        chat_history: List[oci.generative_ai_inference.models.CohereMessage] = []
        tool_results: List[oci.generative_ai_inference.models.CohereToolResult] = []

        for index in range(len(prompt.messages) - 1, -1, -1):
            # Same as for msg in prompt.messages[::-1]:
            msg = prompt.messages[index]
            for content in msg.contents:
                if not isinstance(content, TextContent):
                    raise RuntimeError(
                        f"Cohere models only support text messages as input, passed {content}"
                    )
            text_content = "\n".join(
                [cast(TextContent, content).content for content in msg.contents]
            )
            if (msg.role == "user") and (len(chat_history) == 0):
                message += text_content
            elif (
                msg.message_type == MessageType.TOOL_RESULT
                and len(chat_history) == 0
                and msg.tool_result is not None
            ):
                tool_request = ids_to_tool_requests[msg.tool_result.tool_request_id]
                tool_results.append(
                    oci.generative_ai_inference.models.CohereToolResult(
                        call=oci.generative_ai_inference.models.CohereToolCall(
                            name=tool_request.name,
                            parameters=tool_request.args,
                        ),
                        outputs=[
                            (
                                {"result": msg.tool_result.content}
                                if not isinstance(msg.tool_result.content, dict)
                                else msg.tool_result.content
                            )
                        ],
                    )
                )
            else:
                chat_history.append(
                    _convert_message_into_cohere_oci_message(
                        msg, ids_to_tool_requests, text_content=text_content
                    )
                )

        if message == "" and len(tool_results) == 0:
            # hack, cohere will crash if no user message or tool results. Therefore, we simulate a user message
            message = "Start"

        return oci.generative_ai_inference.models.CohereChatRequest(
            message=message,
            chat_history=chat_history[::-1],
            response_format=cohere_response_format,
            tool_results=tool_results or None,
            tools=(
                [_tools_to_oci_cohere_tools(t) for t in prompt.tools]
                if prompt.tools is not None
                else None
            ),
            **_generation_config_to_cohere_oci_parameters(prompt.generation_config),
        )

    @staticmethod
    def extract_usage(response: Dict[str, Any]) -> Optional[TokenUsage]:
        # only recent versions of oci have `usage` attribute
        if hasattr(response.data.chat_response, "usage"):  # type: ignore
            usage = response.data.chat_response.usage  # type: ignore
            return TokenUsage(
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                exact_count=True,
            )
        return None

    @staticmethod
    def convert_completion_into_message(response: Dict[str, Any]) -> "Message":
        from wayflowcore.messagelist import Message

        chat_response = response.data.chat_response  # type: ignore

        text_content, tool_requests = "", None
        if chat_response.text is not None:
            text_content = chat_response.text
        if chat_response.tool_calls is not None and len(chat_response.tool_calls) > 0:
            tool_requests = [
                ToolRequest(
                    name=tc.name,
                    args=tc.parameters,
                    tool_request_id=str(uuid.uuid4()),
                )
                for tc in chat_response.tool_calls
            ]
        return Message(content=text_content, tool_requests=tool_requests, role="assistant")

    @staticmethod
    def convert_oci_chunk_iterator_into_tagged_chunk_iterator(
        iterator: Iterator[Any],
        post_processing: Optional[Callable[["Message"], "Message"]] = None,
    ) -> Iterator[TaggedMessageChunkTypeWithTokenUsage]:
        from wayflowcore.messagelist import Message, MessageType

        # start the stream
        yield StreamChunkType.START_CHUNK, Message(content="", message_type=MessageType.AGENT), None

        tool_calls = []
        accumulated_text = ""

        for raw_chunk in iterator:
            response = json.loads(raw_chunk.data)
            text_content = ""

            if "text" in response and response["text"] is not None:
                text_content = response["text"]

            if "finishReason" in response:
                if accumulated_text != text_content:
                    logger.info(
                        "Cohere last chunk does not contain the accumulated text:\naccumulated text: %s\nlast_chunk_text: %s",
                        accumulated_text,
                        text_content,
                    )
                break

            if "toolCalls" in response:
                tool_calls = [
                    ToolRequest(
                        name=t["name"],
                        args=t.get("parameters", {}),
                        tool_request_id=str(uuid.uuid4()),
                    )
                    for t in response["toolCalls"]
                ]
                text_content = accumulated_text
                # cohere oci returns the text accumulated in the tool call chunk too
                # we assert so that if it changes in the future, we know about it
                # and don't end up with duplicated content silently
                assert text_content == accumulated_text  # nosec
            else:
                accumulated_text += text_content

            yield StreamChunkType.TEXT_CHUNK, Message(
                content=text_content, message_type=MessageType.AGENT
            ), None

        final_message = Message(
            content=accumulated_text,
            tool_requests=tool_calls or None,
            role="assistant",
        )
        yield StreamChunkType.END_CHUNK, final_message, None


def _convert_message_into_cohere_oci_message(
    m: "Message", id_to_too_requests_dict: Dict[str, ToolRequest], text_content: str
) -> Any:
    import oci

    if m.tool_requests is not None:

        return oci.generative_ai_inference.models.CohereChatBotMessage(
            tool_calls=(
                [
                    oci.generative_ai_inference.models.CohereToolCall(
                        name=tool_call.name,
                        parameters=tool_call.args,
                    )
                    for tool_call in m.tool_requests
                ]
                if m.tool_requests is not None
                else None
            ),
            message=text_content,
        )

    elif m.tool_result is not None:
        tool_request = id_to_too_requests_dict[m.tool_result.tool_request_id]
        return oci.generative_ai_inference.models.CohereToolMessage(
            tool_results=[
                oci.generative_ai_inference.models.CohereToolResult(
                    call=oci.generative_ai_inference.models.CohereToolCall(
                        name=tool_request.name,
                        parameters=tool_request.args,
                    ),
                    outputs=[{"result": stringify(m.tool_result.content)}],
                )
            ]
        )
    if len(m.contents) == 0:
        raise RuntimeError("Empty message")
    if len(m.contents) == 0 or isinstance(m.contents[0], TextContent):
        role = m.role
        message = text_content

        if role == "user":
            return oci.generative_ai_inference.models.CohereUserMessage(message=message)
        elif role == "system":
            return oci.generative_ai_inference.models.CohereSystemMessage(message=message)
        else:
            return oci.generative_ai_inference.models.CohereChatBotMessage(message=message)


def _tools_to_oci_cohere_tools(tool: Tool) -> Any:
    import oci

    return oci.generative_ai_inference.models.CohereTool(
        name=tool.name,
        description=tool.description,
        parameter_definitions={
            parameter_name: oci.generative_ai_inference.models.CohereParameterDefinition(
                description=parameter_json_type.get("description", ""),
                type=parameter_json_type.get("type", ""),
                is_required="default" in parameter_json_type,
            )
            for parameter_name, parameter_json_type in tool.parameters.items()
        },
    )


def _generation_config_to_cohere_oci_parameters(
    generation_config: Optional[LlmGenerationConfig],
) -> Dict[str, Any]:
    # Fix applied as of May 2025, default max_tokens for
    # OCI Cohere is 20, which breaks several of our unit tests tests. If users set max_tokens
    # too low, it might still lead to an uncaught exception
    if generation_config is None or generation_config.max_tokens is None:
        cohere_default_max_tokens = 512
        warnings.warn(
            f"Setting `max_tokens` to {cohere_default_max_tokens} for cohere model to "
            "prevent issues with longer generated texts. To remove this warning, explicitly "
            "provide an LlmGenerationConfig with a max_token configuration when initializing "
            "the model.",
            UserWarning,
        )
        if generation_config is None:
            generation_config = LlmGenerationConfig(max_tokens=cohere_default_max_tokens)
        elif generation_config.max_tokens is None:
            generation_config.max_tokens = cohere_default_max_tokens
    if generation_config is not None and generation_config.frequency_penalty is not None:
        if generation_config.frequency_penalty < 0:
            raise ValueError("Cohere Models do not support negative frequency penalties")
        generation_config.frequency_penalty = generation_config.frequency_penalty / 2
        logger.info("rescaled frequency penalty to [0,1] range for Cohere compatibility")
        generation_config = deepcopy(generation_config)

    kwargs: Dict[str, Any] = {}
    if generation_config is None:
        return kwargs
    if generation_config.top_p is not None:
        kwargs["top_p"] = generation_config.top_p
    if generation_config.temperature is not None:
        kwargs["temperature"] = generation_config.temperature
    if generation_config.max_tokens is not None:
        kwargs["max_tokens"] = generation_config.max_tokens
    if generation_config.stop is not None:
        kwargs["stop_sequences"] = generation_config.stop
    if generation_config.extra_args:
        kwargs.update(generation_config.extra_args)
    return kwargs


_MODEL_PROVIDER_TO_FORMATTER = {
    ModelProvider.META: _MetaOciApiFormatter,
    ModelProvider.OTHER: _GenericOciApiFormatter,
    ModelProvider.COHERE: _CohereOciApiFormatter,
}


_UNSUPPORTED_ARGUMENT_PATTERNS_WITH_NAMES = [
    "Unsupported parameter: '{param_name}'",
    "Unsupported value: '{param_name}'",
    "Argument not supported on this model: {param_name}",
    "does not support parameter {param_name}",
]

_UNSUPPORTED_ARGUMENT_PATTERNS = [
    "Unsupported parameter:",
    "Unsupported value:",
    "Argument not supported on this model:",
    "does not support parameter",
]


def _adapt_generation_config_with_error_message(
    generation_config: LlmGenerationConfig, error_message: str
) -> LlmGenerationConfig:
    """Removes from the generation config any parameter mentioned as not supported in the error message"""
    new_generation_parameters = generation_config.to_dict()

    params_to_remove = []
    for param_name, param_value in new_generation_parameters.items():
        if any(
            pattern.format(param_name=param_name) in error_message
            for pattern in _UNSUPPORTED_ARGUMENT_PATTERNS_WITH_NAMES
        ):
            logger.warning(
                f"Parameter `{param_name}` is not supported by the OCI GenAI endpoint."
                f"Careful, the behavior of the agentic system might be impacted by not using this parameter."
                f"Full error message: {error_message}"
            )
            params_to_remove.append(param_name)

    for param_to_remove in params_to_remove:
        new_generation_parameters.pop(param_to_remove)

    return LlmGenerationConfig.from_dict(new_generation_parameters)
