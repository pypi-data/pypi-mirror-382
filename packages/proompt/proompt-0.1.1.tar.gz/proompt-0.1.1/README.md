# Proompt

**Object-oriented prompt engineering for LLMs**

Stop wrestling with string templates. Build composable, testable, and maintainable prompts using object-oriented design patterns.

```python
# Instead of this messy string concatenation...
prompt = f"""
Analyze this data:
{open('data.csv').read()}

Using these functions:
{str(my_functions)}
"""

# Write clean, composable prompts like this:
from proompt.data import (
    CsvDataProvider,
    FileDataProvider,
    SqliteProvider,
)
from proompt.base.context import ToolContext

section = PromptSection(
    context=ToolContext(my_function),
    CsvDataProvider("data.csv"),
    FileDataProvider("file.txt"),
    SqliteProvider("data.db"),
)
```

## Project Overview

Proompt is organized into a clean, modular structure:

```
proompt/
├── src/proompt/
│   ├── base/              # Abstract base classes
│   │   ├── context.py
│   │   ├── prompt.py
│   │   └── provider.py
│   └── data.py            # Concrete data provider examples
├── examples/              # Complete usage examples
│   ├── 01-simple_quarterly_review.py
│   ├── 02-intermediate_quarterly_review.py
│   └── 03-advanced_quarterly_review.py
└── tests/                 # Unit tests
```

**Key Components:**
- **Base classes** define contracts for providers, contexts, and prompts
- **Data providers** concrete examples of how to extend `DataProviders`
- **Examples** show real-world implementations from simple to advanced
- **Tests** ensure reliability and demonstrate usage patterns

## Why Proompt?

**Traditional string-based prompts are painful:**
- 🔥 Hard to compose and maintain large prompts
- 🐛 No separation between data and prompt logic
- 🚫 Difficult to test individual components
- 🔄 Can't reuse prompt components across projects
- ⚠️ No type safety or validation

**Proompt solves this with:**
- ✅ **Composable objects** - Build prompts from reusable components
- ✅ **Data providers** - Clean separation of data sources and prompt logic
- ✅ **Type safety** - Abstract base classes enforce contracts
- ✅ **Testable** - Unit test each component independently
- ✅ **Extensible** - Easy to create custom providers and contexts
- ✅ **Async ready** - Support for both sync and async operations

## Quick Start

```bash
uv pip install proompt
```

```python
from proompt.data import FileDataProvider

# Read a file and inject it into your prompt
provider = FileDataProvider("data.txt")
content = provider.run()  # Returns file contents as string

print(f"Analyze the data:\n{content}")
```

## Core Concepts

A few example classes for extending the `DataProvider` class can be found in the `proompt.data` module.

### 🔌 Providers - Inject Data from Any Source

Providers fetch data from external sources and format it for LLM consumption:

```python
from proompt.data import CsvDataProvider, SqliteProvider

# CSV data as markdown tables
csv_provider = CsvDataProvider("sales_data.csv")
print(csv_provider.run())
# | Product | Sales | Region |
# | ------- | ----- | ------ |
# | Widget  | 1000  | North  |

# Database queries as markdown tables
db_provider = SqliteProvider(
    "company.db",
    'SELECT * FROM employees WHERE department = "Engineering"'
)
print(db_provider.run())
# | name  | role      | salary |
# | ----- | --------- | ------ |
# | Alice | Developer | 85000  |
```

### 🛠️ Tool Context - Document Functions for LLMs

Automatically generate function documentation that LLMs can understand:

```python
from proompt.base.context import ToolContext

def calculate_tax(income: float, rate: float = 0.25) -> float:
    """Calculate tax owed on income."""
    return income * rate

tool_ctx = ToolContext(calculate_tax)
print(tool_ctx.render())
# Name: calculate_tax
# Description: Calculate tax owed on income.
# Arguments: income: float, rate: float = 0.25
# Returns: float
# Usage: Reference description for usage.
```

### 📝 Prompt Sections - Compose Complex Prompts

Combine providers, tools, and context into reusable sections:

```python
from textwrap import dedent
from proompt.base.prompt import PromptSection

class DataAnalysisSection(PromptSection):

    def formatter(self, instruction: str) -> str:
        data = "\n\n".join(p.run() for p in self.providers)
        tools = "\n\n".join(str(t) for t in self.tools)

        return dedent(f"""
        {instruction}

        Available Data Providers:
        {data}

        Available Tools:
        {tools}
        """)

    def render(self) -> str:
        return self.formatter("Analyze the provided data")

# Use it
section = DataAnalysisSection(
    context=context,  # Use Context to pass dynamic info
    tools=[ToolContext(calculate_tax)],
    CsvDataProvider("metrics.csv"),  # accepts any number of Providers
)

prompt = str(section)  # Ready for your LLM
```

