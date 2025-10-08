# Vultus Serpentis

**Modern Tkinter utilities for TTK and TTKBootstrap applications**

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Vultus Serpentis is a suite of integrated utilities for building modern Python Tkinter applications with support for both plain TTK and TTKBootstrap. It provides a clean, modular architecture for common GUI patterns including actions, validation, undo/redo, and event-driven communication.

## Features

- 🎯 **Actions**: Swing-like Action class for centralizing UI component logic and state
- ✅ **Validation**: Flexible input validation framework with configurable feedback strategies
- ↩️ **Commands**: Robust undo/redo framework based on the command pattern
- 📡 **Event Bus**: Synchronous event bus for decoupled component communication
- 🎨 **TTK/TTKBootstrap Support**: Works with plain TTK, with enhanced features for TTKBootstrap
- 🧪 **Well-Tested**: 90%+ test coverage with comprehensive test suite
- 📦 **Type-Safe**: Full type hints with mypy strict mode compliance

## Installation

### Basic Installation (TTK only)

```bash
pip install vultus-serpentis
```

### With TTKBootstrap Support

```bash
pip install vultus-serpentis[bootstrap]
```

### Development Installation

```bash
pip install vultus-serpentis[dev]
```

## Quick Start

### Actions

```python
from vultus_serpentis import Action
import tkinter as tk

def save_file():
    print("File saved!")

root = tk.Tk()
save_action = Action("Save", save_file, tooltip_text="Save the current file")

# Bind to multiple widgets
button = tk.Button(root)
save_action.bind_widget(button)

# Control state centrally
save_action.enabled = False  # Disables all bound widgets
```

### Validation

```python
from vultus_serpentis import ValidationBinder, RequiredValidator
import tkinter as tk

root = tk.Tk()
var = tk.StringVar()
entry = tk.Entry(root, textvariable=var)

# Validate with automatic feedback
with ValidationBinder(entry, var, [RequiredValidator()], debounce_ms=300):
    root.mainloop()
```

### Commands (Undo/Redo)

```python
from vultus_serpentis import Command, CommandManager

class IncrementCommand(Command):
    def __init__(self, counter):
        self.counter = counter
        self.old_value = counter.value
    
    def execute(self):
        self.counter.value += 1
        return True
    
    def undo(self):
        self.counter.value = self.old_value
        return True

manager = CommandManager.default()
manager.execute(IncrementCommand(my_counter))
manager.undo()  # Reverts the increment
manager.redo()  # Re-applies the increment
```

### Event Bus

```python
from vultus_serpentis import EventBus, Event
from dataclasses import dataclass

@dataclass
class FileOpenedEvent(Event):
    filename: str

bus = EventBus.default()

def on_file_opened(event):
    print(f"File opened: {event.filename}")

bus.subscribe(FileOpenedEvent, on_file_opened)
bus.publish(FileOpenedEvent(filename="document.txt"))
```

## Architecture

Vultus Serpentis is designed with modularity in mind. Each module can be used independently or integrated together:

- **`common`**: Shared base classes (Observable, VultusException)
- **`events`**: Event bus for pub/sub messaging
- **`commands`**: Command pattern implementation for undo/redo
- **`actions`**: Action abstraction for UI components
- **`validation`**: Input validation with feedback strategies

### TTK vs TTKBootstrap

The library works with plain TTK by default, with enhanced features when TTKBootstrap is available:

| Feature | Plain TTK | TTKBootstrap |
|---------|-----------|--------------|
| Core functionality | ✅ Full support | ✅ Full support |
| Validation feedback | Basic (bg/fg colors) | Enhanced (bootstyle, toast) |
| Action styling | Standard | Bootstyle-aware |

## Development

### Running Tests

```bash
pytest
```

### Type Checking

```bash
mypy vultus_serpentis
```

### Code Quality

```bash
pylint vultus_serpentis
```

### Coverage Report

```bash
pytest --cov=vultus_serpentis --cov-report=html
```

## Requirements

- Python 3.9+
- tksimpletooltip >= 2.6.0
- ttkbootstrap >= 1.10.0 (optional, for enhanced features)

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass (`pytest`)
2. Code is type-checked (`mypy --strict`)
3. Code follows style guide (`pylint`)
4. Test coverage remains above 90%

## Roadmap

- [x] Phase 1: Foundation (Observable, VultusException)
- [ ] Phase 2: Event Bus implementation
- [ ] Phase 3: Command Framework
- [ ] Phase 4: Actions Module
- [ ] Phase 5: Validation Module
- [ ] Phase 6: Integration & Examples
- [ ] Phase 7: Documentation & PyPI Release

## Examples

See the `examples/` directory for complete working examples:

- `demo_basic_ttk.py`: Using Vultus Serpentis with plain TTK
- `demo_bootstrap_enhanced.py`: Enhanced features with TTKBootstrap
- `demo_full_integration.py`: All modules working together

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/yourusername/vultus-serpentis).
