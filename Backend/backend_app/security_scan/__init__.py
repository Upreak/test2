"""
Security Scan Module

Local security scanning module with quarantine flow and virus DB management.

This module provides:
- File scanning using ClamAV
- Quarantine management for incoming, scanning, clean, and infected files
- Virus database validation and updates
- Scheduled daily maintenance
- API endpoints for security operations

Components:
- scan_service.py: File scanning operations
- quarantine_manager.py: File movement and quarantine management
- virus_update_manager.py: Virus database management
- cron_scheduler.py: Scheduled maintenance tasks
- io_contract.py: Data structures and contracts
- config.py: Configuration and folder setup
"""

# Import main classes for easy access
from .io_contract import ScanRequest, ScanResult, VirusUpdateStatus, ScanStatus
from .scan_service import ScanService, ClamAVScanService
from .quarantine_manager import QuarantineManager, FileQuarantineManager
from .virus_update_manager import VirusUpdateManager, ClamAVUpdateManager
from .cron_scheduler import CronScheduler, APSchedulerManager
from .middleware import ScanActivityLoggerMiddleware
from .di_container import (
    SecurityScanContainer,
    SecurityScanOrchestrator,
    configure_container,
    get_security_scan_orchestrator,
    create_scan_service,
    create_quarantine_manager,
    create_virus_update_manager,
    create_scheduler,
    security_scan_health_check
)

# Version information
__version__ = "1.0.0"
__author__ = "Security Scan Module Team"

# Module exports
__all__ = [
    # IO Contracts
    "ScanRequest",
    "ScanResult",
    "VirusUpdateStatus",
    "ScanStatus",
    
    # Services
    "ScanService",
    "ClamAVScanService",
    "QuarantineManager",
    "FileQuarantineManager",
    "VirusUpdateManager",
    "ClamAVUpdateManager",
    "CronScheduler",
    "APSchedulerManager",
    
    # Middleware
    "ScanActivityLoggerMiddleware",
    
    # Dependency Injection
    "SecurityScanContainer",
    "SecurityScanOrchestrator",
    "configure_container",
    "get_security_scan_orchestrator",
    "create_scan_service",
    "create_quarantine_manager",
    "create_virus_update_manager",
    "create_scheduler",
    "security_scan_health_check"
]