"""
Comprehensive tests for the validation module.

Target coverage: 90%+
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from vultus_serpentis.validation import (
    ValidationResult,
    Validator,
    RequiredValidator,
    LengthValidator,
    RangeValidator,
    PatternValidator,
    EmailValidator,
    CompositeValidator,
    default_feedback,
    tooltip_feedback,
    ValidationBinder,
)


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_validation_result_valid(self):
        """Test creating a valid result."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.message == ""

    def test_validation_result_invalid(self):
        """Test creating an invalid result with message."""
        result = ValidationResult(is_valid=False, message="Error")
        assert result.is_valid is False
        assert result.message == "Error"


class TestRequiredValidator:
    """Tests for RequiredValidator."""

    def test_required_validator_with_value(self):
        """Test that non-empty values pass."""
        validator = RequiredValidator()
        result = validator("test")
        assert result.is_valid is True

    def test_required_validator_with_empty_string(self):
        """Test that empty strings fail."""
        validator = RequiredValidator()
        result = validator("")
        assert result.is_valid is False
        assert "required" in result.message.lower()

    def test_required_validator_with_whitespace(self):
        """Test that whitespace-only strings fail."""
        validator = RequiredValidator()
        result = validator("   ")
        assert result.is_valid is False

    def test_required_validator_with_none(self):
        """Test that None fails."""
        validator = RequiredValidator()
        result = validator(None)
        assert result.is_valid is False

    def test_required_validator_custom_message(self):
        """Test custom error message."""
        validator = RequiredValidator(message="Custom error")
        result = validator("")
        assert result.message == "Custom error"

    def test_required_validator_with_context(self):
        """Test validator with context parameter."""
        validator = RequiredValidator()
        result = validator("test", context={"field": "value"})
        assert result.is_valid is True


class TestLengthValidator:
    """Tests for LengthValidator."""

    def test_length_validator_min_length_pass(self):
        """Test minimum length validation passes."""
        validator = LengthValidator(min_length=3)
        result = validator("test")
        assert result.is_valid is True

    def test_length_validator_min_length_fail(self):
        """Test minimum length validation fails."""
        validator = LengthValidator(min_length=5)
        result = validator("test")
        assert result.is_valid is False
        assert "at least 5" in result.message

    def test_length_validator_max_length_pass(self):
        """Test maximum length validation passes."""
        validator = LengthValidator(max_length=10)
        result = validator("test")
        assert result.is_valid is True

    def test_length_validator_max_length_fail(self):
        """Test maximum length validation fails."""
        validator = LengthValidator(max_length=3)
        result = validator("test")
        assert result.is_valid is False
        assert "at most 3" in result.message

    def test_length_validator_range(self):
        """Test length validation with both min and max."""
        validator = LengthValidator(min_length=3, max_length=10)
        assert validator("test").is_valid is True
        assert validator("ab").is_valid is False
        assert validator("a" * 11).is_valid is False

    def test_length_validator_custom_message(self):
        """Test custom error message."""
        validator = LengthValidator(min_length=5, message="Too short!")
        result = validator("ab")
        assert result.message == "Too short!"

    def test_length_validator_non_string(self):
        """Test validator converts non-strings."""
        validator = LengthValidator(min_length=2)
        result = validator(123)
        assert result.is_valid is True  # "123" has length 3


class TestRangeValidator:
    """Tests for RangeValidator."""

    def test_range_validator_min_value_pass(self):
        """Test minimum value validation passes."""
        validator = RangeValidator(min_value=0)
        result = validator("5")
        assert result.is_valid is True

    def test_range_validator_min_value_fail(self):
        """Test minimum value validation fails."""
        validator = RangeValidator(min_value=10)
        result = validator("5")
        assert result.is_valid is False
        assert "at least 10" in result.message

    def test_range_validator_max_value_pass(self):
        """Test maximum value validation passes."""
        validator = RangeValidator(max_value=100)
        result = validator("50")
        assert result.is_valid is True

    def test_range_validator_max_value_fail(self):
        """Test maximum value validation fails."""
        validator = RangeValidator(max_value=10)
        result = validator("50")
        assert result.is_valid is False
        assert "at most 10" in result.message

    def test_range_validator_range(self):
        """Test range validation with both min and max."""
        validator = RangeValidator(min_value=0, max_value=100)
        assert validator("50").is_valid is True
        assert validator("-1").is_valid is False
        assert validator("101").is_valid is False

    def test_range_validator_invalid_number(self):
        """Test validation with non-numeric value."""
        validator = RangeValidator(min_value=0)
        result = validator("abc")
        assert result.is_valid is False
        assert "valid number" in result.message

    def test_range_validator_custom_message(self):
        """Test custom error message."""
        validator = RangeValidator(min_value=0, message="Out of range!")
        result = validator("-5")
        assert result.message == "Out of range!"

    def test_range_validator_float_values(self):
        """Test validator with float values."""
        validator = RangeValidator(min_value=0.5, max_value=1.5)
        assert validator("1.0").is_valid is True
        assert validator("0.1").is_valid is False


