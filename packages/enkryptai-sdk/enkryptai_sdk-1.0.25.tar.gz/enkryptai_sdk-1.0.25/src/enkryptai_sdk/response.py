import math
from typing import Dict, Any, List, Optional, Union


class PaginationInfo:
    """
    A class to handle pagination information and calculations.
    """
    
    def __init__(self, page: int = 1, per_page: int = 10, total_count: int = 0):
        """
        Initialize pagination information.
        
        Args:
            page (int): Current page number (1-based)
            per_page (int): Number of items per page
            total_count (int): Total number of items
        """
        self.page = max(1, page)
        self.per_page = max(1, min(100, per_page))  # Ensure per_page is between 1 and 100
        self.total_count = max(0, total_count)
        
    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        if self.total_count == 0:
            return 0
        return math.ceil(self.total_count / self.per_page)
    
    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.total_pages
    
    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1
    
    @property
    def offset(self) -> int:
        """Calculate the offset for database queries."""
        return (self.page - 1) * self.per_page
    
    @property
    def limit(self) -> int:
        """Get the limit for database queries."""
        return self.per_page
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pagination info to dictionary."""
        return {
            "page": self.page,
            "per_page": self.per_page,
            "total_count": self.total_count,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_previous": self.has_previous
        }
    
    @classmethod
    def from_query_params(cls, query_params: Dict[str, Any], default_per_page: int = 10) -> "PaginationInfo":
        """
        Create PaginationInfo from query parameters.
        
        Args:
            query_params (Dict[str, Any]): Dictionary containing query parameters
            default_per_page (int): Default items per page
            
        Returns:
            PaginationInfo: Pagination information object
        """
        try:
            page = int(query_params.get("page", 1))
            per_page = int(query_params.get("per_page", default_per_page))
        except (ValueError, TypeError):
            page = 1
            per_page = default_per_page
            
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = min(max(1, per_page), 100)
            
        return cls(page=page, per_page=per_page)
    
    @classmethod
    def validate_params(cls, page: Union[str, int], per_page: Union[str, int]) -> tuple[int, int]:
        """
        Validate pagination parameters and return validated values.
        
        Args:
            page: Page number (can be string or int)
            per_page: Items per page (can be string or int)
            
        Returns:
            tuple[int, int]: Validated (page, per_page) values
            
        Raises:
            ValueError: If parameters are invalid
        """
        try:
            page_num = int(page) if page is not None else 1
            per_page_num = int(per_page) if per_page is not None else 10
        except (ValueError, TypeError):
            raise ValueError("Page and per_page must be valid integers")
        
        if page_num < 1:
            raise ValueError("Page must be >= 1")
        if per_page_num < 1 or per_page_num > 100:
            raise ValueError("Per_page must be between 1 and 100")
            
        return page_num, per_page_num


class PaginatedResponse(dict):
    """
    A wrapper class for paginated API responses that provides pagination information
    and maintains backward compatibility with dictionary access.
    """
    
    def __init__(self, data: List[Any], pagination: PaginationInfo, **kwargs):
        """
        Initialize the PaginatedResponse object.
        
        Args:
            data (List[Any]): List of items for the current page
            pagination (PaginationInfo): Pagination information
            **kwargs: Additional response data
        """
        response_data = {
            "data": data,
            "pagination": pagination.to_dict(),
            **kwargs
        }
        super().__init__(response_data)
        self._data = response_data
        self._pagination = pagination
    
    def get_data(self) -> List[Any]:
        """Get the data items for the current page."""
        return self._data.get("data", [])
    
    def get_pagination(self) -> Dict[str, Any]:
        """Get pagination information."""
        return self._data.get("pagination", {})
    
    def get_page(self) -> int:
        """Get current page number."""
        return self._pagination.page
    
    def get_per_page(self) -> int:
        """Get items per page."""
        return self._pagination.per_page
    
    def get_total_count(self) -> int:
        """Get total number of items."""
        return self._pagination.total_count
    
    def get_total_pages(self) -> int:
        """Get total number of pages."""
        return self._pagination.total_pages
    
    def has_next_page(self) -> bool:
        """Check if there's a next page."""
        return self._pagination.has_next
    
    def has_previous_page(self) -> bool:
        """Check if there's a previous page."""
        return self._pagination.has_previous
    
    def get_next_page_url(self, base_url: str, **query_params) -> Optional[str]:
        """
        Generate URL for the next page.
        
        Args:
            base_url (str): Base URL for the endpoint
            **query_params: Additional query parameters to include
            
        Returns:
            Optional[str]: Next page URL or None if no next page
        """
        if not self.has_next_page():
            return None
            
        params = {**query_params, "page": self.get_page() + 1, "per_page": self.get_per_page()}
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    
    def get_previous_page_url(self, base_url: str, **query_params) -> Optional[str]:
        """
        Generate URL for the previous page.
        
        Args:
            base_url (str): Base URL for the endpoint
            **query_params: Additional query parameters to include
            
        Returns:
            Optional[str]: Previous page URL or None if no previous page
        """
        if not self.has_previous_page():
            return None
            
        params = {**query_params, "page": self.get_page() - 1, "per_page": self.get_per_page()}
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    
    def get_page_urls(self, base_url: str, **query_params) -> Dict[str, Optional[str]]:
        """
        Generate URLs for all pagination actions.
        
        Args:
            base_url (str): Base URL for the endpoint
            **query_params: Additional query parameters to include
            
        Returns:
            Dict[str, Optional[str]]: Dictionary with pagination URLs
        """
        return {
            "first": f"{base_url}?{self._build_query_string(1, **query_params)}",
            "previous": self.get_previous_page_url(base_url, **query_params),
            "current": f"{base_url}?{self._build_query_string(self.get_page(), **query_params)}",
            "next": self.get_next_page_url(base_url, **query_params),
            "last": f"{base_url}?{self._build_query_string(self.get_total_pages(), **query_params)}" if self.get_total_pages() > 0 else None
        }
    
    def _build_query_string(self, page: int, **query_params) -> str:
        """Build query string for a specific page."""
        params = {**query_params, "page": page, "per_page": self.get_per_page()}
        return "&".join([f"{k}={v}" for k, v in params.items()])
    
    def __str__(self) -> str:
        """String representation of the paginated response."""
        return f"PaginatedResponse(page={self.get_page()}, per_page={self.get_per_page()}, total={self.get_total_count()}, items={len(self.get_data())})"


