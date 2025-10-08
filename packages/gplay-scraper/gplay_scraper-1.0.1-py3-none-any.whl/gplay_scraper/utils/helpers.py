from html import unescape
from typing import Any, List, Optional, Dict
from datetime import datetime, timezone
import re


def nested_lookup(obj: Any, key_list: List[int]) -> Any:
    """Safely navigate nested data structures using a list of keys/indices.
    
    Args:
        obj (Any): The data structure to navigate
        key_list (List[int]): List of keys/indices to traverse
        
    Returns:
        Any: The value at the nested location, or None if not found
    """
    current = obj
    for key in key_list:
        try:
            current = current[key]
        except (IndexError, KeyError, TypeError):
            return None
    return current


def unescape_text(s: Optional[str]) -> Optional[str]:
    """Unescape HTML entities and convert <br> tags to newlines.
    
    Args:
        s (Optional[str]): HTML string to unescape
        
    Returns:
        Optional[str]: Cleaned text or None if input is None
    """
    if s is None:
        return None
    # Convert <br> tags to newlines and unescape HTML entities
    return unescape(s.replace("<br>", "\r\n"))


def extract_categories(s: Any, categories: Optional[List[Dict]] = None) -> List[Dict]:
    """Recursively extract app categories from nested data structure.
    
    Args:
        s (Any): Data structure containing category information
        categories (Optional[List[Dict]]): Accumulator for found categories
        
    Returns:
        List[Dict]: List of category dictionaries with name and id
    """
    if categories is None:
        categories = []
    if not s:
        return categories
    
    # Check if this level contains category data
    if len(s) >= 4 and isinstance(s[0], str):
        categories.append({"name": s[0], "id": s[2]})
    else:
        # Recursively search nested structures
        for sub in s:
            extract_categories(sub, categories)
    return categories


def get_categories(s: Any) -> List[Dict]:
    """Get app categories from Play Store data structure.
    
    Args:
        s (Any): Play Store data structure
        
    Returns:
        List[Dict]: List of app categories with fallback to primary category
    """
    # Try to extract from detailed categories section
    categories = extract_categories(nested_lookup(s, [118]), None)
    
    # Fallback to primary category if no detailed categories found
    if not categories:
        categories.append(
            {
                "name": nested_lookup(s, [79, 0, 0, 0]),
                "id": nested_lookup(s, [79, 0, 0, 2]),
            }
        )
    return categories


def parse_release_date(release_date_str: Optional[str]) -> Optional[datetime]:
    """Parse release date string into datetime object.
    
    Args:
        release_date_str (Optional[str]): Date string in format "Mon DD, YYYY"
        
    Returns:
        Optional[datetime]: Parsed datetime or None if parsing fails
    """
    if release_date_str is None:
        return None
    try:
        return datetime.strptime(release_date_str, "%b %d, %Y")
    except (ValueError, TypeError):
        return None


def calculate_app_age(release_date_str: Optional[str], current_date: datetime) -> Optional[int]:
    """Calculate app age in days from release date to current date.
    
    Args:
        release_date_str (Optional[str]): Release date string
        current_date (datetime): Current date for calculation
        
    Returns:
        Optional[int]: Age in days or None if release date unavailable
    """
    release_date = parse_release_date(release_date_str)
    if release_date is None:
        return None
    
    # Ensure timezone consistency for accurate calculation
    if current_date.tzinfo is not None and release_date.tzinfo is None:
        release_date = release_date.replace(tzinfo=timezone.utc)
    
    days_since_release = (current_date - release_date).days
    return max(0, days_since_release)  # Ensure non-negative result


def parse_installs_string(installs_str: str) -> Optional[int]:
    """Parse install count string into integer.
    
    Args:
        installs_str (str): Install string like "1,000,000+"
        
    Returns:
        Optional[int]: Parsed install count or None if parsing fails
    """
    if installs_str is None:
        return None
    
    # Remove commas and plus signs
    cleaned_str = installs_str.replace(',', '').replace('+', '')
    try:
        return int(cleaned_str)
    except (ValueError, TypeError):
        return None


