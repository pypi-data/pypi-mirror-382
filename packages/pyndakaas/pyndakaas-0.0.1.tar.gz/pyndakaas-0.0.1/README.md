# Pyndakaas

An extensible static site generator written in Python.

## Features

- **Extensible Handler System**: Register custom file handlers for different content types
- **Flexible Renderer System**: Support for multiple rendering engines (Markdown, etc.)
- **Template Support**: Jinja2-based templating with metadata support
- **File Metadata**: JSON frontmatter parsing for rich content metadata
- **Glob Matching**: Template functions for filtering and selecting files

## Installation

```bash
pip install pyndakaas
```

For development:

```bash
git clone https://github.com/rubenvannieuwpoort/pyndakaas
cd pyndakaas
pip install -e .
```

## Quick Start

```python
from pathlib import Path
from pyndakaas import process_dir, Handler, register, renderer

# Define a custom handler
@register()
class MarkdownHandler(Handler):
    suffix = '.html'
    template = 'post'
    renderer = 'markdown'
    
    @staticmethod
    def detect(source_path: Path) -> bool:
        return source_path.suffix == '.md'

# Define a custom renderer
@renderer("markdown")
def render_markdown(source: str) -> str:
    # Your markdown rendering logic here
    return f"<p>{source}</p>"

# Process directory
process_dir(Path('src'), Path('output'))
```

## File Format

Source files use JSON frontmatter followed by content:

```
{
    "title": "My Post",
    "template": "post",
    "renderer": "markdown"
}

# My Content

This is the actual content that will be processed.
```

## Handlers

Handlers define how different file types are processed:

- `suffix`: Output file extension
- `template`: Default template to use
- `renderer`: Default renderer for content
- `detect()`: Method to identify files this handler should process

## Templates

Templates are Jinja2 files in the `templates/` directory. They receive:

- All metadata from the source file
- `body`: Rendered content
- `path`: Source file path
- `source`: Raw source content
- `glob()`: Function to filter files by pattern

## License

MIT License - see LICENSE file for details.