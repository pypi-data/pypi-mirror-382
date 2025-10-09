# Norvelang

Multi-Source Data Processing Language

## Features
- PEMDAS-compliant mathematical expressions
- String functions (upper, lower, len, contains, etc.)
- SQL-like pipelines for CSV, JSON, XML, SQLite, Excel
- Filtering and aggregation with grouping and joins
- Function support in use and where clauses
- Robust join handling with automatic column disambiguation
- Clean, extensible grammar
- CLI and Python API for interactive and programmatic use

## Quick Start

```norvelang
data.csv | use name, age | where age > 30
```

## Installation

```powershell
uv venv
.venv\Scripts\activate
uv pip install -r .\requirements.txt
```

## Usage

### Command Line
```powershell
# Run a sample file
python -m norve samples/math.nv

# Interactive REPL
python -m norve

# Use regular Lark parser (disable cython)
python -m norve samples/queries.nv --no-lark-cython
```

### Python API
```python
import norve

df = norve.execute_query('''data.csv | use name, age | limit 10''')
output = norve.execute_with_output('''data.csv | use name, age | limit 5''')
variables = {'my_table': 'users.csv'}
df = norve.execute_query('''let users = $my_table; $users | use name, age | limit 10''', variables=variables)
```

## Directory Structure

```
norvelang/
├── norve/              # Core language implementation
│   ├── api/            # Python API
│   ├── ast/            # AST definitions
│   ├── error/          # Error handling
│   ├── interpreter/    # Pipeline execution
│   ├── transformer/    # AST transformation
│   ├── grammar.lark    # Grammar definition
│   └── *.py            # Core modules
├── publish/            # Create new release on Github and PyPI
├── samples/            # Example .nv files
├── sample_data/        # Test data files
├── tests/              # Unit tests
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Running Tests

```bash
cd tests
pytest -v
```

## Sample Files
- math.nv: Math and function demos
- queries.nv, queries2.nv: Data processing examples
- data_sources.nv: Multi-format data
- errors.nv: Error handling
