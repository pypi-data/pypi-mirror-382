"""
Comprehensive tests for the events module (Event, EventBus, AllEvents).

Target coverage: 95%+
"""

import pytest
from dataclasses import dataclass
from typing import Callable
from vultus_serpentis.events import Event, EventBus, AllEvents


# Test event classes
@dataclass
class SimpleTestEvent(Event):
    """Simple test event."""

    value: int = 0


@dataclass
class AnotherEvent(Event):
    """Another test event for multiple event type tests."""

    message: str = ""


@dataclass
class ChildEvent(SimpleTestEvent):
    """Event that inherits from SimpleTestEvent."""

    extra: str = ""


class TestEventClass:
    """Tests for the Event base class."""

    def test_event_creation(self) -> None:
        """Test that Event can be instantiated."""
        event = Event()
        assert isinstance(event, Event)

    def test_event_is_dataclass(self) -> None:
        """Test that Event is a dataclass."""
        event = Event()
        assert hasattr(event, "__dataclass_fields__")

    def test_custom_event_creation(self) -> None:
        """Test creating a custom event with fields."""
        event = SimpleTestEvent(value=42)
        assert event.value == 42
        assert isinstance(event, Event)

    def test_custom_event_default_values(self) -> None:
        """Test custom event with default values."""
        event = SimpleTestEvent()
        assert event.value == 0


class TestAllEvents:
    """Tests for the AllEvents sentinel class."""

    def test_allevents_is_class(self) -> None:
        """Test that AllEvents is a class."""
        assert isinstance(AllEvents, type)

    def test_allevents_can_be_used_as_type(self) -> None:
        """Test that AllEvents can be used as a type marker."""
        # This is mainly for type checking, but we can verify it's usable
        event_type = AllEvents
        assert event_type is AllEvents


