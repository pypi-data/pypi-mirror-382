"""
Shared base classes and utilities for the Vultus Serpentis library.

This module contains foundational code shared by other modules to prevent
circular imports and reduce redundancy.
"""

from typing import Any, Callable, List


class VultusException(Exception):
    """Base exception class for the Vultus Serpentis library."""


class Observable:
    """
    A simple mixin class implementing the observer pattern.

    This class provides property-level change notifications, distinct from the
    system-wide Event Bus. It should be used for local, tight bindings such as
    Action-widget synchronization or CommandStack state changes.

    Example:
        >>> class Counter(Observable):
        ...     def __init__(self):
        ...         super().__init__()
        ...         self._count = 0
        ...
        ...     @property
        ...     def count(self):
        ...         return self._count
        ...
        ...     @count.setter
        ...     def count(self, value):
        ...         self._count = value
        ...         self._notify_observers(name='count', value=value)
        ...
        >>> def on_change(name, value):
        ...     print(f"{name} changed to {value}")
        ...
        >>> counter = Counter()
        >>> counter.add_observer(on_change)
        >>> counter.count = 5
        count changed to 5
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the Observable mixin.

        Args:
            *args: Positional arguments passed to parent class
            **kwargs: Keyword arguments passed to parent class
        """
        super().__init__(*args, **kwargs)
        self._observers: List[Callable[..., None]] = []

    def add_observer(self, observer: Callable[..., None]) -> None:
        """
        Register an observer callback.

        The observer will be called when _notify_observers is invoked.
        Duplicate observers are ignored.

        Args:
            observer: A callable that will be invoked on notifications
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Callable[..., None]) -> None:
        """
        Unregister an observer callback.

        Args:
            observer: The observer to remove

        Raises:
            ValueError: If the observer is not registered
        """
        self._observers.remove(observer)

    def _notify_observers(self, *args: Any, **kwargs: Any) -> None:
        """
        Notify all registered observers.

        Creates a copy of the observer list before iteration to avoid
        issues if observers are added/removed during notification.

        Args:
            *args: Positional arguments passed to each observer
            **kwargs: Keyword arguments passed to each observer
        """
        for observer in self._observers[:]:  # Copy to avoid modification issues
            observer(*args, **kwargs)
