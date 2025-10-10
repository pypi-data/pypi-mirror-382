"""
Pagination utilities for Enkrypt AI SDK.

This module provides helper functions for handling pagination in API requests and responses.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from urllib.parse import urlencode, parse_qs, urlparse, urlunparse
from ..response import PaginationInfo, PaginatedResponse


def parse_pagination_params(
    query_string: str = "", 
    default_page: int = 1, 
    default_per_page: int = 10
) -> PaginationInfo:
    """
    Parse pagination parameters from a query string.
    
    Args:
        query_string (str): URL query string (e.g., "page=2&per_page=20")
        default_page (int): Default page number if not specified
        default_per_page (int): Default items per page if not specified
        
    Returns:
        PaginationInfo: Parsed pagination information
        
    Example:
        >>> parse_pagination_params("page=2&per_page=20")
        PaginationInfo(page=2, per_page=20, total_count=0)
    """
    if not query_string:
        return PaginationInfo(default_page, default_per_page)
    
    # Parse query string
    params = parse_qs(query_string)
    
    # Extract pagination parameters
    page = params.get("page", [str(default_page)])[0]
    per_page = params.get("per_page", [str(default_per_page)])[0]
    
    try:
        page_num = int(page)
        per_page_num = int(per_page)
    except (ValueError, TypeError):
        page_num = default_page
        per_page_num = default_per_page
    
    # Validate and create PaginationInfo
    return PaginationInfo(
        page=max(1, page_num),
        per_page=max(1, min(100, per_page_num)),
        total_count=0
    )


def build_pagination_url(
    base_url: str, 
    page: int, 
    per_page: int, 
    **additional_params
) -> str:
    """
    Build a URL with pagination parameters.
    
    Args:
        base_url (str): Base URL without query parameters
        page (int): Page number
        per_page (int): Items per page
        **additional_params: Additional query parameters
        
    Returns:
        str: Complete URL with pagination parameters
        
    Example:
        >>> build_pagination_url("https://api.example.com/users", 2, 20, status="active")
        'https://api.example.com/users?page=2&per_page=20&status=active'
    """
    params = {
        "page": page,
        "per_page": per_page,
        **additional_params
    }
    
    # Filter out None values
    params = {k: v for k, v in params.items() if v is not None}
    
    query_string = urlencode(params)
    return f"{base_url}?{query_string}" if query_string else base_url


def create_paginated_response(
    data: List[Any],
    total_count: int,
    page: int = 1,
    per_page: int = 10,
    **additional_data
) -> PaginatedResponse:
    """
    Create a paginated response object.
    
    Args:
        data (List[Any]): List of items for the current page
        total_count (int): Total number of items across all pages
        page (int): Current page number
        per_page (int): Items per page
        **additional_data: Additional data to include in the response
        
    Returns:
        PaginatedResponse: Paginated response object
        
    Example:
        >>> users = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
        >>> response = create_paginated_response(users, 100, 1, 10)
        >>> response.get_page()
        1
        >>> response.get_total_count()
        100
    """
    pagination = PaginationInfo(page, per_page, total_count)
    return PaginatedResponse(data, pagination, **additional_data)


def validate_pagination_params(
    page: Union[str, int, None], 
    per_page: Union[str, int, None]
) -> Tuple[int, int]:
    """
    Validate pagination parameters and return validated values.
    
    Args:
        page: Page number (can be string, int, or None)
        per_page: Items per page (can be string, int, or None)
        
    Returns:
        Tuple[int, int]: Validated (page, per_page) values
        
    Raises:
        ValueError: If parameters are invalid
        
    Example:
        >>> validate_pagination_params("2", "20")
        (2, 20)
        >>> validate_pagination_params(None, None)
        (1, 10)
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


def get_pagination_metadata(
    total_count: int, 
    page: int, 
    per_page: int
) -> Dict[str, Any]:
    """
    Generate pagination metadata for API responses.
    
    Args:
        total_count (int): Total number of items
        page (int): Current page number
        per_page (int): Items per page
        
    Returns:
        Dict[str, Any]: Pagination metadata dictionary
        
    Example:
        >>> get_pagination_metadata(100, 2, 20)
        {
            'page': 2,
            'per_page': 20,
            'total_count': 100,
            'total_pages': 5,
            'has_next': True,
            'has_previous': True
        }
    """
    pagination = PaginationInfo(page, per_page, total_count)
    return pagination.to_dict()


