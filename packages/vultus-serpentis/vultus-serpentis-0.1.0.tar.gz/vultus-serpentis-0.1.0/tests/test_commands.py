"""
Comprehensive tests for the commands module.

Target coverage: 90%+
"""

import pytest
from vultus_serpentis.commands import (
    Command,
    CommandStack,
    CommandManager,
    BatchCommand,
    CommandExecutedEvent,
    CommandUndoneEvent,
    CommandRedoneEvent,
)
from vultus_serpentis.events import EventBus


# Test command implementations
class SimpleCommand(Command):
    """Simple test command that tracks execution state."""

    def __init__(self, value: int = 0):
        self.value = value
        self.executed = False
        self.undone = False
        self.redone = False

    def execute(self) -> bool:
        self.executed = True
        return True

    def undo(self) -> bool:
        self.undone = True
        return True

    def redo(self) -> bool:
        self.redone = True
        return True


class FailingCommand(Command):
    """Command that fails on execute."""

    def execute(self) -> bool:
        return False

    def undo(self) -> bool:
        return True


class FailingUndoCommand(Command):
    """Command that fails on undo."""

    def __init__(self):
        self.executed = False

    def execute(self) -> bool:
        self.executed = True
        return True

    def undo(self) -> bool:
        return False


class CounterCommand(Command):
    """Command that modifies a counter."""

    def __init__(self, counter: dict, increment: int = 1):
        self.counter = counter
        self.increment = increment
        self.old_value = counter.get("value", 0)

    def execute(self) -> bool:
        self.counter["value"] = self.old_value + self.increment
        return True

    def undo(self) -> bool:
        self.counter["value"] = self.old_value
        return True


