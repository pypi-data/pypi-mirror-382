# pre.dev Architect API - Python Client

A Python client library for the [Pre.dev Architect API](https://docs.pre.dev). Generate comprehensive software specifications using AI-powered analysis.

## Features

- 🚀 **Fast Spec**: Generate comprehensive specifications quickly - perfect for MVPs and prototypes
- 🔍 **Deep Spec**: Generate ultra-detailed specifications for complex systems with enterprise-grade depth
- 📊 **Status Tracking**: Check the status of async specification generation requests
- 🔒 **Enterprise Support**: Both solo and enterprise authentication methods
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

## Usage

### Fast Spec Generation

Generate comprehensive specifications quickly, ideal for MVPs and prototypes:

```python
from predev_api import PredevAPI

predev = PredevAPI(api_key="your_api_key")

result = predev.fast_spec(
    input_text="Build a task management app with team collaboration features",
    output_format="url"  # or "markdown"
)

print(result)
```

### Deep Spec Generation

Generate ultra-detailed specifications for complex systems with enterprise-grade depth:

```python
from predev_api import PredevAPI

predev = PredevAPI(api_key="your_api_key")

result = predev.deep_spec(
    input_text="Build an enterprise resource planning system with inventory, finance, and HR modules",
    output_format="url"  # or "markdown"
)

print(result)
```

### Check Specification Status

For async requests, check the status of your specification generation:

```python
from predev_api import PredevAPI

predev = PredevAPI(api_key="your_api_key")

status = predev.get_spec_status(spec_id="your_spec_id")
print(status)
```

## Examples

Check out the [examples directory](./examples) for more detailed usage examples:

- `fast_spec_example.py` - Generate fast specifications
- `deep_spec_example.py` - Generate deep specifications
- `get_status_example.py` - Check specification status

To run the examples:

```bash
# Set your API key
export PREDEV_API_KEY="your_api_key_here"

# Run an example
python examples/fast_spec_example.py
```

## API Reference

### `PredevAPI`

Main client class for interacting with the Pre.dev API.

#### Constructor

```python
PredevAPI(api_key: str, enterprise: bool = False, base_url: str = "https://api.pre.dev")
```

**Parameters:**
- `api_key` (str): Your API key from pre.dev settings
- `enterprise` (bool): Whether to use enterprise authentication (default: False)
- `base_url` (str): Base URL for the API (default: "https://api.pre.dev")

#### Methods

##### `fast_spec(input_text: str, output_format: Literal["url", "markdown"] = "url", current_context: Optional[str] = None, doc_urls: Optional[List[str]] = None, async_mode: bool = False) -> Union[SpecResponse, AsyncSpecResponse]`

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
- `async_mode` (bool, optional): If True, returns immediately with specId for polling

**Returns:** Either `SpecResponse` or `AsyncSpecResponse`:

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

##### `deep_spec(input_text: str, output_format: Literal["url", "markdown"] = "url", current_context: Optional[str] = None, doc_urls: Optional[List[str]] = None, async_mode: bool = False) -> Union[SpecResponse, AsyncSpecResponse]`

Generate a deep specification (2-3 minutes, 25 credits) with enterprise-grade depth.

**Parameters:**
- `input_text` (str, **required**): Description of what you want to build
- `output_format` (str, optional): Output format - `"url"` (default) or `"markdown"`
- `current_context` (str, optional): Existing project/codebase context
  - **When omitted**: Full new project spec (`isNewBuild: true`)
  - **When provided**: Feature addition spec (`isNewBuild: false`)
- `doc_urls` (List[str], optional): Documentation URLs for reference
- `async_mode` (bool, optional): If True, returns immediately with specId for polling

**Returns:** Same structure as `fast_spec()` - either `SpecResponse` or `AsyncSpecResponse`

**Cost:** 50 credits per request

**Use Cases:** Complex systems, enterprise applications, comprehensive planning

**What's Generated:** Same as fast_spec but with:
- 📊 More detailed architecture diagrams and explanations
- 🔍 Deeper technical analysis
- 📈 More comprehensive risk assessment
- 🎯 More granular implementation steps
- 🏗️ Advanced infrastructure recommendations

**Example:**
```python
result = predev.deep_spec(
    input_text="Build an enterprise resource planning (ERP) system",
    doc_urls=["https://company-docs.com/architecture"],
    output_format="url"
)
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

### Async Mode

For long-running requests, you can use async mode to avoid timeouts:

```python
from predev_api import PredevAPI, AsyncSpecResponse, SpecResponse

# Start async request
async_response = predev.fast_spec(
    input_text="Build a complex enterprise system",
    async_mode=True
)

print(async_response.specId)  # "spec_abc123"

# Poll for status
status = predev.get_spec_status(async_response.specId)
print(status.status)  # "pending" | "processing" | "completed" | "failed"

# When completed, the status response will contain the full spec data
if status.status == 'completed':
    print(status.output)  # The generated specification
```

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
- Client initialization with solo and enterprise authentication
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