## Data Providers

### File Provider
```python
from proompt.data import FileDataProvider

# Read any text file
provider = FileDataProvider("config.yaml")
content = provider.run().  # raw string content
```

**NOTE**: for structured YAML parsing, extend `DataProvider` to create `YamlProvider` class

### CSV Provider
```python
from proompt.data import CsvDataProvider

# Automatically converts CSV to markdown tables
provider = CsvDataProvider("data.csv")
table = provider.run()  # Returns formatted markdown table
```

See `proompt.data.TableData` and `proompt.data.to_markdown_table()` for conversion.

### SQLite Provider
```python
from proompt.data import SqliteProvider

# Execute SQL queries, get markdown tables
provider = SqliteProvider(
    database_path="app.db",
    query="SELECT name, email FROM users WHERE active = 1",
    table_name="users"  # Optional, for better context
)

# Async support; NOTE the async only runs sync method .run()
result = await provider.arun()
```

**NOTE**: A _true_ asynchronous method would need to be defined when extending the `DataProvider` class.

## Advanced Usage

### Custom Providers

Creating custom providers is straightforward:

```python
from proompt.base.provider import BaseProvider
import requests

class ApiProvider(BaseProvider, str):

    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key

    @property
    def name(self) -> str:
        return f"API Provider for {self.url}"

    @property
    def provider_ctx(self) -> str:
        return f"Fetches data from REST API at {self.url}"
        # NOTE: would be useful to include available endpoints

    def run(self, endpoint: str) -> str:
        response = requests.get(
            f"{self.url}/{endpoint}",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()

# Use your custom provider
api = ApiProvider("https://api.example.com", "your-key")
data = api.run("users")
```

### Data Transformation

Convert any data format to LLM-friendly markdown:

```python
from proompt.data import TableData

# From dictionaries
data = [
    {"name": "Alice", "role": "Engineer", "salary": 85000},
    {"name": "Bob", "role": "Designer", "salary": 75000}
]

table = TableData.from_dicts(data)
markdown = table.to_md()
print(markdown)
# | name  | role     | salary |
# | ----- | -------- | ------ |
# | Alice | Engineer | 85000  |
# | Bob   | Designer | 75000  |
```

## API Reference

### Core Classes

- **`BaseProvider`** - Abstract base for all data providers
- **`Context`** - Abstract base for prompt contexts
- **`ToolContext`** - Documents functions for LLM consumption
- **`PromptSection`** - Composable prompt sections
- **`BasePrompt`** - Full prompt composition

### Concrete Providers

- **`FileDataProvider`** - Read text files
- **`CsvDataProvider`** - Read CSV files as markdown tables
- **`SqliteProvider`** - Execute SQL queries as markdown tables

### Utilities

- **`TableData`** - Convert various formats to markdown tables
- **`to_markdown_table()`** - Low-level table formatting

## Why Object-Oriented Prompts?

**Better Organization**
```python
# Instead of managing giant prompt strings
SYSTEM_PROMPT = """You are an assistant..."""
DATA_SECTION = """Here is the data: {data}"""
TOOL_SECTION = """Available tools: {tools}"""

# Compose from organized, testable objects
prompt = ChatPrompt(
    SystemSection("You are an assistant..."),
    DataSection(providers=[csv_provider, db_provider]),
    ToolSection(tools=[calculator, parser])
)
```

**Easier Testing**
```python
# Test individual components
def test_csv_provider():
    provider = CsvDataProvider("test.csv")
    result = provider.run()
    assert "| Name |" in result

def test_tool_context():
    ctx = ToolContext(my_function)
    assert "my_function" in ctx.render()
```

**Reusable Components**
```python
# Define once, use everywhere
analysis_section = DataAnalysisSection(
    providers=[CsvDataProvider("metrics.csv")]
)

# Reuse in different prompts
customer_prompt = CustomerPrompt(analysis_section, ...)
admin_prompt = AdminPrompt(analysis_section, ...)
```

## Contributing

Coming soon

<!--

Proompt is designed to be extensible. Common extension points:

1. **Custom Providers** - Connect to new data sources
2. **Custom Contexts** - New ways to document tools/functions
3. **Custom Sections** - Domain-specific prompt components
4. **Custom Prompts** - Full prompt templates for specific use cases


See the [Contributing Guide](CONTRIBUTING.md) for details.
-->
