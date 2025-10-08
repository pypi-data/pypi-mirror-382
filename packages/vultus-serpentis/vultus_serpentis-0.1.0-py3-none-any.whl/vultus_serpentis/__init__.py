"""
Vultus Serpentis: Modern Tkinter utilities for TTK and TTKBootstrap applications.

This library provides a suite of integrated utilities for building modern Python
Tkinter applications with support for both plain TTK and TTKBootstrap.

Modules:
    - common: Shared base classes and utilities
    - events: Synchronous event bus for decoupled messaging
    - commands: Undo/redo framework based on the command pattern
    - actions: Swing-like Action class for centralizing UI component logic
    - validation: Framework for validating user input with configurable feedback
"""

__version__ = "0.1.0"

# Import core classes for public API
from vultus_serpentis.common import VultusException, Observable
from vultus_serpentis.events import Event, EventBus, AllEvents
from vultus_serpentis.commands import Command, CommandStack, CommandManager, BatchCommand
from vultus_serpentis.actions import Action
from vultus_serpentis.validation import (
    ValidationResult,
    Validator,
    ValidationBinder,
    RequiredValidator,
    CompositeValidator,
    default_feedback,
    tooltip_feedback,
)

__all__ = [
    # Version
    "__version__",
    # Common
    "VultusException",
    "Observable",
    # Events
    "Event",
    "EventBus",
    "AllEvents",
    # Commands
    "Command",
    "CommandStack",
    "CommandManager",
    "BatchCommand",
    # Actions
    "Action",
    # Validation
    "ValidationResult",
    "Validator",
    "ValidationBinder",
    "RequiredValidator",
    "CompositeValidator",
    "default_feedback",
    "tooltip_feedback",
]
