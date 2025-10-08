# AI Script Generator - MCP Server

MCP Server for AL Parser that finds pages and fields for Business Central scenarios. This tool helps analyze Business Central AL objects and generate YAML test scenarios.

## Features

- 🔍 **Find AL Pages**: Search for pages with fields, actions, and repeaters
- 📊 **Find AL Tables**: Analyze table structures with fields and extensions
- 🎯 **Find AL Enums**: Locate enums with values and extensions
- ⚙️ **Find AL Codeunits**: Search codeunits with procedures and fields
- 📋 **Read YAML Templates**: Load and parse YAML template files
- 🎯 **Smart Search**: Fuzzy matching for AL object names

## Installation

### From PyPI (recommended)
```bash
pip install aiscriptgenerator
```

### From Source
```bash
git clone <repository-url>
cd AIScriptGenerator
pip install -e .
```

## Usage

### As MCP Server

1. **Configure MCP Client**: Add to your `mcp.json` configuration:
```json
{
  "servers": {
    "aiscriptgenerator": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "aiscriptgenerator"]
    }
  }
}
```

2. **Run MCP Server**:
```bash
python -m aiscriptgenerator
```

### Available MCP Tools

#### `find_page_info_with_fields`
Find information about AL pages with fields, actions, and repeaters.
```python
find_page_info_with_fields(page_name="Sales Order")
```

#### `find_table_info_with_fields`
Find information about AL tables with fields, including extensions.
```python
find_table_info_with_fields(table_name="Customer")
```

#### `find_enum_info`
Find information about AL enums with values and extensions.
```python
find_enum_info(enum_name="Sales Document Type")
```

#### `find_codeunit_info`
Find information about AL codeunits with procedures and fields.
```python
find_codeunit_info(codeunit_name="Sales-Post")
```

#### `read_yaml_template`
Read and parse YAML template files.
```python
read_yaml_template()
```

## Configuration

The server looks for AL files in the `FoodFresh` directory and caches the parsed information in `al_cache.json`. The cache is automatically rebuilt when AL files are modified.

### Directory Structure
```
project/
├── src/aiscriptgenerator/
│   ├── __init__.py
│   ├── server.py          # MCP server implementation
│   ├── alparser.py        # AL file parser
│   └── extract_al.py      # AL object extractor
├── FoodFresh/             # AL source files
├── al_cache.json          # Parsed AL objects cache
├── mcp.json              # MCP server configuration
└── README.md
```

## Development

### Setup Development Environment
```bash
# Clone repository
git clone <repository-url>
cd AIScriptGenerator

# Install in development mode with dev dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black src/

# Type checking
mypy src/
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=aiscriptgenerator

# Run specific test
pytest tests/test_server.py
```

## Requirements

- Python 3.8+
- FastMCP 2.11.3+
- MCP CLI 1.13.0+
- PyYAML 6.0+
- RapidFuzz 3.13.0+

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and ensure they pass
6. Submit a pull request

## Troubleshooting

### Cache Issues
If you're getting stale results, delete the cache file:
```bash
rm al_cache.json
```

### MCP Connection Issues
Verify your MCP configuration:
```bash
# Test server directly
python -m aiscriptgenerator

# Check MCP configuration
cat mcp.json
```

### AL File Path Issues
Ensure the `FoodFresh` directory contains your AL files and is accessible to the server.

## Support

For issues, questions, or contributions, please open an issue in the repository.
