from typing import Any, Callable, List, Optional
import html
from ..utils.helpers import nested_lookup, unescape_text, get_categories


class ElementSpec:
    """Specification for extracting data from Google Play Store response.
    
    Defines how to navigate nested data structures and process extracted values.
    """
    
    def __init__(
        self,
        ds_num: Optional[int],
        data_map: List[int],
        post_processor: Callable = None,
        fallback_value: Any = None,
    ):
        """Initialize element specification.
        
        Args:
            ds_num (Optional[int]): Data section number (None for main data)
            data_map (List[int]): Path of indices to navigate nested structure
            post_processor (Callable): Function to process extracted value
            fallback_value (Any): Default value if extraction fails
        """
        self.ds_num = ds_num
        self.data_map = data_map
        self.post_processor = post_processor
        self.fallback_value = fallback_value

    def extract_content(self, source: dict) -> Any:
        """Extract and process content from source data.
        
        Args:
            source (dict): Source data structure from Play Store
            
        Returns:
            Any: Extracted and processed value or fallback value
        """
        try:
            # Navigate to the target data location
            if self.ds_num is None:
                result = nested_lookup(source.get("data", {}), self.data_map)
            else:
                result = nested_lookup(source, self.data_map)
            
            # Apply post-processing if specified
            if self.post_processor is not None:
                try:
                    result = self.post_processor(result)
                except Exception:
                    # If post-processing fails, return the raw result
                    pass
        except (KeyError, IndexError, TypeError, AttributeError):
            # Handle extraction failures with fallback values
            if isinstance(self.fallback_value, ElementSpec):
                result = self.fallback_value.extract_content(source)
            else:
                result = self.fallback_value
        return result


def _process_description(s):
    """Extract and clean app description text.
    
    Args:
        s: Source data structure containing description
        
    Returns:
        str: Cleaned description text or None if not found
    """
    # Try primary description location
    desc_text = nested_lookup(s, [72, 0, 0])
    if not desc_text:
        # Try fallback description location
        desc_text = nested_lookup(s, [72, 0, 1])
    
    if desc_text:
        # Unescape HTML and remove line breaks
        cleaned = unescape_text(desc_text)
        return cleaned.replace('\n', '').replace('\r', '') if cleaned else None
    return None


def _process_permissions(perms):
    """Process permissions data from Play Store response.
    
    Args:
        perms: Raw permissions data structure
        
    Returns:
        dict: Organized permissions by category with details
    """
    if not perms or len(perms) <= 2:
        return {}
    
    permissions = {}
    # Navigate through permission sections
    for section in perms[2]:
        if not section:
            continue
        
        # Extract individual permissions
        for perm in section:
            if perm and perm[0]:
                perm_name = perm[0]  # Permission category name
                # Extract permission details/descriptions
                perm_details = [detail[1] for detail in perm[2]] if perm[2] else []
                permissions[perm_name] = perm_details
    
    return permissions