class TestPatternValidator:
    """Tests for PatternValidator."""

    def test_pattern_validator_match(self):
        """Test pattern matching success."""
        validator = PatternValidator(r'^\d{3}$')
        result = validator("123")
        assert result.is_valid is True

    def test_pattern_validator_no_match(self):
        """Test pattern matching failure."""
        validator = PatternValidator(r'^\d{3}$')
        result = validator("abc")
        assert result.is_valid is False

    def test_pattern_validator_custom_message(self):
        """Test custom error message."""
        validator = PatternValidator(r'^\d+$', message="Must be digits")
        result = validator("abc")
        assert result.message == "Must be digits"

    def test_pattern_validator_email_pattern(self):
        """Test email-like pattern."""
        validator = PatternValidator(r'^[\w\.-]+@[\w\.-]+\.\w+$')
        assert validator("test@example.com").is_valid is True
        assert validator("invalid").is_valid is False

    def test_pattern_validator_non_string(self):
        """Test validator converts non-strings."""
        validator = PatternValidator(r'^\d+$')
        result = validator(123)
        assert result.is_valid is True


class TestEmailValidator:
    """Tests for EmailValidator."""

    def test_email_validator_valid_email(self):
        """Test valid email addresses."""
        validator = EmailValidator()
        assert validator("test@example.com").is_valid is True
        assert validator("user.name@domain.co.uk").is_valid is True
        assert validator("test+tag@example.com").is_valid is True

    def test_email_validator_invalid_email(self):
        """Test invalid email addresses."""
        validator = EmailValidator()
        assert validator("invalid").is_valid is False
        assert validator("@example.com").is_valid is False
        assert validator("test@").is_valid is False
        assert validator("test@domain").is_valid is False

    def test_email_validator_custom_message(self):
        """Test custom error message."""
        validator = EmailValidator(message="Bad email!")
        result = validator("invalid")
        assert result.message == "Bad email!"

    def test_email_validator_with_whitespace(self):
        """Test email with surrounding whitespace."""
        validator = EmailValidator()
        result = validator("  test@example.com  ")
        assert result.is_valid is True

    def test_email_validator_non_string(self):
        """Test validator with non-string input."""
        validator = EmailValidator()
        result = validator(123)
        assert result.is_valid is False


class TestCompositeValidator:
    """Tests for CompositeValidator."""

    def test_composite_validator_all_pass(self):
        """Test when all validators pass."""
        validators = [
            RequiredValidator(),
            LengthValidator(min_length=3),
        ]
        composite = CompositeValidator(validators)
        result = composite("test")
        assert result.is_valid is True

    def test_composite_validator_first_fails(self):
        """Test when first validator fails."""
        validators = [
            RequiredValidator(),
            LengthValidator(min_length=3),
        ]
        composite = CompositeValidator(validators)
        result = composite("")
        assert result.is_valid is False
        assert "required" in result.message.lower()

    def test_composite_validator_second_fails(self):
        """Test when second validator fails."""
        validators = [
            RequiredValidator(),
            LengthValidator(min_length=5),
        ]
        composite = CompositeValidator(validators)
        result = composite("ab")
        assert result.is_valid is False
        assert "5" in result.message

    def test_composite_validator_empty_list(self):
        """Test composite with no validators."""
        composite = CompositeValidator([])
        result = composite("anything")
        assert result.is_valid is True

    def test_composite_validator_with_context(self):
        """Test composite validator with context."""
        validators = [RequiredValidator()]
        composite = CompositeValidator(validators)
        result = composite("test", context={"field": "value"})
        assert result.is_valid is True


class TestDefaultFeedback:
    """Tests for default_feedback function."""

    def test_default_feedback_valid_result(self):
        """Test feedback for valid result."""
        widget = Mock()
        widget.keys = Mock(return_value=["text", "state"])
        result = ValidationResult(is_valid=True)

        default_feedback(widget, result)

        # Should configure with success colors
        widget.configure.assert_called()

    def test_default_feedback_invalid_result(self):
        """Test feedback for invalid result."""
        widget = Mock()
        widget.keys = Mock(return_value=["text", "state"])
        result = ValidationResult(is_valid=False, message="Error")

        default_feedback(widget, result)

        widget.configure.assert_called()

    def test_default_feedback_with_bootstyle(self):
        """Test feedback with TTKBootstrap widget."""
        widget = Mock()
        widget.keys = Mock(return_value=["text", "state", "bootstyle"])
        result = ValidationResult(is_valid=False)

        default_feedback(widget, result)

        # Should use bootstyle
        calls = [str(call) for call in widget.configure.call_args_list]
        assert any("bootstyle" in str(call) for call in calls)

    def test_default_feedback_widget_error(self):
        """Test feedback when widget raises TclError."""
        import tkinter as tk
        widget = Mock()
        widget.keys = Mock(side_effect=tk.TclError("Widget destroyed"))
        result = ValidationResult(is_valid=True)

        # Should not raise
        default_feedback(widget, result)


