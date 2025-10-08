# pre.dev Architect API - Python Client

A Python client library for the [Pre.dev Architect API](https://docs.pre.dev). Generate comprehensive software specifications using AI-powered analysis.

## Features

- 🚀 **Fast Spec**: Generate comprehensive specifications quickly - perfect for MVPs and prototypes
- 🔍 **Deep Spec**: Generate ultra-detailed specifications for complex systems with enterprise-grade depth
- ⚡ **Async Spec**: Non-blocking async methods for long-running requests
- 📊 **Status Tracking**: Check the status of async specification generation requests
- ✨ **Type Hints**: Full type annotations for better IDE support
- 🛡️ **Error Handling**: Custom exceptions for different error scenarios

## Installation

```bash
pip install predev-api
```

## Quick Start

```python
from predev_api import PredevAPI

# Initialize the predev client with your API key
predev = PredevAPI(api_key="your_api_key_here")

# Generate a fast specification
result = predev.fast_spec(
    input_text="Build a task management app with team collaboration",
    output_format="url"
)

print(result)
```

## Authentication

The Pre.dev API uses API key authentication. Get your API key from the [pre.dev dashboard](https://pre.dev) under Settings → API Keys:

```python
predev = PredevAPI(api_key="your_api_key")
```

## API Methods

### Synchronous Methods

#### `fast_spec(input_text: str, output_format: Literal["url", "markdown"] = "url", current_context: Optional[str] = None, doc_urls: Optional[List[str]] = None) -> SpecResponse`

Generate a fast specification (30-40 seconds, 10 credits).

**Parameters:**
- `input_text` **(required)**: `str` - Description of what you want to build
- `output_format` **(optional)**: `"url" | "markdown"` - Output format (default: `"url"`)
- `current_context` **(optional)**: `str` - Existing project context
- `doc_urls` **(optional)**: `List[str]` - Documentation URLs to reference

**Returns:** `SpecResponse` object with complete specification data

**Example:**
```python
result = predev.fast_spec(
    input_text="Build a SaaS project management tool with real-time collaboration",
    output_format="url"
)
```

#### `deep_spec(input_text: str, output_format: Literal["url", "markdown"] = "url", current_context: Optional[str] = None, doc_urls: Optional[List[str]] = None) -> SpecResponse`

Generate a deep specification (2-3 minutes, 50 credits).

**Parameters:** Same as `fast_spec`

**Returns:** `SpecResponse` object with comprehensive specification data

**Example:**
```python
result = predev.deep_spec(
    input_text="Build a healthcare platform with HIPAA compliance",
    output_format="url"
)
```

### Asynchronous Methods

#### `fast_spec_async(input_text: str, output_format: Literal["url", "markdown"] = "url", current_context: Optional[str] = None, doc_urls: Optional[List[str]] = None) -> AsyncResponse`

Generate a fast specification asynchronously (returns immediately).

**Parameters:** Same as `fast_spec`

**Returns:** `AsyncResponse` object with `specId` for polling

**Example:**
```python
result = predev.fast_spec_async(
    input_text="Build a comprehensive e-commerce platform",
    output_format="url"
)
# Returns: AsyncResponse(specId="spec_123", status="pending")
```

#### `deep_spec_async(input_text: str, output_format: Literal["url", "markdown"] = "url", current_context: Optional[str] = None, doc_urls: Optional[List[str]] = None) -> AsyncResponse`

Generate a deep specification asynchronously (returns immediately).

**Parameters:** Same as `fast_spec`

**Returns:** `AsyncResponse` object with `specId` for polling

**Example:**
```python
result = predev.deep_spec_async(
    input_text="Build a fintech platform with regulatory compliance",
    output_format="url"
)
# Returns: AsyncResponse(specId="spec_456", status="pending")
```

### Status Checking

#### `get_spec_status(spec_id: str) -> SpecResponse`

Check the status of an async specification generation request.

**Parameters:**
- `spec_id` **(required)**: `str` - The specification ID from async methods

**Returns:** `SpecResponse` object with current status and data (when completed)

**Example:**
```python
status = predev.get_spec_status("spec_123")
# Returns SpecResponse with status: "pending" | "processing" | "completed" | "failed"
```

## Response Types

### `AsyncResponse`
```python
@dataclass
class AsyncResponse:
    specId: str                                    # Unique ID for polling (e.g., "spec_abc123")
    status: Literal['pending', 'processing', 'completed', 'failed']
```

### `SpecResponse`
```python
@dataclass
class SpecResponse:
    # Basic info
    _id: Optional[str] = None                      # Internal ID
    created: Optional[str] = None                  # ISO timestamp
    endpoint: Optional[Literal['fast_spec', 'deep_spec']] = None
    input: Optional[str] = None                    # Original input text
    status: Optional[Literal['pending', 'processing', 'completed', 'failed']] = None
    success: Optional[bool] = None

    # Output data (when completed)
    uploadedFileShortUrl: Optional[str] = None    # URL to input file
    uploadedFileName: Optional[str] = None        # Name of input file
    output: Optional[Any] = None                  # Raw content or URL
    outputFormat: Optional[Literal['markdown', 'url']] = None
    outputFileUrl: Optional[str] = None           # Full URL to hosted spec
    executionTime: Optional[int] = None           # Processing time in milliseconds

    # Integration URLs (when completed)
    predevUrl: Optional[str] = None               # Link to pre.dev project
    lovableUrl: Optional[str] = None              # Link to generate with Lovable
    cursorUrl: Optional[str] = None               # Link to generate with Cursor
    v0Url: Optional[str] = None                   # Link to generate with v0
    boltUrl: Optional[str] = None                 # Link to generate with Bolt

    # Error handling
    errorMessage: Optional[str] = None            # Error details if failed
    progress: Optional[str] = None                # Progress information
```

## Examples Directory

Check out the [examples directory](https://github.com/predotdev/predev-api/tree/main/predev-api-python/examples) for detailed usage examples.

## Documentation

For more information about the Pre.dev Architect API, visit:
- [API Documentation](https://docs.pre.dev)
- [pre.dev Website](https://pre.dev)

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/predotdev/predev-api).
