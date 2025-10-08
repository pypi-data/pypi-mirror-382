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
    uploadedFileShortUrl: Optional[str] = None    # Short URL to hosted spec
    uploadedFileName: Optional[str] = None        # Filename
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

Check out the [examples directory](./examples) for detailed usage examples.

## API Reference

### `PredevAPI`

Main client class for interacting with the Pre.dev API.

#### Constructor

```python
PredevAPI(api_key: str, base_url: str = "https://api.pre.dev")
```

**Parameters:**
- `api_key` (str): Your API key from pre.dev settings
- `base_url` (str): Base URL for the API (default: "https://api.pre.dev")

#### Methods

##### `fast_spec(input_text: str, output_format: Literal["url", "markdown"] = "url", current_context: Optional[str] = None, doc_urls: Optional[List[str]] = None) -> SpecResponse`

Generate a fast specification (30-40 seconds, 10 credits).

**Parameters:**
- `input_text` (str, **required**): Description of what you want to build
- `output_format` (str, optional): Output format
  - `"url"` (default): Returns hosted URL to view the spec
  - `"markdown"`: Returns raw markdown content in response
- `current_context` (str, optional): Existing project/codebase context
  - **When omitted**: Generates full new project spec with setup, deployment, docs, maintenance (`isNewBuild: true`)
  - **When provided**: Generates feature addition spec for existing project (`isNewBuild: false`)
- `doc_urls` (List[str], optional): Array of documentation URLs that Architect will reference when generating specifications (e.g., API docs, design systems)

**Returns:** `SpecResponse`:

**Synchronous Response (`SpecResponse`):**
```python
SpecResponse(
    _id="spec_abc123",
    created="2024-01-01T00:00:00Z",
    endpoint="fast_spec",
    input="Build a task management app",
    status="completed",
    success=True,
    uploadedFileShortUrl="https://api.pre.dev/s/a123112",
    uploadedFileName="rfp.md",
    output="https://api.pre.dev/s/a6hFJRV6",
    outputFormat="url",
    outputFileUrl="https://api.pre.dev/s/a6hFJRV6",
    executionTime=35000,
    predevUrl="https://pre.dev/projects/abc123",
    lovableUrl="https://lovable.dev/?autosubmit=true#prompt=First%20download%20https%3A%2F%2Fapi.pre.dev%2Fs%2Fa6hFJRV6%2C%20then%20save%20it%20to%20a%20file%20called%20%22spec.md%22%20and%20then%20parse%20it%20and%20implement%20it%20step%20by%20step",
    cursorUrl="cursor://anysphere.cursor-deeplink/prompt?text=First+download+https%3A%2F%2Fapi.pre.dev%2Fs%2Fa6hFJRV6%2C+then+save+it+to+a+file+called+%22spec.md%22+and+then+parse+it+and+implement+it+step+by+step",
    v0Url="https://v0.dev/chat?q=First%20download%20https%3A%2F%2Fapi.pre.dev%2Fs%2Fa6hFJRV6%2C%20then%20save%20it%20to%20a%20file%20called%20%22spec.md%22%20and%20then%20parse%20it%20and%20implement%20it%20step%20by%20step",
    boltUrl="https://bolt.new?prompt=First%20download%20https%3A%2F%2Fapi.pre.dev%2Fs%2Fa6hFJRV6%2C%20then%20save%20it%20to%20a%20file%20called%20%22spec.md%22%20and%20then%20parse%20it%20and%20implement%20it%20step%20by%20step",
    errorMessage=None,
    progress="Completed"
)
```

**Async Response (`AsyncSpecResponse`):**
```python
AsyncSpecResponse(
    specId="spec_abc123",
    status="pending"
)
```

**Cost:** 10 credits per request

**Use Cases:** MVPs, prototypes, rapid iteration

**What's Generated:**
- ✅ Executive summary
- ✅ Feature breakdown by category
- ✅ Technical architecture recommendations
- ✅ Implementation milestones with effort estimates
- ✅ User stories and acceptance criteria
- ✅ Task checklist with progress tracking (`[ ]` → `[→]` → `[✓]` → `[⊘]`)
- ✅ Risk analysis and considerations

**Example - New Project:**
```python
result = predev.fast_spec(
    input_text="Build a SaaS project management tool with team collaboration",
    output_format="url"
)
# Returns: isNewBuild=True, includes setup and deployment
```

