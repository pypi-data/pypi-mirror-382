"""
Actions module for Swing-like Action class.

This module provides a Swing-inspired Action class that centralizes UI component
logic and state. Actions can be bound to multiple widgets and automatically
update their state, text, images, and tooltips.

Example:
    >>> from vultus_serpentis import Action
    >>> import tkinter as tk
    >>>
    >>> def save_file():
    ...     print("File saved!")
    >>>
    >>> root = tk.Tk()
    >>> save_action = Action("Save", save_file, tooltip_text="Save the file")
    >>>
    >>> button1 = tk.Button(root)
    >>> button2 = tk.Button(root)
    >>> save_action.bind_widget(button1)
    >>> save_action.bind_widget(button2)
    >>>
    >>> save_action.enabled = False  # Disables both buttons
"""

from __future__ import annotations
from typing import Callable, Optional, Any, TYPE_CHECKING
from weakref import WeakSet
import tkinter as tk
from vultus_serpentis.common import Observable
from vultus_serpentis.events import EventBus

if TYPE_CHECKING:
    from tkinter import Event

# Try to import tkinter-tooltip, but don't fail if not available
try:
    from tkinter_tooltip import ToolTip  # type: ignore[import-not-found,import-untyped]
    HAS_TOOLTIP = True
except ImportError:
    HAS_TOOLTIP = False


