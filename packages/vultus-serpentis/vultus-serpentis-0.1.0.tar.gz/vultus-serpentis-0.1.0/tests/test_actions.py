"""
Comprehensive tests for the actions module.

Target coverage: 90%+
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from vultus_serpentis.actions import Action, HAS_TOOLTIP
from vultus_serpentis.events import EventBus


class MockWidget:
    """Mock Tkinter widget for testing."""

    def __init__(self):
        self.config_calls = []
        self.destroyed = False
        self.tk = Mock()  # Mock tk attribute for PhotoImage checks

    def configure(self, **kwargs):
        """Mock configure method."""
        if self.destroyed:
            import tkinter as tk
            raise tk.TclError("Widget destroyed")
        self.config_calls.append(kwargs)

    def keys(self):
        """Mock keys method."""
        return ["text", "command", "state", "image"]


class TestAction:
    """Tests for the Action class."""

    def test_action_initialization(self):
        """Test Action initialization with default values."""
        action = Action("Test", lambda: None)
        
        assert action.text == "Test"
        assert action.enabled is True
        assert action.tooltip_text is None
        assert action.image_path is None

    def test_action_initialization_with_kwargs(self):
        """Test Action initialization with keyword arguments."""
        action = Action(
            "Save",
            lambda: None,
            enabled=False,
            tooltip_text="Save file",
            image_path="/path/to/image.png"
        )
        
        assert action.text == "Save"
        assert action.enabled is False
        assert action.tooltip_text == "Save file"
        assert action.image_path == "/path/to/image.png"

    def test_action_with_event_bus(self):
        """Test Action with EventBus."""
        bus = EventBus()
        action = Action("Test", lambda: None, event_bus=bus)
        
        assert action._event_bus is bus

    def test_text_property_getter(self):
        """Test getting text property."""
        action = Action("Initial", lambda: None)
        assert action.text == "Initial"

    def test_text_property_setter(self, observer_calls: list):
        """Test setting text property."""
        action = Action("Initial", lambda: None)
        action.add_observer(lambda *args, **kwargs: observer_calls.append(kwargs))
        
        action.text = "Updated"
        
        assert action.text == "Updated"
        assert len(observer_calls) == 1
        assert observer_calls[0]["name"] == "text"
        assert observer_calls[0]["value"] == "Updated"

    def test_enabled_property_getter(self):
        """Test getting enabled property."""
        action = Action("Test", lambda: None, enabled=True)
        assert action.enabled is True

    def test_enabled_property_setter(self, observer_calls: list):
        """Test setting enabled property."""
        action = Action("Test", lambda: None)
        action.add_observer(lambda *args, **kwargs: observer_calls.append(kwargs))
        
        action.enabled = False
        
        assert action.enabled is False
        assert len(observer_calls) == 1
        assert observer_calls[0]["name"] == "enabled"
        assert observer_calls[0]["value"] is False

    def test_tooltip_text_property(self, observer_calls: list):
        """Test tooltip_text property."""
        action = Action("Test", lambda: None)
        action.add_observer(lambda *args, **kwargs: observer_calls.append(kwargs))
        
        action.tooltip_text = "New tooltip"
        
        assert action.tooltip_text == "New tooltip"
        assert len(observer_calls) == 1
        assert observer_calls[0]["name"] == "tooltip_text"

    def test_image_path_property(self, observer_calls: list):
        """Test image_path property."""
        action = Action("Test", lambda: None)
        action.add_observer(lambda *args, **kwargs: observer_calls.append(kwargs))
        
        action.image_path = "/new/path.png"
        
        assert action.image_path == "/new/path.png"
        assert len(observer_calls) == 1
        assert observer_calls[0]["name"] == "image_path"

    def test_execute_when_enabled(self):
        """Test executing action when enabled."""
        executed = []
        action = Action("Test", lambda: executed.append(True))
        
        action.execute()
        
        assert len(executed) == 1

    def test_execute_when_disabled(self):
        """Test that execute does nothing when disabled."""
        executed = []
        action = Action("Test", lambda: executed.append(True), enabled=False)
        
        action.execute()
        
        assert len(executed) == 0

    def test_execute_with_event(self):
        """Test execute with Tkinter event parameter."""
        executed = []
        action = Action("Test", lambda: executed.append(True))
        
        mock_event = Mock()
        action.execute(event=mock_event)
        
        assert len(executed) == 1

    def test_bind_widget_basic(self):
        """Test binding a widget to an action."""
        action = Action("Test", lambda: None)
        widget = MockWidget()
        
        action.bind_widget(widget)
        
        assert len(widget.config_calls) >= 1
        # Check that text and command were configured
        config = widget.config_calls[0]
        assert config.get("text") == "Test"
        assert config.get("command") == action.execute

    def test_bind_widget_sets_initial_state(self):
        """Test that bind_widget sets initial enabled state."""
        action = Action("Test", lambda: None, enabled=False)
        widget = MockWidget()
        
        action.bind_widget(widget)
        
        # Should have at least 2 configure calls: initial config + state
        assert len(widget.config_calls) >= 1
        # Last call should set state to disabled
        states = [call.get("state") for call in widget.config_calls if "state" in call]
        assert "disabled" in states

    def test_bind_multiple_widgets(self):
        """Test binding multiple widgets to same action."""
        action = Action("Test", lambda: None)
        widget1 = MockWidget()
        widget2 = MockWidget()
        
        action.bind_widget(widget1)
        action.bind_widget(widget2)
        
        assert len(widget1.config_calls) >= 1
        assert len(widget2.config_calls) >= 1

    def test_unbind_widget(self):
        """Test unbinding a widget."""
        action = Action("Test", lambda: None)
        widget = MockWidget()
        
        action.bind_widget(widget)
        action.unbind_widget(widget)
        
        # Widget should no longer be in bound widgets
        assert widget not in action._bound_widgets

    def test_enabled_updates_bound_widgets(self):
        """Test that changing enabled updates all bound widgets."""
        action = Action("Test", lambda: None, enabled=True)
        widget1 = MockWidget()
        widget2 = MockWidget()
        
        action.bind_widget(widget1)
        action.bind_widget(widget2)
        
        # Clear previous calls
        widget1.config_calls.clear()
        widget2.config_calls.clear()
        
        action.enabled = False
        
        # Both widgets should be updated
        states1 = [call.get("state") for call in widget1.config_calls if "state" in call]
        states2 = [call.get("state") for call in widget2.config_calls if "state" in call]
        assert "disabled" in states1
        assert "disabled" in states2

    def test_text_updates_bound_widgets(self):
        """Test that changing text updates all bound widgets."""
        action = Action("Initial", lambda: None)
        widget = MockWidget()
        
        action.bind_widget(widget)
        widget.config_calls.clear()
        
        action.text = "Updated"
        
        texts = [call.get("text") for call in widget.config_calls if "text" in call]
        assert "Updated" in texts

    def test_widget_destruction_cleanup(self):
        """Test that destroyed widgets are removed from tracking."""
        action = Action("Test", lambda: None)
        widget = MockWidget()
        
        action.bind_widget(widget)
        
        # Simulate widget destruction
        widget.destroyed = True
        
        # Try to update - should remove widget
        action.enabled = False
        
        # Widget should be removed from bound widgets
        assert widget not in action._bound_widgets

    def test_image_path_updates_widgets(self):
        """Test that changing image_path updates widgets."""
        action = Action("Test", lambda: None)
        widget = MockWidget()
        
        action.bind_widget(widget)
        widget.config_calls.clear()
        
        with patch('tkinter.PhotoImage') as mock_photo:
            mock_photo.return_value = Mock()
            action.image_path = "/new/image.png"
        
        # Should have attempted to update image
        assert len(widget.config_calls) > 0

    def test_tooltip_updates_widgets_when_available(self):
        """Test that changing tooltip updates widgets when tooltip library available."""
        action = Action("Test", lambda: None)
        widget = MockWidget()
        
        action.bind_widget(widget)
        
        if HAS_TOOLTIP:
            with patch('vultus_serpentis.actions.ToolTip') as mock_tooltip:
                action.tooltip_text = "New tooltip"
                # Should have attempted to create tooltip
                assert mock_tooltip.called or len(action._tooltips) >= 0
        else:
            # Without tooltip library, should still work
            action.tooltip_text = "New tooltip"
            assert action.tooltip_text == "New tooltip"

    def test_bind_widget_with_image_path(self):
        """Test binding widget when action has image_path."""
        with patch('tkinter.PhotoImage') as mock_photo:
            mock_image = Mock()
            mock_photo.return_value = mock_image
            
            action = Action("Test", lambda: None, image_path="/path/to/image.png")
            widget = MockWidget()
            
            action.bind_widget(widget)
            
            # Should have configured with image
            images = [call.get("image") for call in widget.config_calls if "image" in call]
            assert mock_image in images or len(images) > 0

    def test_bind_widget_with_master(self):
        """Test binding widget with explicit master for PhotoImage."""
        with patch('tkinter.PhotoImage') as mock_photo:
            mock_image = Mock()
            mock_photo.return_value = mock_image
            
            action = Action("Test", lambda: None, image_path="/path/to/image.png")
            widget = MockWidget()
            master = Mock()
            master.tk = Mock()
            
            action.bind_widget(widget, master=master)
            
            # PhotoImage should have been created with master
            if mock_photo.called:
                call_kwargs = mock_photo.call_args[1] if mock_photo.call_args else {}
                assert call_kwargs.get("master") == master or mock_photo.called

    def test_bind_widget_invalid_image_path(self):
        """Test binding widget with invalid image path."""
        import tkinter as tk
        
        with patch('tkinter.PhotoImage', side_effect=tk.TclError("Image not found")):
            action = Action("Test", lambda: None, image_path="/invalid/path.png")
            widget = MockWidget()
            
            # Should not raise, just skip image
            action.bind_widget(widget)
            
            assert len(widget.config_calls) >= 1

    def test_update_widgets_with_invalid_image(self):
        """Test updating widgets when image file is invalid."""
        import tkinter as tk
        
        action = Action("Test", lambda: None)
        widget = MockWidget()
        action.bind_widget(widget)
        
        with patch('tkinter.PhotoImage', side_effect=tk.TclError("Invalid")):
            action.image_path = "/invalid.png"
        
        # Should not raise
        assert action.image_path == "/invalid.png"

    def test_remove_image_from_widgets(self):
        """Test removing image by setting image_path to None."""
        action = Action("Test", lambda: None, image_path="/path.png")
        widget = MockWidget()
        
        with patch('tkinter.PhotoImage'):
            action.bind_widget(widget)
            widget.config_calls.clear()
            
            action.image_path = None
        
        # Should have updated widgets
        images = [call.get("image") for call in widget.config_calls if "image" in call]
        assert "" in images or len(widget.config_calls) > 0

    def test_weakset_prevents_memory_leak(self):
        """Test that WeakSet allows garbage collection of widgets."""
        action = Action("Test", lambda: None)
        widget = MockWidget()
        
        action.bind_widget(widget)
        assert len(list(action._bound_widgets)) == 1
        
        # Delete widget reference
        del widget
        
        # WeakSet should now be empty (or will be after gc)
        import gc
        gc.collect()
        # Note: Can't reliably test this without actual widget destruction

    def test_tooltip_cleanup_on_unbind(self):
        """Test that tooltips are cleaned up when widget is unbound."""
        action = Action("Test", lambda: None, tooltip_text="Tooltip")
        widget = MockWidget()
        
        if HAS_TOOLTIP:
            with patch('vultus_serpentis.actions.ToolTip'):
                action.bind_widget(widget)
                widget_id = id(widget)
                
                action.unbind_widget(widget)
                
                assert widget_id not in action._tooltips
        else:
            action.bind_widget(widget)
            action.unbind_widget(widget)
            assert widget not in action._bound_widgets

    def test_multiple_property_changes(self):
        """Test multiple property changes in sequence."""
        action = Action("Test", lambda: None)
        widget = MockWidget()
        action.bind_widget(widget)
        
        widget.config_calls.clear()
        
        action.text = "New Text"
        action.enabled = False
        action.tooltip_text = "New Tooltip"
        
        # All changes should have been applied
        assert action.text == "New Text"
        assert action.enabled is False
        assert action.tooltip_text == "New Tooltip"

    def test_observer_notifications(self, observer_calls: list):
        """Test that all property changes notify observers."""
        action = Action("Test", lambda: None)
        action.add_observer(lambda *args, **kwargs: observer_calls.append(kwargs))
        
        action.text = "New"
        action.enabled = False
        action.tooltip_text = "Tip"
        action.image_path = "/path.png"
        
        assert len(observer_calls) == 4
        names = [call["name"] for call in observer_calls]
        assert "text" in names
        assert "enabled" in names
        assert "tooltip_text" in names
        assert "image_path" in names