**Example - Feature Addition:**
```python
result = predev.fast_spec(
    input_text="Add calendar view and Gantt chart visualization",
    current_context="Existing task management system with list/board views, auth, team features",
    output_format="url"
)
# Returns: isNewBuild=False, focuses only on new features
```

**Example - With Documentation URLs:**
```python
result = predev.fast_spec(
    input_text="Build a customer support ticketing system",
    doc_urls=["https://docs.pre.dev", "https://docs.stripe.com"],
    output_format="markdown"
)
```

**Raises:**
- `AuthenticationError`: If authentication fails
- `RateLimitError`: If rate limit is exceeded
- `PredevAPIError`: For other API errors

##### `deep_spec(input_text: str, output_format: Literal["url", "markdown"] = "url", current_context: Optional[str] = None, doc_urls: Optional[List[str]] = None) -> SpecResponse`

Generate a deep specification (2-3 minutes, 25 credits).

**Parameters:**
- `input_text` (str, **required**): Description of what you want to build
- `output_format` (str, optional): Output format - `"url"` (default) or `"markdown"`
- `current_context` (str, optional): Existing project/codebase context
  - **When omitted**: Full new project spec (`isNewBuild: true`)
  - **When provided**: Feature addition spec (`isNewBuild: false`)
- `doc_urls` (List[str], optional): Documentation URLs for reference

**Returns:** `SpecResponse`

**Cost:** 50 credits per request

**Use Cases:** Complex systems, comprehensive planning

**What's Generated:** Same as fast_spec but with:
- 📊 More detailed architecture diagrams and explanations
- 🔍 Deeper technical analysis
- 📈 More comprehensive risk assessment
- 🎯 More granular implementation steps
- 🏗️ Advanced infrastructure recommendations

**Example:**
```python
result = predev.deep_spec(
    input_text="Build a resource planning (ERP) system",
    doc_urls=["https://company-docs.com/architecture"],
    output_format="url"
)
```

**Raises:**
- `AuthenticationError`: If authentication fails
- `RateLimitError`: If rate limit is exceeded
- `PredevAPIError`: For other API errors

##### `fast_spec_async(input_text: str, output_format: Literal["url", "markdown"] = "url", current_context: Optional[str] = None, doc_urls: Optional[List[str]] = None) -> AsyncResponse`

Generate a fast specification asynchronously (30-40 seconds, 10 credits).

**Parameters:**
- `input_text` (str, **required**): Description of what you want to build
- `output_format` (str, optional): Output format - `"url"` (default) or `"markdown"`
- `current_context` (str, optional): Existing project/codebase context
- `doc_urls` (List[str], optional): Documentation URLs for reference

**Returns:** `AsyncResponse` with specId for polling:
```python
AsyncResponse(
    specId="spec_abc123",
    status="pending"
)
```

**Cost:** 10 credits per request

**Example:**
```python
result = predev.fast_spec_async(
    input_text="Build a task management app",
    output_format="url"
)
# Use result.specId with get_spec_status() to check progress
```

**Raises:**
- `AuthenticationError`: If authentication fails
- `RateLimitError`: If rate limit is exceeded
- `PredevAPIError`: For other API errors

##### `deep_spec_async(input_text: str, output_format: Literal["url", "markdown"] = "url", current_context: Optional[str] = None, doc_urls: Optional[List[str]] = None) -> AsyncResponse`

Generate a deep specification asynchronously (2-3 minutes, 25 credits).

**Parameters:**
- `input_text` (str, **required**): Description of what you want to build
- `output_format` (str, optional): Output format - `"url"` (default) or `"markdown"`
- `current_context` (str, optional): Existing project/codebase context
- `doc_urls` (List[str], optional): Documentation URLs for reference

**Returns:** `AsyncResponse` with specId for polling:
```python
AsyncResponse(
    specId="spec_abc123",
    status="pending"
)
```

**Cost:** 50 credits per request

**Example:**
```python
result = predev.deep_spec_async(
    input_text="Build an ERP system",
    output_format="url"
)
# Use result.specId with get_spec_status() to check progress
```

**Raises:**
- `AuthenticationError`: If authentication fails
- `RateLimitError`: If rate limit is exceeded
- `PredevAPIError`: For other API errors

