"""Tests for Point dataclass with enums."""

import pytest
from pi_web_sdk.models.data import Point, PointClass, PointType


def test_point_with_enum_values():
    """Test creating a Point with enum values."""
    point = Point(
        name="TestPoint",
        point_class=PointClass.CLASSIC,
        point_type=PointType.FLOAT32,
        engineering_units="degC",
        step=False,
        future=False,
        display_digits=2
    )

    assert point.name == "TestPoint"
    assert point.point_class == PointClass.CLASSIC
    assert point.point_type == PointType.FLOAT32
    assert point.engineering_units == "degC"


def test_point_enum_to_dict():
    """Test that Point.to_dict() correctly converts enums to strings."""
    point = Point(
        name="TestPoint",
        point_class=PointClass.BASE,
        point_type=PointType.FLOAT64
    )

    result = point.to_dict()

    # Enums should be converted to their string values
    assert result["PointClass"] == "base"
    assert result["PointType"] == "Float64"
    assert result["Name"] == "TestPoint"


def test_point_with_string_values():
    """Test creating a Point with string values (backward compatibility)."""
    point = Point(
        name="TestPoint",
        point_class="classic",
        point_type="Int32"
    )

    assert point.name == "TestPoint"
    assert point.point_class == "classic"
    assert point.point_type == "Int32"


def test_point_string_to_dict():
    """Test that Point.to_dict() works with string values."""
    point = Point(
        name="TestPoint",
        point_class="base",
        point_type="Digital",
        digital_set_name="MyDigitalSet"
    )

    result = point.to_dict()

    # Strings should pass through unchanged
    assert result["PointClass"] == "base"
    assert result["PointType"] == "Digital"
    assert result["DigitalSetName"] == "MyDigitalSet"


def test_point_mixed_enum_and_string():
    """Test mixing enum and string values."""
    point = Point(
        name="TestPoint",
        point_class=PointClass.CLASSIC,
        point_type="String"  # Using string instead of enum
    )

    result = point.to_dict()

    assert result["PointClass"] == "classic"
    assert result["PointType"] == "String"


def test_point_class_enum_values():
    """Test PointClass enum values."""
    assert PointClass.BASE.value == "base"
    assert PointClass.CLASSIC.value == "classic"


def test_point_type_enum_values():
    """Test PointType enum values."""
    assert PointType.FLOAT32.value == "Float32"
    assert PointType.FLOAT64.value == "Float64"
    assert PointType.FLOAT16.value == "Float16"
    assert PointType.INT16.value == "Int16"
    assert PointType.INT32.value == "Int32"
    assert PointType.DIGITAL.value == "Digital"
    assert PointType.TIMESTAMP.value == "Timestamp"
    assert PointType.STRING.value == "String"
    assert PointType.BLOB.value == "blob"


def test_point_all_types():
    """Test creating points with all available PointType values."""
    for point_type in PointType:
        point = Point(
            name=f"TestPoint_{point_type.name}",
            point_type=point_type
        )
        result = point.to_dict()
        assert result["PointType"] == point_type.value


def test_point_exclude_none():
    """Test that Point.to_dict(exclude_none=True) excludes None values."""
    point = Point(
        name="TestPoint",
        point_type=PointType.FLOAT32
        # point_class is not set (None)
    )

    result = point.to_dict(exclude_none=True)

    assert "PointType" in result
    assert "PointClass" not in result
    assert result["Name"] == "TestPoint"


def test_point_include_none():
    """Test that Point.to_dict(exclude_none=False) includes None values."""
    point = Point(
        name="TestPoint",
        point_type=PointType.INT32
        # point_class is not set (None)
    )

    result = point.to_dict(exclude_none=False)

    assert "PointType" in result
    assert "PointClass" in result
    assert result["PointClass"] is None