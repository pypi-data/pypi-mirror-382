"""
Workflow models for HiAgent SDK.

This module contains all data models and type definitions for workflow operations.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, RootModel
from enum import Enum


class NodeStatus(str, Enum):
    """Node execution status enumeration"""
    TO_START = "to_start"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    STOPPED = "stopped"


class WorkflowStatus(str, Enum):
    """Workflow execution status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class NodeType(str, Enum):
    """Node type enumeration"""
    REMOTE_TOOL = "remote_tool"
    PY = "py"
    LOOP = "loop"
    START = "start"
    LLM = "llm"
    END = "end"
    BATCH = "batch"
    CONDITION = "condition"
    VARIABLES_MERGE = "variables_merge"
    HTTP_REQUEST = "http_request"


class NodeExecutionInfo(BaseModel):
    """Node execution information"""
    input: Optional[str] = None
    output: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None
    costMs: Optional[int] = None
    costToken: Optional[int] = None
    nodeType: Optional[str] = None


class LoopBlockHistory(RootModel[Dict[str, NodeExecutionInfo]]):
    """Loop block history - dictionary format with node ID as key and execution info as value"""
    root: Dict[str, NodeExecutionInfo]


class WorkflowNode(BaseModel):
    """Workflow node model"""
    input: str  # JSON string format input data
    output: str  # JSON string format output data
    status: NodeStatus
    message: str
    costMs: int
    costToken: int
    nodeType: NodeType
    loopBlock: Optional[Dict[str, Any]] = None
    loopBlockHistories: Optional[List] = None


class WorkflowResult(BaseModel):
    """Workflow execution result model"""
    runId: str
    status: WorkflowStatus
    nodes: Dict[str, WorkflowNode]
    steps: List[str]  # Node execution order
    costMs: int
    costToken: int
    output: Optional[str] = None


# API Request/Response models
class RunWorkflowRequest(BaseModel):
    """Run workflow request model"""
    InputData: Dict  # JSON string format input parameters
    UserID: str     # User identifier
    NoDebug: Optional[bool] = True  # Non-debug mode flag


class RunWorkflowResponse(BaseModel):
    """Run workflow response model"""
    runId: str  # Async execution task ID


class QueryWorkflowRequest(BaseModel):
    """Query workflow progress request model"""
    RunID: str   # Workflow execution task ID
    UserID: str  # User identifier


class QueryWorkflowResponse(BaseModel):
    """Query workflow progress response model"""
    runId: Optional[str] = None
    status: Optional[str] = None
    nodes: Optional[Dict[str, Dict[str, Any]]] = None
    steps: Optional[List[str]] = None
    code: Optional[int] = None
    message: Optional[str] = None
    costMs: Optional[int] = None
    output: Optional[str] = None
    lastInterruptedNodeId: Optional[str] = None
    checkpointExpireTimestamp: Optional[int] = None
    msg: Optional[str] = None
    costToken: Optional[int] = None
    parsed_output: Optional[Dict] = None