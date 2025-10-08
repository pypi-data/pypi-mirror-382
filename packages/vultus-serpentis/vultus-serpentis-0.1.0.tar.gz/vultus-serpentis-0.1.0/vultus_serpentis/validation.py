"""
Validation module for user input validation with configurable feedback.

This module provides a flexible validation framework for Tkinter applications
with support for multiple validators, feedback strategies, debouncing, and
context-based validation.

Example:
    >>> from vultus_serpentis import ValidationBinder, RequiredValidator
    >>> import tkinter as tk
    >>>
    >>> root = tk.Tk()
    >>> var = tk.StringVar()
    >>> entry = tk.Entry(root, textvariable=var)
    >>>
    >>> with ValidationBinder(entry, var, [RequiredValidator()], debounce_ms=300):
    ...     root.mainloop()
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
import re
import tkinter as tk


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    is_valid: bool
    message: str = ""


class Validator(ABC):
    """
    Abstract base class for validators.

    Subclasses must implement __call__ to perform validation logic.

    Example:
        >>> class PositiveNumberValidator(Validator):
        ...     def __call__(self, value, context=None):
        ...         try:
        ...             if float(value) > 0:
        ...                 return ValidationResult(True)
        ...             return ValidationResult(False, "Must be positive")
        ...         except ValueError:
        ...             return ValidationResult(False, "Must be a number")
    """

    @abstractmethod
    def __call__(
        self, value: Any, context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate a value and return the result.

        Args:
            value: The value to validate
            context: Optional context dictionary for cross-field validation

        Returns:
            ValidationResult indicating success or failure
        """
        ...