##### `get_spec_status(spec_id: str) -> SpecResponse`

Get the status of a specification generation request (for async requests).

**Parameters:**
- `spec_id` (str): The ID of the specification request

**Returns:** `SpecResponse` with status information:
```python
SpecResponse(
    _id="spec_abc123",
    created="2024-01-01T00:00:00Z",
    endpoint="fast_spec",
    input="Build a task management app",
    status="completed",
    success=True,
    uploadedFileShortUrl="https://pre.dev/s/abc123",
    uploadedFileName="spec.md",
    output="https://pre.dev/s/abc123",
    outputFormat="url",
    outputFileUrl="https://pre.dev/s/abc123",
    executionTime=35000,
    predevUrl="https://pre.dev/s/abc123",
    lovableUrl="https://lovable.dev/?autosubmit=true#prompt=First%20download%20https%3A%2F%2Fapi.pre.dev%2Fs%2Fa6hFJRV6%2C%20then%20save%20it%20to%20a%20file%20called%20%22spec.md%22%20and%20then%20parse%20it%20and%20implement%20it%20step%20by%20step",
    cursorUrl="cursor://anysphere.cursor-deeplink/prompt?text=First+download+https%3A%2F%2Fapi.pre.dev%2Fs%2Fa6hFJRV6%2C+then+save+it+to+a+file+called+%22spec.md%22+and+then+parse+it+and+implement+it+step+by+step",
    v0Url="https://v0.dev/chat?q=First%20download%20https%3A%2F%2Fapi.pre.dev%2Fs%2Fa6hFJRV6%2C%20then%20save%20it%20to%20a%20file%20called%20%22spec.md%22%20and%20then%20parse%20it%20and%20implement%20it%20step%20by%20step",
    boltUrl="https://bolt.new?prompt=First%20download%20https%3A%2F%2Fapi.pre.dev%2Fs%2Fa6hFJRV6%2C%20then%20save%20it%20to%20a%20file%20called%20%22spec.md%22%20and%20then%20parse%20it%20and%20implement%20it%20step%20by%20step",
    errorMessage=None,
    progress="Completed"
)
```

**Raises:**
- `AuthenticationError`: If authentication fails
- `PredevAPIError`: For other API errors

### Output Formats

#### URL Format (`output_format="url"`)
Returns a hosted URL where you can view the specification in a formatted interface:
```python
SpecResponse(
    output="https://pre.dev/s/abc123",
    outputFormat="url",
    outputFileUrl="https://pre.dev/s/abc123",
    predevUrl="https://pre.dev/s/abc123",
    lovableUrl="https://lovable.dev/s/abc123",
    cursorUrl="https://cursor.sh/s/abc123",
    v0Url="https://v0.dev/s/abc123",
    boltUrl="https://bolt.new/s/abc123"
)
```

#### Markdown Format (`output_format="markdown"`)
Returns the raw markdown content directly in the response:
```python
SpecResponse(
    output="# Project Specification\n\n## Executive Summary...",
    outputFormat="markdown",
    outputFileUrl="https://pre.dev/s/abc123"
)
```

**Fast Spec Markdown Example:**
```markdown
### - [ ] **Milestone 1**: User authentication and profile management

- [ ] **User Registration** - (M): As a: new user, I want to: register an account with email and password, So that: I can access the platform
  - **Acceptance Criteria:**
    - [ ] User can register with valid email and password
    - [ ] Email verification sent upon registration
    - [ ] Duplicate emails handled gracefully
    - [ ] Password strength requirements enforced

- [ ] **User Login** - (S): As a: registered user, I want to: log in securely, So that: I can access my account
  - **Acceptance Criteria:**
    - [ ] User can log in with correct credentials
    - [ ] Invalid credentials rejected with clear message
    - [ ] Session persists across browser tabs
    - [ ] Password reset option available

- [ ] **User Profile** - (M): As a: registered user, I want to: manage my profile, So that: I can update my information
  - **Acceptance Criteria:**
    - [ ] User can view and edit profile details
    - [ ] Shipping addresses can be saved
    - [ ] Password can be changed with re-authentication
    - [ ] Account can be deactivated
```

