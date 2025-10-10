"""
Tests for pagination functionality in Enkrypt AI SDK.
"""

import pytest
from enkryptai_sdk.utils.pagination import (
    PaginationInfo,
    PaginatedResponse,
    parse_pagination_params,
    build_pagination_url,
    create_paginated_response,
    validate_pagination_params,
    get_pagination_metadata,
    calculate_page_info,
    create_pagination_links,
    apply_pagination_to_list,
    format_pagination_response
)


class TestPaginationInfo:
    """Test PaginationInfo class."""
    
    def test_basic_initialization(self):
        """Test basic initialization of PaginationInfo."""
        pagination = PaginationInfo(page=1, per_page=10, total_count=100)
        
        assert pagination.page == 1
        assert pagination.per_page == 10
        assert pagination.total_count == 100
        assert pagination.total_pages == 10
        assert pagination.has_next is True
        assert pagination.has_previous is False
        assert pagination.offset == 0
        assert pagination.limit == 10
    
    def test_edge_cases(self):
        """Test edge cases for pagination."""
        # Zero total count
        pagination = PaginationInfo(page=1, per_page=10, total_count=0)
        assert pagination.total_pages == 0
        assert pagination.has_next is False
        assert pagination.has_previous is False
        
        # Single page
        pagination = PaginationInfo(page=1, per_page=100, total_count=50)
        assert pagination.total_pages == 1
        assert pagination.has_next is False
        assert pagination.has_previous is False
    
    def test_parameter_validation(self):
        """Test that parameters are properly validated and constrained."""
        # Page should be at least 1
        pagination = PaginationInfo(page=0, per_page=10, total_count=100)
        assert pagination.page == 1
        
        # Per_page should be between 1 and 100
        pagination = PaginationInfo(page=1, per_page=0, total_count=100)
        assert pagination.per_page == 1
        
        pagination = PaginationInfo(page=1, per_page=150, total_count=100)
        assert pagination.per_page == 100
        
        # Total count should be non-negative
        pagination = PaginationInfo(page=1, per_page=10, total_count=-10)
        assert pagination.total_count == 0
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        pagination = PaginationInfo(page=2, per_page=20, total_count=100)
        pagination_dict = pagination.to_dict()
        
        expected = {
            "page": 2,
            "per_page": 20,
            "total_count": 100,
            "total_pages": 5,
            "has_next": True,
            "has_previous": True
        }
        
        assert pagination_dict == expected
    
    def test_from_query_params(self):
        """Test creating PaginationInfo from query parameters."""
        query_params = {"page": "3", "per_page": "25"}
        pagination = PaginationInfo.from_query_params(query_params)
        
        assert pagination.page == 3
        assert pagination.per_page == 25
        
        # Test with invalid parameters
        query_params = {"page": "invalid", "per_page": "invalid"}
        pagination = PaginationInfo.from_query_params(query_params)
        
        assert pagination.page == 1
        assert pagination.per_page == 10
    
    def test_validate_params(self):
        """Test parameter validation."""
        # Valid parameters
        page, per_page = PaginationInfo.validate_params("2", "20")
        assert page == 2
        assert per_page == 20
        
        # Invalid page
        with pytest.raises(ValueError, match="Page must be >= 1"):
            PaginationInfo.validate_params("0", "20")
        
        # Invalid per_page
        with pytest.raises(ValueError, match="Per_page must be between 1 and 100"):
            PaginationInfo.validate_params("1", "150")
        
        # Invalid types
        with pytest.raises(ValueError, match="Page and per_page must be valid integers"):
            PaginationInfo.validate_params("invalid", "20")


class TestPaginatedResponse:
    """Test PaginatedResponse class."""
    
    def test_basic_initialization(self):
        """Test basic initialization of PaginatedResponse."""
        data = [{"id": 1}, {"id": 2}]
        pagination = PaginationInfo(page=1, per_page=10, total_count=100)
        
        response = PaginatedResponse(data, pagination, status="success")
        
        assert response.get_data() == data
        assert response.get_page() == 1
        assert response.get_per_page() == 10
        assert response.get_total_count() == 100
        assert response.get_total_pages() == 10
        assert response.has_next_page() is True
        assert response.has_previous_page() is False
        assert response.get_pagination() == pagination.to_dict()
        assert response["status"] == "success"
    
    def test_url_generation(self):
        """Test URL generation for pagination."""
        data = [{"id": 1}]
        pagination = PaginationInfo(page=2, per_page=10, total_count=100)
        response = PaginatedResponse(data, pagination)
        
        base_url = "https://api.example.com/users"
        
        # Test next page URL
        next_url = response.get_next_page_url(base_url, status="active")
        assert next_url == "https://api.example.com/users?page=3&per_page=10&status=active"
        
        # Test previous page URL
        prev_url = response.get_previous_page_url(base_url, status="active")
        assert prev_url == "https://api.example.com/users?page=1&per_page=10&status=active"
        
        # Test all page URLs
        urls = response.get_page_urls(base_url, status="active")
        assert "first" in urls
        assert "previous" in urls
        assert "current" in urls
        assert "next" in urls
        assert "last" in urls