class GuardrailsResponse(dict):
    """
    A wrapper class for Enkrypt AI API responses that provides additional functionality
    while maintaining backward compatibility with dictionary access.
    """
    
    def __init__(self, response_data: dict):
        """
        Initialize the Response object with API response data.
        
        Args:
            response_data (dict): The raw API response dictionary
        """
        super().__init__(response_data)
        self._data = response_data

    def get_summary(self) -> dict:
        """
        Get the summary section of the response.
        
        Returns:
            dict: The summary data or empty dict if not found
        """
        return self._data.get("summary", {})

    def get_details(self) -> dict:
        """
        Get the details section of the response.
        
        Returns:
            dict: The details data or empty dict if not found
        """
        return self._data.get("details", {})

    def has_violations(self) -> bool:
        """
        Check if any detectors found violations in the content.
        
        Returns:
            bool: True if any detector reported a violation (score > 0), False otherwise
        """
        summary = self.get_summary()
        for key, value in summary.items():
            if key == "toxicity" and isinstance(value, list) and len(value) > 0:
                return True
            elif isinstance(value, (int, float)) and value > 0:
                return True
        return False

    def get_violations(self) -> list[str]:
        """
        Get a list of detector names that found violations.
        
        Returns:
            list[str]: Names of detectors that reported violations
        """
        summary = self.get_summary()
        violations = []
        for detector, value in summary.items():
            if detector == "toxicity" and isinstance(value, list) and len(value) > 0:
                violations.append(detector)
            elif isinstance(value, (int, float)) and value > 0:
                violations.append(detector)
        return violations

    def is_safe(self) -> bool:
        """
        Check if the content is safe (no violations detected).
        
        Returns:
            bool: True if no violations were detected, False otherwise
        """
        return not self.has_violations()
    
    def is_attack(self) -> bool:
        """
        Check if the content is attacked (violations detected).
        
        Returns:
            bool: True if violations were detected, False otherwise
        """
        return self.has_violations()

    def __str__(self) -> str:
        """
        String representation of the response.
        
        Returns:
            str: A formatted string showing summary and violation status
        """
        violations = self.get_violations()
        status = "UNSAFE" if violations else "SAFE"
        
        if violations:
            violation_str = f"Violations detected: {', '.join(violations)}"
        else:
            violation_str = "No violations detected"
            
        return f"Response Status: {status}\n{violation_str}"
    
    def get_pagination(self) -> Optional[Dict[str, Any]]:
        """
        Get pagination information if available.
        
        Returns:
            Optional[Dict[str, Any]]: Pagination data or None if not available
        """
        return self._data.get("pagination")
    
    def is_paginated(self) -> bool:
        """
        Check if the response contains pagination information.
        
        Returns:
            bool: True if response is paginated, False otherwise
        """
        return "pagination" in self._data


class PIIResponse(dict):
    """
    A wrapper class for Enkrypt AI PII API responses that provides additional functionality
    while maintaining backward compatibility with dictionary access.
    """ 
    
    def __init__(self, response_data: dict):
        """
        Initialize the Response object with API response data.
        
        Args:
            response_data (dict): The raw API response dictionary
        """ 
        super().__init__(response_data)
        self._data = response_data

    def get_text(self) -> str:
        """
        Get the text section of the response.
        
        Returns:
            str: The text data or empty string if not found
        """ 
        return self._data.get("text", "")

    def get_key(self) -> str:
        """
        Get the key section of the response.
        """ 
        return self._data.get("key", "")
    
    def get_pagination(self) -> Optional[Dict[str, Any]]:
        """
        Get pagination information if available.
        
        Returns:
            Optional[Dict[str, Any]]: Pagination data or None if not available
        """
        return self._data.get("pagination")
    
    def is_paginated(self) -> bool:
        """
        Check if the response contains pagination information.
        
        Returns:
            bool: True if response is paginated, False otherwise
        """
        return "pagination" in self._data 
    
    