class Action(Observable):
    """
    Centralizes logic and state for a UI action.

    Inspired by Java Swing's Action interface, this class provides a way to
    centralize the logic and state for UI actions. Multiple widgets can be
    bound to a single Action, and changes to the Action's properties
    automatically update all bound widgets.

    Supports both plain TTK and TTKBootstrap widgets.

    Args:
        text: The text label for the action
        command: The callable to execute when the action is triggered
        event_bus: Optional EventBus for publishing action events
        **kwargs: Additional options:
            - enabled (bool): Initial enabled state (default: True)
            - image_path (str): Path to image file for icon
            - tooltip_text (str): Tooltip text
            - accelerator (str): Keyboard accelerator text (e.g., "Ctrl+S")

    Example:
        >>> action = Action("Open", open_file, tooltip_text="Open a file")
        >>> action.bind_widget(my_button)
        >>> action.enabled = False  # Disables the button
    """

    def __init__(
        self,
        text: str,
        command: Callable[[], None],
        event_bus: Optional[EventBus] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize the Action.

        Args:
            text: Action text/label
            command: Callable to execute
            event_bus: Optional EventBus for events
            **kwargs: Additional options (enabled, image_path, tooltip_text, accelerator)
        """
        super().__init__()
        self._text = text
        self._command = command
        self._enabled = bool(kwargs.get("enabled", True))
        self._image_path: Optional[str] = kwargs.get("image_path", None)
        self._tooltip_text: Optional[str] = kwargs.get("tooltip_text", None)
        self._accelerator: Optional[str] = kwargs.get("accelerator", None)
        self._event_bus = event_bus

        self._image_ref: Optional[tk.PhotoImage] = None
        self._bound_widgets: WeakSet[tk.Widget] = WeakSet()
        self._tooltips: dict[int, Any] = {}  # Track tooltips by widget id

    @property
    def text(self) -> str:
        """Get the action text."""
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        """
        Set the action text and update all bound widgets.

        Args:
            value: New text value
        """
        self._text = value
        self._update_widgets_text()
        self._notify_observers(name="text", value=value)

    @property
    def enabled(self) -> bool:
        """Get the enabled state."""
        return bool(self._enabled)

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Set the enabled state and update all bound widgets.

        Args:
            value: New enabled state
        """
        self._enabled = bool(value)
        self._update_widgets_state()
        self._notify_observers(name="enabled", value=value)

    @property
    def tooltip_text(self) -> Optional[str]:
        """Get the tooltip text."""
        return self._tooltip_text

    @tooltip_text.setter
    def tooltip_text(self, value: Optional[str]) -> None:
        """
        Set the tooltip text and update all bound widgets.

        Args:
            value: New tooltip text (None to remove)
        """
        self._tooltip_text = value
        self._update_widgets_tooltips()
        self._notify_observers(name="tooltip_text", value=value)

    @property
    def image_path(self) -> Optional[str]:
        """Get the image path."""
        return self._image_path

    @image_path.setter
    def image_path(self, value: Optional[str]) -> None:
        """
        Set the image path and update all bound widgets.

        Args:
            value: Path to image file (None to remove image)
        """
        self._image_path = value
        self._image_ref = None  # Clear cached image
        self._update_widgets_image()
        self._notify_observers(name="image_path", value=value)

    def execute(self, event: Optional[Event] = None) -> None:
        """
        Execute the action's command if enabled.

        Args:
            event: Optional Tkinter event (for use as event handler)
        """
        if self.enabled:
            self._command()

    def bind_widget(self, widget: tk.Widget, master: Optional[tk.Tk] = None) -> None:
        """
        Bind a widget to this action.

        Configures the widget with the action's current state and tracks it
        for future updates.

        Args:
            widget: The widget to bind
            master: Optional master window for PhotoImage (if using images)
        """
        self._bound_widgets.add(widget)

        # Configure widget with current action state
        config: dict[str, Any] = {
            "text": self._text,
            "command": self.execute
        }

        # Handle image if specified
        if self._image_path:
            if self._image_ref is None or (
                master and self._image_ref.tk != master.tk  # type: ignore[attr-defined]
            ):
                # Create or recreate PhotoImage with correct master
                try:
                    if master:
                        self._image_ref = tk.PhotoImage(master=master, file=self._image_path)
                    else:
                        self._image_ref = tk.PhotoImage(file=self._image_path)
                except tk.TclError:
                    # Image file not found or invalid
                    pass

            if self._image_ref:
                config["image"] = self._image_ref
                config["compound"] = "left"  # Show both text and image

        # Apply configuration
        try:
            widget.configure(**config)  # type: ignore[call-arg]
        except tk.TclError:
            pass

        # Set initial state
        self._update_widget_state(widget)

        # Add tooltip if available and requested
        if self._tooltip_text and HAS_TOOLTIP:
            try:
                tooltip = ToolTip(widget, msg=self._tooltip_text, delay=0.5)
                self._tooltips[id(widget)] = tooltip
            except Exception:  # Catch any tooltip creation errors
                pass

    def unbind_widget(self, widget: tk.Widget) -> None:
        """
        Unbind a widget from this action.

        Args:
            widget: The widget to unbind
        """
        self._bound_widgets.discard(widget)
        # Remove tooltip if it exists
        widget_id = id(widget)
        if widget_id in self._tooltips:
            del self._tooltips[widget_id]

    def _update_widgets_state(self) -> None:
        """Update the enabled/disabled state of all bound widgets."""
        for widget in list(self._bound_widgets):
            self._update_widget_state(widget)

    def _update_widget_state(self, widget: tk.Widget) -> None:
        """
        Update the state of a single widget.

        Args:
            widget: The widget to update
        """
        state = "normal" if self._enabled else "disabled"
        try:
            widget.configure(state=state)  # type: ignore[call-arg]
        except tk.TclError:
            # Widget destroyed or doesn't support state
            self._bound_widgets.discard(widget)
            widget_id = id(widget)
            if widget_id in self._tooltips:
                del self._tooltips[widget_id]

    def _update_widgets_text(self) -> None:
        """Update the text of all bound widgets."""
        for widget in list(self._bound_widgets):
            try:
                widget.configure(text=self._text)  # type: ignore[call-arg]
            except tk.TclError:
                self._bound_widgets.discard(widget)

    def _update_widgets_image(self) -> None:
        """Update the image of all bound widgets."""
        # Clear old image reference
        self._image_ref = None

        for widget in list(self._bound_widgets):
            try:
                if self._image_path:
                    # Create new image if needed
                    if self._image_ref is None:
                        try:
                            self._image_ref = tk.PhotoImage(file=self._image_path)
                        except tk.TclError:
                            continue

                    widget.configure(
                        image=self._image_ref, compound="left"
                    )  # type: ignore[call-arg]
                else:
                    # Remove image
                    widget.configure(image="")  # type: ignore[call-arg]
            except tk.TclError:
                self._bound_widgets.discard(widget)

    def _update_widgets_tooltips(self) -> None:
        """Update tooltips for all bound widgets."""
        if not HAS_TOOLTIP:
            return

        for widget in list(self._bound_widgets):
            widget_id = id(widget)

            # Remove old tooltip
            if widget_id in self._tooltips:
                del self._tooltips[widget_id]

            # Add new tooltip if text is provided
            if self._tooltip_text:
                try:
                    tooltip = ToolTip(widget, msg=self._tooltip_text, delay=0.5)
                    self._tooltips[widget_id] = tooltip
                except Exception:
                    pass
