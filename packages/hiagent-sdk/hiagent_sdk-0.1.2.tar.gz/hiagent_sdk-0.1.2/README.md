# HiAgent SDK

A Python SDK for interacting with HiAgent Workflow API. Execute and monitor AI workflows with ease.

## Features

- **Simple API**: Easy-to-use client interface for workflow execution
- **HTTP Client**: Built on httpx for efficient HTTP requests with retry logic
- **Robust Error Handling**: Comprehensive error handling with custom exceptions
- **Type Safety**: Full type hints and Pydantic models
- **Configurable**: Flexible configuration via environment variables or parameters
- **Proxy Server**: Built-in FastAPI proxy server with API key authentication
- **Logging**: Built-in logging with loguru

## Installation

```bash
# Install from source
pip install -e .

# Or using uv (recommended for development)
uv pip install -e .
```

## Quick Start

### Basic Usage

```python
from hiagent_sdk import HiAgentClient, RunWorkflowRequest, QueryWorkflowRequest, WorkflowStatus

# Initialize client with direct parameters (Recommended)
client = HiAgentClient(
    api_key="your-api-key",
    base_url="https://hiagent-byteplus.volcenginepaas.com/api/proxy/api/v1"
)

# Create workflow request
request = RunWorkflowRequest(
    InputData={"prompt": "Your input data"},
    UserID="your_user_id",
    NoDebug=True
)

# Run workflow
response = client.run_workflow(request)
print(f"Workflow started: {response.runId}")

# Query workflow status
query_request = QueryWorkflowRequest(
    RunID=response.runId,
    UserID="your_user_id"
)
status_response = client.query_workflow(query_request)
print(f"Status: {status_response.status}")
```

### Environment Variables Configuration

```python
# Set environment variables
# HIAGENT_API_KEY="your-api-key"
# HIAGENT_BASE_URL="https://hiagent-byteplus.volcenginepaas.com/api/proxy/api/v1"
# HIAGENT_TIMEOUT=30
# HIAGENT_MAX_RETRIES=3

# Initialize client (will load from environment)
client = HiAgentClient()
```

### Advanced Usage with Polling

```python
from hiagent_sdk import HiAgentClient, RunWorkflowRequest, WorkflowStatus
import time

client = HiAgentClient(
    api_key="your-api-key",
    base_url="https://hiagent-byteplus.volcenginepaas.com/api/proxy/api/v1"
)

# Start workflow
request = RunWorkflowRequest(
    InputData={"prompt": "Create a video about space exploration"},
    UserID="user123",
    NoDebug=True
)
response = client.run_workflow(request)
print(f"Workflow started: {response.runId}")

# Wait for completion with built-in polling
final_response = client.wait_for_completion(
    execution_id=response.runId,
    user_id="user123",
    timeout=600.0,  # 10 minutes
    poll_interval=2.0  # Poll every 2 seconds
)

if final_response.status == WorkflowStatus.SUCCESS:
    print("Workflow completed successfully!")
    print(f"Output: {final_response.output}")
else:
    print(f"Workflow failed: {final_response.message}")
```

## Configuration

The SDK can be configured via environment variables or programmatically:

### Environment Variables

```bash
export HIAGENT_API_KEY="your-api-key"
export HIAGENT_BASE_URL="https://hiagent-byteplus.volcenginepaas.com/api/proxy/api/v1"
export HIAGENT_TIMEOUT=30
export HIAGENT_MAX_RETRIES=3
export HIAGENT_LOG_LEVEL=INFO
```

### Programmatic Configuration

```python
from hiagent_sdk import HiAgentClient

client = HiAgentClient(
    api_key="your-api-key",
    base_url="https://hiagent-byteplus.volcenginepaas.com/api/proxy/api/v1",
    timeout=30.0,
    max_retries=3
)
```

## Proxy Server

The SDK includes a FastAPI-based proxy server that provides API key authentication and forwards requests to the HiAgent service.

### Running the Proxy Server

```bash
# Using the run script
python run_proxy.py

# Or directly
python -m src.proxy

# With custom configuration
PROXY_HOST=0.0.0.0 PROXY_PORT=8080 python run_proxy.py
```

### Proxy Server Endpoints

- `GET /health` - Health check endpoint
- `POST /api/v1/workflow/run` - Run workflow asynchronously
- `POST /api/v1/workflow/query` - Query workflow status
- `POST /api/v1/workflow/run-sync` - Run workflow synchronously with polling

### Using the Proxy Server

```python
import requests

# Run workflow via proxy
response = requests.post(
    "http://localhost:8000/api/v1/workflow/run",
    headers={"Apikey": "your-api-key"},
    json={
        "InputData": {"prompt": "Your input"},
        "UserID": "user123",
        "NoDebug": True
    }
)

run_id = response.json()["runId"]

# Query status via proxy
status_response = requests.post(
    "http://localhost:8000/api/v1/workflow/query",
    headers={"Apikey": "your-api-key"},
    json={
        "RunID": run_id,
        "UserID": "user123"
    }
)
```

