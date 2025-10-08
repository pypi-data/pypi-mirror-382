import inspect
import traceback
from typing import Callable, Type, TypeVar

from pydantic import BaseModel

from pharia_skill import Csi
from pharia_skill.message_stream.writer import MessageWriter, Payload

UserInput = TypeVar("UserInput", bound=BaseModel)


def message_stream(
    func: Callable[[Csi, MessageWriter[Payload], UserInput], None],
) -> Callable[[Csi, MessageWriter[Payload], UserInput], None]:
    """Turn a function with a specific signature into a (streaming) skill that can be deployed on Pharia Kernel.

    By using the response object, a Skill decorated with `@message_stream` can return intermediate results
    that are streamed to the caller.

    The decorated function must be typed. It must have exactly three arguments. The first argument
    must be of type `Csi`. The second argument must be a `Response` object. The third argument
    must be a Pydantic model. The function must not return anything.

    Example::

        from pharia_skill import Csi, ChatParams, Message, message_stream, MessageWriter
        from pydantic import BaseModel
        from pharia_skill.csi.inference import FinishReason

        class Input(BaseModel):
            topic: str

        class SkillOutput(BaseModel):
            finish_reason: FinishReason

        @message_stream
        def haiku_stream(csi: Csi, writer: MessageWriter[SkillOutput], input: Input) -> None:
            model = "llama-3.1-8b-instruct"
            messages = [
                Message.system("You are a poet who strictly speaks in haikus."),
                Message.user(input.topic),
            ]
            params = ChatParams()
            with csi.chat_stream(model, messages, params) as response:
                writer.begin_message()
                for event in response.stream():
                    writer.append_to_message(event.content)
                writer.end_message(SkillOutput(finish_reason=response.finish_reason()))
    """
    # The import is inside the decorator to ensure the imports only run when the decorator is interpreted.
    # This is because we can only import them when targeting the `message-stream-skill` world.
    # If we target the `skill` world with a component and have the imports for the `message-stream-skill` world
    # in this module at the top-level, we will get a build error in case this module is in the module graph.
    from pharia_skill.bindings import exports
    from pharia_skill.bindings.exports.message_stream import (
        Error_Internal,
        Error_InvalidInput,
    )
    from pharia_skill.bindings.imports import streaming_output as wit
    from pharia_skill.bindings.types import Err
    from pharia_skill.message_stream.wit_writer import WitMessageWriter
    from pharia_skill.wit_csi.csi import WitCsi

    signature = list(inspect.signature(func).parameters.values())
    assert len(signature) == 3, (
        "Message Stream Skills must have exactly three arguments."
    )

    input_model: Type[UserInput] = signature[2].annotation
    assert isinstance(input_model, type) and issubclass(input_model, BaseModel), (
        "The third argument must be a Pydantic model, found: " + str(input_model)
    )

    assert func.__annotations__.get("return") is None, (
        "The function must not return anything"
    )

    # We don't require the schema of the end payload in the function definition.
    # The only use case for this would be to know the metadata of the end payload.
    # Since we don't do metadata for streaming skills at the moment, it is not needed.

    class MessageStream(exports.MessageStream):
        def run(self, input: bytes, output: wit.StreamOutput) -> None:
            """This is the function that gets executed when running the Skill as a Wasm component."""
            try:
                validated = input_model.model_validate_json(input)
            except Exception:
                raise Err(Error_InvalidInput(traceback.format_exc()))
            try:
                with WitMessageWriter[Payload](output) as writer:
                    func(WitCsi(), writer, validated)
            except Exception:
                raise Err(Error_Internal(traceback.format_exc()))

    assert "MessageStream" not in func.__globals__, (
        "Make sure to decorate with `@message_stream` only once."
    )

    def trace_message_stream(
        csi: Csi, writer: MessageWriter[Payload], input: UserInput
    ) -> None:
        """This function is returned by the decorator and executed at test time.

        The `opentelemetry` library import is moved to within the function to not make it a dependency of the
        Wasm component.
        """
        from opentelemetry import trace

        from pharia_skill.testing.dev.streaming_output import MessageRecorder

        with trace.get_tracer(__name__).start_as_current_span(func.__name__) as span:
            writer.span = span  # type: ignore

            span.set_attribute("input", input.model_dump_json())
            func(csi, writer, input)

            # We do rely on the user passing in a message recorder at test time if they
            # want tracing to work.
            if isinstance(writer, MessageRecorder):
                span.set_attribute("output", writer.skill_output())
            return

    func.__globals__["MessageStream"] = MessageStream
    trace_message_stream.__globals__["MessageStream"] = MessageStream
    return trace_message_stream
