"""
Chatbot File Utilities
"""

import os
import zipfile
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path


def create_export_zip(
    excel_file_path: str,
    resume_files: List[str],
    metadata: Dict[str, Any],
    output_path: str
) -> bool:
    """
    Create ZIP file for export containing Excel, resumes, and metadata
    """
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add Excel file
            if os.path.exists(excel_file_path):
                zipf.write(excel_file_path, 'candidates.xlsx')
            
            # Add resume files
            for resume_path in resume_files:
                if os.path.exists(resume_path):
                    filename = os.path.basename(resume_path)
                    zipf.write(resume_path, f'resumes/{filename}')
            
            # Add metadata JSON
            metadata_path = os.path.join(tempfile.gettempdir(), 'metadata.json')
            import json
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            zipf.write(metadata_path, 'metadata.json')
            
            # Clean up temp metadata file
            os.remove(metadata_path)
        
        return True
    except Exception as e:
        print(f"Error creating ZIP file: {e}")
        return False


def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    if not os.path.exists(file_path):
        return 0.0
    
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    return round(size_mb, 2)


def ensure_directory(path: str) -> bool:
    """Ensure directory exists, create if it doesn't"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {path}: {e}")
        return False


def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return os.path.splitext(filename)[1].lower()


def is_allowed_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """Check if file type is allowed"""
    extension = get_file_extension(filename)
    return extension in allowed_extensions


def cleanup_temp_files(file_paths: List[str]) -> None:
    """Clean up temporary files"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up {file_path}: {e}")


def get_file_mime_type(file_path: str) -> Optional[str]:
    """Get MIME type based on file extension"""
    extension = get_file_extension(file_path)
    
    mime_types = {
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.txt': 'text/plain',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.zip': 'application/zip'
    }
    
    return mime_types.get(extension)


def validate_file_size(file_path: str, max_size_mb: int = 10) -> bool:
    """Validate file size is within limits"""
    size_mb = get_file_size_mb(file_path)
    return size_mb <= max_size_mb


def sanitize_filename(filename: str) -> str:
    """Remove unsafe characters from filename"""
    # Remove path separators and special characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename