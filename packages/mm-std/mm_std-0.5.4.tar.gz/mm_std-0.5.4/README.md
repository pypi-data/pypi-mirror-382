# mm-std

A collection of Python utilities for common data manipulation tasks with strict type safety and modern Python support.

## Features

- **JSON Utilities**: Extended JSON encoder with support for datetime, UUID, Decimal, dataclasses, enums, and Pydantic models
- **Dictionary Utilities**: Advanced dictionary manipulation with type preservation
- **Date Utilities**: UTC-focused datetime operations and flexible date parsing
- **Random Utilities**: Type-safe random generation for decimals and datetimes
- **String Utilities**: Efficient string matching utilities for prefixes, suffixes, and substrings, plus multiline text parsing
- **Subprocess Utilities**: Safe shell command execution with comprehensive result handling
- **Full Type Safety**: Strict mypy compliance with comprehensive type annotations

## Quick Start

### String Utilities

Efficient string matching for common patterns:

```python
from mm_std import str_starts_with_any, str_ends_with_any, str_contains_any

# Check URL protocols
url = "https://example.com"
is_web_url = str_starts_with_any(url, ["http://", "https://"])  # True

# Check file extensions
filename = "document.pdf"
is_document = str_ends_with_any(filename, [".pdf", ".doc", ".docx"])  # True

# Check log levels in messages
log_message = "ERROR: Database connection failed"
has_error = str_contains_any(log_message, ["ERROR", "CRITICAL", "FATAL"])  # True

# All functions accept any iterable
prefixes = ("admin_", "super_", "root_")
username = "admin_john"
is_privileged = str_starts_with_any(username, prefixes)  # True
```

Parse multiline text into cleaned lines:

```python
from mm_std import parse_lines

# Basic line parsing
text = """
line1
line2
   line3

line4
"""
lines = parse_lines(text)  # ["line1", "line2", "line3", "line4"]

# Advanced parsing with options
config_text = """
DEBUG=true # Enable debug mode
HOST=localhost
PORT=8080 # Application port
# This is a comment
DEBUG=true # Duplicate line
"""

# Parse with all options
parsed = parse_lines(
    config_text,
    lowercase=True,        # Convert to lowercase
    remove_comments=True,  # Remove everything after '#'
    deduplicate=True       # Remove duplicates, preserve order
)
# Result: ["debug=true", "host=localhost", "port=8080"]
```

### Subprocess Utilities

Execute shell commands safely with comprehensive result handling:

```python
from mm_std import shell, ssh_shell, ShellResult

# Execute local commands
result = shell("ls -la /tmp")
print(f"Exit code: {result.code}")
print(f"Output: {result.stdout}")
print(f"Errors: {result.stderr}")
print(f"Combined: {result.combined_output}")

# Handle command errors gracefully
result = shell("grep 'pattern' nonexistent.txt")
if result.code != 0:
    print(f"Command failed: {result.stderr}")

# Execute with timeout
result = shell("long-running-command", timeout=30)
if result.code == 255:  # TIMEOUT_EXIT_CODE
    print("Command timed out")

# Echo commands for debugging
result = shell("echo 'Hello World'", echo_command=True)

# Complex shell operations with pipes
result = shell("ps aux | grep python | wc -l")
python_processes = int(result.stdout.strip())

# Execute commands on remote hosts via SSH
ssh_result = ssh_shell(
    host="server.example.com",
    cmd="systemctl status nginx",
    ssh_key_path="~/.ssh/id_rsa",
    timeout=10
)

# SSH commands are automatically quoted for security
ssh_result = ssh_shell(
    "server.example.com",
    "echo 'hello world; ls -la'",  # Properly escaped
    echo_command=True
)
```

### JSON Utilities

Extended JSON serialization with automatic handling of Python types:

```python
from mm_std import json_dumps, ExtendedJSONEncoder
from datetime import datetime
from decimal import Decimal
from uuid import UUID

data = {
    "timestamp": datetime.now(),
    "price": Decimal("19.99"),
    "user_id": UUID("12345678-1234-5678-1234-567812345678"),
    "tags": {"python", "json"}  # set will be converted to list
}

# Simple serialization
json_str = json_dumps(data)

# Custom type handlers for specific use cases
json_str = json_dumps(data, type_handlers={
    Decimal: lambda d: float(d)  # Convert Decimal to float instead of string
})
```

### Dictionary Utilities

Clean up dictionaries by replacing or removing empty values:

```python
from mm_std import replace_empty_dict_entries

data = {
    "name": "John",
    "age": None,
    "email": "",
    "score": 0,
    "active": False
}

# Remove empty entries entirely
cleaned = replace_empty_dict_entries(data)
# Result: {"name": "John"}

# Replace with defaults
defaults = {"age": 25, "email": "unknown@example.com"}
cleaned = replace_empty_dict_entries(data, defaults=defaults)
# Result: {"name": "John", "age": 25, "email": "unknown@example.com"}

# Treat zero and false as empty too
cleaned = replace_empty_dict_entries(
    data,
    defaults=defaults,
    treat_zero_as_empty=True,
    treat_false_as_empty=True
)
```

### Date Utilities

UTC-focused datetime operations:

```python
from mm_std import utc_now, utc_delta, parse_date

# Current UTC time
now = utc_now()

# Time calculations
past = utc_delta(hours=-2, minutes=-30)
future = utc_delta(days=7)

# Flexible date parsing
dates = [
    "2023-12-25",
    "2023-12-25T10:30:00Z",
    "2023-12-25 10:30:00.123456+00:00",
    "2023/12/25"
]

parsed_dates = [parse_date(d) for d in dates]

# Parse and ignore timezone info
local_time = parse_date("2023-12-25T10:30:00+02:00", ignore_tz=True)
```

### Random Utilities

Generate random values with precision:

```python
from mm_std import random_decimal, random_datetime
from decimal import Decimal
from datetime import datetime

# Random decimal with preserved precision
price = random_decimal(Decimal("10.00"), Decimal("99.99"))

# Random datetime within a range
base_time = datetime.now()
random_time = random_datetime(
    base_time,
    hours=24,      # Up to 24 hours later
    minutes=30,    # Plus up to 30 minutes
    seconds=45     # Plus up to 45 seconds
)
```
