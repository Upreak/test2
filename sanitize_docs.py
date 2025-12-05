#!/usr/bin/env python3
"""
Script to sanitize sensitive information from documentation files.
Removes API keys and other secrets that triggered GitHub push protection.
"""

import re
import os

def sanitize_file(file_path):
    """Remove sensitive information from a file."""
    if not os.path.exists(file_path):
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patterns to remove sensitive information
    patterns = [
        # API keys
        (r'gsk_[a-zA-Z0-9]+', 'gsk_[REDACTED_API_KEY]'),
        (r'groq_api_key\s*=\s*[\'"][^\'"]*[\'"]', 'groq_api_key = "[REDACTED_API_KEY]"'),
        (r'GROQ_API_KEY\s*=\s*[\'"][^\'"]*[\'"]', 'GROQ_API_KEY = "[REDACTED_API_KEY]"'),
        
        # OpenRouter keys
        (r'openrouter-api-key\s*:\s*[\'"][^\'"]*[\'"]', 'openrouter-api-key: "[REDACTED_API_KEY]"'),
        (r'OPENROUTER_API_KEY\s*=\s*[\'"][^\'"]*[\'"]', 'OPENROUTER_API_KEY = "[REDACTED_API_KEY]"'),
        
        # Other common API key patterns
        (r'api_key\s*=\s*[\'"][^\'"]*[\'"]', 'api_key = "[REDACTED_API_KEY]"'),
        (r'API_KEY\s*=\s*[\'"][^\'"]*[\'"]', 'API_KEY = "[REDACTED_API_KEY]"'),
        
        # URLs with keys
        (r'https://[^\'"\s]*api_key=[^\'"\s]*', '[REDACTED_URL_WITH_API_KEY]'),
        
        # JWT secrets
        (r'JWT_SECRET\s*=\s*[\'"][^\'"]*[\'"]', 'JWT_SECRET = "[REDACTED_JWT_SECRET]"'),
        
        # Database URLs
        (r'postgresql://[^\'"\s]*', 'postgresql://[REDACTED_DB_URL]'),
        
        # Email credentials
        (r'SMTP_PASSWORD\s*=\s*[\'"][^\'"]*[\'"]', 'SMTP_PASSWORD = "[REDACTED_SMTP_PASSWORD]"'),
        
        # Phone numbers (for WhatsApp)
        (r'\+\d{10,15}', '[REDACTED_PHONE_NUMBER]'),
        
        # Email addresses
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]'),
    ]
    
    original_content = content
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Sanitized: {file_path}")
    else:
        print(f"No changes needed: {file_path}")

def main():
    """Sanitize sensitive files."""
    files_to_sanitize = [
        'DOCS/CONSOLIDATED_DOCUMENTATION.md',
        'DOCS/ORIGINAL_MD_BACKUPS/DOCS/CONSOLIDATED_DOCUMENTATION.md',
        'cleanup_backups/test2/test_all_apis.py',
        'cleanup_backups/test2/test_resume_parser.py'
    ]
    
    for file_path in files_to_sanitize:
        sanitize_file(file_path)

if __name__ == "__main__":
    main()