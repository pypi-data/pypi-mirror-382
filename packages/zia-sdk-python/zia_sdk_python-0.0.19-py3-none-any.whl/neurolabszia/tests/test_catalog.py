#!/usr/bin/env python3
"""
Tests for catalog models and validation.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from neurolabszia.models.catalog import (
    NLCatalogItem,
    NLCatalogItemCreate,
    NLCatalogItemStatus,
)


class TestNLCatalogItem:
    """Test NLCatalogItem model with new fields."""

    def test_catalog_item_with_all_fields(self):
        """Test NLCatalogItem with all new fields populated."""
        item_data = {
            "uuid": "test-uuid-123",
            "status": NLCatalogItemStatus.READY,
            "thumbnail_url": "https://example.com/thumb.jpg",
            "name": "Test Product",
            "barcode": "1234567890123",
            "custom_id": "CUSTOM-001",
            "height": 0.15,
            "width": 0.10,
            "depth": 0.05,
            "brand": "Test Brand",
            "size": "Large",
            "container_type": "Bottle",
            "flavour": "Vanilla",
            "packaging_size": "500ml",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        item = NLCatalogItem.model_validate(item_data)
        
        # Test all new fields
        assert item.brand == "Test Brand"
        assert item.size == "Large"
        assert item.container_type == "Bottle"
        assert item.flavour == "Vanilla"
        assert item.packaging_size == "500ml"
        assert item.barcode == "1234567890123"
        assert item.custom_id == "CUSTOM-001"
        assert item.height == 0.15
        assert item.width == 0.10
        assert item.depth == 0.05

    def test_catalog_item_with_minimal_fields(self):
        """Test NLCatalogItem with only required fields."""
        item_data = {
            "uuid": "test-uuid-456",
            "status": NLCatalogItemStatus.PROCESSING,
            "thumbnail_url": "https://example.com/thumb2.jpg",
            "name": "Minimal Product",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        item = NLCatalogItem.model_validate(item_data)
        
        # Test that optional fields are None
        assert item.brand is None
        assert item.size is None
        assert item.container_type is None
        assert item.flavour is None
        assert item.packaging_size is None
        assert item.barcode is None
        assert item.custom_id is None
        assert item.height is None
        assert item.width is None
        assert item.depth is None

    def test_catalog_item_with_partial_new_fields(self):
        """Test NLCatalogItem with some new fields populated."""
        item_data = {
            "uuid": "test-uuid-789",
            "status": NLCatalogItemStatus.READY,
            "thumbnail_url": "https://example.com/thumb3.jpg",
            "name": "Partial Product",
            "brand": "Premium Brand",
            "size": "Medium",
            "container_type": "Can",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        item = NLCatalogItem.model_validate(item_data)
        
        # Test populated fields
        assert item.brand == "Premium Brand"
        assert item.size == "Medium"
        assert item.container_type == "Can"
        
        # Test unpopulated fields
        assert item.flavour is None
        assert item.packaging_size is None

    def test_catalog_item_empty_strings(self):
        """Test NLCatalogItem with empty string values for optional fields."""
        item_data = {
            "uuid": "test-uuid-empty",
            "status": NLCatalogItemStatus.READY,
            "thumbnail_url": "https://example.com/thumb4.jpg",
            "name": "Empty Strings Product",
            "brand": "",
            "size": "",
            "container_type": "",
            "flavour": "",
            "packaging_size": "",
            "barcode": "",
            "custom_id": "",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        item = NLCatalogItem.model_validate(item_data)
        
        # Empty strings should be preserved
        assert item.brand == ""
        assert item.size == ""
        assert item.container_type == ""
        assert item.flavour == ""
        assert item.packaging_size == ""
        assert item.barcode == ""
        assert item.custom_id == ""


class TestNLCatalogItemCreate:
    """Test NLCatalogItemCreate model with new fields."""

    def test_catalog_item_create_with_all_fields(self):
        """Test NLCatalogItemCreate with all new fields."""
        create_data = {
            "name": "New Product",
            "thumbnail": b"fake_image_data",
            "barcode": "9876543210987",
            "custom_id": "NEW-001",
            "height": 0.20,
            "width": 0.15,
            "depth": 0.08,
            "brand": "New Brand",
            "size": "Extra Large",
            "container_type": "Jar",
            "flavour": "Chocolate",
            "packaging_size": "1L",
        }
        
        item = NLCatalogItemCreate.model_validate(create_data)
        
        # Test all new fields
        assert item.brand == "New Brand"
        assert item.size == "Extra Large"
        assert item.container_type == "Jar"
        assert item.flavour == "Chocolate"
        assert item.packaging_size == "1L"
        assert item.barcode == "9876543210987"
        assert item.custom_id == "NEW-001"
        assert item.height == 0.20
        assert item.width == 0.15
        assert item.depth == 0.08

    def test_catalog_item_create_validation_rules(self):
        """Test validation rules for NLCatalogItemCreate."""
        # Test valid name
        valid_data = {
            "name": "Valid Product Name",
            "barcode": "1234567890123",
        }
        item = NLCatalogItemCreate.model_validate(valid_data)
        assert item.name == "Valid Product Name"
        assert item.barcode == "1234567890123"

    def test_catalog_item_create_name_validation(self):
        """Test name validation rules."""
        # Test empty name
        with pytest.raises(ValidationError) as exc_info:
            NLCatalogItemCreate.model_validate({"name": ""})
        assert "Item name cannot be empty" in str(exc_info.value)

        # Test whitespace-only name
        with pytest.raises(ValidationError) as exc_info:
            NLCatalogItemCreate.model_validate({"name": "   "})
        assert "Item name cannot be empty" in str(exc_info.value)

        # Test name too long
        long_name = "x" * 256
        with pytest.raises(ValidationError) as exc_info:
            NLCatalogItemCreate.model_validate({"name": long_name})
        assert "Item name cannot exceed 255 characters" in str(exc_info.value)

        # Test name trimming
        item = NLCatalogItemCreate.model_validate({"name": "  Trimmed Name  "})
        assert item.name == "Trimmed Name"

    def test_catalog_item_create_barcode_validation(self):
        """Test barcode validation rules."""
        # Test valid barcode
        item = NLCatalogItemCreate.model_validate({
            "name": "Test Product",
            "barcode": "1234567890123"
        })
        assert item.barcode == "1234567890123"

        # Test barcode too long
        with pytest.raises(ValidationError) as exc_info:
            NLCatalogItemCreate.model_validate({
                "name": "Test Product",
                "barcode": "123456789012345"  # 15 characters
            })
        assert "Barcode cannot exceed 14 characters" in str(exc_info.value)

        # Test barcode with invalid characters
        with pytest.raises(ValidationError) as exc_info:
            NLCatalogItemCreate.model_validate({
                "name": "Test Product",
                "barcode": "123-456-789"
            })
        assert "Barcode must contain only alphanumeric characters" in str(exc_info.value)

    def test_catalog_item_create_with_new_fields_validation(self):
        """Test that new fields accept various data types."""
        # Test with string values
        item = NLCatalogItemCreate.model_validate({
            "name": "String Fields Product",
            "brand": "Brand Name",
            "size": "Large",
            "container_type": "Bottle",
            "flavour": "Vanilla",
            "packaging_size": "500ml",
        })
        
        assert item.brand == "Brand Name"
        assert item.size == "Large"
        assert item.container_type == "Bottle"
        assert item.flavour == "Vanilla"
        assert item.packaging_size == "500ml"

        # Test with None values
        item = NLCatalogItemCreate.model_validate({
            "name": "None Fields Product",
            "brand": None,
            "size": None,
            "container_type": None,
            "flavour": None,
            "packaging_size": None,
        })
        
        assert item.brand is None
        assert item.size is None
        assert item.container_type is None
        assert item.flavour is None
        assert item.packaging_size is None


class TestCatalogDataFrameIntegration:
    """Test catalog fields in DataFrame context."""

    def test_catalog_fields_in_ir_results(self):
        """Test that catalog fields are properly handled in IR results DataFrame."""
        # This would be tested in test_dataframe.py when IR results contain catalog data
        pass
