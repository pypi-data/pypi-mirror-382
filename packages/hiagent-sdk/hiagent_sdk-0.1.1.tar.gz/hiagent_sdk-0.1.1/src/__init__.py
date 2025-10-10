"""HiAgent SDK - Python SDK for HiAgent Workflow API.

This SDK provides a comprehensive interface for interacting with HiAgent
workflows, including execution, monitoring, and result parsing.

Example usage:
    from hiagent_sdk import HiAgentClient, WorkflowStatus, RunWorkflowRequest
    
    # Initialize client with direct parameters (Recommended)
    client = HiAgentClient(
        api_key="your-api-key",
        base_url="https://hiagent-byteplus.volcenginepaas.com/api/proxy/api/v1"
    )
    
    # Create and run workflow
    request = RunWorkflowRequest(
        InputData={"prompt": "Create a video about cats"},
        UserID="user123",
        NoDebug=True
    )
    response = client.run_workflow(request)
    
    # Wait for completion
    result = client.wait_for_completion(response.runId, "user123")
    if result.status == WorkflowStatus.SUCCESS:
        print(f"Workflow completed: {result.output}")
"""

# Main client interface
from .client import HiAgentClient, HiAgentClientError, WorkflowExecutionError, WorkflowTimeoutError

# Models
from .models.workflow import (
    # Enums
    NodeStatus, WorkflowStatus, NodeType,
    
    # Data models
    NodeExecutionInfo, LoopBlockHistory, WorkflowNode, WorkflowResult,
    
    # Request/Response models
    RunWorkflowRequest, RunWorkflowResponse,
    QueryWorkflowRequest, QueryWorkflowResponse
)

# Utilities (for advanced usage)
from .utils.http_client import HTTPClient, HTTPClientError, HTTPRequestError

__version__ = "0.1.0"

__all__ = [
    # Main interface
    "HiAgentClient",
    "HiAgentClientError", 
    "WorkflowExecutionError",
    "WorkflowTimeoutError",
    
    # Workflow models - Enums
    "NodeStatus",
    "WorkflowStatus", 
    "NodeType",
    
    # Workflow models - Data structures
    "NodeExecutionInfo",
    "LoopBlockHistory",
    "WorkflowNode",
    "WorkflowResult",
    
    # Workflow models - Request/Response
    "RunWorkflowRequest",
    "RunWorkflowResponse",
    "QueryWorkflowRequest", 
    "QueryWorkflowResponse",
    
    # Utilities
    "HTTPClient",
    "HTTPClientError",
    "HTTPRequestError",
]