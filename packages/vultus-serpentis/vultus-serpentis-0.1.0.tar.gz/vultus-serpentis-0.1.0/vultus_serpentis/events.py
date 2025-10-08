"""
Event Bus module for synchronous, decoupled messaging.

This module provides a lightweight, synchronous event bus for decoupled
communication between components in a Tkinter application.

Example:
    >>> from dataclasses import dataclass
    >>> from vultus_serpentis import EventBus, Event
    >>>
    >>> @dataclass
    >>> class FileOpenedEvent(Event):
    ...     filename: str
    >>>
    >>> bus = EventBus.default()
    >>>
    >>> def on_file_opened(event: Event) -> None:
    ...     print(f"File opened: {event.filename}")
    >>>
    >>> bus.subscribe(FileOpenedEvent, on_file_opened)
    >>> bus.publish(FileOpenedEvent(filename="document.txt"))
    File opened: document.txt

Thread Safety:
    EventBus is NOT thread-safe. All subscribe/publish operations should
    occur on the same thread (typically the main/GUI thread in Tkinter apps).
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Type, Union
from collections import defaultdict


@dataclass
class Event:
    """
    Base class for events passed through the EventBus.

    All custom events should inherit from this class. Use dataclasses
    for convenient event definition with typed fields.

    Example:
        >>> from dataclasses import dataclass
        >>> from vultus_serpentis import Event
        >>>
        >>> @dataclass
        >>> class UserLoggedInEvent(Event):
        ...     username: str
        ...     timestamp: float
    """


class AllEvents:
    """
    Sentinel class for wildcard subscriptions.

    Subscribe to AllEvents to receive notifications for all event types
    published through the EventBus.

    Example:
        >>> def log_all_events(event: Event) -> None:
        ...     print(f"Event: {type(event).__name__}")
        >>>
        >>> bus.subscribe(AllEvents, log_all_events)
    """


class EventBus:
    """
    A synchronous event bus for decoupled component communication.

    The EventBus provides a publish-subscribe pattern for loosely coupled
    communication between components. It supports both specific event type
    subscriptions and wildcard subscriptions via AllEvents.

    This implementation is synchronous - all subscribers are notified
    immediately when an event is published, in the order they subscribed.

    Example:
        >>> bus = EventBus()
        >>> def handler(event: Event) -> None:
        ...     print(f"Received: {event}")
        >>>
        >>> bus.subscribe(MyEvent, handler)
        >>> bus.publish(MyEvent())
        Received: MyEvent()

    Thread Safety:
        NOT thread-safe. Use only from a single thread (e.g., GUI thread).
    """

    _default_instance: Union["EventBus", None] = None

    @classmethod
    def default(cls) -> "EventBus":
        """
        Get the default EventBus instance.

        Provides a convenient singleton-like instance for application-wide
        event communication. Use this for most cases unless you need
        isolated event buses for testing or specific subsystems.

        Returns:
            The default EventBus instance

        Example:
            >>> bus = EventBus.default()
            >>> bus.subscribe(MyEvent, my_handler)
        """
        if cls._default_instance is None:
            cls._default_instance = cls()
        return cls._default_instance

    def __init__(self) -> None:
        """
        Initialize a new EventBus instance.

        Creates an empty subscriber registry. Typically you'll use
        EventBus.default() instead of creating instances directly.
        """
        self._subscribers: Dict[
            Union[Type[Event], Type[AllEvents]], List[Callable[[Event], None]]
        ] = defaultdict(list)

    def reset(self) -> None:
        """
        Reset all subscribers for testing.

        Clears all event subscriptions. Useful in test teardown to ensure
        test isolation.

        Example:
            >>> bus = EventBus.default()
            >>> bus.subscribe(MyEvent, handler)
            >>> bus.reset()  # Clear all subscriptions
        """
        self._subscribers.clear()

    def subscribe(
        self,
        event_type: Union[Type[Event], Type[AllEvents]],
        callback: Callable[[Event], None],
    ) -> None:
        """
        Subscribe a callback to an event type.

        The callback will be invoked whenever an event of the specified type
        (or AllEvents for wildcard) is published. Callbacks are invoked
        synchronously in subscription order.

        Args:
            event_type: The event class to subscribe to, or AllEvents for all events
            callback: Function to call when event is published. Must accept Event parameter.

        Example:
            >>> def on_save(event: FileSavedEvent) -> None:
            ...     print(f"Saved: {event.filename}")
            >>>
            >>> bus.subscribe(FileSavedEvent, on_save)
        """
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)

    def unsubscribe(
        self,
        event_type: Union[Type[Event], Type[AllEvents]],
        callback: Callable[[Event], None],
    ) -> None:
        """
        Unsubscribe a callback from an event type.

        Removes the callback from the subscriber list for the specified
        event type. If the callback is not subscribed, this is a no-op.

        Args:
            event_type: The event class to unsubscribe from
            callback: The callback function to remove

        Example:
            >>> bus.unsubscribe(FileSavedEvent, on_save)
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
            except ValueError:
                # Callback not in list - ignore
                pass

    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribed listeners.

        Notifies all subscribers of the specific event type, plus all
        AllEvents wildcard subscribers. Subscribers are called synchronously
        in subscription order.

        If a subscriber raises an exception, it will propagate and prevent
        subsequent subscribers from being notified. Subscribers should
        handle their own exceptions if this is not desired.

        Args:
            event: The event instance to publish

        Example:
            >>> bus.publish(FileSavedEvent(filename="document.txt"))
        """
        event_type = type(event)
        # Notify specific event type subscribers, then wildcard subscribers
        for typ in [event_type, AllEvents]:
            if typ in self._subscribers:
                # Copy list to allow unsubscribe during notification
                for callback in self._subscribers[typ][:]:
                    callback(event)

    def subscriber_count(
        self, event_type: Union[Type[Event], Type[AllEvents], None] = None
    ) -> int:
        """
        Get the number of subscribers.

        Args:
            event_type: If provided, count subscribers for this event type only.
                       If None, count all subscribers across all event types.

        Returns:
            Number of subscribers

        Example:
            >>> count = bus.subscriber_count(MyEvent)
            >>> total = bus.subscriber_count()  # All subscribers
        """
        if event_type is not None:
            return len(self._subscribers.get(event_type, []))
        return sum(len(callbacks) for callbacks in self._subscribers.values())