def calculate_page_info(
    total_count: int, 
    page: int, 
    per_page: int
) -> Dict[str, Any]:
    """
    Calculate detailed pagination information.
    
    Args:
        total_count (int): Total number of items
        page (int): Current page number
        per_page (int): Items per page
        
    Returns:
        Dict[str, Any]: Detailed pagination information
        
    Example:
        >>> calculate_page_info(100, 2, 20)
        {
            'current_page': 2,
            'per_page': 20,
            'total_count': 100,
            'total_pages': 5,
            'has_next': True,
            'has_previous': True,
            'offset': 20,
            'limit': 20,
            'start_item': 21,
            'end_item': 40
        }
    """
    pagination = PaginationInfo(page, per_page, total_count)
    
    start_item = (page - 1) * per_page + 1
    end_item = min(page * per_page, total_count)
    
    return {
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'total_count': pagination.total_count,
        'total_pages': pagination.total_pages,
        'has_next': pagination.has_next,
        'has_previous': pagination.has_previous,
        'offset': pagination.offset,
        'limit': pagination.limit,
        'start_item': start_item if total_count > 0 else 0,
        'end_item': end_item if total_count > 0 else 0
    }


def create_pagination_links(
    base_url: str,
    current_page: int,
    total_pages: int,
    per_page: int,
    **additional_params
) -> Dict[str, Optional[str]]:
    """
    Create pagination links for navigation.
    
    Args:
        base_url (str): Base URL for the endpoint
        current_page (int): Current page number
        total_pages (int): Total number of pages
        per_page (int): Items per page
        **additional_params: Additional query parameters
        
    Returns:
        Dict[str, Optional[str]]: Dictionary with pagination links
        
    Example:
        >>> links = create_pagination_links("https://api.example.com/users", 2, 5, 20)
        >>> links
        {
            'first': 'https://api.example.com/users?page=1&per_page=20',
            'previous': 'https://api.example.com/users?page=1&per_page=20',
            'current': 'https://api.example.com/users?page=2&per_page=20',
            'next': 'https://api.example.com/users?page=3&per_page=20',
            'last': 'https://api.example.com/users?page=5&per_page=20'
        }
    """
    links = {}
    
    # First page
    links['first'] = build_pagination_url(base_url, 1, per_page, **additional_params)
    
    # Previous page
    if current_page > 1:
        links['previous'] = build_pagination_url(base_url, current_page - 1, per_page, **additional_params)
    else:
        links['previous'] = None
    
    # Current page
    links['current'] = build_pagination_url(base_url, current_page, per_page, **additional_params)
    
    # Next page
    if current_page < total_pages:
        links['next'] = build_pagination_url(base_url, current_page + 1, per_page, **additional_params)
    else:
        links['next'] = None
    
    # Last page
    if total_pages > 0:
        links['last'] = build_pagination_url(base_url, total_pages, per_page, **additional_params)
    else:
        links['last'] = None
    
    return links


def apply_pagination_to_list(
    data: List[Any], 
    page: int, 
    per_page: int
) -> Tuple[List[Any], int]:
    """
    Apply pagination to a list of data.
    
    Args:
        data (List[Any]): Complete list of data
        page (int): Page number (1-based)
        per_page (int): Items per page
        
    Returns:
        Tuple[List[Any], int]: (paginated_data, total_count)
        
    Example:
        >>> all_users = [{"id": i, "name": f"User{i}"} for i in range(1, 101)]
        >>> page_data, total = apply_pagination_to_list(all_users, 2, 20)
        >>> len(page_data)
        20
        >>> total
        100
    """
    total_count = len(data)
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    
    paginated_data = data[start_index:end_index]
    return paginated_data, total_count


def format_pagination_response(
    data: List[Any],
    total_count: int,
    page: int,
    per_page: int,
    include_links: bool = True,
    base_url: str = "",
    **additional_data
) -> Dict[str, Any]:
    """
    Format a complete paginated response.
    
    Args:
        data (List[Any]): List of items for the current page
        total_count (int): Total number of items
        page (int): Current page number
        per_page (int): Items per page
        include_links (bool): Whether to include pagination links
        base_url (str): Base URL for generating pagination links
        **additional_data: Additional data to include
        
    Returns:
        Dict[str, Any]: Formatted paginated response
        
    Example:
        >>> response = format_pagination_response(
        ...     [{"id": 1, "name": "John"}], 
        ...     100, 1, 10, 
        ...     base_url="https://api.example.com/users"
        ... )
        >>> response.keys()
        dict_keys(['data', 'pagination', 'links'])
    """
    # Create pagination metadata
    pagination = get_pagination_metadata(total_count, page, per_page)
    
    # Build response
    response = {
        "data": data,
        "pagination": pagination,
        **additional_data
    }
    
    # Add pagination links if requested
    if include_links and base_url:
        links = create_pagination_links(
            base_url, page, pagination['total_pages'], per_page
        )
        response["links"] = links
    
    return response