def calculate_daily_installs(install_count: Any, release_date_str: Optional[str], current_date: datetime) -> Optional[int]:
    """Calculate average daily installs since app release.
    
    Args:
        install_count (Any): Total install count (string or int)
        release_date_str (Optional[str]): App release date string
        current_date (datetime): Current date for calculation
        
    Returns:
        Optional[int]: Average daily installs or None if calculation impossible
    """
    # Parse install count if it's a string
    if isinstance(install_count, str):
        install_count = parse_installs_string(install_count)
    
    if install_count is None or release_date_str is None:
        return None
    
    release_date = parse_release_date(release_date_str)
    if release_date is None:
        return None
    
    # Ensure timezone consistency
    if current_date.tzinfo is not None and release_date.tzinfo is None:
        release_date = release_date.replace(tzinfo=timezone.utc)
    
    days_since_release = (current_date - release_date).days
    if days_since_release <= 0:
        return 0
    
    # Calculate average daily installs
    return int(install_count / days_since_release)


def calculate_monthly_installs(install_count: Any, release_date_str: Optional[str], current_date: datetime) -> Optional[int]:
    """Calculate average monthly installs since app release.
    
    Args:
        install_count (Any): Total install count (string or int)
        release_date_str (Optional[str]): App release date string
        current_date (datetime): Current date for calculation
        
    Returns:
        Optional[int]: Average monthly installs or None if calculation impossible
    """
    # Parse install count if it's a string
    if isinstance(install_count, str):
        install_count = parse_installs_string(install_count)
    
    if install_count is None or release_date_str is None:
        return None
    
    release_date = parse_release_date(release_date_str)
    if release_date is None:
        return None
    
    # Ensure timezone consistency
    if current_date.tzinfo is not None and release_date.tzinfo is None:
        release_date = release_date.replace(tzinfo=timezone.utc)
    
    days_since_release = (current_date - release_date).days
    if days_since_release <= 0:
        return 0
    
    # Calculate average monthly installs (365.25 days per year / 12 months = 30.44 days per month)
    months_since_release = days_since_release / 30.44
    return int(install_count / months_since_release)


def clean_json_string(json_str: str) -> str:
    """Clean and normalize malformed JSON string for parsing.
    
    Args:
        json_str (str): Raw JSON string that may have formatting issues
        
    Returns:
        str: Cleaned JSON string ready for parsing
    """
    # Remove sideChannel objects that cause parsing issues
    json_str = re.sub(r',\s*sideChannel:\s*\{\}', '', json_str)
    
    # Fix unquoted object keys (the main issue with Play Store data)
    json_str = re.sub(r'([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:', r'\1"\2":', json_str)
    
    # Handle malformed function calls and undefined values
    json_str = re.sub(r'\bfunction\s*\([^)]*\)\s*\{[^}]*\}', 'null', json_str)
    json_str = re.sub(r'\bundefined\b', 'null', json_str)
    
    # Convert single quotes to double quotes for string values
    json_str = re.sub(r":\s*'([^']*)\'", r': "\1"', json_str)
    
    # Handle malformed arrays with missing commas
    json_str = re.sub(r'(\])\s*(\[)', r'\1,\2', json_str)
    json_str = re.sub(r'(\})\s*(\{)', r'\1,\2', json_str)
    
    # Fix trailing commas before closing brackets
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # Fix multiple consecutive commas
    json_str = re.sub(r',,+', ',', json_str)
    
    # Handle malformed price/currency data (common in paid apps)
    json_str = re.sub(r':\s*\$([0-9.]+)', r': "$\1"', json_str)
    
    # Fix missing quotes around numeric strings that should be strings
    json_str = re.sub(r'"version"\s*:\s*([0-9.]+)(?=\s*[,}])', r'"version": "\1"', json_str)
    
    return json_str