## Error Handling

The SDK provides comprehensive error handling:

```python
from hiagent_sdk import (
    HiAgentClient, 
    HiAgentClientError,
    WorkflowExecutionError, 
    WorkflowTimeoutError
)
from hiagent_sdk.utils import HTTPRequestError

client = HiAgentClient(
    api_key="your-api-key",
    base_url="https://hiagent-byteplus.volcenginepaas.com/api/proxy/api/v1"
)

try:
    request = RunWorkflowRequest(
        InputData={"prompt": "Create a video"},
        UserID="user123",
        NoDebug=True
    )
    response = client.run_workflow(request)
    
    # Wait for completion with custom timeout
    final_response = client.wait_for_completion(
        execution_id=response.runId,
        user_id="user123",
        timeout=60  # Custom timeout
    )
except WorkflowTimeoutError:
    print("Workflow execution timed out")
except WorkflowExecutionError as e:
    print(f"Workflow execution failed: {e}")
except HTTPRequestError as e:
    print(f"HTTP request failed: {e.status_code} - {e}")
except HiAgentClientError as e:
    print(f"Client error: {e}")
```

## Workflow Results

The SDK provides structured access to workflow results:

```python
from hiagent_sdk import HiAgentClient, QueryWorkflowRequest, WorkflowStatus

client = HiAgentClient()

# Query workflow result
query_request = QueryWorkflowRequest(RunID="your_run_id", UserID="user123")
result = client.query_workflow(query_request)

# Check workflow status
if result.status == WorkflowStatus.SUCCESS:
    print("Workflow completed successfully!")
    
    # Access workflow nodes
    if result.nodes:
        for node_id, node_data in result.nodes.items():
            print(f"Node {node_id}: {node_data}")
    
    # Access final output
    if result.output:
        print(f"Final output: {result.output}")
        
    # Access execution steps
    if result.steps:
        print(f"Execution steps: {result.steps}")
        
    # Access cost information
    print(f"Total cost: {result.costMs}ms, {result.costToken} tokens")

elif result.status == WorkflowStatus.FAILED:
    print(f"Workflow failed: {result.message}")
    
elif result.status == WorkflowStatus.PROCESSING:
    print("Workflow is still processing...")
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/hiagent/hiagent-sdk.git
cd hiagent-sdk

# Create virtual environment using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run integration tests
pytest -m integration
```

### Code Quality

```bash
# Format code
black src tests
isort src tests

# Lint code
flake8 src tests
mypy src

# Run all quality checks
pre-commit run --all-files
```

## API Reference

### HiAgentClient

Main client class for interacting with HiAgent API.

#### Constructor

```python
HiAgentClient(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: Optional[float] = None,
    max_retries: Optional[int] = None,
    user_id: Optional[str] = None
)
```

#### Methods

- `run_workflow(request: RunWorkflowRequest) -> RunWorkflowResponse`: Start workflow execution
- `query_workflow(request: QueryWorkflowRequest) -> QueryWorkflowResponse`: Query workflow status
- `wait_for_completion(execution_id: str, user_id: str = "", timeout: Optional[float] = None, poll_interval: Optional[float] = None) -> QueryWorkflowResponse`: Wait for workflow completion with polling

### Models

#### WorkflowStatus
- `PENDING`: Workflow is pending execution
- `PROCESSING`: Workflow is currently running
- `SUCCESS`: Workflow completed successfully
- `FAILED`: Workflow execution failed

#### NodeStatus
- `TO_START`: Node is waiting to start
- `PROCESSING`: Node is currently processing
- `SUCCESS`: Node completed successfully
- `FAILED`: Node execution failed
- `STOPPED`: Node execution was stopped

#### NodeType
- `REMOTE_TOOL`: Remote tool execution node
- `PY`: Python code execution node
- `LOOP`: Loop control node
- `START`: Workflow start node
- `LLM`: Large Language Model node
- `END`: Workflow end node
- `BATCH`: Batch processing node
- `CONDITION`: Conditional logic node
- `VARIABLES_MERGE`: Variable merging node
- `HTTP_REQUEST`: HTTP request node

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Documentation: [https://hiagent-sdk.readthedocs.io](https://hiagent-sdk.readthedocs.io)
- Issues: [https://github.com/hiagent/hiagent-sdk/issues](https://github.com/hiagent/hiagent-sdk/issues)
- Discussions: [https://github.com/hiagent/hiagent-sdk/discussions](https://github.com/hiagent/hiagent-sdk/discussions)