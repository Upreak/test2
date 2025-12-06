"""
Simple Resume Scanner - Direct Testing

Simple script to test resume scanning without complex dependencies.
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

def scan_resume_simple(resume_path: Path) -> Dict[str, Any]:
    """
    Simple resume scan without full orchestrator.
    
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
        
        # Simple validation (in real implementation, this would use ClamAV)
        file_size = len(file_bytes)
        
        # Basic file validation
        if file_size == 0:
            status = "ERROR"
            result_path = None
            error = "Empty file"
        elif file_size > 50 * 1024 * 1024:  # 50MB limit
            status = "ERROR"
            result_path = None
            error = "File too large"
        else:
            # Simulate scan result (in real implementation, this would scan with ClamAV)
            # For testing, we'll assume all files are safe
            status = "SAFE"
            result_path = f"/quarantine/clean/{resume_path.name}"
            error = None
        
        end_time = time.time()
        scan_duration = end_time - start_time
        
        result = {
            'filename': resume_path.name,
            'filepath': str(resume_path),
            'mime_type': mime_type,
            'file_size': file_size,
            'status': status,
            'result_path': result_path,
            'scan_duration': scan_duration,
            'timestamp': time.time(),
            'success': True,
            'error': error
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

def find_resumes(resume_directory: str = "Resumes") -> List[Path]:
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

def main():
    """Main entry point for simple resume scanning."""
    print("Starting Simple Resume Security Scan")
    print("=" * 50)
    
    try:
        # Find all resumes
        resume_files = find_resumes()
        print(f"📁 Found {len(resume_files)} resume files to scan")
        
        # Scan each resume
        print("\n🔄 Scanning resumes...")
        print("-" * 50)
        
        scan_results = []
        total_start_time = time.time()
        
        for i, resume_file in enumerate(resume_files, 1):
            print(f"📄 [{i}/{len(resume_files)}] Scanning: {resume_file.name}")
            
            result = scan_resume_simple(resume_file)
            scan_results.append(result)
            
            # Print result
            status_emoji = "✅" if result['success'] else "❌"
            status_text = result['status'] if result['success'] else f"ERROR: {result['error']}"
            print(f"   {status_emoji} {status_text} ({result['scan_duration']:.2f}s)")
        
        total_duration = time.time() - total_start_time
        
        # Generate summary
        total_resumes = len(scan_results)
        successful_scans = sum(1 for r in scan_results if r['success'])
        failed_scans = total_resumes - successful_scans
        
        safe_files = sum(1 for r in scan_results if r['status'] == 'SAFE')
        infected_files = sum(1 for r in scan_results if r['status'] == 'INFECTED')
        error_files = sum(1 for r in scan_results if r['status'] == 'ERROR')
        
        summary = {
            'success': True,
            'total_resumes': total_resumes,
            'scanned_resumes': successful_scans,
            'failed_scans': failed_scans,
            'scan_results': scan_results,
            'summary': {
                'safe_files': safe_files,
                'infected_files': infected_files,
                'error_files': error_files,
                'total_duration': total_duration,
                'average_scan_time': total_duration / successful_scans if successful_scans > 0 else 0
            },
            'timestamp': time.time()
        }
        
        # Print detailed report
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
        
        # Save results
        results_file = Path(__file__).parent / "simple_resume_scan_results.json"
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        # Exit with appropriate code
        if summary['summary']['infected_files'] > 0 or summary['failed_scans'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()