"""
Command Framework module for undo/redo functionality.

This module provides a robust command pattern implementation for building
undo/redo functionality in applications. It includes support for batch
commands, stack size limits, and optional event bus integration.

Example:
    >>> from vultus_serpentis import Command, CommandManager
    >>>
    >>> class IncrementCommand(Command):
    ...     def __init__(self, counter):
    ...         self.counter = counter
    ...         self.old_value = counter.value
    ...
    ...     def execute(self) -> bool:
    ...         self.counter.value += 1
    ...         return True
    ...
    ...     def undo(self) -> bool:
    ...         self.counter.value = self.old_value
    ...         return True
    >>>
    >>> manager = CommandManager.default()
    >>> manager.execute(IncrementCommand(my_counter))
    >>> manager.undo()  # Reverts the increment
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Union
from dataclasses import dataclass
from vultus_serpentis.common import Observable
from vultus_serpentis.events import EventBus, Event


# Event classes for command execution
@dataclass
class CommandExecutedEvent(Event):
    """Event published when a command is executed."""

    command_name: str
    success: bool


@dataclass
class CommandUndoneEvent(Event):
    """Event published when a command is undone."""

    command_name: str


@dataclass
class CommandRedoneEvent(Event):
    """Event published when a command is redone."""

    command_name: str


class Command(ABC):
    """
    Abstract base class for an undoable/redoable command.

    Subclasses must implement execute() and undo() methods. The redo()
    method has a default implementation that calls execute() again, but
    can be overridden for optimization.

    Example:
        >>> class SetValueCommand(Command):
        ...     def __init__(self, obj, new_value):
        ...         self.obj = obj
        ...         self.old_value = obj.value
        ...         self.new_value = new_value
        ...
        ...     def execute(self) -> bool:
        ...         self.obj.value = self.new_value
        ...         return True
        ...
        ...     def undo(self) -> bool:
        ...         self.obj.value = self.old_value
        ...         return True
    """

    @abstractmethod
    def execute(self) -> bool:
        """
        Execute the command's logic.

        Returns:
            True if execution succeeded, False otherwise

        Note:
            If this returns False, the command will not be added to the
            undo stack.
        """
        ...

    @abstractmethod
    def undo(self) -> bool:
        """
        Revert the changes made by execute().

        Returns:
            True if undo succeeded, False otherwise
        """
        ...

    def redo(self) -> bool:
        """
        Re-apply the changes.

        Default implementation calls execute() again. Override this if you
        can optimize the redo operation.

        Returns:
            True if redo succeeded, False otherwise
        """
        return self.execute()


class CommandStack(Observable):
    """
    Stack for managing undo/redo commands with optional size limits.

    The stack maintains two lists: undo_stack and redo_stack. When a new
    command is pushed, the redo stack is cleared. If a maximum size is set,
    the oldest commands are removed (FIFO) when the limit is exceeded.

    Observers are notified whenever the stack state changes.

    Args:
        max_size: Maximum number of commands to keep in undo stack.
                 None means unlimited. Default: None

    Example:
        >>> stack = CommandStack(max_size=100)
        >>> stack.push(my_command)
        >>> if stack.can_undo():
        ...     cmd = stack.pop_undo()
        ...     cmd.undo()
    """

    def __init__(self, max_size: Optional[int] = None) -> None:
        """
        Initialize the CommandStack.

        Args:
            max_size: Maximum number of commands in undo stack (None = unlimited)
        """
        super().__init__()
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []
        self._max_size = max_size

    @property
    def max_size(self) -> Optional[int]:
        """Get the maximum stack size."""
        return self._max_size

    @max_size.setter
    def max_size(self, value: Optional[int]) -> None:
        """
        Set the maximum stack size.

        If the new size is smaller than the current stack, oldest commands
        are removed.
        """
        self._max_size = value
        if value is not None and len(self.undo_stack) > value:
            # Remove oldest commands
            self.undo_stack = self.undo_stack[-value:]
            self._notify_observers()

    def push(self, command: Command) -> None:
        """
        Push a command onto the undo stack.

        Clears the redo stack and enforces max_size limit if set.

        Args:
            command: The command to push
        """
        self.undo_stack.append(command)
        self.redo_stack.clear()

        # Enforce max size (FIFO eviction)
        if self._max_size is not None and len(self.undo_stack) > self._max_size:
            self.undo_stack.pop(0)

        self._notify_observers()

    def push_batch(self, commands: List[Command]) -> None:
        """
        Push a group of commands as a single undoable unit.

        Args:
            commands: List of commands to batch together
        """
        batch = BatchCommand(commands)
        self.push(batch)

    def pop_undo(self) -> Optional[Command]:
        """
        Pop a command from the undo stack.

        Returns:
            The command, or None if stack is empty
        """
        if self.can_undo():
            return self.undo_stack.pop()
        return None

    def pop_redo(self) -> Optional[Command]:
        """
        Pop a command from the redo stack.

        Returns:
            The command, or None if stack is empty
        """
        if self.can_redo():
            return self.redo_stack.pop()
        return None

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self.redo_stack) > 0

    def clear(self) -> None:
        """Clear both undo and redo stacks."""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._notify_observers()


class BatchCommand(Command):
    """Command that groups multiple commands as a single undoable unit."""

    def __init__(self, commands: List[Command]) -> None:
        """Initialize with a list of commands."""
        self.commands = commands

    def execute(self) -> bool:
        """Execute all commands in the batch."""
        executed: List[Command] = []
        for cmd in self.commands:
            if not cmd.execute():
                # Rollback previously executed commands
                for prev_cmd in reversed(executed):
                    prev_cmd.undo()
                return False
            executed.append(cmd)
        return True

    def undo(self) -> bool:
        """Undo all commands in reverse order."""
        for cmd in reversed(self.commands):
            if not cmd.undo():
                return False
        return True

    def redo(self) -> bool:
        """Redo all commands in order."""
        for cmd in self.commands:
            if not cmd.redo():
                return False
        return True


class CommandManager:
    """
    High-level API for command execution and undo/redo.

    Provides a convenient interface for executing commands and managing
    undo/redo operations. Optionally publishes events to an EventBus
    for loose coupling with UI components.

    Example:
        >>> manager = CommandManager.default()
        >>> manager.execute(MyCommand())
        >>> manager.undo()
        >>> manager.redo()
    """

    _default_instance: Union["CommandManager", None] = None

    @classmethod
    def default(cls) -> "CommandManager":
        """
        Get the default CommandManager instance.

        Returns:
            The default CommandManager instance
        """
        if cls._default_instance is None:
            cls._default_instance = cls()
        return cls._default_instance

    def __init__(
        self, event_bus: Optional[EventBus] = None, max_stack_size: Optional[int] = None
    ) -> None:
        """
        Initialize the CommandManager.

        Args:
            event_bus: Optional EventBus for publishing command events
            max_stack_size: Maximum undo stack size (None = unlimited)
        """
        self._stack = CommandStack(max_size=max_stack_size)
        self._bus = event_bus

    def reset(self) -> None:
        """
        Reset the command manager for testing.

        Clears all commands from the stack.
        """
        self._stack.clear()

    @property
    def stack(self) -> CommandStack:
        """Get the command stack."""
        return self._stack

    def execute(self, command: Command) -> bool:
        """
        Execute a command and push it to the stack if successful.

        Args:
            command: The command to execute

        Returns:
            True if execution succeeded, False otherwise
        """
        success = command.execute()
        if success:
            self.stack.push(command)

        # Publish event if bus is configured
        if self._bus:
            event = CommandExecutedEvent(
                command_name=command.__class__.__name__, success=success
            )
            self._bus.publish(event)

        return success

    def undo(self) -> bool:
        """
        Undo the last command.

        Returns:
            True if undo succeeded, False if no command to undo or undo failed
        """
        cmd = self._stack.pop_undo()
        if cmd is None:
            return False

        success = cmd.undo()
        if success:
            self._stack.redo_stack.append(cmd)
            self._stack._notify_observers()

            # Publish event if bus is configured
            if self._bus:
                event = CommandUndoneEvent(command_name=cmd.__class__.__name__)
                self._bus.publish(event)

        return success

    def redo(self) -> bool:
        """
        Redo the last undone command.

        Returns:
            True if redo succeeded, False if no command to redo or redo failed
        """
        cmd = self._stack.pop_redo()
        if cmd is None:
            return False

        success = cmd.redo()
        if success:
            self._stack.undo_stack.append(cmd)
            self._stack._notify_observers()

            # Publish event if bus is configured
            if self._bus:
                event = CommandRedoneEvent(command_name=cmd.__class__.__name__)
                self._bus.publish(event)

        return success

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self._stack.can_undo()

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self._stack.can_redo()
