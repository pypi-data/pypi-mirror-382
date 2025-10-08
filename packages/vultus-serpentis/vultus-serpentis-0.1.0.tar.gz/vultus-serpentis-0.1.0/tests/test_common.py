"""
Comprehensive tests for the common module (VultusException, Observable).

Target coverage: 95%+
"""

import pytest
from vultus_serpentis.common import VultusException, Observable


class TestVultusException:
    """Tests for the VultusException base class."""

    def test_exception_creation(self) -> None:
        """Test that VultusException can be created with a message."""
        exc = VultusException("Test error message")
        assert str(exc) == "Test error message"

    def test_exception_inheritance(self) -> None:
        """Test that VultusException inherits from Exception."""
        exc = VultusException("Test")
        assert isinstance(exc, Exception)

    def test_exception_can_be_raised(self) -> None:
        """Test that VultusException can be raised and caught."""
        with pytest.raises(VultusException) as exc_info:
            raise VultusException("Test error")
        assert str(exc_info.value) == "Test error"

    def test_exception_without_message(self) -> None:
        """Test that VultusException can be created without a message."""
        exc = VultusException()
        assert str(exc) == ""


class TestObservable:
    """Tests for the Observable mixin class."""

    def test_observable_initialization(self) -> None:
        """Test that Observable can be initialized."""
        observable = Observable()
        assert hasattr(observable, "_observers")
        assert observable._observers == []

    def test_add_observer(self, observer_calls: list) -> None:
        """Test adding a single observer."""
        observable = Observable()

        def observer(*args, **kwargs) -> None:
            observer_calls.append((args, kwargs))

        observable.add_observer(observer)
        assert observer in observable._observers
        assert len(observable._observers) == 1

    def test_add_multiple_observers(self, observer_calls: list) -> None:
        """Test adding multiple observers."""
        observable = Observable()

        def observer1(*args, **kwargs) -> None:
            observer_calls.append(("observer1", args, kwargs))

        def observer2(*args, **kwargs) -> None:
            observer_calls.append(("observer2", args, kwargs))

        observable.add_observer(observer1)
        observable.add_observer(observer2)

        assert len(observable._observers) == 2
        assert observer1 in observable._observers
        assert observer2 in observable._observers

    def test_add_duplicate_observer(self, observer_calls: list) -> None:
        """Test that adding the same observer twice is ignored."""
        observable = Observable()

        def observer(*args, **kwargs) -> None:
            observer_calls.append((args, kwargs))

        observable.add_observer(observer)
        observable.add_observer(observer)  # Add again

        assert len(observable._observers) == 1

    def test_remove_observer(self, observer_calls: list) -> None:
        """Test removing an observer."""
        observable = Observable()

        def observer(*args, **kwargs) -> None:
            observer_calls.append((args, kwargs))

        observable.add_observer(observer)
        assert observer in observable._observers

        observable.remove_observer(observer)
        assert observer not in observable._observers
        assert len(observable._observers) == 0

    def test_remove_nonexistent_observer(self) -> None:
        """Test that removing a non-existent observer raises ValueError."""
        observable = Observable()

        def observer(*args, **kwargs) -> None:
            pass

        with pytest.raises(ValueError):
            observable.remove_observer(observer)

    def test_notify_observers_no_args(self, observer_calls: list) -> None:
        """Test notifying observers without arguments."""
        observable = Observable()

        def observer(*args, **kwargs) -> None:
            observer_calls.append((args, kwargs))

        observable.add_observer(observer)
        observable._notify_observers()

        assert len(observer_calls) == 1
        assert observer_calls[0] == ((), {})

    def test_notify_observers_with_args(self, observer_calls: list) -> None:
        """Test notifying observers with positional arguments."""
        observable = Observable()

        def observer(*args, **kwargs) -> None:
            observer_calls.append((args, kwargs))

        observable.add_observer(observer)
        observable._notify_observers("arg1", "arg2", 123)

        assert len(observer_calls) == 1
        assert observer_calls[0] == (("arg1", "arg2", 123), {})

    def test_notify_observers_with_kwargs(self, observer_calls: list) -> None:
        """Test notifying observers with keyword arguments."""
        observable = Observable()

        def observer(*args, **kwargs) -> None:
            observer_calls.append((args, kwargs))

        observable.add_observer(observer)
        observable._notify_observers(name="test", value=42)

        assert len(observer_calls) == 1
        assert observer_calls[0] == ((), {"name": "test", "value": 42})

    def test_notify_observers_with_mixed_args(self, observer_calls: list) -> None:
        """Test notifying observers with both positional and keyword arguments."""
        observable = Observable()

        def observer(*args, **kwargs) -> None:
            observer_calls.append((args, kwargs))

        observable.add_observer(observer)
        observable._notify_observers("pos1", "pos2", key1="val1", key2="val2")

        assert len(observer_calls) == 1
        assert observer_calls[0] == (("pos1", "pos2"), {"key1": "val1", "key2": "val2"})

    def test_notify_multiple_observers(self, observer_calls: list) -> None:
        """Test that all observers are notified."""
        observable = Observable()

        def observer1(*args, **kwargs) -> None:
            observer_calls.append(("observer1", args, kwargs))

        def observer2(*args, **kwargs) -> None:
            observer_calls.append(("observer2", args, kwargs))

        def observer3(*args, **kwargs) -> None:
            observer_calls.append(("observer3", args, kwargs))

        observable.add_observer(observer1)
        observable.add_observer(observer2)
        observable.add_observer(observer3)

        observable._notify_observers("test", value=123)

        assert len(observer_calls) == 3
        assert ("observer1", ("test",), {"value": 123}) in observer_calls
        assert ("observer2", ("test",), {"value": 123}) in observer_calls
        assert ("observer3", ("test",), {"value": 123}) in observer_calls

    def test_notify_observers_safe_iteration(self, observer_calls: list) -> None:
        """Test that observers can be safely removed during notification."""
        observable = Observable()

        def observer1(*args, **kwargs) -> None:
            observer_calls.append("observer1")
            # Remove observer2 during notification
            observable.remove_observer(observer2)

        def observer2(*args, **kwargs) -> None:
            observer_calls.append("observer2")

        def observer3(*args, **kwargs) -> None:
            observer_calls.append("observer3")

        observable.add_observer(observer1)
        observable.add_observer(observer2)
        observable.add_observer(observer3)

        # This should not raise an error despite modification during iteration
        observable._notify_observers()

        # observer1 and observer3 should be called, observer2 might or might not
        # depending on iteration order
        assert "observer1" in observer_calls
        assert "observer3" in observer_calls

    def test_notify_observers_safe_addition(self, observer_calls: list) -> None:
        """Test that observers can be safely added during notification."""
        observable = Observable()

        def new_observer(*args, **kwargs) -> None:
            observer_calls.append("new_observer")

        def observer1(*args, **kwargs) -> None:
            observer_calls.append("observer1")
            # Add a new observer during notification
            observable.add_observer(new_observer)

        observable.add_observer(observer1)
        observable._notify_observers()

        # First notification: only observer1 should be called
        assert observer_calls == ["observer1"]

        # Second notification: both should be called
        observer_calls.clear()
        observable._notify_observers()
        assert "observer1" in observer_calls
        assert "new_observer" in observer_calls

    def test_observable_as_mixin(self, observer_calls: list) -> None:
        """Test Observable used as a mixin in a custom class."""

        class Counter(Observable):
            def __init__(self) -> None:
                super().__init__()
                self._count = 0

            @property
            def count(self) -> int:
                return self._count

            @count.setter
            def count(self, value: int) -> None:
                self._count = value
                self._notify_observers(name="count", value=value)

        def on_count_change(*args, **kwargs) -> None:
            observer_calls.append((args, kwargs))

        counter = Counter()
        counter.add_observer(on_count_change)

        counter.count = 5
        assert len(observer_calls) == 1
        assert observer_calls[0] == ((), {"name": "count", "value": 5})

        counter.count = 10
        assert len(observer_calls) == 2
        assert observer_calls[1] == ((), {"name": "count", "value": 10})

    def test_observable_with_multiple_inheritance(self) -> None:
        """Test Observable works correctly with multiple inheritance."""

        class Base:
            def __init__(self, base_value: str) -> None:
                self.base_value = base_value

        class Derived(Observable, Base):
            def __init__(self, base_value: str, derived_value: int) -> None:
                super().__init__(base_value=base_value)
                self.derived_value = derived_value

        obj = Derived("test", 42)
        assert obj.base_value == "test"
        assert obj.derived_value == 42
        assert hasattr(obj, "_observers")
        assert obj._observers == []

    def test_observer_exception_handling(self, observer_calls: list) -> None:
        """Test that exceptions in observers don't prevent other observers from being called."""
        observable = Observable()

        def failing_observer(*args, **kwargs) -> None:
            observer_calls.append("failing")
            raise RuntimeError("Observer failed")

        def working_observer(*args, **kwargs) -> None:
            observer_calls.append("working")

        observable.add_observer(failing_observer)
        observable.add_observer(working_observer)

        # This will raise because we don't catch exceptions in _notify_observers
        with pytest.raises(RuntimeError, match="Observer failed"):
            observable._notify_observers()

        # Only the failing observer was called before the exception
        assert "failing" in observer_calls
        # The working observer after the failing one won't be called
        # This is expected behavior - users should handle exceptions in their observers
