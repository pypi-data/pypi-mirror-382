import asyncio
import json
from collections.abc import AsyncIterator
from datetime import datetime
from inspect import cleandoc
from typing import (
    Annotated,
    Any,
    AsyncGenerator,
    Awaitable,
    Generic,
    Sequence,
    TypeVar,
    assert_never,
    cast,
)

from agents import (
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    RunResultStreaming,
    StreamEvent,
    TResponseInputItem,
)
from openai.types.responses import (
    EasyInputMessageParam,
    ResponseFunctionToolCallParam,
    ResponseInputContentParam,
    ResponseInputMessageContentListParam,
    ResponseInputTextParam,
    ResponseOutputText,
)
from openai.types.responses.response_input_item_param import (
    FunctionCallOutput,
    Message,
)
from openai.types.responses.response_output_message import Content
from openai.types.responses.response_output_text import (
    Annotation as ResponsesAnnotation,
)
from pydantic import BaseModel, ConfigDict, SkipValidation, TypeAdapter

from .server import stream_widget
from .store import Store, StoreItemType
from .types import (
    Annotation,
    AssistantMessageContent,
    AssistantMessageContentPartAdded,
    AssistantMessageContentPartDone,
    AssistantMessageContentPartTextDelta,
    AssistantMessageItem,
    Attachment,
    ClientToolCallItem,
    DurationSummary,
    EndOfTurnItem,
    FileSource,
    HiddenContextItem,
    Task,
    TaskItem,
    ThoughtTask,
    ThreadItem,
    ThreadItemAddedEvent,
    ThreadItemDoneEvent,
    ThreadItemRemovedEvent,
    ThreadItemUpdated,
    ThreadMetadata,
    ThreadStreamEvent,
    URLSource,
    UserMessageItem,
    UserMessageTagContent,
    UserMessageTextContent,
    WidgetItem,
    Workflow,
    WorkflowItem,
    WorkflowSummary,
    WorkflowTaskAdded,
    WorkflowTaskUpdated,
)
from .widgets import Markdown, Text, WidgetRoot


class ClientToolCall(BaseModel):
    """
    Returned from tool methods to indicate a client-side tool call.
    """

    name: str
    arguments: dict[str, Any]


class _QueueCompleteSentinel: ...


TContext = TypeVar("TContext")


