"""
Security Scan Module - Scan Service

Interface definitions for file scanning operations using ClamAV.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
import time
import subprocess
import mimetypes
from .io_contract import ScanRequest, ScanResult, ScanStatus
from .config import get_config


class ScanService(ABC):
    """Abstract base class for file scanning services."""
    
    @abstractmethod
    def scan_file(self, scan_request: ScanRequest) -> ScanResult:
        """
        Scan a file for viruses.
        
        Args:
            scan_request (ScanRequest): The scan request containing file details
            
        Returns:
            ScanResult: The result of the scan operation
        """
        pass
    
    @abstractmethod
    def run_clamav_scan(self, file_path: str) -> Dict[str, Any]:
        """
        Execute ClamAV scan on a file.
        
        Args:
            file_path (str): Path to the file to scan
            
        Returns:
            Dict[str, Any]: Scan results from ClamAV
        """
        pass
    
    @abstractmethod
    def log_scan_result(self, scan_result: ScanResult) -> None:
        """
        Log scan results for auditing and debugging.
        
        Args:
            scan_result (ScanResult): The scan result to log
        """
        pass


class ClamAVScanService(ScanService):
    """Concrete implementation of ScanService using ClamAV."""
    
    def __init__(self, clamav_socket: Optional[str] = None):
        """
        Initialize ClamAV scan service.
        
        Args:
            clamav_socket (Optional[str]): Path to ClamAV socket or None for localhost
        """
        self.clamav_socket = clamav_socket
        self.logger = None  # Will be injected
    
    def scan_file(self, scan_request: ScanRequest) -> ScanResult:
        """
        Scan a file for viruses using ClamAV.
        
        Args:
            scan_request (ScanRequest): The scan request containing file details
            
        Returns:
            ScanResult: The result of the scan operation
        """
        try:
            # Get file size
            file_size = os.path.getsize(scan_request.file_path)
            
            # Check size limits
            config = get_config()
            
            if file_size > config.max_hard_limit_mb * 1024 * 1024:
                # File exceeds hard limit (15MB)
                return ScanResult(
                    status=ScanStatus.REJECTED_SIZE_LIMIT,
                    details={
                        'engine': 'SizeValidation',
                        'error': f'File exceeds {config.max_hard_limit_mb}MB limit',
                        'file_size_bytes': file_size,
                        'scan_time': None
                    },
                    file_size_bytes=file_size
                )
            elif file_size > config.max_upload_size_mb * 1024 * 1024:
                # File exceeds default limit (5MB) but under hard limit
                return ScanResult(
                    status=ScanStatus.REJECTED_SIZE_LIMIT,
                    details={
                        'engine': 'SizeValidation',
                        'error': f'File exceeds {config.max_upload_size_mb}MB default limit, please compress and retry',
                        'file_size_bytes': file_size,
                        'scan_time': None
                    },
                    file_size_bytes=file_size
                )
            
            # Run ClamAV scan
            clamav_result = self.run_clamav_scan(scan_request.file_path)
            
            # Determine scan status based on ClamAV result
            if clamav_result.get('status') == 'FOUND':
                status = ScanStatus.INFECTED
                details = {
                    'engine': 'ClamAV',
                    'virus_name': clamav_result.get('virus_name'),
                    'scan_time': clamav_result.get('scan_time'),
                    'error': None
                }
                infected_path = scan_request.file_path
                safe_path = None
            elif clamav_result.get('status') == 'OK':
                status = ScanStatus.SAFE
                details = {
                    'engine': 'ClamAV',
                    'scan_time': clamav_result.get('scan_time'),
                    'error': None
                }
                safe_path = scan_request.file_path
                infected_path = None
            else:
                status = ScanStatus.ERROR
                details = {
                    'engine': 'ClamAV',
                    'error': clamav_result.get('error', 'Unknown error'),
                    'scan_time': clamav_result.get('scan_time')
                }
                safe_path = None
                infected_path = None
            
            scan_result = ScanResult(
                status=status,
                details=details,
                file_size_bytes=file_size,
                safe_path=safe_path,
                infected_path=infected_path
            )
            
            # Log the result
            self.log_scan_result(scan_result)
            
            return scan_result
            
        except Exception as e:
            # Handle exceptions and return error result
            error_result = ScanResult(
                status=ScanStatus.ERROR,
                details={
                    'engine': 'ClamAV',
                    'error': str(e),
                    'scan_time': None
                },
                safe_path=None,
                infected_path=None
            )
            
            self.log_scan_result(error_result)
            return error_result
    
    def run_clamav_scan(self, file_path: str) -> Dict[str, Any]:
        """
        Execute ClamAV scan on a file.
        
        Args:
            file_path (str): Path to the file to scan
            
        Returns:
            Dict[str, Any]: Scan results from ClamAV
        """
        # This is a placeholder implementation
        # In a real implementation, this would:
        # 1. Connect to ClamAV daemon
        # 2. Execute the scan
        # 3. Parse and return results
        
        try:
            start_time = time.time()
            
            # Example command (would need actual ClamAV integration)
            # result = subprocess.run(['clamdscan', '--fd-pass', file_path], 
            #                        capture_output=True, text=True)
            
            # Placeholder result structure
            result = {
                'status': 'OK',  # or 'FOUND' or 'ERROR'
                'virus_name': None,
                'scan_time': time.time() - start_time,
                'error': None
            }
            
            return result
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'virus_name': None,
                'scan_time': None,
                'error': str(e)
            }
    
    def log_scan_result(self, scan_result: ScanResult) -> None:
        """
        Log scan results for auditing and debugging.
        
        Args:
            scan_result (ScanResult): The scan result to log
        """
        if self.logger:
            self.logger.info(
                f"Scan completed - Status: {scan_result.status}, "
                f"Timestamp: {scan_result.timestamp}, "
                f"Details: {scan_result.details}"
            )
    
    def scan_and_return_paths(self, file_bytes: bytes, original_filename: str, quarantine_manager: 'FileQuarantineManager') -> tuple:
        """
        Orchestrator-ready helper method to scan a file and return paths.
        
        This method:
        1. Moves file to incoming folder
        2. Runs scan
        3. Returns status and appropriate path (safe or infected)
        
        Args:
            file_bytes (bytes): File content as bytes
            original_filename (str): Original filename
            quarantine_manager (FileQuarantineManager): Quarantine manager instance
            
        Returns:
            tuple: (status: str, path: str or None)
                   status: "SAFE", "INFECTED", or "ERROR"
                   path: Path to safe file, infected file, or None if error
        """
        try:
            # Move to incoming folder
            incoming_path = quarantine_manager.move_to_incoming(file_bytes, original_filename)
            
            # Move to scanning folder
            scanning_path = quarantine_manager.move_to_scanning(incoming_path)
            
            # Create scan request
            scan_request = ScanRequest(
                file_id=f"orchestrator_{quarantine_manager._generate_unique_id()}",
                file_path=scanning_path,
                mime_type=self._guess_mime_type(original_filename)
            )
            
            # Perform scan
            scan_result = self.scan_file(scan_request)
            
            # Return appropriate path based on status
            if scan_result.status == ScanStatus.SAFE:
                # Move to clean folder and return clean path
                clean_path = quarantine_manager.mark_as_safe(scanning_path)
                return ("SAFE", clean_path)
            elif scan_result.status == ScanStatus.INFECTED:
                # Move to infected folder and return infected path
                infected_path = quarantine_manager.mark_as_infected(scanning_path)
                return ("INFECTED", infected_path)
            else:
                # ERROR status - keep in scanning folder
                return ("ERROR", scanning_path)
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Orchestrator scan failed: {str(e)}")
            return ("ERROR", None)
    
    def _guess_mime_type(self, filename: str) -> str:
        """
        Guess MIME type from filename extension.
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Guessed MIME type
        """
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or "application/octet-stream"