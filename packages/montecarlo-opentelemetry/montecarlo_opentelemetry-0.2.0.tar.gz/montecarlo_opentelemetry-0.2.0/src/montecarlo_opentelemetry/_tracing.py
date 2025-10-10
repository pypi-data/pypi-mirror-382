import inspect

import wrapt
from opentelemetry import baggage, context

from montecarlo_opentelemetry._setup import get_tracer


def trace(span_name: str):
    """
    Decorator to trace a function or method.

    This decorator will create a span and set it as the current span in
    the current tracer's context.

    :param span_name: Name of the span.
    """

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        async def async_wrapper():
            tracer = get_tracer()
            with tracer.start_as_current_span(span_name):
                return await wrapped(*args, **kwargs)

        def sync_wrapper():
            tracer = get_tracer()
            with tracer.start_as_current_span(span_name):
                return wrapped(*args, **kwargs)

        if inspect.iscoroutinefunction(wrapped):
            return async_wrapper()
        else:
            return sync_wrapper()

    return wrapper


def trace_with_attributes(
    span_name: str, attributes: dict[str, str | int | float | bool]
):
    """
    Decorator to trace a function or method with attributes.

    This decorator will create a span and set it as the current span in
    the current tracer's context.

    For each attribute, it will prepend the key with the "montecarlo."
    prefix. It will add the attributes to the current span, and propagate
    them to child spans.

    :param span_name: Name of the span.
    :param attributes: Dictionary of attributes to add to the span.
    """

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        async def async_wrapper():
            ctx = context.get_current()

            for key, value in attributes.items():
                mc_key = f"montecarlo.{key}"
                ctx = baggage.set_baggage(mc_key, value, ctx)

            token = context.attach(ctx)
            try:
                tracer = get_tracer()
                with tracer.start_as_current_span(span_name):
                    return await wrapped(*args, **kwargs)
            finally:
                context.detach(token)

        def sync_wrapper():
            ctx = context.get_current()

            for key, value in attributes.items():
                mc_key = f"montecarlo.{key}"
                ctx = baggage.set_baggage(mc_key, value, ctx)

            token = context.attach(ctx)
            try:
                tracer = get_tracer()
                with tracer.start_as_current_span(span_name):
                    return wrapped(*args, **kwargs)
            finally:
                context.detach(token)

        if inspect.iscoroutinefunction(wrapped):
            return async_wrapper()
        else:
            return sync_wrapper()

    return wrapper


def trace_with_tags(span_name: str, tags: list[str]):
    """
    Decorator to trace a function or method with tags.

    This decorator will create a span and set it as the current span in
    the current tracer's context. It merges the provided tags with any
    existing tags from the current context and propagates them to child
    spans.

    Tags are stored as a sorted comma-separated string in baggage under
    the key "montecarlo.tags".

    :param span_name: Name of the span.
    :param tags: List of tags to add to the span.
    """

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        async def async_wrapper():
            curr_ctx = context.get_current()

            # Merge existing tags with new tags.
            existing_tags = []
            curr_tags = baggage.get_baggage("montecarlo.tags", curr_ctx)
            if curr_tags and isinstance(curr_tags, str):
                existing_tags = curr_tags.split(",")
            all_tags = set(existing_tags + tags)
            joined_tags = ",".join(sorted(all_tags))

            ctx = baggage.set_baggage("montecarlo.tags", joined_tags, curr_ctx)

            token = context.attach(ctx)
            try:
                tracer = get_tracer()
                with tracer.start_as_current_span(span_name):
                    return await wrapped(*args, **kwargs)
            finally:
                context.detach(token)

        def sync_wrapper():
            curr_ctx = context.get_current()

            # Merge existing tags with new tags.
            existing_tags = []
            curr_tags = baggage.get_baggage("montecarlo.tags", curr_ctx)
            if curr_tags and isinstance(curr_tags, str):
                existing_tags = curr_tags.split(",")
            all_tags = set(existing_tags + tags)
            joined_tags = ",".join(sorted(all_tags))

            ctx = baggage.set_baggage("montecarlo.tags", joined_tags, curr_ctx)

            token = context.attach(ctx)
            try:
                tracer = get_tracer()
                with tracer.start_as_current_span(span_name):
                    return wrapped(*args, **kwargs)
            finally:
                context.detach(token)

        if inspect.iscoroutinefunction(wrapped):
            return async_wrapper()
        else:
            return sync_wrapper()

    return wrapper