class AgentContext(BaseModel, Generic[TContext]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    thread: ThreadMetadata
    store: Annotated[Store[TContext], SkipValidation]
    request_context: TContext
    previous_response_id: str | None = None
    client_tool_call: ClientToolCall | None = None
    workflow_item: WorkflowItem | None = None
    _events: asyncio.Queue[ThreadStreamEvent | _QueueCompleteSentinel] = asyncio.Queue()

    def generate_id(
        self, type: StoreItemType, thread: ThreadMetadata | None = None
    ) -> str:
        if type == "thread":
            return self.store.generate_thread_id(self.request_context)
        return self.store.generate_item_id(
            type, thread or self.thread, self.request_context
        )

    async def stream_widget(
        self,
        widget: WidgetRoot | AsyncGenerator[WidgetRoot, None],
        copy_text: str | None = None,
    ) -> None:
        async for event in stream_widget(
            self.thread,
            widget,
            copy_text,
            lambda item_type: self.store.generate_item_id(
                item_type, self.thread, self.request_context
            ),
        ):
            await self._events.put(event)

    async def end_workflow(
        self, summary: WorkflowSummary | None = None, expanded: bool = False
    ) -> None:
        if not self.workflow_item:
            # No workflow to end
            return

        if summary is not None:
            self.workflow_item.workflow.summary = summary
        elif self.workflow_item.workflow.summary is None:
            # If no summary was set or provided, set a basic work summary
            delta = datetime.now() - self.workflow_item.created_at
            duration = int(delta.total_seconds())
            self.workflow_item.workflow.summary = DurationSummary(duration=duration)
        self.workflow_item.workflow.expanded = expanded
        await self.stream(ThreadItemDoneEvent(item=self.workflow_item))
        self.workflow_item = None

    async def start_workflow(self, workflow: Workflow) -> None:
        self.workflow_item = WorkflowItem(
            id=self.generate_id("workflow"),
            created_at=datetime.now(),
            workflow=workflow,
            thread_id=self.thread.id,
        )

        if workflow.type != "reasoning" and len(workflow.tasks) == 0:
            # Defer sending added event until we have tasks
            return

        await self.stream(ThreadItemAddedEvent(item=self.workflow_item))

    async def update_workflow_task(self, task: Task, task_index: int) -> None:
        if self.workflow_item is None:
            raise ValueError("Workflow is not set")
        # ensure reference is updated in case task is a copy
        self.workflow_item.workflow.tasks[task_index] = task
        await self.stream(
            ThreadItemUpdated(
                item_id=self.workflow_item.id,
                update=WorkflowTaskUpdated(
                    task=task,
                    task_index=task_index,
                ),
            )
        )

    async def add_workflow_task(self, task: Task) -> None:
        self.workflow_item = self.workflow_item or WorkflowItem(
            id=self.generate_id("workflow"),
            created_at=datetime.now(),
            workflow=Workflow(type="custom", tasks=[]),
            thread_id=self.thread.id,
        )
        workflow = self.workflow_item.workflow
        workflow.tasks.append(task)

        if workflow.type != "reasoning" and len(workflow.tasks) == 1:
            await self.stream(ThreadItemAddedEvent(item=self.workflow_item))
        else:
            await self.stream(
                ThreadItemUpdated(
                    item_id=self.workflow_item.id,
                    update=WorkflowTaskAdded(
                        task=task,
                        task_index=workflow.tasks.index(task),
                    ),
                )
            )

    async def stream(self, event: ThreadStreamEvent) -> None:
        await self._events.put(event)

    def _complete(self):
        self._events.put_nowait(_QueueCompleteSentinel())


def _convert_content(content: Content) -> AssistantMessageContent:
    if content.type == "output_text":
        annotations = []
        for annotation in content.annotations:
            annotations.extend(_convert_annotation(annotation))
        return AssistantMessageContent(
            text=content.text,
            annotations=annotations,
        )
    else:
        return AssistantMessageContent(
            text=content.refusal,
            annotations=[],
        )


def _convert_annotation(
    annotation: ResponsesAnnotation,
) -> list[Annotation]:
    # There is a bug in the OpenAPI client that sometimes parses the annotation delta event into the wrong class
    # resulting into annotation being a dict instead of a ResponsesAnnotation
    if isinstance(annotation, dict):
        annotation = TypeAdapter(ResponsesAnnotation).validate_python(annotation)

    result: list[Annotation] = []
    if annotation.type == "file_citation":
        filename = annotation.filename
        if not filename:
            return []
        result.append(
            Annotation(
                source=FileSource(filename=filename, title=filename),
                index=annotation.index,
            )
        )
    elif annotation.type == "url_citation":
        result.append(
            Annotation(
                source=URLSource(
                    url=annotation.url,
                    title=annotation.title,
                ),
                index=annotation.end_index,
            )
        )

    return result


T1 = TypeVar("T1")
T2 = TypeVar("T2")


async def _merge_generators(
    a: AsyncIterator[T1],
    b: AsyncIterator[T2],
) -> AsyncIterator[T1 | T2]:
    pending: list[AsyncIterator[T1 | T2]] = [a, b]
    pending_tasks: dict[asyncio.Task, AsyncIterator[T1 | T2]] = {
        asyncio.ensure_future(g.__anext__()): g for g in pending
    }
    while len(pending_tasks) > 0:
        done, _ = await asyncio.wait(
            pending_tasks.keys(), return_when="FIRST_COMPLETED"
        )
        stop = False
        for d in done:
            try:
                result = d.result()
                yield result
                dg = pending_tasks[d]
                pending_tasks[asyncio.ensure_future(dg.__anext__())] = dg
            except StopAsyncIteration:
                stop = True
            finally:
                del pending_tasks[d]
        if stop:
            for task in pending_tasks.keys():
                if not task.cancel():
                    try:
                        yield task.result()
                    except asyncio.CancelledError:
                        pass
                    except asyncio.InvalidStateError:
                        pass
            break


class _EventWrapper:
    def __init__(self, event: ThreadStreamEvent):
        self.event = event


class _AsyncQueueIterator(AsyncIterator[_EventWrapper]):
    def __init__(
        self, queue: asyncio.Queue[ThreadStreamEvent | _QueueCompleteSentinel]
    ):
        self.queue = queue
        self.completed = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.completed:
            raise StopAsyncIteration

        item = await self.queue.get()
        if isinstance(item, _QueueCompleteSentinel):
            self.completed = True
            raise StopAsyncIteration
        return _EventWrapper(item)

    def drain_and_complete(self) -> None:
        """Empty the underlying queue without awaiting and mark this iterator completed.

        This is intended for cleanup paths where we must guarantee no awaits
        occur. All queued items, including any completion sentinel, are
        discarded.
        """
        while True:
            try:
                self.queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        self.completed = True


class StreamingThoughtTracker(BaseModel):
    item_id: str
    index: int
    task: ThoughtTask


async def stream_agent_response(
    context: AgentContext, result: RunResultStreaming
) -> AsyncIterator[ThreadStreamEvent]:
    current_item_id = None
    current_tool_call = None
    ctx = context
    thread = context.thread
    queue_iterator = _AsyncQueueIterator(context._events)
    produced_items = set()
    streaming_thought: None | StreamingThoughtTracker = None

    # check if the last item in the thread was a workflow or a client tool call
    # if it was a client tool call, check if the second last item was a workflow
    # if either was, continue the workflow
    items = await context.store.load_thread_items(
        thread.id, None, 2, "desc", context.request_context
    )
    last_item = items.data[0] if len(items.data) > 0 else None
    second_last_item = items.data[1] if len(items.data) > 1 else None

    if last_item and last_item.type == "workflow":
        ctx.workflow_item = last_item
    elif (
        last_item
        and last_item.type == "client_tool_call"
        and second_last_item
        and second_last_item.type == "workflow"
    ):
        ctx.workflow_item = second_last_item

    def end_workflow(item: WorkflowItem):
        if item == ctx.workflow_item:
            ctx.workflow_item = None
        delta = datetime.now() - item.created_at
        duration = int(delta.total_seconds())
        if item.workflow.summary is None:
            item.workflow.summary = DurationSummary(duration=duration)
        # Default to closing all workflows
        # To keep a workflow open on completion, close it explicitly with
        # AgentContext.end_workflow(expanded=True)
        item.workflow.expanded = False
        return ThreadItemDoneEvent(item=item)

    try:
        async for event in _merge_generators(result.stream_events(), queue_iterator):
            # Events emitted from agent context helpers
            if isinstance(event, _EventWrapper):
                event = event.event
                if (
                    event.type == "thread.item.added"
                    or event.type == "thread.item.done"
                ):
                    # End the current workflow if visual item is added after it
                    if (
                        ctx.workflow_item
                        and ctx.workflow_item.id != event.item.id
                        and event.item.type != "client_tool_call"
                        and event.item.type != "hidden_context_item"
                    ):
                        yield end_workflow(ctx.workflow_item)

                    # track the current workflow if one is added
                    if (
                        event.type == "thread.item.added"
                        and event.item.type == "workflow"
                    ):
                        ctx.workflow_item = event.item

                    # track integration produced items so we can clean them up if
                    # there is a guardrail tripwire
                    produced_items.add(event.item.id)
                yield event
                continue

            if event.type == "run_item_stream_event":
                event = event.item
                if (
                    event.type == "tool_call_item"
                    and event.raw_item.type == "function_call"
                ):
                    current_tool_call = event.raw_item.call_id
                    current_item_id = event.raw_item.id
                    assert current_item_id
                    produced_items.add(current_item_id)
                continue

            if event.type != "raw_response_event":
                # Ignore everything else that isn't a raw response event
                continue

            # Handle Responses events
            event = event.data
            if event.type == "response.content_part.added":
                if event.part.type == "reasoning_text":
                    continue
                content = _convert_content(event.part)
                yield ThreadItemUpdated(
                    item_id=event.item_id,
                    update=AssistantMessageContentPartAdded(
                        content_index=event.content_index,
                        content=content,
                    ),
                )
            elif event.type == "response.output_text.delta":
                yield ThreadItemUpdated(
                    item_id=event.item_id,
                    update=AssistantMessageContentPartTextDelta(
                        content_index=event.content_index,
                        delta=event.delta,
                    ),
                )
            elif event.type == "response.output_text.done":
                yield ThreadItemUpdated(
                    item_id=event.item_id,
                    update=AssistantMessageContentPartDone(
                        content_index=event.content_index,
                        content=AssistantMessageContent(
                            text=event.text,
                            annotations=[],
                        ),
                    ),
                )
            elif event.type == "response.output_text.annotation.added":
                # Ignore annotation-added events; annotations are reflected in the final item content.
                continue
            elif event.type == "response.output_item.added":
                item = event.item
                if item.type == "reasoning" and not ctx.workflow_item:
                    ctx.workflow_item = WorkflowItem(
                        id=ctx.generate_id("workflow"),
                        created_at=datetime.now(),
                        workflow=Workflow(type="reasoning", tasks=[]),
                        thread_id=thread.id,
                    )
                    produced_items.add(ctx.workflow_item.id)
                    yield ThreadItemAddedEvent(item=ctx.workflow_item)
                if item.type == "message":
                    if ctx.workflow_item:
                        yield end_workflow(ctx.workflow_item)
                    produced_items.add(item.id)
                    yield ThreadItemAddedEvent(
                        item=AssistantMessageItem(
                            # Reusing the Responses message ID
                            id=item.id,
                            thread_id=thread.id,
                            content=[_convert_content(c) for c in item.content],
                            created_at=datetime.now(),
                        ),
                    )
            elif event.type == "response.reasoning_summary_text.delta":
                if not ctx.workflow_item:
                    continue

                # stream the first thought in a new workflow so that we can show it earlier
                if (
                    ctx.workflow_item.workflow.type == "reasoning"
                    and len(ctx.workflow_item.workflow.tasks) == 0
                ):
                    streaming_thought = StreamingThoughtTracker(
                        item_id=event.item_id,
                        index=event.summary_index,
                        task=ThoughtTask(content=event.delta),
                    )
                    ctx.workflow_item.workflow.tasks.append(streaming_thought.task)
                    yield ThreadItemUpdated(
                        item_id=ctx.workflow_item.id,
                        update=WorkflowTaskAdded(
                            task=streaming_thought.task,
                            task_index=0,
                        ),
                    )
                elif (
                    streaming_thought
                    and streaming_thought.task in ctx.workflow_item.workflow.tasks
                    and event.item_id == streaming_thought.item_id
                    and event.summary_index == streaming_thought.index
                ):
                    streaming_thought.task.content += event.delta
                    yield ThreadItemUpdated(
                        item_id=ctx.workflow_item.id,
                        update=WorkflowTaskUpdated(
                            task=streaming_thought.task,
                            task_index=ctx.workflow_item.workflow.tasks.index(
                                streaming_thought.task
                            ),
                        ),
                    )
            elif event.type == "response.reasoning_summary_text.done":
                if ctx.workflow_item:
                    if (
                        streaming_thought
                        and streaming_thought.task in ctx.workflow_item.workflow.tasks
                        and event.item_id == streaming_thought.item_id
                        and event.summary_index == streaming_thought.index
                    ):
                        task = streaming_thought.task
                        task.content = event.text
                        streaming_thought = None
                        update = WorkflowTaskUpdated(
                            task=task,
                            task_index=ctx.workflow_item.workflow.tasks.index(task),
                        )
                    else:
                        task = ThoughtTask(content=event.text)
                        ctx.workflow_item.workflow.tasks.append(task)
                        update = WorkflowTaskAdded(
                            task=task,
                            task_index=ctx.workflow_item.workflow.tasks.index(task),
                        )
                    yield ThreadItemUpdated(
                        item_id=ctx.workflow_item.id,
                        update=update,
                    )
            elif event.type == "response.output_item.done":
                item = event.item
                if item.type == "message":
                    produced_items.add(item.id)
                    yield ThreadItemDoneEvent(
                        item=AssistantMessageItem(
                            # Reusing the Responses message ID
                            id=item.id,
                            thread_id=thread.id,
                            content=[_convert_content(c) for c in item.content],
                            created_at=datetime.now(),
                        ),
                    )

    except (InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered):
        for item_id in produced_items:
            yield ThreadItemRemovedEvent(item_id=item_id)

        # Drain remaining events without processing them
        context._complete()
        queue_iterator.drain_and_complete()

        raise

    context._complete()

    # Drain remaining events
    async for event in queue_iterator:
        yield event.event

    # If there is still an active workflow at the end of the run, store
    # it's current state so that we can continue it in the next turn.
    if ctx.workflow_item:
        await ctx.store.add_thread_item(
            thread.id, ctx.workflow_item, ctx.request_context
        )

    if context.client_tool_call:
        yield ThreadItemDoneEvent(
            item=ClientToolCallItem(
                id=current_item_id
                or context.store.generate_item_id(
                    "tool_call", thread, context.request_context
                ),
                thread_id=thread.id,
                name=context.client_tool_call.name,
                arguments=context.client_tool_call.arguments,
                created_at=datetime.now(),
                call_id=current_tool_call
                or context.store.generate_item_id(
                    "tool_call", thread, context.request_context
                ),
            ),
        )


TWidget = TypeVar("TWidget", bound=Markdown | Text)


async def accumulate_text(
    events: AsyncIterator[StreamEvent],
    base_widget: TWidget,
) -> AsyncIterator[TWidget]:
    text = ""
    yield base_widget
    async for event in events:
        if event.type == "raw_response_event":
            if event.data.type == "response.output_text.delta":
                text += event.data.delta
                yield base_widget.model_copy(update={"value": text})
    yield base_widget.model_copy(update={"value": text, "streaming": False})


class ThreadItemConverter:
    """
    Converts thread items to Agent SDK input items.
    Widgets, Tasks, and Workflows have default conversions but can be customized.
    Attachments, Tags, and HiddenContextItems require custom handling based on the use case.
    Other item types are converted automatically.
    """

    def attachment_to_message_content(
        self, attachment: Attachment
    ) -> Awaitable[ResponseInputContentParam]:
        """
        Convert an attachment in a user message into a message content part to send to the model.
        Required when attachments are enabled.
        """
        raise NotImplementedError(
            "An Attachment was included in a UserMessageItem but Converter.attachment_to_message_content was not implemented"
        )

    def tag_to_message_content(
        self, tag: UserMessageTagContent
    ) -> ResponseInputContentParam:
        """
        Convert a tag in a user message into a message content part to send to the model as context.
        Required when tags are used.
        """
        raise NotImplementedError(
            "A Tag was included in a UserMessageItem but Converter.tag_to_message_content is not implemented"
        )

    def hidden_context_to_input(
        self, item: HiddenContextItem
    ) -> TResponseInputItem | list[TResponseInputItem] | None:
        """
        Convert a HiddenContextItem into input item(s) to send to the model.
        Required when HiddenContextItem are used.
        """
        raise NotImplementedError(
            "HiddenContextItem were present in a user message but Converter.hidden_context_to_input was not implemented"
        )

    def task_to_input(
        self, item: TaskItem
    ) -> TResponseInputItem | list[TResponseInputItem] | None:
        """
        Convert a TaskItem into input item(s) to send to the model.
        """
        if item.task.type != "custom" or (
            not item.task.title and not item.task.content
        ):
            return None
        title = f"{item.task.title}" if item.task.title else ""
        content = f"{item.task.content}" if item.task.content else ""
        task_text = f"{title}: {content}" if title and content else title or content
        text = f"A message was displayed to the user that the following task was performed:\n<Task>\n{task_text}\n</Task>"
        return Message(
            type="message",
            content=[
                ResponseInputTextParam(
                    type="input_text",
                    text=text,
                )
            ],
            role="user",
        )

    def workflow_to_input(
        self, item: WorkflowItem
    ) -> TResponseInputItem | list[TResponseInputItem] | None:
        """
        Convert a TaskItem into input item(s) to send to the model.
        Returns WorkflowItem.response_items by default.
        """
        messages = []
        for task in item.workflow.tasks:
            if task.type != "custom" or (not task.title and not task.content):
                continue

            title = f"{task.title}" if task.title else ""
            content = f"{task.content}" if task.content else ""
            task_text = f"{title}: {content}" if title and content else title or content
            text = f"A message was displayed to the user that the following task was performed:\n<Task>\n{task_text}\n</Task>"
            messages.append(
                Message(
                    type="message",
                    content=[
                        ResponseInputTextParam(
                            type="input_text",
                            text=text,
                        )
                    ],
                    role="user",
                )
            )
        return messages

    def widget_to_input(
        self, item: WidgetItem
    ) -> TResponseInputItem | list[TResponseInputItem] | None:
        """
        Convert a WidgetItem into input item(s) to send to the model.
        By default, WidgetItems converted to a text description with a JSON representation of the widget.
        """
        return Message(
            type="message",
            content=[
                ResponseInputTextParam(
                    type="input_text",
                    text=f"The following graphical UI widget (id: {item.id}) was displayed to the user:"
                    + item.widget.model_dump_json(
                        exclude_unset=True, exclude_none=True
                    ),
                )
            ],
            role="user",
        )

    async def user_message_to_input(
        self, item: UserMessageItem, is_last_message: bool = True
    ) -> TResponseInputItem | list[TResponseInputItem] | None:
        # Build the user text exactly as typed, rendering tags as @key
        message_text_parts: list[str] = []
        # Track tags separately to add system context
        raw_tags: list[UserMessageTagContent] = []

        for part in item.content:
            if isinstance(part, UserMessageTextContent):
                message_text_parts.append(part.text)
            elif isinstance(part, UserMessageTagContent):
                message_text_parts.append(f"@{part.text}")
                raw_tags.append(part)
            else:
                assert_never(part)

        user_text_item = Message(
            role="user",
            type="message",
            content=[
                ResponseInputTextParam(
                    type="input_text", text="".join(message_text_parts)
                ),
                *[
                    await self.attachment_to_message_content(a)
                    for a in item.attachments
                ],
            ],
        )

        # Build system items (prepend later): quoted text and @-mention context
        context_items: list[TResponseInputItem] = []

        if item.quoted_text and is_last_message:
            context_items.append(
                Message(
                    role="user",
                    type="message",
                    content=[
                        ResponseInputTextParam(
                            type="input_text",
                            text=f"The user is referring to this in particular: \n{item.quoted_text}",
                        )
                    ],
                )
            )

        # Dedupe tags (preserve order) and resolve to message content
        if raw_tags:
            seen, uniq_tags = set(), []
            for t in raw_tags:
                if t.text not in seen:
                    seen.add(t.text)
                    uniq_tags.append(t)

            tag_content: ResponseInputMessageContentListParam = [
                # should return summarized text items
                self.tag_to_message_content(tag)
                for tag in uniq_tags
            ]

            if tag_content:
                context_items.append(
                    Message(
                        role="user",
                        type="message",
                        content=[
                            ResponseInputTextParam(
                                type="input_text",
                                text=cleandoc("""
                                    # User-provided context for @-mentions
                                    - When referencing resolved entities, use their canonical names **without** '@'.
                                    - The '@' form appears only in user text and should not be echoed.
                                """).strip(),
                            ),
                            *tag_content,
                        ],
                    )
                )

        return [user_text_item, *context_items]

    async def assistant_message_to_input(
        self, item: AssistantMessageItem
    ) -> TResponseInputItem | list[TResponseInputItem] | None:
        return EasyInputMessageParam(
            type="message",
            content=[
                # content param doesn't support the assistant message content types
                cast(
                    ResponseInputContentParam,
                    ResponseOutputText(
                        type="output_text",
                        text=c.text,
                        annotations=[],  # TODO: these should be sent back as well
                    ).model_dump(),
                )
                for c in item.content
            ],
            role="assistant",
        )

    async def client_tool_call_to_input(
        self, item: ClientToolCallItem
    ) -> TResponseInputItem | list[TResponseInputItem] | None:
        if item.status == "pending":
            # Filter out pending tool calls - they cannot be sent to the model
            return None

        return [
            ResponseFunctionToolCallParam(
                type="function_call",
                call_id=item.call_id,
                name=item.name,
                arguments=json.dumps(item.arguments),
            ),
            FunctionCallOutput(
                type="function_call_output",
                call_id=item.call_id,
                output=json.dumps(item.output),
            ),
        ]

    async def end_of_turn_to_input(
        self, item: EndOfTurnItem
    ) -> TResponseInputItem | list[TResponseInputItem] | None:
        # Only used for UI hints - you shouldn't need to override this
        return None

    async def _thread_item_to_input_item(
        self,
        item: ThreadItem,
        is_last_message: bool = True,
    ) -> list[TResponseInputItem]:
        match item:
            case UserMessageItem():
                out = await self.user_message_to_input(item, is_last_message) or []
                return out if isinstance(out, list) else [out]
            case AssistantMessageItem():
                out = await self.assistant_message_to_input(item) or []
                return out if isinstance(out, list) else [out]
            case ClientToolCallItem():
                out = await self.client_tool_call_to_input(item) or []
                return out if isinstance(out, list) else [out]
            case EndOfTurnItem():
                out = await self.end_of_turn_to_input(item) or []
                return out if isinstance(out, list) else [out]
            case WidgetItem():
                out = self.widget_to_input(item) or []
                return out if isinstance(out, list) else [out]
            case WorkflowItem():
                out = self.workflow_to_input(item) or []
                return out if isinstance(out, list) else [out]
            case TaskItem():
                out = self.task_to_input(item) or []
                return out if isinstance(out, list) else [out]
            case HiddenContextItem():
                out = self.hidden_context_to_input(item) or []
                return out if isinstance(out, list) else [out]
            case _:
                assert_never(item)

    async def to_agent_input(
        self,
        thread_items: Sequence[ThreadItem] | ThreadItem,
    ) -> list[TResponseInputItem]:
        if isinstance(thread_items, Sequence):
            # shallow copy in case caller mutates the list while we're iterating
            thread_items = thread_items[:]
        else:
            thread_items = [thread_items]
        output: list[TResponseInputItem] = []
        for item in thread_items:
            output.extend(
                await self._thread_item_to_input_item(
                    item,
                    is_last_message=item is thread_items[-1],
                )
            )
        return output


_DEFAULT_CONVERTER = ThreadItemConverter()


def simple_to_agent_input(thread_items: Sequence[ThreadItem] | ThreadItem):
    return _DEFAULT_CONVERTER.to_agent_input(thread_items)