class TestPaginationUtilities:
    """Test pagination utility functions."""
    
    def test_parse_pagination_params(self):
        """Test parsing pagination parameters from query string."""
        query_string = "page=3&per_page=25&status=active"
        pagination = parse_pagination_params(query_string)
        
        assert pagination.page == 3
        assert pagination.per_page == 25
        
        # Test empty query string
        pagination = parse_pagination_params("")
        assert pagination.page == 1
        assert pagination.per_page == 10
    
    def test_build_pagination_url(self):
        """Test building pagination URLs."""
        base_url = "https://api.example.com/users"
        url = build_pagination_url(base_url, 2, 20, status="active")
        
        assert url == "https://api.example.com/users?page=2&per_page=20&status=active"
        
        # Test with no additional params
        url = build_pagination_url(base_url, 1, 10)
        assert url == "https://api.example.com/users?page=1&per_page=10"
    
    def test_create_paginated_response(self):
        """Test creating paginated response."""
        data = [{"id": 1}, {"id": 2}]
        response = create_paginated_response(data, 100, 2, 20, status="success")
        
        assert isinstance(response, PaginatedResponse)
        assert response.get_data() == data
        assert response.get_page() == 2
        assert response.get_per_page() == 20
        assert response.get_total_count() == 100
        assert response["status"] == "success"
    
    def test_get_pagination_metadata(self):
        """Test getting pagination metadata."""
        metadata = get_pagination_metadata(100, 2, 20)
        
        expected = {
            "page": 2,
            "per_page": 20,
            "total_count": 100,
            "total_pages": 5,
            "has_next": True,
            "has_previous": True
        }
        
        assert metadata == expected
    
    def test_calculate_page_info(self):
        """Test calculating detailed page information."""
        page_info = calculate_page_info(100, 2, 20)
        
        assert page_info["current_page"] == 2
        assert page_info["per_page"] == 20
        assert page_info["total_count"] == 100
        assert page_info["total_pages"] == 5
        assert page_info["has_next"] is True
        assert page_info["has_previous"] is True
        assert page_info["offset"] == 20
        assert page_info["limit"] == 20
        assert page_info["start_item"] == 21
        assert page_info["end_item"] == 40
    
    def test_create_pagination_links(self):
        """Test creating pagination links."""
        base_url = "https://api.example.com/users"
        links = create_pagination_links(base_url, 2, 5, 20, status="active")
        
        assert "first" in links
        assert "previous" in links
        assert "current" in links
        assert "next" in links
        assert "last" in links
        
        # Test edge cases
        links = create_pagination_links(base_url, 1, 1, 20)
        assert links["previous"] is None
        assert links["next"] is None
    
    def test_apply_pagination_to_list(self):
        """Test applying pagination to a list."""
        data = [{"id": i} for i in range(1, 101)]
        page_data, total_count = apply_pagination_to_list(data, 3, 15)
        
        assert len(page_data) == 15
        assert total_count == 100
        assert page_data[0]["id"] == 31  # (3-1) * 15 + 1
        assert page_data[-1]["id"] == 45  # 3 * 15
    
    def test_format_pagination_response(self):
        """Test formatting complete pagination response."""
        data = [{"id": 1}, {"id": 2}]
        response = format_pagination_response(
            data=data,
            total_count=100,
            page=2,
            per_page=20,
            include_links=True,
            base_url="https://api.example.com/users",
            status="success"
        )
        
        assert "data" in response
        assert "pagination" in response
        assert "links" in response
        assert "status" in response
        
        assert response["data"] == data
        assert response["status"] == "success"
        assert response["pagination"]["page"] == 2
        assert response["pagination"]["per_page"] == 20


class TestPaginationEdgeCases:
    """Test pagination edge cases and error conditions."""
    
    def test_empty_data(self):
        """Test pagination with empty data."""
        pagination = PaginationInfo(page=1, per_page=10, total_count=0)
        response = PaginatedResponse([], pagination)
        
        assert response.get_data() == []
        assert response.get_total_count() == 0
        assert response.get_total_pages() == 0
        assert response.has_next_page() is False
        assert response.has_previous_page() is False
    
    def test_single_page(self):
        """Test pagination with single page."""
        pagination = PaginationInfo(page=1, per_page=100, total_count=50)
        response = PaginatedResponse([{"id": 1}], pagination)
        
        assert response.get_total_pages() == 1
        assert response.has_next_page() is False
        assert response.has_previous_page() is False
    
    def test_last_page(self):
        """Test pagination on last page."""
        pagination = PaginationInfo(page=5, per_page=20, total_count=100)
        response = PaginatedResponse([{"id": 99}, {"id": 100}], pagination)
        
        assert response.has_next_page() is False
        assert response.has_previous_page() is True
    
    def test_invalid_page_numbers(self):
        """Test handling of invalid page numbers."""
        # Page number greater than total pages
        pagination = PaginationInfo(page=10, per_page=20, total_count=100)
        response = PaginatedResponse([], pagination)
        
        # Should still work but indicate no next page
        assert response.has_next_page() is False


if __name__ == "__main__":
    pytest.main([__file__])
