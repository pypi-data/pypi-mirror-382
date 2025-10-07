# JSONMacros

A JSON preprocessor with macros, conditionals, and includes for Python.

## Overview

JSONMacros allows you to write dynamic JSON files with macro definitions, conditional logic, file includes, and Python expression evaluation. It's perfect for configuration files, data templates, and any scenario where you need programmatic JSON generation.

## Features

- **Macros**: Define reusable variables and functions with parameters
- **Conditionals**: Use `$if`, `$then`, `$else` for conditional content
- **File Includes**: Import and merge other JSON files with `$include`
- **Python Expressions**: Evaluate Python code within JSON using `${...}` syntax
- **Flexible Merging**: Control how included files are merged

## Installation

```bash
pip install jsonmacros
```

## Quick Start

```python
from jsonmacros import JsonMacroProcessor

processor = JsonMacroProcessor()
result = processor.process_file("path/to/your/template.json")
print(result)
```

## Usage Examples

### Basic Macros

**Input**
```json
{
    "$macros": [
        {
            "name": "greeting",
            "body": "Hello, world!"
        },
        {
            "name": "number",
            "body": 42
        }
    ],
    "message": "${greeting}",
    "value": "${number}"
}
```
**Output**
```json
{
    "message": "Hello, world!",
    "value": 42
}
```

### Parameterized Macros

**Input**
```json
{
    "$macros": [
        {
            "name": "add",
            "params": ["x", "y"],
            "body": "${x + y}"
        }
    ],
    "value": {
        "$macro": "add",
        "$params": {
            "x": 6,
            "y": 7
        }
    }
}
```
**Output**
```json
{
    "value": 13
}
```

### Conditionals
**Input**
```json
{
    "$macros": [
        {
            "name": "score",
            "body": 85
        }
    ],
    "result": {
        "$if": "${score >= 90}",
        "$then": "Excellent",
        "$else": {
            "$if": "${score >= 70}",
            "$then": "Good",
            "$else": "Needs Improvement"
        }
    }
}
```
**Output**
```json
{
    "result": "Good"
}
```

### File Includes

Create modular JSON files by including others:

**base.json**:
```json
{
    "$macros": [
        {
            "name": "app_name",
            "body": "MyApp"
        }
    ],
    "config": {
        "name": "${app_name}",
        "version": "1.0.0"
    }
}
```

**extended.json**:
```json
{
    "$include": ["base.json"],
    "$macros": [
        {
            "name": "environment",
            "body": "production"
        }
    ],
    "config": {
        "environment": "${environment}",
        "debug": false
    }
}
```

**output.json** (with merge strategy `MERGE`):
```json
{
    "config": {
        "name": "MyApp",
        "version": "1.0.0",
        "environment": "production",
        "debug": false
    }
}
```

## API Reference

### JsonMacroProcessor

The main class for processing JSON with macros.

```python
from jsonmacros import JsonMacroProcessor, JsonMergeStrategy

processor = JsonMacroProcessor(merge_strategy=JsonMergeStrategy.OVERRIDE)
```

### JsonMergeStrategy

Controls how included files are merged:
- Define merge strategies for handling conflicts and combining data

## Examples

See the [examples/](examples/) directory for more comprehensive examples:

- [examples/test.json](examples/test.json) - Parameterized macros with Python expressions
- [examples/merge_a.json](examples/merge_a.json) - Base configuration with macros
- [examples/merge_b.json](examples/merge_b.json) - Extended configuration with includes and conditionals

## Requirements

- Python >=3.9

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE.md](LICENSE.md) file for details.

## Contributing

Issues and contributions are welcome! Please visit the [GitHub repository](https://github.com/rix-ros/jsonmacros) to report bugs or request features.

## Authors

- Broderick Riopelle <broderio@umich.edu>