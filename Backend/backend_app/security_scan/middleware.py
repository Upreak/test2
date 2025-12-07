"""
Security Scan Module - FastAPI Middleware

Middleware for logging scan activity to /data/quarantine/logs/scan_activity.log.
"""

import logging
import time
from datetime import datetime
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class ScanActivityLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware to log scan activity for security endpoints."""
    
    def __init__(
        self,
        app,
        log_file_path: str = None,
        log_endpoints: list = None
    ):
        """
        Initialize the middleware.
        
        Args:
            app: FastAPI application instance
            log_file_path: Path to the log file
            log_endpoints: List of endpoints to log (default: scan-related endpoints)
        """
        super().__init__(app)
        
        # Default log file path
        if log_file_path is None:
            from .config import get_config
            config = get_config()
            log_file_path = f"{config.logs_path}/scan_activity.log"
        
        # Default endpoints to log
        if log_endpoints is None:
            log_endpoints = [
                "/security/scan-file",
                "/security/virus-db-status",
                "/security/manual-db-restore"
            ]
        
        # Setup logger
        self.logger = logging.getLogger("scan_activity")
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            # Create file handler
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(message)s'  # Custom format for scan logs
            )
            file_handler.setFormatter(formatter)
            
            # Add handler to logger
            self.logger.addHandler(file_handler)
        
        self.log_endpoints = log_endpoints
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and log scan activity."""
        
        # Check if this endpoint should be logged
        if request.url.path not in self.log_endpoints:
            return await call_next(request)
        
        # Get start time
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Extract information for logging
        endpoint = request.url.path
        timestamp = datetime.utcnow().isoformat()
        method = request.method
        status_code = response.status_code
        
        # Extract file information from request
        file_name = self._extract_file_name(request)
        
        # Determine result status based on endpoint and status code
        result_status = self._determine_result_status(endpoint, status_code, request)
        
        # Log the activity
        log_entry = self._format_log_entry(
            endpoint=endpoint,
            timestamp=timestamp,
            method=method,
            status_code=status_code,
            result_status=result_status,
            file_name=file_name,
            process_time=process_time
        )
        
        self.logger.info(log_entry)
        
        return response
    
    def _extract_file_name(self, request: Request) -> str:
        """
        Extract file name from the request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            str: File name or "N/A" if not available
        """
        try:
            # For file upload endpoints, try to get filename from form data
            if request.method == "POST" and "file" in str(request.url.path):
                # This is a simplified extraction - in practice, you might need
                # to read the form data to get the filename
                return "file_upload"
            
            # For other endpoints, check query parameters or path parameters
            file_name = request.query_params.get("file_name", "N/A")
            if file_name == "N/A":
                # Check path parameters
                path_params = getattr(request, "path_params", {})
                file_name = path_params.get("file_name", "N/A")
            
            return file_name
            
        except Exception:
            return "N/A"
    
    def _determine_result_status(self, endpoint: str, status_code: int, request: Request) -> str:
        """
        Determine the result status based on endpoint and response.
        
        Args:
            endpoint: API endpoint
            status_code: HTTP status code
            request: FastAPI request object
            
        Returns:
            str: Result status (SAFE, INFECTED, ERROR, or N/A)
        """
        try:
            # For scan-file endpoint, check the response content
            if endpoint == "/security/scan-file" and status_code == 200:
                # In a real implementation, you would parse the response JSON
                # to determine the actual scan result
                # For now, return a placeholder that will be updated by the endpoint
                return "PENDING"
            
            # For other endpoints, map status codes to result types
            if status_code >= 400:
                return "ERROR"
            elif status_code >= 200 and status_code < 300:
                return "SUCCESS"
            else:
                return "UNKNOWN"
                
        except Exception:
            return "ERROR"
    
    def _format_log_entry(
        self,
        endpoint: str,
        timestamp: str,
        method: str,
        status_code: int,
        result_status: str,
        file_name: str,
        process_time: float
    ) -> str:
        """
        Format the log entry.
        
        Args:
            endpoint: API endpoint
            timestamp: ISO timestamp
            method: HTTP method
            status_code: HTTP status code
            result_status: Scan result status
            file_name: Name of the file (if applicable)
            process_time: Processing time in seconds
            
        Returns:
            str: Formatted log entry
        """
        return (
            f"[{timestamp}] "
            f"ENDPOINT: {endpoint} | "
            f"METHOD: {method} | "
            f"STATUS: {status_code} | "
            f"RESULT: {result_status} | "
            f"FILE: {file_name} | "
            f"TIME: {process_time:.3f}s"
        )


def create_scan_activity_logger(log_file_path: str = None):
    """
    Factory function to create scan activity logger middleware.
    
    Args:
        log_file_path: Optional custom log file path
        
    Returns:
        ScanActivityLoggerMiddleware: Configured middleware instance
    """
    return ScanActivityLoggerMiddleware(
        app=None,  # Will be set when added to FastAPI app
        log_file_path=log_file_path,
        log_endpoints=[
            "/security/scan-file",
            "/security/virus-db-status", 
            "/security/manual-db-restore"
        ]
    )