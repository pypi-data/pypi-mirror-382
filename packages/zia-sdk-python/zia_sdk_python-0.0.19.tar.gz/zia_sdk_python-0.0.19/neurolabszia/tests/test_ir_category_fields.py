#!/usr/bin/env python3
"""
Tests for NLIRCOCONeurolabsCategory model with all fields.
"""

import pytest
from pydantic import ValidationError

from neurolabszia.models.image_recognition import NLIRCOCONeurolabsCategory


class TestNLIRCOCONeurolabsCategory:
    """Test NLIRCOCONeurolabsCategory model with new fields."""

    def test_ir_category_with_all_new_fields(self):
        """Test NLIRCOCONeurolabsCategory with all new fields populated."""
        category_data = {
            "barcode": "1234567890123",
            "customId": "CUSTOM-001",
            "label": "Premium Product",
            "productUuid": "product-uuid-123",
            "brand": "Test Brand",
            "name": "Test Product Name",
            "size": "Large",
            "containerType": "Bottle",
            "flavour": "Vanilla",
            "packagingSize": "500ml",
            "IsCompetitor": "False",
        }
        
        category = NLIRCOCONeurolabsCategory.model_validate(category_data)
        
        # Test all new fields
        assert category.size == "Large"
        assert category.containerType == "Bottle"
        assert category.flavour == "Vanilla"
        assert category.packagingSize == "500ml"
        assert category.IsCompetitor == "False"
        
        # Test existing fields
        assert category.barcode == "1234567890123"
        assert category.customId == "CUSTOM-001"
        assert category.label == "Premium Product"
        assert category.productUuid == "product-uuid-123"
        assert category.brand == "Test Brand"
        assert category.name == "Test Product Name"

    def test_ir_category_with_minimal_fields(self):
        """Test NLIRCOCONeurolabsCategory with only required fields."""
        category_data = {
            "barcode": "9876543210987",
            "customId": "MINIMAL-001",
        }
        
        category = NLIRCOCONeurolabsCategory.model_validate(category_data)
        
        # Test that new optional fields are None
        assert category.size is None
        assert category.containerType is None
        assert category.flavour is None
        assert category.packagingSize is None
        assert category.IsCompetitor is None
        
        # Test existing fields
        assert category.barcode == "9876543210987"
        assert category.customId == "MINIMAL-001"

    def test_ir_category_with_partial_new_fields(self):
        """Test NLIRCOCONeurolabsCategory with some new fields populated."""
        category_data = {
            "barcode": "5555555555555",
            "customId": "PARTIAL-001",
            "brand": "Partial Brand",
            "size": "Medium",
            "containerType": "Can",
            "IsCompetitor": "True",
        }
        
        category = NLIRCOCONeurolabsCategory.model_validate(category_data)
        
        # Test populated new fields
        assert category.size == "Medium"
        assert category.containerType == "Can"
        assert category.IsCompetitor == "True"
        
        # Test unpopulated new fields
        assert category.flavour is None
        assert category.packagingSize is None

    def test_ir_category_boolean_fields(self):
        """Test boolean field handling in NLIRCOCONeurolabsCategory."""
        # Test IsCompetitor as True
        category_data = {
            "barcode": "1111111111111",
            "IsCompetitor": "True",
        }
        category = NLIRCOCONeurolabsCategory.model_validate(category_data)
        assert category.IsCompetitor == "True"

        # Test IsCompetitor as False
        category_data = {
            "barcode": "2222222222222",
            "IsCompetitor": "False",
        }
        category = NLIRCOCONeurolabsCategory.model_validate(category_data)
        assert category.IsCompetitor == "False"

        # Test IsCompetitor as None
        category_data = {
            "barcode": "3333333333333",
            "IsCompetitor": None,
        }
        category = NLIRCOCONeurolabsCategory.model_validate(category_data)
        assert category.IsCompetitor is None

    def test_ir_category_string_fields(self):
        """Test string field handling in NLIRCOCONeurolabsCategory."""
        category_data = {
            "barcode": "4444444444444",
            "size": "Extra Large",
            "containerType": "Jar",
            "flavour": "Chocolate Mint",
            "packagingSize": "1.5L",
        }
        
        category = NLIRCOCONeurolabsCategory.model_validate(category_data)
        
        assert category.size == "Extra Large"
        assert category.containerType == "Jar"
        assert category.flavour == "Chocolate Mint"
        assert category.packagingSize == "1.5L"

    def test_ir_category_empty_strings(self):
        """Test NLIRCOCONeurolabsCategory with empty string values."""
        category_data = {
            "barcode": "5555555555555",
            "size": "",
            "containerType": "",
            "flavour": "",
            "packagingSize": "",
        }
        
        category = NLIRCOCONeurolabsCategory.model_validate(category_data)
        
        # Empty strings should be preserved
        assert category.size == ""
        assert category.containerType == ""
        assert category.flavour == ""
        assert category.packagingSize == ""

    def test_ir_category_mixed_data_types(self):
        """Test NLIRCOCONeurolabsCategory with mixed data types."""
        category_data = {
            "barcode": "6666666666666",
            "size": "Small",
            "containerType": "Box",
            "flavour": "Strawberry",
            "packagingSize": "250g",
            "IsCompetitor": "False",
            "brand": "Mixed Brand",
            "name": "Mixed Product",
        }
        
        category = NLIRCOCONeurolabsCategory.model_validate(category_data)
        
        # Test all field types
        assert isinstance(category.size, str)
        assert isinstance(category.containerType, str)
        assert isinstance(category.flavour, str)
        assert isinstance(category.packagingSize, str)
        assert isinstance(category.IsCompetitor, str)
        assert isinstance(category.brand, str)
        assert isinstance(category.name, str)

    def test_ir_category_validation_edge_cases(self):
        """Test edge cases for NLIRCOCONeurolabsCategory validation."""
        # Test with all fields as None
        category_data = {
            "barcode": None,
            "customId": None,
            "label": None,
            "productUuid": None,
            "brand": None,
            "name": None,
            "size": None,
            "containerType": None,
            "flavour": None,
            "packagingSize": None,
            "IsCompetitor": None,
        }
        
        category = NLIRCOCONeurolabsCategory.model_validate(category_data)
        
        # All fields should be None
        for field_name in category.model_fields:
            assert getattr(category, field_name) is None

    def test_ir_category_serialization(self):
        """Test that NLIRCOCONeurolabsCategory can be serialized and deserialized."""
        original_data = {
            "barcode": "7777777777777",
            "customId": "SERIAL-001",
            "label": "Serial Test Product",
            "productUuid": "serial-uuid-123",
            "brand": "Serial Brand",
            "name": "Serial Product",
            "size": "X-Large",
            "containerType": "Tetra Pak",
            "flavour": "Mango",
            "packagingSize": "1L",
            "IsCompetitor": "True",
        }
        
        category = NLIRCOCONeurolabsCategory.model_validate(original_data)
        
        # Test serialization
        serialized = category.model_dump()
        assert serialized["size"] == "X-Large"
        assert serialized["containerType"] == "Tetra Pak"
        assert serialized["flavour"] == "Mango"
        assert serialized["packagingSize"] == "1L"
        assert serialized["IsCompetitor"] == "True"
        
        # Test deserialization
        deserialized = NLIRCOCONeurolabsCategory.model_validate(serialized)
        assert deserialized.size == "X-Large"
        assert deserialized.containerType == "Tetra Pak"
        assert deserialized.flavour == "Mango"
        assert deserialized.packagingSize == "1L"
        assert deserialized.IsCompetitor == "True"
