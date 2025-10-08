import json
from typing import Sequence

from pharia_skill.csi.inference import (
    ChatStreamResponse,
    CompletionStreamResponse,
)
from pharia_skill.csi.inference.tool import Tool

from ..bindings.imports import chunking as wit_chunking
from ..bindings.imports import document_index as wit_document_index
from ..bindings.imports import inference as wit_inference
from ..bindings.imports import language as wit_language
from ..bindings.types import Ok, Result
from ..csi import (
    ChatParams,
    ChatRequest,
    ChatResponse,
    Chunk,
    ChunkRequest,
    Completion,
    CompletionParams,
    CompletionRequest,
    Csi,
    Document,
    DocumentPath,
    ExplanationRequest,
    InvokeRequest,
    JsonSerializable,
    Language,
    Message,
    SearchRequest,
    SearchResult,
    SelectLanguageRequest,
    TextScore,
    ToolError,
    ToolOutput,
    ToolResult,
)
from .chunking import chunk_from_wit, chunk_request_to_wit
from .document_index import (
    document_from_wit,
    document_path_to_wit,
    search_request_to_wit,
    search_result_from_wit,
)
from .inference import (
    WitChatStreamResponse,
    WitCompletionStreamResponse,
    chat_request_to_wit,
    chat_response_from_wit,
    completion_from_wit,
    completion_request_to_wit,
    completion_request_to_wit_v2,
    explanation_request_to_wit,
    text_score_from_wit,
)
from .language import language_from_wit, language_request_to_wit


class WitCsi(Csi):
    """Implementation of the Cognitive System Interface (CSI) that gets injected to skills at runtime.

    Responsible to translate between the types we expose in the SDK and the types in the `wit.imports` module,
    which are automatically generated from the WIT world via `componentize-py`.

    All parameters to any methods on the `WitCsi` must be type checked, as otherwise `componentize-py`
    produces a non-helpful error message. This is done by using `pydantic.dataclasses`. See the
    docstring of `csi` module for more information.
    """

    def invoke_tool_concurrent(
        self, requests: Sequence[InvokeRequest]
    ) -> list[ToolResult]:
        from ..bindings.imports import tool as wit_tool

        def invoke_request_to_wit(request: InvokeRequest) -> wit_tool.InvokeRequest:
            return wit_tool.InvokeRequest(
                tool_name=request.name,
                arguments=[
                    wit_tool.Argument(name=name, value=json.dumps(value).encode())
                    for name, value in request.arguments.items()
                ],
            )

        def tool_output_from_wit(
            response: Result[list[wit_tool.Modality], str],
        ) -> ToolResult:
            return (
                ToolOutput(contents=[modality.value for modality in response.value])
                if isinstance(response, Ok)
                else ToolError(message=response.value)
            )

        wit_requests = [invoke_request_to_wit(request) for request in requests]
        responses = wit_tool.invoke_tool(wit_requests)
        return [tool_output_from_wit(response) for response in responses]

    def list_tools(self) -> list[Tool]:
        from ..bindings.imports import tool as wit_tool

        return [
            Tool(
                name=tool.name,
                description=tool.description,
                input_schema=json.loads(tool.input_schema),
            )
            for tool in wit_tool.list_tools()
        ]

    def _completion_stream(
        self, model: str, prompt: str, params: CompletionParams
    ) -> CompletionStreamResponse:
        request = completion_request_to_wit(CompletionRequest(model, prompt, params))
        stream = wit_inference.CompletionStream(request)
        return WitCompletionStreamResponse(stream)

    def _chat_stream(
        self, model: str, messages: list[Message], params: ChatParams
    ) -> ChatStreamResponse:
        request = chat_request_to_wit(ChatRequest(model, messages, params))
        stream = wit_inference.ChatStream(request)
        return WitChatStreamResponse(stream)

    def complete_concurrent(
        self, requests: Sequence[CompletionRequest]
    ) -> list[Completion]:
        wit_requests = [completion_request_to_wit_v2(r) for r in requests]
        completions = wit_inference.complete_v2(wit_requests)
        return [completion_from_wit(completion) for completion in completions]

    def chat_concurrent(self, requests: Sequence[ChatRequest]) -> list[ChatResponse]:
        wit_requests = [chat_request_to_wit(r) for r in requests]
        responses = wit_inference.chat(wit_requests)
        return [chat_response_from_wit(response) for response in responses]

    def explain_concurrent(
        self, requests: Sequence[ExplanationRequest]
    ) -> list[list[TextScore]]:
        wit_requests = [explanation_request_to_wit(r) for r in requests]
        responses = wit_inference.explain(wit_requests)
        return [
            [text_score_from_wit(score) for score in scores] for scores in responses
        ]

    def chunk_concurrent(self, requests: Sequence[ChunkRequest]) -> list[list[Chunk]]:
        wit_requests = [chunk_request_to_wit(r) for r in requests]
        responses = wit_chunking.chunk_with_offsets(wit_requests)
        return [[chunk_from_wit(chunk) for chunk in response] for response in responses]

    def select_language_concurrent(
        self, requests: Sequence[SelectLanguageRequest]
    ) -> list[Language | None]:
        wit_requests = [language_request_to_wit(r) for r in requests]
        languages = wit_language.select_language(wit_requests)
        return [
            language_from_wit(lang) if lang is not None else None for lang in languages
        ]

    def search_concurrent(
        self, requests: Sequence[SearchRequest]
    ) -> list[list[SearchResult]]:
        wit_requests = [search_request_to_wit(r) for r in requests]
        results = wit_document_index.search(wit_requests)
        return [
            [search_result_from_wit(result) for result in results_per_request]
            for results_per_request in results
        ]

    def documents(self, document_paths: Sequence[DocumentPath]) -> list[Document]:
        requests = [document_path_to_wit(path) for path in document_paths]
        documents = wit_document_index.documents(requests)
        return [document_from_wit(document) for document in documents]

    def documents_metadata(
        self, document_paths: Sequence[DocumentPath]
    ) -> list[JsonSerializable]:
        requests = [document_path_to_wit(path) for path in document_paths]
        metadata = wit_document_index.document_metadata(requests)
        return [json.loads(metadata) if metadata else None for metadata in metadata]