class TestEventBus:
    """Tests for the EventBus class."""

    def test_eventbus_creation(self) -> None:
        """Test that EventBus can be instantiated."""
        bus = EventBus()
        assert isinstance(bus, EventBus)

    def test_eventbus_default_singleton(self) -> None:
        """Test that default() returns the same instance."""
        bus1 = EventBus.default()
        bus2 = EventBus.default()
        assert bus1 is bus2

    def test_eventbus_default_is_eventbus(self) -> None:
        """Test that default() returns an EventBus instance."""
        bus = EventBus.default()
        assert isinstance(bus, EventBus)

    def test_eventbus_multiple_instances(self) -> None:
        """Test that multiple EventBus instances can be created."""
        bus1 = EventBus()
        bus2 = EventBus()
        assert bus1 is not bus2

    def test_subscribe_single_callback(self, observer_calls: list) -> None:
        """Test subscribing a single callback."""
        bus = EventBus()

        def callback(event: Event) -> None:
            observer_calls.append(event)

        bus.subscribe(SimpleTestEvent, callback)
        assert bus.subscriber_count(SimpleTestEvent) == 1

    def test_subscribe_multiple_callbacks(self, observer_calls: list) -> None:
        """Test subscribing multiple callbacks to the same event."""
        bus = EventBus()

        def callback1(event: Event) -> None:
            observer_calls.append(("callback1", event))

        def callback2(event: Event) -> None:
            observer_calls.append(("callback2", event))

        bus.subscribe(SimpleTestEvent, callback1)
        bus.subscribe(SimpleTestEvent, callback2)
        assert bus.subscriber_count(SimpleTestEvent) == 2

    def test_subscribe_duplicate_callback_ignored(self, observer_calls: list) -> None:
        """Test that subscribing the same callback twice is ignored."""
        bus = EventBus()

        def callback(event: Event) -> None:
            observer_calls.append(event)

        bus.subscribe(SimpleTestEvent, callback)
        bus.subscribe(SimpleTestEvent, callback)  # Duplicate
        assert bus.subscriber_count(SimpleTestEvent) == 1

    def test_subscribe_to_allevents(self, observer_calls: list) -> None:
        """Test subscribing to AllEvents wildcard."""
        bus = EventBus()

        def callback(event: Event) -> None:
            observer_calls.append(event)

        bus.subscribe(AllEvents, callback)
        assert bus.subscriber_count(AllEvents) == 1

    def test_publish_to_specific_subscribers(self, observer_calls: list) -> None:
        """Test publishing an event to specific subscribers."""
        bus = EventBus()

        def callback(event: Event) -> None:
            observer_calls.append(event)

        bus.subscribe(SimpleTestEvent, callback)
        event = SimpleTestEvent(value=42)
        bus.publish(event)

        assert len(observer_calls) == 1
        assert observer_calls[0] is event
        assert observer_calls[0].value == 42

    def test_publish_to_multiple_subscribers(self, observer_calls: list) -> None:
        """Test that all subscribers receive the event."""
        bus = EventBus()

        def callback1(event: Event) -> None:
            observer_calls.append(("callback1", event))

        def callback2(event: Event) -> None:
            observer_calls.append(("callback2", event))

        bus.subscribe(SimpleTestEvent, callback1)
        bus.subscribe(SimpleTestEvent, callback2)

        event = SimpleTestEvent(value=42)
        bus.publish(event)

        assert len(observer_calls) == 2
        assert ("callback1", event) in observer_calls
        assert ("callback2", event) in observer_calls

    def test_publish_to_allevents_subscribers(self, observer_calls: list) -> None:
        """Test that AllEvents subscribers receive all events."""
        bus = EventBus()

        def callback(event: Event) -> None:
            observer_calls.append(event)

        bus.subscribe(AllEvents, callback)

        event1 = SimpleTestEvent(value=1)
        event2 = AnotherEvent(message="test")

        bus.publish(event1)
        bus.publish(event2)

        assert len(observer_calls) == 2
        assert event1 in observer_calls
        assert event2 in observer_calls

    def test_publish_to_both_specific_and_wildcard(self, observer_calls: list) -> None:
        """Test that both specific and AllEvents subscribers receive events."""
        bus = EventBus()

        def specific_callback(event: Event) -> None:
            observer_calls.append(("specific", event))

        def wildcard_callback(event: Event) -> None:
            observer_calls.append(("wildcard", event))

        bus.subscribe(SimpleTestEvent, specific_callback)
        bus.subscribe(AllEvents, wildcard_callback)

        event = SimpleTestEvent(value=42)
        bus.publish(event)

        assert len(observer_calls) == 2
        assert ("specific", event) in observer_calls
        assert ("wildcard", event) in observer_calls

    def test_publish_no_subscribers(self, observer_calls: list) -> None:
        """Test publishing when there are no subscribers."""
        bus = EventBus()
        event = SimpleTestEvent(value=42)
        bus.publish(event)  # Should not raise
        assert len(observer_calls) == 0

    def test_publish_different_event_types(self, observer_calls: list) -> None:
        """Test that only matching event type subscribers are notified."""
        bus = EventBus()

        def test_callback(event: Event) -> None:
            observer_calls.append(("test", event))

        def another_callback(event: Event) -> None:
            observer_calls.append(("another", event))

        bus.subscribe(SimpleTestEvent, test_callback)
        bus.subscribe(AnotherEvent, another_callback)

        event1 = SimpleTestEvent(value=1)
        event2 = AnotherEvent(message="hello")

        bus.publish(event1)
        assert len(observer_calls) == 1
        assert observer_calls[0] == ("test", event1)

        observer_calls.clear()
        bus.publish(event2)
        assert len(observer_calls) == 1
        assert observer_calls[0] == ("another", event2)

    def test_unsubscribe_callback(self, observer_calls: list) -> None:
        """Test unsubscribing a callback."""
        bus = EventBus()

        def callback(event: Event) -> None:
            observer_calls.append(event)

        bus.subscribe(SimpleTestEvent, callback)
        assert bus.subscriber_count(SimpleTestEvent) == 1

        bus.unsubscribe(SimpleTestEvent, callback)
        assert bus.subscriber_count(SimpleTestEvent) == 0

        # Publish should not call the unsubscribed callback
        bus.publish(SimpleTestEvent(value=42))
        assert len(observer_calls) == 0

    def test_unsubscribe_nonexistent_callback(self) -> None:
        """Test unsubscribing a callback that was never subscribed."""
        bus = EventBus()

        def callback(event: Event) -> None:
            pass

        # Should not raise
        bus.unsubscribe(SimpleTestEvent, callback)
        assert bus.subscriber_count(SimpleTestEvent) == 0

    def test_unsubscribe_from_nonexistent_event_type(self) -> None:
        """Test unsubscribing from an event type with no subscribers."""
        bus = EventBus()

        def callback(event: Event) -> None:
            pass

        # Should not raise
        bus.unsubscribe(SimpleTestEvent, callback)

    def test_unsubscribe_one_of_multiple(self, observer_calls: list) -> None:
        """Test unsubscribing one callback when multiple are subscribed."""
        bus = EventBus()

        def callback1(event: Event) -> None:
            observer_calls.append("callback1")

        def callback2(event: Event) -> None:
            observer_calls.append("callback2")

        bus.subscribe(SimpleTestEvent, callback1)
        bus.subscribe(SimpleTestEvent, callback2)

        bus.unsubscribe(SimpleTestEvent, callback1)
        assert bus.subscriber_count(SimpleTestEvent) == 1

        bus.publish(SimpleTestEvent(value=1))
        assert observer_calls == ["callback2"]

    def test_reset_clears_all_subscribers(self, observer_calls: list) -> None:
        """Test that reset() clears all subscribers."""
        bus = EventBus()

        def callback(event: Event) -> None:
            observer_calls.append(event)

        bus.subscribe(SimpleTestEvent, callback)
        bus.subscribe(AnotherEvent, callback)
        bus.subscribe(AllEvents, callback)

        assert bus.subscriber_count() > 0

        bus.reset()
        assert bus.subscriber_count() == 0

        # Publishing should not call any callbacks
        bus.publish(SimpleTestEvent(value=1))
        bus.publish(AnotherEvent(message="test"))
        assert len(observer_calls) == 0

    def test_subscriber_count_specific_event(self) -> None:
        """Test subscriber_count for a specific event type."""
        bus = EventBus()

        def callback1(event: Event) -> None:
            pass

        def callback2(event: Event) -> None:
            pass

        bus.subscribe(SimpleTestEvent, callback1)
        bus.subscribe(SimpleTestEvent, callback2)
        bus.subscribe(AnotherEvent, callback1)

        assert bus.subscriber_count(SimpleTestEvent) == 2
        assert bus.subscriber_count(AnotherEvent) == 1
        assert bus.subscriber_count(AllEvents) == 0

    def test_subscriber_count_all_events(self) -> None:
        """Test subscriber_count without arguments returns total."""
        bus = EventBus()

        def callback(event: Event) -> None:
            pass

        bus.subscribe(SimpleTestEvent, callback)
        bus.subscribe(AnotherEvent, callback)
        bus.subscribe(AllEvents, callback)

        assert bus.subscriber_count() == 3

    def test_subscriber_count_empty_bus(self) -> None:
        """Test subscriber_count on empty bus."""
        bus = EventBus()
        assert bus.subscriber_count() == 0
        assert bus.subscriber_count(SimpleTestEvent) == 0

    def test_publish_with_exception_in_subscriber(self, observer_calls: list) -> None:
        """Test that exceptions in subscribers propagate."""
        bus = EventBus()

        def failing_callback(event: Event) -> None:
            observer_calls.append("failing")
            raise RuntimeError("Subscriber error")

        def working_callback(event: Event) -> None:
            observer_calls.append("working")

        bus.subscribe(SimpleTestEvent, failing_callback)
        bus.subscribe(SimpleTestEvent, working_callback)

        with pytest.raises(RuntimeError, match="Subscriber error"):
            bus.publish(SimpleTestEvent(value=1))

        # Only the failing callback was called before exception
        assert "failing" in observer_calls
        assert "working" not in observer_calls

    def test_unsubscribe_during_publish(self, observer_calls: list) -> None:
        """Test that unsubscribing during publish is safe."""
        bus = EventBus()

        def callback2(event: Event) -> None:
            observer_calls.append("callback2")

        def callback1(event: Event) -> None:
            observer_calls.append("callback1")
            # Unsubscribe callback2 during notification
            bus.unsubscribe(SimpleTestEvent, callback2)

        def callback3(event: Event) -> None:
            observer_calls.append("callback3")

        bus.subscribe(SimpleTestEvent, callback1)
        bus.subscribe(SimpleTestEvent, callback2)
        bus.subscribe(SimpleTestEvent, callback3)

        bus.publish(SimpleTestEvent(value=1))

        # All callbacks should be called because we copy the list
        assert "callback1" in observer_calls
        assert "callback2" in observer_calls
        assert "callback3" in observer_calls

    def test_subscribe_during_publish(self, observer_calls: list) -> None:
        """Test that subscribing during publish doesn't affect current publish."""
        bus = EventBus()

        def new_callback(event: Event) -> None:
            observer_calls.append("new")

        def callback1(event: Event) -> None:
            observer_calls.append("callback1")
            # Subscribe new callback during notification
            bus.subscribe(SimpleTestEvent, new_callback)

        bus.subscribe(SimpleTestEvent, callback1)
        bus.publish(SimpleTestEvent(value=1))

        # First publish: only callback1
        assert observer_calls == ["callback1"]

        # Second publish: both callbacks
        observer_calls.clear()
        bus.publish(SimpleTestEvent(value=2))
        assert "callback1" in observer_calls
        assert "new" in observer_calls

    def test_event_inheritance(self, observer_calls: list) -> None:
        """Test that event inheritance works as expected."""
        bus = EventBus()

        def parent_callback(event: Event) -> None:
            observer_calls.append("parent")

        def child_callback(event: Event) -> None:
            observer_calls.append("child")

        bus.subscribe(SimpleTestEvent, parent_callback)
        bus.subscribe(ChildEvent, child_callback)

        # Publishing ChildEvent should only notify ChildEvent subscribers
        # (not SimpleTestEvent subscribers, as we match on exact type)
        child_event = ChildEvent(value=1, extra="test")
        bus.publish(child_event)

        assert "child" in observer_calls
        assert "parent" not in observer_calls  # Exact type matching

    def test_performance_many_subscribers(self) -> None:
        """Test performance with many subscribers."""
        bus = EventBus()
        call_count = 0

        def make_callback(n: int) -> Callable[[Event], None]:
            def callback(event: Event) -> None:
                nonlocal call_count
                call_count += 1

            return callback

        # Subscribe 100 callbacks
        for i in range(100):
            bus.subscribe(SimpleTestEvent, make_callback(i))

        assert bus.subscriber_count(SimpleTestEvent) == 100

        # Publish event - all should be called
        bus.publish(SimpleTestEvent(value=42))
        assert call_count == 100

    def test_multiple_event_types_isolation(self, observer_calls: list) -> None:
        """Test that different event types are properly isolated."""
        bus = EventBus()

        def callback1(event: Event) -> None:
            observer_calls.append(("type1", event))

        def callback2(event: Event) -> None:
            observer_calls.append(("type2", event))

        bus.subscribe(SimpleTestEvent, callback1)
        bus.subscribe(AnotherEvent, callback2)

        event1 = SimpleTestEvent(value=1)
        event2 = AnotherEvent(message="test")

        bus.publish(event1)
        assert len(observer_calls) == 1
        assert observer_calls[0] == ("type1", event1)

        observer_calls.clear()
        bus.publish(event2)
        assert len(observer_calls) == 1
        assert observer_calls[0] == ("type2", event2)

    def test_default_instance_isolation_after_reset(self) -> None:
        """Test that reset() properly clears the default instance."""
        bus = EventBus.default()

        def callback(event: Event) -> None:
            pass

        bus.subscribe(SimpleTestEvent, callback)
        assert bus.subscriber_count(SimpleTestEvent) == 1

        bus.reset()
        assert bus.subscriber_count(SimpleTestEvent) == 0

        # Verify it's still the same instance
        bus2 = EventBus.default()
        assert bus is bus2