class TestCommand:
    """Tests for the Command ABC."""

    def test_command_is_abstract(self) -> None:
        """Test that Command cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Command()  # type: ignore[abstract]

    def test_simple_command_execute(self) -> None:
        """Test executing a simple command."""
        cmd = SimpleCommand()
        assert cmd.execute() is True
        assert cmd.executed is True

    def test_simple_command_undo(self) -> None:
        """Test undoing a simple command."""
        cmd = SimpleCommand()
        cmd.execute()
        assert cmd.undo() is True
        assert cmd.undone is True

    def test_simple_command_redo_default(self) -> None:
        """Test that default redo calls execute."""
        cmd = SimpleCommand()
        cmd.execute()
        cmd.undo()
        # Default redo should call execute again
        result = cmd.redo()
        assert result is True

    def test_custom_redo(self) -> None:
        """Test command with custom redo implementation."""
        cmd = SimpleCommand()
        cmd.execute()
        cmd.undo()
        cmd.redo()
        assert cmd.redone is True


class TestCommandStack:
    """Tests for the CommandStack class."""

    def test_stack_initialization(self) -> None:
        """Test CommandStack initialization."""
        stack = CommandStack()
        assert len(stack.undo_stack) == 0
        assert len(stack.redo_stack) == 0
        assert stack.max_size is None

    def test_stack_with_max_size(self) -> None:
        """Test CommandStack with maximum size."""
        stack = CommandStack(max_size=5)
        assert stack.max_size == 5

    def test_push_command(self, observer_calls: list) -> None:
        """Test pushing a command onto the stack."""
        stack = CommandStack()
        stack.add_observer(lambda *args, **kwargs: observer_calls.append("notified"))

        cmd = SimpleCommand()
        stack.push(cmd)

        assert len(stack.undo_stack) == 1
        assert stack.undo_stack[0] is cmd
        assert len(observer_calls) == 1

    def test_push_clears_redo_stack(self) -> None:
        """Test that pushing a command clears the redo stack."""
        stack = CommandStack()
        cmd1 = SimpleCommand()
        cmd2 = SimpleCommand()

        stack.push(cmd1)
        stack.redo_stack.append(cmd2)  # Manually add to redo
        assert len(stack.redo_stack) == 1

        stack.push(SimpleCommand())
        assert len(stack.redo_stack) == 0

    def test_push_enforces_max_size(self) -> None:
        """Test that push enforces maximum stack size."""
        stack = CommandStack(max_size=3)

        for i in range(5):
            stack.push(SimpleCommand(value=i))

        assert len(stack.undo_stack) == 3
        # Should keep the last 3 commands (values 2, 3, 4)
        assert stack.undo_stack[0].value == 2
        assert stack.undo_stack[1].value == 3
        assert stack.undo_stack[2].value == 4

    def test_max_size_property(self) -> None:
        """Test getting and setting max_size property."""
        stack = CommandStack()
        assert stack.max_size is None

        stack.max_size = 10
        assert stack.max_size == 10

    def test_set_max_size_trims_stack(self, observer_calls: list) -> None:
        """Test that setting max_size trims existing stack."""
        stack = CommandStack()
        stack.add_observer(lambda *args, **kwargs: observer_calls.append("notified"))

        for i in range(5):
            stack.push(SimpleCommand(value=i))

        observer_calls.clear()
        stack.max_size = 3

        assert len(stack.undo_stack) == 3
        assert stack.undo_stack[0].value == 2
        assert len(observer_calls) == 1  # Notified of change

    def test_push_batch(self) -> None:
        """Test pushing a batch of commands."""
        stack = CommandStack()
        commands = [SimpleCommand(value=i) for i in range(3)]

        stack.push_batch(commands)

        assert len(stack.undo_stack) == 1
        assert isinstance(stack.undo_stack[0], BatchCommand)

    def test_pop_undo(self) -> None:
        """Test popping from undo stack."""
        stack = CommandStack()
        cmd = SimpleCommand()
        stack.push(cmd)

        popped = stack.pop_undo()
        assert popped is cmd
        assert len(stack.undo_stack) == 0

    def test_pop_undo_empty_stack(self) -> None:
        """Test popping from empty undo stack."""
        stack = CommandStack()
        assert stack.pop_undo() is None

    def test_pop_redo(self) -> None:
        """Test popping from redo stack."""
        stack = CommandStack()
        cmd = SimpleCommand()
        stack.redo_stack.append(cmd)

        popped = stack.pop_redo()
        assert popped is cmd
        assert len(stack.redo_stack) == 0

    def test_pop_redo_empty_stack(self) -> None:
        """Test popping from empty redo stack."""
        stack = CommandStack()
        assert stack.pop_redo() is None

    def test_can_undo(self) -> None:
        """Test can_undo method."""
        stack = CommandStack()
        assert stack.can_undo() is False

        stack.push(SimpleCommand())
        assert stack.can_undo() is True

    def test_can_redo(self) -> None:
        """Test can_redo method."""
        stack = CommandStack()
        assert stack.can_redo() is False

        stack.redo_stack.append(SimpleCommand())
        assert stack.can_redo() is True

    def test_clear(self, observer_calls: list) -> None:
        """Test clearing the stack."""
        stack = CommandStack()
        stack.add_observer(lambda *args, **kwargs: observer_calls.append("notified"))

        stack.push(SimpleCommand())
        stack.redo_stack.append(SimpleCommand())

        stack.clear()

        assert len(stack.undo_stack) == 0
        assert len(stack.redo_stack) == 0
        assert len(observer_calls) == 2  # One for push, one for clear


class TestBatchCommand:
    """Tests for the BatchCommand class."""

    def test_batch_execute_all_succeed(self) -> None:
        """Test batch execution when all commands succeed."""
        commands = [SimpleCommand(value=i) for i in range(3)]
        batch = BatchCommand(commands)

        assert batch.execute() is True
        for cmd in commands:
            assert cmd.executed is True

    def test_batch_execute_with_failure(self) -> None:
        """Test batch execution with a failing command."""
        cmd1 = SimpleCommand(value=1)
        cmd2 = FailingCommand()
        cmd3 = SimpleCommand(value=3)

        batch = BatchCommand([cmd1, cmd2, cmd3])

        assert batch.execute() is False
        assert cmd1.executed is True
        assert cmd1.undone is True  # Should be rolled back
        assert cmd3.executed is False  # Should not execute

    def test_batch_undo(self) -> None:
        """Test batch undo."""
        commands = [SimpleCommand(value=i) for i in range(3)]
        batch = BatchCommand(commands)

        batch.execute()
        assert batch.undo() is True

        # Should undo in reverse order
        for cmd in commands:
            assert cmd.undone is True

    def test_batch_undo_with_failure(self) -> None:
        """Test batch undo when a command fails to undo."""
        cmd1 = SimpleCommand()
        cmd2 = FailingUndoCommand()
        cmd3 = SimpleCommand()

        batch = BatchCommand([cmd1, cmd2, cmd3])
        batch.execute()

        assert batch.undo() is False

    def test_batch_redo(self) -> None:
        """Test batch redo."""
        commands = [SimpleCommand(value=i) for i in range(3)]
        batch = BatchCommand(commands)

        batch.execute()
        batch.undo()
        assert batch.redo() is True

        for cmd in commands:
            assert cmd.redone is True


class TestCommandManager:
    """Tests for the CommandManager class."""

    def test_manager_initialization(self) -> None:
        """Test CommandManager initialization."""
        manager = CommandManager()
        assert isinstance(manager.stack, CommandStack)
        assert manager.stack.max_size is None

    def test_manager_with_max_stack_size(self) -> None:
        """Test CommandManager with maximum stack size."""
        manager = CommandManager(max_stack_size=10)
        assert manager.stack.max_size == 10

    def test_manager_default_singleton(self) -> None:
        """Test that default() returns the same instance."""
        manager1 = CommandManager.default()
        manager2 = CommandManager.default()
        assert manager1 is manager2

    def test_execute_successful_command(self) -> None:
        """Test executing a successful command."""
        manager = CommandManager()
        cmd = SimpleCommand()

        result = manager.execute(cmd)

        assert result is True
        assert cmd.executed is True
        assert manager.stack.can_undo() is True

    def test_execute_failing_command(self) -> None:
        """Test executing a failing command."""
        manager = CommandManager()
        cmd = FailingCommand()

        result = manager.execute(cmd)

        assert result is False
        assert manager.stack.can_undo() is False  # Not added to stack

    def test_undo_command(self) -> None:
        """Test undoing a command."""
        manager = CommandManager()
        cmd = SimpleCommand()

        manager.execute(cmd)
        result = manager.undo()

        assert result is True
        assert cmd.undone is True
        assert manager.can_undo() is False
        assert manager.can_redo() is True

    def test_undo_with_empty_stack(self) -> None:
        """Test undoing when stack is empty."""
        manager = CommandManager()
        result = manager.undo()
        assert result is False

    def test_undo_failing_command(self) -> None:
        """Test undoing a command that fails."""
        manager = CommandManager()
        cmd = FailingUndoCommand()

        manager.execute(cmd)
        result = manager.undo()

        assert result is False
        assert manager.can_redo() is False  # Not added to redo stack

    def test_redo_command(self) -> None:
        """Test redoing a command."""
        manager = CommandManager()
        cmd = SimpleCommand()

        manager.execute(cmd)
        manager.undo()
        result = manager.redo()

        assert result is True
        assert cmd.redone is True
        assert manager.can_undo() is True
        assert manager.can_redo() is False

    def test_redo_with_empty_stack(self) -> None:
        """Test redoing when redo stack is empty."""
        manager = CommandManager()
        result = manager.redo()
        assert result is False

    def test_can_undo(self) -> None:
        """Test can_undo method."""
        manager = CommandManager()
        assert manager.can_undo() is False

        manager.execute(SimpleCommand())
        assert manager.can_undo() is True

    def test_can_redo(self) -> None:
        """Test can_redo method."""
        manager = CommandManager()
        assert manager.can_redo() is False

        manager.execute(SimpleCommand())
        manager.undo()
        assert manager.can_redo() is True

    def test_reset(self) -> None:
        """Test resetting the manager."""
        manager = CommandManager()
        manager.execute(SimpleCommand())
        manager.execute(SimpleCommand())

        manager.reset()

        assert manager.can_undo() is False
        assert manager.can_redo() is False

    def test_execute_with_event_bus(self, observer_calls: list) -> None:
        """Test that execute publishes events."""
        bus = EventBus()
        bus.subscribe(CommandExecutedEvent, lambda e: observer_calls.append(e))

        manager = CommandManager(event_bus=bus)
        cmd = SimpleCommand()
        manager.execute(cmd)

        assert len(observer_calls) == 1
        event = observer_calls[0]
        assert isinstance(event, CommandExecutedEvent)
        assert event.command_name == "SimpleCommand"
        assert event.success is True

    def test_undo_with_event_bus(self, observer_calls: list) -> None:
        """Test that undo publishes events."""
        bus = EventBus()
        bus.subscribe(CommandUndoneEvent, lambda e: observer_calls.append(e))

        manager = CommandManager(event_bus=bus)
        manager.execute(SimpleCommand())
        manager.undo()

        assert len(observer_calls) == 1
        event = observer_calls[0]
        assert isinstance(event, CommandUndoneEvent)
        assert event.command_name == "SimpleCommand"

    def test_redo_with_event_bus(self, observer_calls: list) -> None:
        """Test that redo publishes events."""
        bus = EventBus()
        bus.subscribe(CommandRedoneEvent, lambda e: observer_calls.append(e))

        manager = CommandManager(event_bus=bus)
        manager.execute(SimpleCommand())
        manager.undo()
        manager.redo()

        assert len(observer_calls) == 1
        event = observer_calls[0]
        assert isinstance(event, CommandRedoneEvent)
        assert event.command_name == "SimpleCommand"

    def test_complex_undo_redo_sequence(self) -> None:
        """Test a complex sequence of undo/redo operations."""
        counter = {"value": 0}
        manager = CommandManager()

        # Execute several commands
        manager.execute(CounterCommand(counter, increment=1))
        assert counter["value"] == 1

        manager.execute(CounterCommand(counter, increment=2))
        assert counter["value"] == 3

        manager.execute(CounterCommand(counter, increment=3))
        assert counter["value"] == 6

        # Undo twice
        manager.undo()
        assert counter["value"] == 3

        manager.undo()
        assert counter["value"] == 1

        # Redo once
        manager.redo()
        assert counter["value"] == 3

        # Execute new command (should clear redo stack)
        manager.execute(CounterCommand(counter, increment=10))
        assert counter["value"] == 13
        assert manager.can_redo() is False

    def test_stack_size_limit_in_manager(self) -> None:
        """Test that manager respects stack size limit."""
        manager = CommandManager(max_stack_size=3)

        for i in range(5):
            manager.execute(SimpleCommand(value=i))

        assert len(manager.stack.undo_stack) == 3
