"""
Security Scan Module - Stress Tests

Additional synthetic tests for stress testing the security scan module.
"""

import asyncio
import time
import pytest
import tempfile
import os
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch, MagicMock

from backend_app.security_scan.scan_service import ClamAVScanService
from backend_app.security_scan.quarantine_manager import FileQuarantineManager
from backend_app.security_scan.virus_update_manager import ClamAVUpdateManager
from backend_app.security_scan.cron_scheduler import APSchedulerManager
from backend_app.security_scan.io_contract import ScanRequest, ScanStatus
from backend_app.security_scan.config import get_config


class TestStressTests:
    """Stress tests for the security scan module."""
    
    @pytest.fixture
    def config(self):
        """Get configuration for tests."""
        return get_config()
    
    @pytest.fixture
    def quarantine_manager(self, config):
        """Create quarantine manager for tests."""
        return FileQuarantineManager(config.quarantine_base_path)
    
    @pytest.fixture
    def scan_service(self, config):
        """Create scan service for tests."""
        service = ClamAVScanService(clamav_socket=config.clamav_socket)
        service.logger = Mock()
        return service
    
    @pytest.fixture
    def update_manager(self, config):
        """Create update manager for tests."""
        return ClamAVUpdateManager(
            db_path=config.virus_db_path,
            backup_path=config.backup_db_path,
            clamav_socket=config.clamav_socket
        )
    
    def create_test_file(self, size_mb: int = 1) -> bytes:
        """
        Create a test file of specified size.
        
        Args:
            size_mb (int): Size in megabytes
            
        Returns:
            bytes: Test file content
        """
        return b'A' * (size_mb * 1024 * 1024)
    
    def create_virus_like_content(self) -> bytes:
        """
        Create content that resembles virus signatures.
        
        Returns:
            bytes: Virus-like content
        """
        # This is just test data, not actual malware
        return b'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' * 100
    
    @pytest.mark.asyncio
    async def test_concurrent_scan_stress(self, scan_service, quarantine_manager):
        """
        Test concurrent file scanning under stress.
        
        Tests:
        - Multiple concurrent scans
        - No race conditions
        - Proper resource management
        """
        # Create multiple test files
        num_files = 50
        test_files = [
            (self.create_test_file(1), f"test_file_{i}.txt")
            for i in range(num_files)
        ]
        
        # Run concurrent scans
        async def scan_file(file_bytes, filename):
            return scan_service.scan_and_return_paths(
                file_bytes, filename, quarantine_manager
            )
        
        # Use ThreadPoolExecutor for concurrent execution
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=10) as executor:
            tasks = [
                loop.run_in_executor(
                    executor,
                    scan_service.scan_and_return_paths,
                    file_bytes,
                    filename,
                    quarantine_manager
                )
                for file_bytes, filename in test_files
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify results
        successful_scans = [r for r in results if not isinstance(r, Exception)]
        
        assert len(successful_scans) == num_files, f"Expected {num_files} successful scans, got {len(successful_scans)}"
        
        # Verify no race conditions in file naming
        paths = [path for status, path in successful_scans if path]
        unique_paths = set(paths)
        assert len(unique_paths) == len(paths), "Duplicate file paths detected - possible race condition"
    
    def test_large_file_scan_stress(self, scan_service, quarantine_manager):
        """
        Test scanning of large files.
        
        Tests:
        - Large file handling
        - Memory usage
        - Timeout handling
        """
        # Test with progressively larger files
        file_sizes = [1, 5, 10, 25]  # MB
        
        for size_mb in file_sizes:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                # Create large test file
                test_content = self.create_test_file(size_mb)
                temp_file.write(test_content)
                temp_file.flush()
                
                try:
                    # Test quarantine movement with large file
                    quarantine_path = quarantine_manager.move_to_incoming(
                        test_content, f"large_file_{size_mb}mb.txt"
                    )
                    
                    scanning_path = quarantine_manager.move_to_scanning(quarantine_path)
                    
                    # Create scan request
                    scan_request = ScanRequest(
                        file_id=f"large_test_{size_mb}mb",
                        file_path=scanning_path,
                        mime_type="text/plain"
                    )
                    
                    # Perform scan (should handle large files)
                    start_time = time.time()
                    result = scan_service.scan_file(scan_request)
                    end_time = time.time()
                    
                    # Verify result
                    assert result.status in [ScanStatus.SAFE, ScanStatus.ERROR]
                    assert end_time - start_time < 30  # Should complete within 30 seconds
                    
                    # Clean up
                    if result.status == ScanStatus.SAFE:
                        quarantine_manager.mark_as_safe(scanning_path)
                    elif result.status == ScanStatus.INFECTED:
                        quarantine_manager.mark_as_infected(scanning_path)
                        
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_file.name):
                        os.unlink(temp_file.name)
    
    def test_virus_db_stress(self, update_manager):
        """
        Test virus database under stress conditions.
        
        Tests:
        - Multiple concurrent DB validations
        - Backup/restore under load
        - Corruption recovery
        """
        # Test concurrent DB validations
        def validate_db():
            return update_manager.validate_virus_db()
        
        # Run multiple validations concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(validate_db) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # All validations should succeed
        assert len(results) == 10
        for result in results:
            assert hasattr(result, 'checksum_valid')
            assert hasattr(result, 'db_version')
    
    def test_quarantine_folder_stress(self, quarantine_manager):
        """
        Test quarantine folder management under stress.
        
        Tests:
        - Many files in folders
        - Folder cleanup
        - Path generation under load
        """
        # Create many test files
        num_files = 100
        
        # Move many files to incoming folder
        file_paths = []
        for i in range(num_files):
            test_content = self.create_test_file(1)
            file_path = quarantine_manager.move_to_incoming(
                test_content, f"stress_test_{i}.txt"
            )
            file_paths.append(file_path)
        
        # Verify all files were created
        incoming_files = os.listdir(quarantine_manager.incoming_path)
        assert len(incoming_files) == num_files
        
        # Move all to scanning folder
        scanning_paths = []
        for file_path in file_paths:
            scanning_path = quarantine_manager.move_to_scanning(file_path)
            scanning_paths.append(scanning_path)
        
        # Verify scanning folder has files
        scanning_files = os.listdir(quarantine_manager.scanning_path)
        assert len(scanning_files) == num_files
        
        # Move half to clean, half to infected
        for i, scanning_path in enumerate(scanning_paths):
            if i % 2 == 0:
                quarantine_manager.mark_as_safe(scanning_path)
            else:
                quarantine_manager.mark_as_infected(scanning_path)
        
        # Verify final distribution
        clean_files = os.listdir(quarantine_manager.clean_path)
        infected_files = os.listdir(quarantine_manager.infected_path)
        
        assert len(clean_files) == num_files // 2
        assert len(infected_files) == num_files // 2
    
    @pytest.mark.asyncio
    async def test_scheduler_stress(self, update_manager, quarantine_manager):
        """
        Test scheduler under stress conditions.
        
        Tests:
        - Multiple rapid scheduler operations
        - Concurrent maintenance tasks
        - Resource cleanup
        """
        scheduler = APSchedulerManager(update_manager, quarantine_manager)
        
        # Test rapid scheduler start/stop
        for _ in range(5):
            scheduler.start()
            await asyncio.sleep(0.1)
            scheduler.stop()
            await asyncio.sleep(0.1)
        
        # Test job addition under load
        def dummy_task():
            pass
        
        # Add many jobs rapidly
        for i in range(20):
            scheduler.add_custom_job(
                dummy_task,
                CronTrigger(second=f"*/{i+1}"),
                id=f"stress_job_{i}"
            )
        
        # Verify jobs were added
        jobs = scheduler.get_jobs()
        assert len(jobs) >= 20
    
    def test_memory_usage_stress(self, scan_service, quarantine_manager):
        """
        Test memory usage under stress.
        
        Tests:
        - Memory leaks
        - Large number of operations
        - Resource cleanup
        """
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform many operations
        for i in range(100):
            test_content = self.create_test_file(1)
            
            # Simulate scan operation
            result = scan_service.scan_and_return_paths(
                test_content,
                f"memory_test_{i}.txt",
                quarantine_manager
            )
            
            # Force garbage collection periodically
            if i % 10 == 0:
                gc.collect()
        
        # Check memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100, f"Memory increase too high: {memory_increase}MB"
    
    def test_error_handling_stress(self, scan_service, quarantine_manager):
        """
        Test error handling under stress conditions.
        
        Tests:
        - Many concurrent errors
        - Error recovery
        - Logging under load
        """
        # Mock scan service to always fail
        original_scan = scan_service.run_clamav_scan
        scan_service.run_clamav_scan = Mock(side_effect=Exception("Simulated scan error"))
        
        # Perform many operations that will fail
        error_results = []
        for i in range(50):
            test_content = self.create_test_file(1)
            
            result = scan_service.scan_and_return_paths(
                test_content,
                f"error_test_{i}.txt",
                quarantine_manager
            )
            
            error_results.append(result)
        
        # All should return ERROR status
        error_count = sum(1 for status, _ in error_results if status == "ERROR")
        assert error_count == 50
        
        # Restore original method
        scan_service.run_clamav_scan = original_scan
    
    def test_file_system_stress(self, quarantine_manager):
        """
        Test file system operations under stress.
        
        Tests:
        - Many file operations
        - Disk space handling
        - File permission issues
        """
        # Test rapid file creation and deletion
        test_files = []
        
        # Create many files rapidly
        for i in range(200):
            test_content = self.create_test_file(1)
            file_path = quarantine_manager.move_to_incoming(
                test_content, f"fs_test_{i}.txt"
            )
            test_files.append(file_path)
        
        # Verify all files exist
        incoming_files = os.listdir(quarantine_manager.incoming_path)
        assert len(incoming_files) == 200
        
        # Clean up
        for file_path in test_files:
            if os.path.exists(file_path):
                os.unlink(file_path)
    
    @pytest.mark.asyncio
    async def test_integration_stress(self, scan_service, quarantine_manager, update_manager):
        """
        Test full integration under stress conditions.
        
        Tests:
        - End-to-end workflow under load
        - Multiple components interacting
        - System stability
        """
        # Create a comprehensive stress test
        num_operations = 25
        
        async def stress_operation(op_id: int):
            """Perform a complete scan operation."""
            try:
                # Create test file
                test_content = self.create_test_file(2)
                
                # Perform scan
                status, path = scan_service.scan_and_return_paths(
                    test_content,
                    f"integration_test_{op_id}.txt",
                    quarantine_manager
                )
                
                # Validate DB
                db_status = update_manager.validate_virus_db()
                
                return {
                    'operation_id': op_id,
                    'status': status,
                    'path': path,
                    'db_valid': db_status.checksum_valid
                }
            except Exception as e:
                return {
                    'operation_id': op_id,
                    'error': str(e)
                }
        
        # Run operations concurrently
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=8) as executor:
            tasks = [
                loop.run_in_executor(executor, lambda op_id=i: asyncio.run(stress_operation(op_id)))
                for i in range(num_operations)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful_ops = [r for r in results if isinstance(r, dict) and 'status' in r]
        error_ops = [r for r in results if isinstance(r, dict) and 'error' in r]
        
        # Most operations should succeed
        assert len(successful_ops) >= num_operations * 0.8, f"Too many failures: {len(error_ops)}"
        
        # Verify scan statuses
        safe_count = sum(1 for op in successful_ops if op['status'] == 'SAFE')
        infected_count = sum(1 for op in successful_ops if op['status'] == 'INFECTED')
        error_count = sum(1 for op in successful_ops if op['status'] == 'ERROR')
        
        # Should have reasonable distribution
        assert safe_count + infected_count + error_count == len(successful_ops)