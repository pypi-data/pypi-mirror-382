"""HiAgent SDK - Python SDK for HiAgent Workflow API.

This SDK provides a comprehensive interface for interacting with HiAgent
workflows, including execution, monitoring, and result parsing.

Example usage:
    from hiagent_sdk import HiAgentClient, WorkflowStatus
    
    # Initialize client with direct parameters (Recommended)
    client = HiAgentClient(
        api_key="your-api-key",
        base_url="https://api.hiagent.com"
    )
    
    # Execute workflow
    response = client.execute_workflow(
        workflow_id="my_workflow",
        inputs={"prompt": "Create a video about cats"}
    )
    
    # Get results
    if response.status == WorkflowStatus.COMPLETED:
        result = client.get_workflow_result(response.execution_id)
        video_data = client.get_final_video(response.execution_id)
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
from .utils import HTTPClient, HTTPClientError, HTTPRequestError

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
    "IntermediateStageType",
    
    # Workflow models - Data structures
    "NodeExecutionInfo",
    "LoopBlockHistory",
    "WorkflowNode",
    "WorkflowResult",
    "ImageLibraryItem",
    "ImageLibraryData",
    "StoryBoardFrame", 
    "StoryBoardData",
    "VideoCandidatesData",
    "FinalVideoData",
    "IntermediateStage",
    
    # Workflow models - Request/Response
    "RunWorkflowRequest",
    "RunWorkflowResponse",
    "QueryWorkflowRequest", 
    "QueryWorkflowResponse",
    
    # Node mapping
    "NodeMapping",
    "DEFAULT_NODE_MAPPING",
    "PRODUCTION_NODE_MAPPING",
    "get_node_description",
    "get_stage_priority_nodes", 
    "is_image_library_node",
    "is_story_board_node",
    "is_video_candidates_node",
    "is_final_video_node",
    
    # Parser
    "WorkflowParser",
    
    # Utilities
    "HTTPClient",
    "HTTPClientError",
    "HTTPRequestError", 
    "with_retry",
    "RetryableOperation",
]