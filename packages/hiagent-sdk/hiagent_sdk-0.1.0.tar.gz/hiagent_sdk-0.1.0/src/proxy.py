"""
HiAgent Proxy Server.

This module provides a FastAPI-based proxy server that accepts API key authentication
and forwards workflow requests to the HiAgent service.
"""

import os
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Header, status
from loguru import logger

from src.models.workflow import RunWorkflowRequest, RunWorkflowResponse, QueryWorkflowRequest, QueryWorkflowResponse
from src.client import HiAgentClient, HiAgentClientError, WorkflowExecutionError, WorkflowTimeoutError


# Initialize FastAPI app
app = FastAPI(
    title="HiAgent Proxy Server",
    description="Proxy server for HiAgent workflow API with API key authentication",
    version="1.0.0"
)

# Global client instance (will be initialized with environment variables)
hiagent_client: Optional[HiAgentClient] = None


def get_api_key(apikey: str = Header(..., alias="Apikey")) -> str:
    """
    Extract and validate API key from apikey header.
    
    Args:
        apikey: API key from apikey header
        
    Returns:
        str: The API key
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not apikey or not apikey.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required in apikey header"
        )
    
    return apikey.strip()


def get_hiagent_client(api_key: str = Depends(get_api_key)) -> HiAgentClient:
    """
    Get or create HiAgent client instance with the provided API key.
    
    Args:
        api_key: API key for authentication
        
    Returns:
        HiAgentClient: Configured client instance
        
    Raises:
        HTTPException: If client initialization fails
    """
    try:
        # Create a new client instance for each request with the provided API key
        return HiAgentClient(
            api_key=api_key,
            base_url=os.getenv('HIAGENT_BASE_URL'),
            timeout=float(os.getenv('HIAGENT_TIMEOUT', '30')),
            max_retries=int(os.getenv('HIAGENT_MAX_RETRIES', '3'))
        )
    except Exception as e:
        logger.error(f"Failed to initialize HiAgent client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize workflow client"
        )


@app.on_event("startup")
async def startup_event():
    """Initialize the proxy server on startup."""
    logger.info("Starting HiAgent Proxy Server...")
    
    # Configure logging
    log_level = os.getenv('HIAGENT_LOG_LEVEL', 'INFO').upper()
    logger.remove()
    logger.add(
        sink=lambda msg: print(msg, end=''),
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    logger.info("HiAgent Proxy Server started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down HiAgent Proxy Server...")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "hiagent-proxy"}


@app.post("/api/v1/workflow/run", response_model=RunWorkflowResponse)
async def run_workflow(
    request: RunWorkflowRequest,
    client: HiAgentClient = Depends(get_hiagent_client)
) -> RunWorkflowResponse:
    """
    Run a workflow with the provided parameters.
    
    Args:
        request: Workflow execution request
        client: HiAgent client instance
        
    Returns:
        RunWorkflowResponse: Workflow execution response with run ID
        
    Raises:
        HTTPException: If workflow execution fails
    """
    try:
        logger.info(f"Running workflow for user: {request.UserID}")
        logger.debug(f"Workflow request: {request.model_dump()}")
        
        response = client.run_workflow(request)
        
        logger.info(f"Workflow started successfully with run ID: {response.runId}")
        return response
        
    except (WorkflowExecutionError, WorkflowTimeoutError) as e:
        logger.error(f"Workflow execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Workflow execution failed: {str(e)}"
        )
    except HiAgentClientError as e:
        logger.error(f"HiAgent client error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Client error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during workflow execution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.post("/api/v1/workflow/query", response_model=QueryWorkflowResponse)
async def query_workflow(
    request: QueryWorkflowRequest,
    client: HiAgentClient = Depends(get_hiagent_client)
) -> QueryWorkflowResponse:
    """
    Query the status and results of a workflow execution.
    
    Args:
        request: Workflow query request
        client: HiAgent client instance
        
    Returns:
        QueryWorkflowResponse: Workflow status and results
        
    Raises:
        HTTPException: If workflow query fails
    """
    try:
        logger.info(f"Querying workflow {request.RunID} for user: {request.UserID}")
        
        response = client.query_workflow(request)
        
        logger.info(f"Workflow query completed for run ID: {request.RunID}")
        return response
        
    except HiAgentClientError as e:
        logger.error(f"HiAgent client error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Client error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during workflow query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.post("/api/v1/workflow/run-sync", response_model=QueryWorkflowResponse)
async def run_workflow_sync(
    request: RunWorkflowRequest,
    timeout: Optional[float] = 600.0,
    poll_interval: Optional[float] = 2.0,
    client: HiAgentClient = Depends(get_hiagent_client)
) -> QueryWorkflowResponse:
    """
    Run a workflow synchronously and wait for completion.
    
    This endpoint starts a workflow execution and polls for completion,
    returning the final result when the workflow finishes.
    
    Args:
        request: Workflow execution request
        timeout: Maximum time to wait for completion in seconds (default: 300)
        poll_interval: Polling interval in seconds (default: 2.0)
        client: HiAgent client instance
        
    Returns:
        QueryWorkflowResponse: Final workflow execution result
        
    Raises:
        HTTPException: If workflow execution or polling fails
    """
    try:
        logger.info(f"Running workflow synchronously for user: {request.UserID}")
        logger.debug(f"Sync workflow request: {request.model_dump()}")
        logger.info(f"Timeout: {timeout}s, Poll interval: {poll_interval}s")
        
        # Start workflow execution
        run_response = client.run_workflow(request)
        run_id = run_response.runId
        
        logger.info(f"Workflow started with run ID: {run_id}, waiting for completion...")
        
        # Wait for completion using the client's wait_for_completion method
        final_response = client.wait_for_completion(
            execution_id=run_id,
            user_id=request.UserID,
            timeout=timeout,
            poll_interval=poll_interval
        )
        
        logger.info(f"Synchronous workflow execution completed for run ID: {run_id}")
        return final_response
        
    except (WorkflowExecutionError, WorkflowTimeoutError) as e:
        logger.error(f"Workflow execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Workflow execution failed: {str(e)}"
        )
    except HiAgentClientError as e:
        logger.error(f"HiAgent client error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Client error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during synchronous workflow execution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment variables
    host = os.getenv("PROXY_HOST", "0.0.0.0")
    port = int(os.getenv("PROXY_PORT", "8000"))
    
    logger.info(f"Starting HiAgent Proxy Server on {host}:{port}")
    
    uvicorn.run(
        "src.proxy:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )