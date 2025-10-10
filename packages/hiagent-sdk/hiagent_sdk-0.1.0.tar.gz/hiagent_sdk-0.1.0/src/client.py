"""
HiAgent API Client.

This module provides the main client interface for interacting with
the HiAgent workflow API, including workflow execution, status polling,
and result retrieval.
"""

import os
import time
import json
from typing import Optional, Dict, Any, List
from loguru import logger

from .models.workflow import (
    RunWorkflowRequest, RunWorkflowResponse,
    QueryWorkflowRequest, QueryWorkflowResponse,
    WorkflowResult, WorkflowStatus
)
# from .parser.workflow_parser import WorkflowParser
from .utils.http_client import HTTPClient, HTTPRequestError


class HiAgentClientError(Exception):
    """Base exception for HiAgent client errors"""
    pass


class WorkflowExecutionError(HiAgentClientError):
    """Exception raised for workflow execution errors"""
    pass


class WorkflowTimeoutError(HiAgentClientError):
    """Exception raised when workflow execution times out"""
    pass


class HiAgentClient:
    """
    Main client for interacting with HiAgent workflow API.
    
    This client provides methods for:
    - Running workflows
    - Polling workflow status
    - Retrieving workflow results
    - Parsing intermediate stages
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        user_id: Optional[str] = None
    ):
        """
        Initialize HiAgent client.
        
        Args:
            api_key: API key for authentication (loads from HIAGENT_API_KEY if None)
            base_url: Base URL for API endpoints (loads from HIAGENT_BASE_URL if None)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries (default: 3)
            user_id: User identifier (optional)
        """
        # Load configuration from parameters or environment
        self.api_key = api_key or os.getenv('HIAGENT_API_KEY')
        self.base_url = base_url or os.getenv('HIAGENT_BASE_URL', 'https://hiagent-byteplus.volcenginepaas.com/api/proxy/api/v1')
        self.timeout = timeout or float(os.getenv('HIAGENT_TIMEOUT', '30'))
        self.max_retries = max_retries or int(os.getenv('HIAGENT_MAX_RETRIES', '3'))
        
        # Validate required parameters
        if not self.api_key:
            raise ValueError("API key is required. Provide it via api_key parameter or HIAGENT_API_KEY environment variable.")
        
        # Ensure base_url ends with /
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        
        # Configure logging
        self._configure_logging()
        
        # Initialize HTTP client and parser
        self.http_client = HTTPClient(
            base_url=self.base_url,
            headers=self._get_headers(),
            timeout=self.timeout,
            max_retries=self.max_retries
        )
    
    def _configure_logging(self):
        """Configure loguru logging"""
        log_level = os.getenv('HIAGENT_LOG_LEVEL', 'INFO').upper()
        
        # Remove default handler and add configured one
        logger.remove()
        logger.add(
            sink=lambda msg: print(msg, end=''),
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests"""
        headers = {
            'Content-Type': 'application/json',
            'Apikey': self.api_key
        }
            
        return headers
    
    def _get_run_workflow_url(self) -> str:
        """Get run workflow API endpoint URL"""
        return f"{self.base_url}run_app_workflow"
    
    def _get_query_workflow_url(self) -> str:
        """Get query workflow API endpoint URL"""
        return f"{self.base_url}query_run_app_process"
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the HTTP client"""
        self.http_client.close()
    
    def run_workflow(self, request: RunWorkflowRequest) -> RunWorkflowResponse:
        """
        Start a workflow execution.
        
        Args:
            request: Workflow run request
            
        Returns:
            Workflow run response with execution ID
            
        Raises:
            WorkflowExecutionError: If workflow execution fails
        """
        try:
            logger.info(f"Starting workflow execution: {request.InputData}")
            
            url = self._get_run_workflow_url()
            data = request.model_dump()
            data['InputData'] = json.dumps(data['InputData'])
            response_data = self.http_client.post(url, data)
            
            response = RunWorkflowResponse(**response_data)
            
            logger.info(f"Workflow started successfully. Execution ID: {response.runId}")
            return response
            
        except HTTPRequestError as e:
            error_msg = f"Failed to start workflow: {e}"
            logger.error(error_msg)
            raise WorkflowExecutionError(error_msg) from e
        
        except Exception as e:
            error_msg = f"Unexpected error starting workflow: {e}"
            logger.error(error_msg)
            raise WorkflowExecutionError(error_msg) from e
    
    def query_workflow(self, request: QueryWorkflowRequest) -> QueryWorkflowResponse:
        """
        Query workflow execution status and results.
        
        Args:
            request: Workflow query request
            
        Returns:
            Workflow query response with status and results
            
        Raises:
            WorkflowExecutionError: If query fails
        """
        try:
            logger.debug(f"Querying workflow status: {request.RunID}")
            
            url = self._get_query_workflow_url()
            response_data = self.http_client.post(url, request.model_dump())
            
            response = QueryWorkflowResponse(**response_data)
            try:
                json_output = json.loads(response.output)
            except json.JSONDecodeError:
                json_output = None
            finally:
                response.parsed_output = json_output
            
            logger.debug(f"Workflow status: {response.status}")
            return response
            
        except HTTPRequestError as e:
            error_msg = f"Failed to query workflow: {e}"
            logger.error(error_msg)
            raise WorkflowExecutionError(error_msg) from e
        
        except Exception as e:
            error_msg = f"Unexpected error querying workflow: {e}"
            logger.error(error_msg)
            raise WorkflowExecutionError(error_msg) from e
    
    def wait_for_completion(
        self,
        execution_id: str,
        user_id: str = "",
        timeout: Optional[float] = None,
        poll_interval: Optional[float] = None
    ) -> QueryWorkflowResponse:
        """
        Wait for workflow to complete by polling status.
        
        Args:
            execution_id: Workflow execution ID
            user_id: User identifier (default: empty string)
            timeout: Maximum time to wait in seconds (default: 300)
            poll_interval: Polling interval in seconds (default: 2.0)
            
        Returns:
            Final workflow query response
            
        Raises:
            WorkflowTimeoutError: If workflow doesn't complete within timeout
            WorkflowExecutionError: If workflow fails or query fails
        """
        # Use provided values or defaults
        timeout = timeout or 300.0  # 5 minutes default
        poll_interval = poll_interval or 2.0  # 2 seconds default
        
        logger.info(f"Waiting for workflow completion: {execution_id}")
        logger.info(f"Timeout: {timeout}s, Poll interval: {poll_interval}s")
        
        start_time = time.time()
        
        while True:
            # Check timeout
            elapsed_time = time.time() - start_time
            if elapsed_time >= timeout:
                error_msg = f"Workflow execution timed out after {timeout} seconds"
                logger.error(error_msg)
                raise WorkflowTimeoutError(error_msg)
            
            # Query workflow status
            try:
                request = QueryWorkflowRequest(RunID=execution_id, UserID=user_id)
                response = self.query_workflow(request)
                
                # Check if workflow is complete
                if response.status in [WorkflowStatus.SUCCESS, WorkflowStatus.FAILED]:
                    if response.status == WorkflowStatus.SUCCESS:
                        logger.info(f"Workflow completed successfully: {execution_id}")
                    else:
                        logger.error(f"Workflow failed: {execution_id}")
                        if response.error:
                            logger.error(f"Error details: {response.error}")
                    
                    return response
                
                # Wait before next poll
                logger.debug(f"Workflow still running, waiting {poll_interval}s before next poll...")
                time.sleep(poll_interval)
                
            except WorkflowExecutionError:
                # Re-raise workflow execution errors
                raise
            
            except Exception as e:
                error_msg = f"Unexpected error while waiting for completion: {e}"
                logger.error(error_msg)
                raise WorkflowExecutionError(error_msg) from e
