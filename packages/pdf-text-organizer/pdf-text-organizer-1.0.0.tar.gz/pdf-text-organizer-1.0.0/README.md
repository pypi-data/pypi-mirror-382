# PDF Text Organizer

A demonstration application showcasing the **Vultus Serpentis** framework for building robust Tkinter applications.

## Features

- **PDF Text Extraction** - Extract text with bounding box coordinates
- **Spatial Grouping** - Automatically group text by proximity
- **Visual Preview** - See text layout on canvas
- **Undo/Redo** - Full undo/redo support for all operations
- **Export** - Save grouped text to JSON or CSV
- **Modern UI** - TTKBootstrap themes for a modern look

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Vultus Serpentis (from parent directory)
cd ../Main
pip install -e .
cd ../pdf_text_organizer

# Install PDF Text Organizer
pip install -e .
```

## Usage

```bash
# Run the application
pdf-organizer

# Or run directly
python -m pdf_text_organizer.app
```

## Framework Integration

This application demonstrates all modules of the Vultus Serpentis framework:

- **Observable** - Reactive data model with property notifications
- **Event Bus** - Decoupled component communication
- **Actions** - Centralized UI command logic with state management
- **Validation** - Input validation with visual feedback
- **Commands** - Undo/redo functionality for all operations

## Development

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=pdf_text_organizer --cov-report=html

# Type checking
mypy pdf_text_organizer/

# Linting
pylint pdf_text_organizer/
```

## License

MIT License - See LICENSE file for details
