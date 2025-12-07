"""
Resume Scan Test - Simple Version

Simple test to scan resumes without Unicode issues.
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import json

def scan_resume(resume_path: Path) -> Dict[str, Any]:
    """Simple resume scan."""
    start_time = time.time()
    
    try:
        # Read file
        with open(resume_path, 'rb') as f:
            file_bytes = f.read()
        
        # Get info
        file_size = len(file_bytes)
        
        # Simple validation
        if file_size == 0:
            status = "ERROR"
            error = "Empty file"
        elif file_size > 50 * 1024 * 1024:  # 50MB
            status = "ERROR"
            error = "File too large"
        else:
            status = "SAFE"
            error = None
        
        duration = time.time() - start_time
        
        return {
            'filename': resume_path.name,
            'status': status,
            'file_size': file_size,
            'scan_time': duration,
            'error': error
        }
        
    except Exception as e:
        duration = time.time() - start_time
        return {
            'filename': resume_path.name,
            'status': 'ERROR',
            'file_size': 0,
            'scan_time': duration,
            'error': str(e)
        }

def main():
    """Main function."""
    print("Resume Security Scan Test")
    print("=" * 40)
    
    # Find resumes
    project_root = Path(__file__).parent.parent.parent.parent
    resume_dir = project_root / "Resumes"
    
    if not resume_dir.exists():
        print("Error: Resumes directory not found")
        return
    
    resume_files = list(resume_dir.glob("*"))
    # Filter for actual resume files
    resume_files = [f for f in resume_files if f.is_file() and f.suffix.lower() in ['.pdf', '.doc', '.docx', '.txt', '.rtf']]
    
    if not resume_files:
        print("No resume files found")
        return
    
    print(f"Found {len(resume_files)} resume files")
    print()
    
    # Scan resumes
    results = []
    total_time = 0
    
    for i, resume_file in enumerate(resume_files, 1):
        print(f"Scanning {i}/{len(resume_files)}: {resume_file.name}")
        
        result = scan_resume(resume_file)
        results.append(result)
        total_time += result['scan_time']
        
        status_text = result['status']
        if result['error']:
            status_text += f" - {result['error']}"
        
        print(f"  Status: {status_text}")
        print(f"  Size: {result['file_size']} bytes")
        print(f"  Time: {result['scan_time']:.3f}s")
        print()
    
    # Summary
    safe_count = sum(1 for r in results if r['status'] == 'SAFE')
    error_count = sum(1 for r in results if r['status'] == 'ERROR')
    
    print("Scan Summary:")
    print(f"  Total files: {len(results)}")
    print(f"  Safe files: {safe_count}")
    print(f"  Error files: {error_count}")
    print(f"  Total time: {total_time:.3f}s")
    print(f"  Average time: {total_time/len(results):.3f}s")
    
    # Save results
    results_file = Path(__file__).parent / "resume_scan_test_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            'total_files': len(results),
            'safe_files': safe_count,
            'error_files': error_count,
            'total_time': total_time,
            'results': results
        }, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")

if __name__ == "__main__":
    main()