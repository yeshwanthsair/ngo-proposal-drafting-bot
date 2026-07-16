"""
Utility functions for datetime formatting.
"""
from datetime import datetime


def get_human_readable_timestamp() -> str:
    """
    Get current timestamp in human-readable format.
    
    Returns:
        str: Formatted timestamp like "May 6, 2026 at 7:34 PM"
    """
    now = datetime.now()
    return now.strftime("%B %d, %Y at %I:%M %p")


def format_iso_to_human(iso_timestamp: str) -> str:
    """
    Convert ISO timestamp to human-readable format.
    
    Args:
        iso_timestamp: ISO format timestamp string
        
    Returns:
        str: Human-readable timestamp
    """
    try:
        # Parse ISO timestamp (handles both with and without microseconds)
        if 'T' in iso_timestamp:
            # Remove timezone info if present and parse
            clean_timestamp = iso_timestamp.split('+')[0].split('Z')[0]
            if '.' in clean_timestamp:
                dt = datetime.fromisoformat(clean_timestamp)
            else:
                dt = datetime.fromisoformat(clean_timestamp)
        else:
            # Handle simple date format
            dt = datetime.fromisoformat(iso_timestamp)
            
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except (ValueError, AttributeError):
        # Fallback to original if parsing fails
        return iso_timestamp


def get_relative_time(iso_timestamp: str) -> str:
    """
    Get relative time description (e.g., "2 minutes ago").
    
    Args:
        iso_timestamp: ISO format timestamp string
        
    Returns:
        str: Relative time description
    """
    try:
        # Parse timestamp
        clean_timestamp = iso_timestamp.split('+')[0].split('Z')[0]
        if '.' in clean_timestamp:
            dt = datetime.fromisoformat(clean_timestamp)
        else:
            dt = datetime.fromisoformat(clean_timestamp)
            
        now = datetime.now()
        diff = now - dt
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:  # Less than 1 hour
            minutes = int(seconds // 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:  # Less than 1 day
            hours = int(seconds // 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif seconds < 604800:  # Less than 1 week
            days = int(seconds // 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
        else:
            # For older entries, show the full date
            return dt.strftime("%B %d, %Y")
            
    except (ValueError, AttributeError):
        return iso_timestamp