"""
Resume Scanner - Security Scan Module Test

Script to scan all resumes in the Resumes directory using the security scan module.
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import json

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend_app.security_scan.di_container import (
    configure_container,
    get_security_scan_orchestrator
)
from backend_app.security_scan.config import get_config


class ResumeScanner:
    """Resume scanner using the security scan module."""
    
    def __init__(self):
        """Initialize the resume scanner."""
        # Configure dependency injection
        configure_container()
        
        # Get orchestrator
        self.orchestrator = get_security_scan_orchestrator()
        
        # Get configuration
        self.config = get_config()
        
        # Results storage
        self.scan_results = []
    
    def find_resumes(self, resume_directory: str = "Resumes") -> List[Path]:
        """
        Find all resume files in the specified directory.
        
        Args:
            resume_directory (str): Directory containing resumes
            
        Returns:
            List[Path]: List of resume file paths
        """
        resume_dir = Path(project_root) / resume_directory
        
        if not resume_dir.exists():
            raise FileNotFoundError(f"Resume directory not found: {resume_dir}")
        
        # Supported resume file extensions
        resume_extensions = {'.pdf', '.doc', '.docx', '.txt', '.rtf'}
        
        resume_files = []
        for file_path in resume_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in resume_extensions:
                resume_files.append(file_path)
        
        return sorted(resume_files)
    
    def scan_resume(self, resume_path: Path) -> Dict[str, Any]:
        """
        Scan a single resume file.
        
        Args:
            resume_path (Path): Path to the resume file
            
        Returns:
            Dict[str, Any]: Scan results
        """
        start_time = time.time()
        
        try:
            # Read file content
            with open(resume_path, 'rb') as f:
                file_bytes = f.read()
            
            # Get MIME type
            import mimetypes
            mime_type, _ = mimetypes.guess_type(resume_path)
            if not mime_type:
                mime_type = "application/octet-stream"
            
            # Scan using orchestrator
            status, path = self.orchestrator.scan_file_for_orchestrator(
                file_bytes=file_bytes,
                filename=resume_path.name
            )
            
            end_time = time.time()
            scan_duration = end_time - start_time
            
            result = {
                'filename': resume_path.name,
                'filepath': str(resume_path),
                'mime_type': mime_type,
                'file_size': len(file_bytes),
                'status': status,
                'result_path': path,
                'scan_duration': scan_duration,
                'timestamp': time.time(),
                'success': True,
                'error': None
            }
            
            return result
            
        except Exception as e:
            end_time = time.time()
            scan_duration = end_time - start_time
            
            result = {
                'filename': resume_path.name,
                'filepath': str(resume_path),
                'mime_type': mime_type if 'mime_type' in locals() else "unknown",
                'file_size': len(file_bytes) if 'file_bytes' in locals() else 0,
                'status': 'ERROR',
                'result_path': None,
                'scan_duration': scan_duration,
                'timestamp': time.time(),
                'success': False,
                'error': str(e)
            }
            
            return result
    
    def scan_all_resumes(self, resume_directory: str = "Resumes") -> Dict[str, Any]:
        """
        Scan all resumes in the directory.
        
        Args:
            resume_directory (str): Directory containing resumes
            
        Returns:
            Dict[str, Any]: Complete scan results
        """
        print("🔍 Starting Resume Security Scan")
        print("=" * 50)
        
        # Find all resumes
        try:
            resume_files = self.find_resumes(resume_directory)
            print(f"📁 Found {len(resume_files)} resume files to scan")
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_resumes': 0,
                'scanned_resumes': 0,
                'results': []
            }
        
        # Scan each resume
        print("\n🔄 Scanning resumes...")
        print("-" * 50)
        
        total_start_time = time.time()
        
        for i, resume_file in enumerate(resume_files, 1):
            print(f"📄 [{i}/{len(resume_files)}] Scanning: {resume_file.name}")
            
            result = self.scan_resume(resume_file)
            self.scan_results.append(result)
            
            # Print result
            status_emoji = "✅" if result['success'] else "❌"
            status_text = result['status'] if result['success'] else f"ERROR: {result['error']}"
            print(f"   {status_emoji} {status_text} ({result['scan_duration']:.2f}s)")
        
        total_duration = time.time() - total_start_time
        
        # Generate summary
        summary = self._generate_summary(total_duration)
        
        return summary
    
    def _generate_summary(self, total_duration: float) -> Dict[str, Any]:
        """Generate scan summary."""
        total_resumes = len(self.scan_results)
        successful_scans = sum(1 for r in self.scan_results if r['success'])
        failed_scans = total_resumes - successful_scans
        
        safe_files = sum(1 for r in self.scan_results if r['status'] == 'SAFE')
        infected_files = sum(1 for r in self.scan_results if r['status'] == 'INFECTED')
        error_files = sum(1 for r in self.scan_results if r['status'] == 'ERROR')
        
        # Get system status
        system_status = self.orchestrator.get_scan_status()
        
        summary = {
            'success': True,
            'total_resumes': total_resumes,
            'scanned_resumes': successful_scans,
            'failed_scans': failed_scans,
            'scan_results': self.scan_results,
            'summary': {
                'safe_files': safe_files,
                'infected_files': infected_files,
                'error_files': error_files,
                'total_duration': total_duration,
                'average_scan_time': total_duration / successful_scans if successful_scans > 0 else 0
            },
            'system_status': system_status,
            'timestamp': time.time()
        }
        
        return summary
    
    def print_report(self, summary: Dict[str, Any]):
        """Print detailed scan report."""
        print("\n" + "=" * 60)
        print("📋 RESUME SECURITY SCAN REPORT")
        print("=" * 60)
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"   Total Resumes: {summary['total_resumes']}")
        print(f"   Successfully Scanned: {summary['scanned_resumes']}")
        print(f"   Failed Scans: {summary['failed_scans']}")
        
        print(f"\n🛡️ Scan Results:")
        print(f"   Safe Files: {summary['summary']['safe_files']}")
        print(f"   Infected Files: {summary['summary']['infected_files']}")
        print(f"   Error Files: {summary['summary']['error_files']}")
        
        print(f"\n⏱️ Performance:")
        print(f"   Total Duration: {summary['summary']['total_duration']:.2f}s")
        print(f"   Average Scan Time: {summary['summary']['average_scan_time']:.2f}s")
        
        # Detailed results
        print(f"\n📄 Detailed Results:")
        print("-" * 60)
        
        for result in summary['scan_results']:
            status_emoji = {
                'SAFE': '✅',
                'INFECTED': '🚨',
                'ERROR': '❌'
            }.get(result['status'], '❓')
            
            print(f"{status_emoji} {result['filename']}")
            print(f"   Status: {result['status']}")
            print(f"   Size: {result['file_size']:,} bytes")
            print(f"   MIME: {result['mime_type']}")
            print(f"   Time: {result['scan_duration']:.2f}s")
            
            if result['result_path']:
                print(f"   Path: {result['result_path']}")
            
            if result['error']:
                print(f"   Error: {result['error']}")
            
            print()
        
        # System status
        print(f"🖥️ System Status:")
        print(f"   Folders: {summary['system_status']['folders']}")
        print(f"   DB Checksum Valid: {summary['system_status']['db_checksum_valid']}")
        print(f"   Scheduler Active: {summary['system_status']['scheduler_active']}")
        print(f"   DB Version: {summary['system_status']['db_version']}")
        
        # Final recommendation
        if summary['summary']['infected_files'] > 0:
            print(f"\n⚠️ WARNING: {summary['summary']['infected_files']} infected file(s) detected!")
            print("   Please review the infected files and take appropriate action.")
        elif summary['failed_scans'] > 0:
            print(f"\n⚠️ WARNING: {summary['failed_scans']} scan(s) failed!")
            print("   Please check the error messages above.")
        else:
            print(f"\n🎉 All resumes scanned successfully! No threats detected.")
        
        print("\n" + "=" * 60)
    
    def save_results(self, summary: Dict[str, Any], filename: str = "resume_scan_results.json"):
        """Save scan results to JSON file."""
        results_file = Path(__file__).parent / filename
        
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")


def main():
    """Main entry point for resume scanning."""
    scanner = ResumeScanner()
    
    # Scan all resumes
    summary = scanner.scan_all_resumes()
    
    if not summary['success']:
        print(f"\n❌ Scan failed: {summary['error']}")
        sys.exit(1)
    
    # Print detailed report
    scanner.print_report(summary)
    
    # Save results
    scanner.save_results(summary)
    
    # Exit with appropriate code
    if summary['summary']['infected_files'] > 0 or summary['failed_scans'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()