**Deep Spec Markdown Example (includes subtasks):**
```markdown
### - [ ] **Milestone 2**: User authentication and profile management

- [ ] **User Registration** - (M): As a: new user, I want to: register an account with email and password, So that: I can access the platform
  - **Acceptance Criteria:**
    - [ ] User can register with valid email and password
    - [ ] Email verification sent upon registration
    - [ ] Duplicate emails handled gracefully
    - [ ] Password strength requirements enforced
  - [ ] DB: Create/verify table_users migration - (M)
  - [ ] Infra: Configure Clerk (external_clerk) & auth settings - (M)
  - [ ] FE: Implement /RegisterPage UI comp_registerPage_mainForm - (M)
  - [ ] FE: Add client-side validation & reCAPTCHA on register form - (M)
  - [ ] API: Implement registerWithEmail mutation in router_route_registerPage - (M)
  - [ ] Backend: Create user record in table_users and auth_methods - (M)
  - [ ] Integration: Connect API to Clerk for email confirmation/session - (M)
  - [ ] QA: Write unit and integration tests for registration flow - (M)
  - [ ] Docs: Document registration API and front-end behavior - (M)

- [ ] **Password Reset** - (M): As a: registered user, I want to: reset my password securely, So that: I can regain access
  - **Acceptance Criteria:**
    - [ ] User can request password reset link via valid email
    - [ ] Reset link expires after a defined period
    - [ ] New password must meet strength requirements
    - [ ] System invalidates existing sessions after password change
  - [ ] DB: Create password_resets table migration - (M)
  - [ ] API: Implement requestPasswordReset mutation (validate, create token) - (M)
  - [ ] API: Implement verifyResetToken and finalizeReset mutation - (M)
  - [ ] Frontend: Add Password Reset Request page (/auth/password-reset) - (M)
  - [ ] Frontend: Add Password Reset Form page (/auth/reset?token=) - (M)
  - [ ] Auth Integration: Wire Clerk for account lookup and session invalidation - (M)
  - [ ] Infra: Email service integration and template for reset link - (M)
  - [ ] Security: Add reCAPTCHA and rate limiting to request endpoint - (M)
  - [ ] Testing: End-to-end tests for reset flow - (M)
  - [ ] Docs: Document API, pages, and operational runbook - (M)
```

**Key Differences:**
- **Fast Spec**: Milestones → User Stories with Acceptance Criteria
- **Deep Spec**: Milestones → User Stories → Granular Subtasks (DB, API, FE, QA, Docs)
- Complexity estimates: (XS, S, M, L, XL)

### Task Status Legend

Task status legend: `[ ]` → `[→]` → `[✓]` → `[⊘]`

Update as your agent completes work to keep both you and AI aligned on progress.

## Error Handling

The library provides custom exceptions for different error scenarios:

```python
from predev_api import PredevAPI, PredevAPIError, AuthenticationError, RateLimitError, SpecResponse, AsyncSpecResponse

predev = PredevAPI(api_key="your_api_key")

try:
    result = predev.fast_spec(
        input_text="Build a mobile app",
        async_mode=True
    )
    
    # Type-safe response handling
    if isinstance(result, AsyncSpecResponse):
        print(f"Async request started: {result.specId}")
        
        # Poll for status
        status = predev.get_spec_status(result.specId)
        if isinstance(status, SpecResponse):
            print(f"Status: {status.status}")
            if status.status == 'completed':
                print(f"Output: {status.output}")
    else:
        # Synchronous response
        print(f"Sync response: {result.output}")
        
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except PredevAPIError as e:
    print(f"API error: {e}")
```

## Requirements

- Python 3.8 or higher
- requests >= 2.25.0

## Development & Testing

### Running Tests

The package includes a comprehensive test suite using pytest. To run the tests:

```bash
# Install dependencies (including test dependencies)
pip install -r requirements.txt

# Run all tests
python -m pytest

# Run tests with coverage report
python -m pytest --cov=predev_api --cov-report=term-missing

# Run tests in verbose mode
python -m pytest -v
```

### Test Coverage

The test suite covers:
- Client initialization and authentication
- Fast spec generation
- Deep spec generation  
- Spec status checking
- Error handling (authentication errors, rate limits, API errors)
- Custom exceptions

Current test coverage: **94%**

## Documentation

For more information about the Pre.dev Architect API, visit:
- [API Documentation](https://docs.pre.dev)
- [Pre.dev Website](https://pre.dev)


## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/predotdev/predev-api).