class ElementSpecs:
    """Collection of element specifications for extracting Play Store data.
    
    Contains mapping definitions for all supported app data fields including
    basic info, ratings, technical details, media content, and developer info.
    """
    
    # Dictionary mapping field names to their extraction specifications
    Detail = {
        "title": ElementSpec(None, [1, 2, 0, 0]),
        "description": ElementSpec(
            None,
            [1, 2],
            lambda s: _process_description(s),
        ),
        "summary": ElementSpec(None, [1, 2, 73, 0, 1], unescape_text),
        "installs": ElementSpec(None, [1, 2, 13, 0]),
        "minInstalls": ElementSpec(None, [1, 2, 13, 1]),
        "realInstalls": ElementSpec(None, [1, 2, 13, 2]),
        "score": ElementSpec(None, [1, 2, 51, 0, 1]),
        "ratings": ElementSpec(None, [1, 2, 51, 2, 1]),
        "reviews": ElementSpec(None, [1, 2, 51, 3, 1]),
        "histogram": ElementSpec(
            None,
            [1, 2, 51, 1],
            lambda container: [
                container[1][1],
                container[2][1],
                container[3][1],
                container[4][1],
                container[5][1],
            ],
            [0, 0, 0, 0, 0],
        ),
        "price": ElementSpec(
            None, [1, 2, 57, 0, 0, 0, 0, 1, 0, 0], lambda price: (price / 1000000) or 0
        ),
        "free": ElementSpec(None, [1, 2, 57, 0, 0, 0, 0, 1, 0, 0], lambda s: s == 0),
        "currency": ElementSpec(None, [1, 2, 57, 0, 0, 0, 0, 1, 0, 1]),
        "sale": ElementSpec(None, [1, 2, 57, 0, 0, 0, 0, 14, 0, 0], bool, False),
        "originalPrice": ElementSpec(None, [1, 2, 57, 0, 0, 0, 0, 1, 1, 0], lambda price: (price / 1000000) if price else None),
        "offersIAP": ElementSpec(None, [1, 2, 19, 0], bool, False),
        "inAppProductPrice": ElementSpec(None, [1, 2, 19, 0]),
        "developer": ElementSpec(None, [1, 2, 68, 0]),
        "developerId": ElementSpec(None, [1, 2, 68, 1, 4, 2], lambda s: s.split("id=")[1] if s and "id=" in s else None),
        "developerEmail": ElementSpec(None, [1, 2, 69, 1, 0]),
        "developerWebsite": ElementSpec(None, [1, 2, 69, 0, 5, 2]),
        "developerAddress": ElementSpec(None, [1, 2, 69, 4, 2, 0]),
        "developerPhone": ElementSpec(None, [1, 2, 69, 4, 3]),
        "privacyPolicy": ElementSpec(None, [1, 2, 99, 0, 5, 2]),
        "genre": ElementSpec(None, [1, 2, 79, 0, 0, 0]),
        "genreId": ElementSpec(None, [1, 2, 79, 0, 0, 2]),
        "categories": ElementSpec(None, [1, 2], lambda s: [cat['name'] for cat in get_categories(s) if cat['name']], []),
        "icon": ElementSpec(None, [1, 2, 95, 0, 3, 2], lambda url: f"{url}=w9999" if url else None),
        "headerImage": ElementSpec(None, [1, 2, 96, 0, 3, 2], lambda url: f"{url}=w9999" if url else None),
        "screenshots": ElementSpec(
            None, [1, 2, 78, 0], lambda container: [f"{item[3][2]}=w9999" for item in container] if container else [], []
        ),
        "video": ElementSpec(None, [1, 2, 100, 0, 0, 3, 2]),
        "videoImage": ElementSpec(None, [1, 2, 100, 1, 0, 3, 2], lambda url: f"{url}=w9999" if url else None),
        "contentRating": ElementSpec(None, [1, 2, 9, 0]),
        "contentRatingDescription": ElementSpec(None, [1, 2, 9, 6, 1]),
        "appId": ElementSpec(None, [1, 2, 1, 0, 0]),
        "url": ElementSpec(None, [1, 2, 1, 0, 0], lambda app_id: f"https://play.google.com/store/apps/details?id={app_id}" if app_id else None),
        "adSupported": ElementSpec(None, [1, 2, 48], bool),
        "containsAds": ElementSpec(None, [1, 2, 48], bool, False),
        "released": ElementSpec(None, [1, 2, 10, 0]),
        "lastUpdatedOn": ElementSpec(None, [1, 2, 145, 0, 0]),
        "updated": ElementSpec(None, [1, 2, 145, 0, 1, 0]),
        "version": ElementSpec(
            None, [1, 2, 140, 0, 0, 0], fallback_value="Varies with device"
        ),
        "androidVersion": ElementSpec(None, [1, 11, 0, 1]),
        "permissions": ElementSpec(None, [1, 2, 74], _process_permissions),
        "dataSafety": ElementSpec(None, [1, 2, 136], lambda data: [item[1] for item in data[1] if item and len(item) > 1] if data and len(data) > 1 and data[1] else []),
        "appBundle": ElementSpec(None, [1, 2, 77, 0]),
        "maxandroidapi": ElementSpec(None, [1, 2, 140, 1, 0, 0, 0]),
        "minandroidapi": ElementSpec(None, [1, 2, 140, 1, 1, 0, 0, 0]),
        "whatsNew": ElementSpec(None, [1, 2, 144, 1, 1], lambda x: [line.strip() for line in html.unescape(x).split('<br>') if line.strip()] if x else []),
        "available": ElementSpec(None, [1, 2, 18, 0], bool, False),
    }