def trace_with_workflow(span_name: str, workflow_name: str):
    """
    Decorator to trace a function or method as part of a workflow.

    A workflow is a logical grouping of tasks.

    This decorator will create a span and set it as the current span in
    the current tracer's context. It sets the workflow name as an attribute
    under the key "montecarlo.workflow" and propagates it to child spans.

    :param span_name: Name of the span.
    :param workflow_name: Name of the workflow to associate with the span.
    """
    return trace_with_attributes(span_name, {"workflow": workflow_name})


def trace_with_task(span_name: str, task_name: str):
    """
    Decorator to trace a function or method as a task.

    A task is a unit of work that is part of a workflow.

    This decorator will create a span and set it as the current span in
    the current tracer's context. It sets the task name as an attribute
    under the key "montecarlo.task" and propagates it to child spans.

    :param span_name: Name of the span.
    :param task_name: Name of the task to associate with the span.
    """
    return trace_with_attributes(span_name, {"task": task_name})


class create_span_with_attributes:
    """
    Context manager to create a span with the given name, set it as the
    current span, and add attributes to it.

    For each attribute, it will prepend the key with the "montecarlo."
    prefix. It will add the attributes to the current span, and propagate
    them to child spans.

    This context manager supports both synchronous and asynchronous usage:

    Synchronous usage:
        with create_span_with_attributes("span-name", {"key": "value"}) as span:
            # do work
            pass

    Asynchronous usage:
        async with create_span_with_attributes("span-name", {"key": "value"}) as span:
            # do async work
            pass

    :param span_name: Name of the span.
    :param attributes: Dictionary of attributes to add to the span.
    """

    def __init__(self, span_name: str, attributes: dict[str, str | int | float | bool]):
        self.span_name = span_name
        self.attributes = attributes
        self._token = None
        self._span_context_manager = None

    def __enter__(self):
        ctx = context.get_current()
        for key, value in self.attributes.items():
            mc_key = f"montecarlo.{key}"
            ctx = baggage.set_baggage(mc_key, value, ctx)

        self._token = context.attach(ctx)

        try:
            tracer = get_tracer()
            self._span_context_manager = tracer.start_as_current_span(self.span_name)
            return self._span_context_manager.__enter__()
        except:
            # If entering the span fails, clean up and detach token
            if self._token is not None:
                context.detach(self._token)
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._span_context_manager is not None:
                return self._span_context_manager.__exit__(exc_type, exc_val, exc_tb)
        finally:
            if self._token is not None:
                context.detach(self._token)

    async def __aenter__(self):
        ctx = context.get_current()
        for key, value in self.attributes.items():
            mc_key = f"montecarlo.{key}"
            ctx = baggage.set_baggage(mc_key, value, ctx)

        self._token = context.attach(ctx)

        try:
            tracer = get_tracer()
            self._span_context_manager = tracer.start_as_current_span(self.span_name)
            return self._span_context_manager.__enter__()
        except:
            # If entering the span fails, clean up and detach token
            if self._token is not None:
                context.detach(self._token)
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._span_context_manager is not None:
                return self._span_context_manager.__exit__(exc_type, exc_val, exc_tb)
        finally:
            if self._token is not None:
                context.detach(self._token)