class RequiredValidator(Validator):
    """
    Validator that checks if a value is present.

    Considers empty strings, None, and whitespace-only strings as invalid.
    """

    def __init__(self, message: str = "This field is required.") -> None:
        """
        Initialize the validator.

        Args:
            message: Custom error message
        """
        self.message = message

    def __call__(
        self, value: Any, context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Check if value is not empty."""
        if not value or (isinstance(value, str) and not value.strip()):
            return ValidationResult(False, self.message)
        return ValidationResult(True)


class LengthValidator(Validator):
    """Validator that checks string length."""

    def __init__(
        self,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        message: Optional[str] = None
    ) -> None:
        """
        Initialize the validator.

        Args:
            min_length: Minimum allowed length (inclusive)
            max_length: Maximum allowed length (inclusive)
            message: Custom error message
        """
        self.min_length = min_length
        self.max_length = max_length
        self.message = message

    def __call__(
        self, value: Any, context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Check if value length is within bounds."""
        if not isinstance(value, str):
            value = str(value)

        length = len(value)

        if self.min_length is not None and length < self.min_length:
            msg = self.message or f"Must be at least {self.min_length} characters."
            return ValidationResult(False, msg)

        if self.max_length is not None and length > self.max_length:
            msg = self.message or f"Must be at most {self.max_length} characters."
            return ValidationResult(False, msg)

        return ValidationResult(True)


class RangeValidator(Validator):
    """Validator that checks if a numeric value is within a range."""

    def __init__(
        self,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        message: Optional[str] = None
    ) -> None:
        """
        Initialize the validator.

        Args:
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive)
            message: Custom error message
        """
        self.min_value = min_value
        self.max_value = max_value
        self.message = message

    def __call__(
        self, value: Any, context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Check if value is within range."""
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return ValidationResult(False, "Must be a valid number.")

        if self.min_value is not None and num_value < self.min_value:
            msg = self.message or f"Must be at least {self.min_value}."
            return ValidationResult(False, msg)

        if self.max_value is not None and num_value > self.max_value:
            msg = self.message or f"Must be at most {self.max_value}."
            return ValidationResult(False, msg)

        return ValidationResult(True)


class PatternValidator(Validator):
    """Validator that checks if a value matches a regular expression."""

    def __init__(self, pattern: str, message: str = "Invalid format.") -> None:
        """
        Initialize the validator.

        Args:
            pattern: Regular expression pattern
            message: Error message for non-matching values
        """
        self.pattern = re.compile(pattern)
        self.message = message

    def __call__(
        self, value: Any, context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Check if value matches the pattern."""
        if not isinstance(value, str):
            value = str(value)

        if self.pattern.match(value):
            return ValidationResult(True)
        return ValidationResult(False, self.message)


class EmailValidator(Validator):
    """Validator that checks if a value is a valid email address."""

    # Simple email pattern - not RFC-compliant but practical
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    def __init__(self, message: str = "Invalid email address.") -> None:
        """
        Initialize the validator.

        Args:
            message: Custom error message
        """
        self.pattern = re.compile(self.EMAIL_PATTERN)
        self.message = message

    def __call__(
        self, value: Any, context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Check if value is a valid email."""
        if not isinstance(value, str):
            return ValidationResult(False, self.message)

        if self.pattern.match(value.strip()):
            return ValidationResult(True)
        return ValidationResult(False, self.message)


class CompositeValidator(Validator):
    """
    Validator that combines multiple validators.

    Runs validators in sequence and returns the first failure, or success
    if all validators pass.
    """

    def __init__(self, validators: List[Validator]) -> None:
        """
        Initialize with a list of validators.

        Args:
            validators: List of validators to run in sequence
        """
        self.validators = validators

    def __call__(
        self, value: Any, context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Run all validators and return first failure or success."""
        for validator in self.validators:
            result = validator(value, context)
            if not result.is_valid:
                return result
        return ValidationResult(True)


def default_feedback(widget: tk.Widget, result: ValidationResult) -> None:
    """
    Default feedback strategy that works with both TTK and TTKBootstrap.

    For TTKBootstrap widgets, uses bootstyle ('danger' for invalid, 'success'
    for valid). For plain TTK/Tkinter widgets, uses background and foreground
    colors.

    Args:
        widget: The widget to apply feedback to
        result: The validation result
    """
    # Check if widget supports bootstyle (TTKBootstrap)
    try:
        if hasattr(widget, "configure"):
            keys = widget.keys()  # type: ignore[attr-defined,no-untyped-call]
            if "bootstyle" in keys:
                style = "danger" if not result.is_valid else "success"
                widget.configure(bootstyle=style)  # type: ignore[call-arg]
                return
    except tk.TclError:
        pass

    # Fallback to standard TTK/Tkinter
    bg = "pink" if not result.is_valid else "white"
    fg = "red" if not result.is_valid else "black"
    try:
        widget.configure(background=bg, foreground=fg)  # type: ignore[call-arg]
    except tk.TclError:
        # Some widgets don't support bg/fg
        pass


def tooltip_feedback(widget: tk.Widget, result: ValidationResult) -> None:
    """
    Feedback strategy using tooltips.

    Shows a tooltip with the error message when validation fails.
    Requires tkinter-tooltip library.

    Args:
        widget: The widget to apply feedback to
        result: The validation result
    """
    from tkinter_tooltip import ToolTip  # type: ignore[import-not-found,import-untyped]

    if not result.is_valid:
        ToolTip(widget, msg=result.message, delay=0.0)


class ValidationBinder:
    """
    Binds validation to a widget and variable with automatic feedback.

    Monitors a Tkinter variable and validates its value whenever it changes.
    Provides visual feedback through a configurable feedback strategy and
    supports debouncing to avoid excessive validation calls.

    Can be used as a context manager for automatic cleanup.

    Example:
        >>> var = tk.StringVar()
        >>> entry = tk.Entry(root, textvariable=var)
        >>> validators = [RequiredValidator(), EmailValidator()]
        >>>
        >>> with ValidationBinder(entry, var, validators, debounce_ms=300):
        ...     root.mainloop()
    """

    def __init__(
        self,
        widget: tk.Widget,
        variable: tk.Variable,
        validators: List[Validator],
        feedback_strategy: Callable[[tk.Widget, ValidationResult], None] = default_feedback,
        debounce_ms: int = 0,
    ) -> None:
        """
        Initialize the ValidationBinder.

        Args:
            widget: The widget to apply feedback to
            variable: The Tkinter variable to monitor
            validators: List of validators to run
            feedback_strategy: Function to apply visual feedback
            debounce_ms: Milliseconds to wait before validating (0 = immediate)
        """
        self._widget = widget
        self._variable = variable
        self._validators = validators
        self._feedback = feedback_strategy
        self._debounce_ms = debounce_ms
        self._after_id: Optional[str] = None
        self._trace_id = self._variable.trace_add("write", self._debounced_validate)

    def __enter__(self) -> "ValidationBinder":
        """
        Context manager entry.

        Returns:
            self for use in with statement
        """
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Context manager exit - cleanup.

        Removes variable trace and cancels pending validation.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        self._variable.trace_remove("write", self._trace_id)
        if self._after_id:
            self._widget.after_cancel(self._after_id)

    def _debounced_validate(self, *args: Any) -> None:
        """
        Debounced validation trigger.

        Cancels any pending validation and schedules a new one after the
        debounce delay.

        Args:
            *args: Arguments from trace callback (ignored)
        """
        if self._after_id:
            self._widget.after_cancel(self._after_id)
        self._after_id = self._widget.after(self._debounce_ms, self.validate, *args)

    def validate(self, *args: Any, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Run validators and apply feedback.

        Validates the current variable value against all validators in sequence.
        Stops at the first failure and applies feedback.

        Args:
            *args: Arguments from trace callback (ignored)
            context: Optional context dictionary for cross-field validation

        Returns:
            True if all validators pass, False otherwise
        """
        value: Any = self._variable.get()  # type: ignore[no-untyped-call]
        for validator in self._validators:
            result = validator(value, context)
            if not result.is_valid:
                self._feedback(self._widget, result)
                return False

        self._feedback(self._widget, ValidationResult(True))
        return True