class TestTooltipFeedback:
    """Tests for tooltip_feedback function."""

    def test_tooltip_feedback_without_library(self):
        """Test tooltip feedback when library is not available."""
        # This test just ensures the function doesn't crash
        widget = Mock()
        result = ValidationResult(is_valid=False, message="Error")
        
        # Should handle missing library gracefully
        try:
            tooltip_feedback(widget, result)
        except ImportError:
            # Expected if library not installed
            pass


class TestValidationBinder:
    """Tests for ValidationBinder class."""

    def test_validation_binder_initialization(self):
        """Test ValidationBinder initialization."""
        widget = Mock()
        variable = Mock()
        variable.trace_add = Mock(return_value="trace_id")
        validators = [RequiredValidator()]

        binder = ValidationBinder(widget, variable, validators)

        assert binder._widget is widget
        assert binder._variable is variable
        assert binder._validators == validators
        variable.trace_add.assert_called_once()

    def test_validation_binder_context_manager(self):
        """Test ValidationBinder as context manager."""
        widget = Mock()
        variable = Mock()
        variable.trace_add = Mock(return_value="trace_id")
        validators = [RequiredValidator()]

        with ValidationBinder(widget, variable, validators) as binder:
            assert binder is not None

        variable.trace_remove.assert_called_once_with("write", "trace_id")

    def test_validation_binder_validate_success(self):
        """Test successful validation."""
        widget = Mock()
        widget.keys = Mock(return_value=["text", "state"])
        variable = Mock()
        variable.get.return_value = "test"
        variable.trace_add = Mock(return_value="trace_id")
        validators = [RequiredValidator()]

        binder = ValidationBinder(widget, variable, validators)
        result = binder.validate()

        assert result is True

    def test_validation_binder_validate_failure(self):
        """Test failed validation."""
        widget = Mock()
        widget.keys = Mock(return_value=["text", "state"])
        variable = Mock()
        variable.get.return_value = ""
        variable.trace_add = Mock(return_value="trace_id")
        validators = [RequiredValidator()]

        binder = ValidationBinder(widget, variable, validators)
        result = binder.validate()

        assert result is False

    def test_validation_binder_with_context(self):
        """Test validation with context."""
        widget = Mock()
        widget.keys = Mock(return_value=["text", "state"])
        variable = Mock()
        variable.get.return_value = "test"
        variable.trace_add = Mock(return_value="trace_id")
        validators = [RequiredValidator()]

        binder = ValidationBinder(widget, variable, validators)
        result = binder.validate(context={"field": "value"})

        assert result is True

    def test_validation_binder_debounce(self):
        """Test debounced validation."""
        widget = Mock()
        widget.after = Mock(return_value="after_id")
        widget.after_cancel = Mock()
        variable = Mock()
        variable.trace_add = Mock(return_value="trace_id")
        validators = [RequiredValidator()]

        binder = ValidationBinder(widget, variable, validators, debounce_ms=300)

        # Trigger debounced validation
        binder._debounced_validate()

        widget.after.assert_called_once_with(300, binder.validate)

    def test_validation_binder_debounce_cancel(self):
        """Test that debounce cancels previous validation."""
        widget = Mock()
        widget.after = Mock(return_value="after_id")
        widget.after_cancel = Mock()
        variable = Mock()
        variable.trace_add = Mock(return_value="trace_id")
        validators = [RequiredValidator()]

        binder = ValidationBinder(widget, variable, validators, debounce_ms=300)
        binder._after_id = "old_id"

        binder._debounced_validate()

        widget.after_cancel.assert_called_once_with("old_id")

    def test_validation_binder_cleanup(self):
        """Test cleanup on context manager exit."""
        widget = Mock()
        widget.after_cancel = Mock()
        variable = Mock()
        variable.trace_add = Mock(return_value="trace_id")
        variable.trace_remove = Mock()
        validators = [RequiredValidator()]

        binder = ValidationBinder(widget, variable, validators)
        binder._after_id = "after_id"

        binder.__exit__(None, None, None)

        variable.trace_remove.assert_called_once()
        widget.after_cancel.assert_called_once_with("after_id")

    def test_validation_binder_custom_feedback(self):
        """Test ValidationBinder with custom feedback strategy."""
        widget = Mock()
        variable = Mock()
        variable.get.return_value = ""
        variable.trace_add = Mock(return_value="trace_id")
        validators = [RequiredValidator()]
        feedback_calls = []

        def custom_feedback(w, r):
            feedback_calls.append((w, r))

        binder = ValidationBinder(widget, variable, validators, feedback_strategy=custom_feedback)
        binder.validate()

        assert len(feedback_calls) == 1
        assert feedback_calls[0][0] is widget
        assert feedback_calls[0][1].is_valid is False

    def test_validation_binder_multiple_validators(self):
        """Test ValidationBinder with multiple validators."""
        widget = Mock()
        widget.keys = Mock(return_value=["text", "state"])
        variable = Mock()
        variable.get.return_value = "ab"
        variable.trace_add = Mock(return_value="trace_id")
        validators = [
            RequiredValidator(),
            LengthValidator(min_length=5),
        ]

        binder = ValidationBinder(widget, variable, validators)
        result = binder.validate()

        assert result is False  # Fails on length validator
