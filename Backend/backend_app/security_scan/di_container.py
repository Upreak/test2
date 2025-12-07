"""
Security Scan Module - Dependency Injection Container

Container bindings for orchestrator integration.
"""

from typing import Protocol
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from .scan_service import ScanService, ClamAVScanService
from .quarantine_manager import QuarantineManager, FileQuarantineManager
from .virus_update_manager import VirusUpdateManager, ClamAVUpdateManager
from .cron_scheduler import CronScheduler, APSchedulerManager
from .config import SecurityScanConfig


class SecurityScanContainer(containers.DeclarativeContainer):
    """Dependency injection container for security scan module."""
    
    # Configuration
    config = providers.Singleton(
        SecurityScanConfig.create_default_config
    )
    
    # Quarantine Manager
    quarantine_manager = providers.Singleton(
        FileQuarantineManager,
        base_quarantine_path=config.provided.quarantine_base_path
    )
    
    # Scan Service
    scan_service = providers.Factory(
        ClamAVScanService,
        clamav_socket=config.provided.clamav_socket
    )
    
    # Virus Update Manager
    virus_update_manager = providers.Factory(
        ClamAVUpdateManager,
        db_path=config.provided.virus_db_path,
        backup_path=config.provided.backup_db_path,
        clamav_socket=config.provided.clamav_socket
    )
    
    # Scheduler
    scheduler = providers.Factory(
        APSchedulerManager,
        virus_update_manager=virus_update_manager,
        quarantine_manager=quarantine_manager
    )


# Global container instance
container = SecurityScanContainer()


class SecurityScanOrchestrator:
    """
    Orchestrator-ready interface for security scan operations.
    
    This class provides a clean interface for orchestrator integration
    with dependency injection support.
    """
    
    @inject
    def __init__(
        self,
        scan_service: ScanService = Provide[container.scan_service],
        quarantine_manager: QuarantineManager = Provide[container.quarantine_manager],
        virus_update_manager: VirusUpdateManager = Provide[container.virus_update_manager],
        scheduler: CronScheduler = Provide[container.scheduler]
    ):
        """
        Initialize orchestrator with dependencies.
        
        Args:
            scan_service: Scan service instance
            quarantine_manager: Quarantine manager instance
            virus_update_manager: Virus update manager instance
            scheduler: Scheduler instance
        """
        self.scan_service = scan_service
        self.quarantine_manager = quarantine_manager
        self.virus_update_manager = virus_update_manager
        self.scheduler = scheduler
    
    def scan_file_for_orchestrator(self, file_bytes: bytes, filename: str) -> tuple:
        """
        Orchestrator method to scan a file.
        
        Args:
            file_bytes (bytes): File content
            filename (str): Original filename
            
        Returns:
            tuple: (status: str, path: str or None)
        """
        return self.scan_service.scan_and_return_paths(
            file_bytes, filename, self.quarantine_manager
        )
    
    def get_scan_status(self) -> dict:
        """
        Get current scan system status.
        
        Returns:
            dict: System status information
        """
        # Get DB status
        db_status = self.virus_update_manager.validate_virus_db()
        
        # Get folder counts
        folders = self.quarantine_manager.get_quarantine_paths()
        folder_counts = {}
        
        for folder_name, folder_path in folders.items():
            if folder_name != 'logs' and os.path.exists(folder_path):
                try:
                    file_count = len([
                        f for f in os.listdir(folder_path)
                        if os.path.isfile(os.path.join(folder_path, f))
                    ])
                    folder_counts[folder_name] = file_count
                except Exception:
                    folder_counts[folder_name] = 0
            else:
                folder_counts[folder_name] = 0
        
        return {
            "folders": folder_counts,
            "db_checksum_valid": db_status.checksum_valid,
            "db_version": db_status.db_version,
            "scheduler_active": self.scheduler.scheduler.running if hasattr(self.scheduler, 'scheduler') else False,
            "last_db_update": db_status.last_update.isoformat() if db_status.last_update else None
        }
    
    def start_maintenance_scheduler(self):
        """Start the daily maintenance scheduler."""
        self.scheduler.schedule_midnight_db_check()
        self.scheduler.start()
    
    def stop_maintenance_scheduler(self):
        """Stop the daily maintenance scheduler."""
        self.scheduler.stop()
    
    def validate_system_health(self) -> bool:
        """
        Validate overall system health.
        
        Returns:
            bool: True if system is healthy, False otherwise
        """
        try:
            # Check DB validity
            db_status = self.virus_update_manager.validate_virus_db()
            if not db_status.checksum_valid:
                return False
            
            # Check folder structure
            self.quarantine_manager.ensure_folder_structure()
            
            return True
            
        except Exception:
            return False


# Wiring configuration for dependency injection
wire_packages = [
    'backend_app.security_scan',
    'backend_app.routers.security_scan'
]


def configure_container():
    """Configure the dependency injection container."""
    container.wire(modules=wire_packages)


def get_security_scan_orchestrator() -> SecurityScanOrchestrator:
    """
    Get configured security scan orchestrator instance.
    
    Returns:
        SecurityScanOrchestrator: Configured orchestrator instance
    """
    return SecurityScanOrchestrator()


# Convenience functions for orchestrator integration
@inject
def create_scan_service(
    scan_service: ScanService = Provide[container.scan_service]
) -> ScanService:
    """Create and return scan service instance."""
    return scan_service


@inject
def create_quarantine_manager(
    quarantine_manager: QuarantineManager = Provide[container.quarantine_manager]
) -> QuarantineManager:
    """Create and return quarantine manager instance."""
    return quarantine_manager


@inject
def create_virus_update_manager(
    virus_update_manager: VirusUpdateManager = Provide[container.virus_update_manager]
) -> VirusUpdateManager:
    """Create and return virus update manager instance."""
    return virus_update_manager


@inject
def create_scheduler(
    scheduler: CronScheduler = Provide[container.scheduler]
) -> CronScheduler:
    """Create and return scheduler instance."""
    return scheduler


# Example usage in orchestrator
def example_orchestrator_usage():
    """
    Example of how to use the security scan module in orchestrator.
    
    This is documentation for orchestrator integration.
    """
    # Configure container (should be done once at app startup)
    configure_container()
    
    # Method 1: Get orchestrator instance
    orchestrator = get_security_scan_orchestrator()
    
    # Scan a file
    status, path = orchestrator.scan_file_for_orchestrator(
        file_bytes=b"test content",
        filename="test.txt"
    )
    
    # Get system status
    status_info = orchestrator.get_scan_status()
    
    # Start scheduler
    orchestrator.start_maintenance_scheduler()
    
    # Method 2: Get individual components
    scan_service = create_scan_service()
    quarantine_manager = create_quarantine_manager()
    
    # Use components directly
    status, path = scan_service.scan_and_return_paths(
        b"test", "test.txt", quarantine_manager
    )


# Health check function for orchestrator
@inject
def security_scan_health_check(
    orchestrator: SecurityScanOrchestrator = Provide[container]
) -> dict:
    """
    Health check function for orchestrator.
    
    Args:
        orchestrator: Security scan orchestrator instance
        
    Returns:
        dict: Health check results
    """
    try:
        is_healthy = orchestrator.validate_system_health()
        status_info = orchestrator.get_scan_status()
        
        return {
            "module": "security_scan",
            "healthy": is_healthy,
            "status": status_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "module": "security_scan",
            "healthy": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# Import required modules
import os
from datetime import datetime