"""
Chatbot Time Utilities
"""

from datetime import datetime, timedelta
from typing import Optional


def get_utc_now() -> datetime:
    """Get current UTC datetime"""
    return datetime.utcnow()


def format_timestamp(dt: datetime) -> str:
    """Format datetime as ISO string"""
    return dt.isoformat()


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO timestamp string to datetime"""
    return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))


def is_fresh(timestamp: datetime, freshness_days: int = 30) -> bool:
    """Check if timestamp is within freshness period"""
    return (get_utc_now() - timestamp).days < freshness_days


def add_days(dt: datetime, days: int) -> datetime:
    """Add days to datetime"""
    return dt + timedelta(days=days)


def get_age_in_days(timestamp: datetime) -> int:
    """Get age of timestamp in days"""
    return (get_utc_now() - timestamp).days