class create_span_with_tags:
    """
    Context manager to create a span with the given name, set it as the
    current span, and add tags to it. It merges the provided tags with
    any existing tags from the current context and propagates them to
    child spans.

    Tags are stored as a sorted comma-separated string in baggage under
    the key "montecarlo.tags".

    This context manager supports both synchronous and asynchronous usage:

    Synchronous usage:
        with create_span_with_tags("span-name", ["tag1", "tag2"]) as span:
            # do work
            pass

    Asynchronous usage:
        async with create_span_with_tags("span-name", ["tag1", "tag2"]) as span:
            # do async work
            pass

    :param span_name: Name of the span.
    :param tags: List of tags to add to the span.
    """

    def __init__(self, span_name: str, tags: list[str]):
        self.span_name = span_name
        self.tags = tags
        self._token = None
        self._span_context_manager = None

    def __enter__(self):
        curr_ctx = context.get_current()

        # Merge existing tags with new tags.
        existing_tags = []
        curr_tags = baggage.get_baggage("montecarlo.tags", curr_ctx)
        if curr_tags and isinstance(curr_tags, str):
            existing_tags = curr_tags.split(",")
        all_tags = set(existing_tags + self.tags)
        joined_tags = ",".join(sorted(all_tags))

        ctx = baggage.set_baggage("montecarlo.tags", joined_tags, curr_ctx)
        self._token = context.attach(ctx)

        try:
            tracer = get_tracer()
            self._span_context_manager = tracer.start_as_current_span(self.span_name)
            return self._span_context_manager.__enter__()
        except:
            # If entering the span fails, clean up and detach token
            if self._token is not None:
                context.detach(self._token)
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._span_context_manager is not None:
                return self._span_context_manager.__exit__(exc_type, exc_val, exc_tb)
        finally:
            if self._token is not None:
                context.detach(self._token)

    async def __aenter__(self):
        curr_ctx = context.get_current()

        # Merge existing tags with new tags.
        existing_tags = []
        curr_tags = baggage.get_baggage("montecarlo.tags", curr_ctx)
        if curr_tags and isinstance(curr_tags, str):
            existing_tags = curr_tags.split(",")
        all_tags = set(existing_tags + self.tags)
        joined_tags = ",".join(sorted(all_tags))

        ctx = baggage.set_baggage("montecarlo.tags", joined_tags, curr_ctx)
        self._token = context.attach(ctx)

        try:
            tracer = get_tracer()
            self._span_context_manager = tracer.start_as_current_span(self.span_name)
            return self._span_context_manager.__enter__()
        except:
            # If entering the span fails, clean up and detach token
            if self._token is not None:
                context.detach(self._token)
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._span_context_manager is not None:
                return self._span_context_manager.__exit__(exc_type, exc_val, exc_tb)
        finally:
            if self._token is not None:
                context.detach(self._token)


class create_span_with_workflow:
    """
    Context manager to create a span with the given name, set it as the
    current span, and add a workflow attribute to it. It sets the
    workflow name to "montecarlo.workflow" and propagates it to child
    spans.

    A workflow is a logical grouping of tasks.

    This context manager supports both synchronous and asynchronous usage:

    Synchronous usage:
        with create_span_with_workflow("span-name", "workflow-name") as span:
            # do work
            pass

    Asynchronous usage:
        async with create_span_with_workflow("span-name", "workflow-name") as span:
            # do async work
            pass

    :param span_name: Name of the span.
    :param workflow_name: Name of the workflow to associate with the span.
    """

    def __init__(self, span_name: str, workflow_name: str):
        self.span_name = span_name
        self.workflow_name = workflow_name
        self._span_context_manager = None

    def __enter__(self):
        self._span_context_manager = create_span_with_attributes(
            self.span_name, {"workflow": self.workflow_name}
        )
        return self._span_context_manager.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._span_context_manager is not None:
            return self._span_context_manager.__exit__(exc_type, exc_val, exc_tb)

    async def __aenter__(self):
        self._span_context_manager = create_span_with_attributes(
            self.span_name, {"workflow": self.workflow_name}
        )
        return await self._span_context_manager.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._span_context_manager is not None:
            return await self._span_context_manager.__aexit__(exc_type, exc_val, exc_tb)


class create_span_with_task:
    """
    Context manager to create a span with the given name, set it as the
    current span, and add a task attribute to it. It sets the task name
    to "montecarlo.task" and propagates it to child spans.

    A task is a unit of work that is part of a workflow.

    This context manager supports both synchronous and asynchronous usage:

    Synchronous usage:
        with create_span_with_task("span-name", "task-name") as span:
            # do work
            pass

    Asynchronous usage:
        async with create_span_with_task("span-name", "task-name") as span:
            # do async work
            pass

    :param span_name: Name of the span.
    :param task_name: Name of the task to associate with the span.
    """

    def __init__(self, span_name: str, task_name: str):
        self.span_name = span_name
        self.task_name = task_name
        self._span_context_manager = None

    def __enter__(self):
        self._span_context_manager = create_span_with_attributes(
            self.span_name, {"task": self.task_name}
        )
        return self._span_context_manager.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._span_context_manager is not None:
            return self._span_context_manager.__exit__(exc_type, exc_val, exc_tb)

    async def __aenter__(self):
        self._span_context_manager = create_span_with_attributes(
            self.span_name, {"task": self.task_name}
        )
        return await self._span_context_manager.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._span_context_manager is not None:
            return await self._span_context_manager.__aexit__(exc_type, exc_val, exc_tb)
