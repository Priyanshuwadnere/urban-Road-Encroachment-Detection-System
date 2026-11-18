"""Unit tests for Reference Layer Validator module."""

import pytest
from src.gis.validator import ReferenceDataValidator
from src.core.schemas import CadastralParcel, RoadROW
from src.config import STATUS_REFERENCE_REQUIRED


@pytest.fixture
def valid_parcel():
    return CadastralParcel(
        parcel_id="P-101",
        owner_name_synthetic="Test Owner",
        address_synthetic="Test Address",
        geometry_geojson={
            "type": "Polygon",
            "coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]],
        },
    )


@pytest.fixture
def valid_row():
    return RoadROW(
        row_id="ROW-01",
        road_name="Main Road",
        legal_width_m=8.0,
        geometry_geojson={
            "type": "Polygon",
            "coordinates": [[[10.0, -10.0], [18.0, -10.0], [18.0, 20.0], [10.0, 20.0], [10.0, -10.0]]],
        },
    )


def test_validator_all_valid(valid_parcel, valid_row):
    is_valid, status, err = ReferenceDataValidator.validate_layers(valid_parcel, valid_row)
    assert is_valid is True
    assert status == "REFERENCE_DATA_VALID"
    assert err is None


def test_validator_missing_parcel(valid_row):
    is_valid, status, err = ReferenceDataValidator.validate_layers(None, valid_row)
    assert is_valid is False
    assert status == STATUS_REFERENCE_REQUIRED
    assert "parcel" in err.lower()


def test_validator_missing_row(valid_parcel):
    is_valid, status, err = ReferenceDataValidator.validate_layers(valid_parcel, None)
    assert is_valid is False
    assert status == STATUS_REFERENCE_REQUIRED
    assert "row" in err.lower()


def test_validator_missing_both():
    is_valid, status, err = ReferenceDataValidator.validate_layers(None, None)
    assert is_valid is False
    assert status == STATUS_REFERENCE_REQUIRED


def test_validator_invalid_geometry(valid_row):
    invalid_parcel = CadastralParcel(
        parcel_id="P-BAD",
        owner_name_synthetic="Bad Owner",
        address_synthetic="Bad Address",
        geometry_geojson={
            "type": "Polygon",
            "coordinates": [[[0.0, 0.0], [10.0, 10.0]]],  # Unclosed line, invalid polygon
        },
    )
    is_valid, status, err = ReferenceDataValidator.validate_layers(invalid_parcel, valid_row)
    assert is_valid is False
    assert status == STATUS_REFERENCE_REQUIRED
    assert "geometry" in err.lower()
