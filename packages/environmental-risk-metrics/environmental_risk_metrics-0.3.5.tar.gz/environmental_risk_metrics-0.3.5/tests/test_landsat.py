import geopandas as gpd
import pytest
from shapely.geometry import Polygon

from environmental_risk_metrics.metrics.landsat import LandsatItems


@pytest.fixture
def sample_gdf():
    """Create a sample GeoDataFrame for testing."""
    polygon = Polygon(
        [
            (-74.0060, 40.7128),
            (-73.9354, 40.7128),
            (-73.9354, 40.7831),
            (-74.0060, 40.7831),
            (-74.0060, 40.7128),
        ]
    )
    return gpd.GeoDataFrame([1], geometry=[polygon], crs="EPSG:4326")


def test_landsat_items_initialization(sample_gdf):
    """Test the initialization of the LandsatItems class."""
    landsat_items = LandsatItems(
        gdf=sample_gdf, start_date="2023-01-01", end_date="2023-01-31"
    )
    assert landsat_items is not None
    assert landsat_items.collections == ["landsat-c2-l2"]
    assert landsat_items.gdf.crs == "EPSG:4326"


def test_get_items_with_real_data(sample_gdf):
    """Test get_items with a real call to Planetary Computer."""
    landsat_items = LandsatItems(
        gdf=sample_gdf,
        start_date="2023-01-01",
        end_date="2023-01-31",
        max_entire_image_cloud_cover=90,
    )
    items_dict = landsat_items.get_items()

    assert "landsat-c2-l2" in items_dict
    assert len(items_dict["landsat-c2-l2"]) > 0
    assert len(items_dict["landsat-c2-l2"][0]) > 0
    assert "pystac.item.Item" in str(type(items_dict["landsat-c2-l2"][0][0]))


def test_load_xarray_with_real_data(sample_gdf):
    """Test load_xarray with a real call to Planetary Computer."""
    landsat = LandsatItems(
        gdf=sample_gdf,
        start_date="2021-01-01",
        end_date="2021-12-31",
        max_entire_image_cloud_cover=90,
        max_cropped_area_cloud_cover=100,
        max_workers=2,
    )
    xarray_data = landsat.load_xarray(include_rgb=True, filter_cloud_cover=False)

    assert "landsat-c2-l2" in xarray_data
    assert len(xarray_data["landsat-c2-l2"]) > 0
    
    dataset = xarray_data["landsat-c2-l2"][0]
    assert dataset is not None
    assert "xarray.core.dataset.Dataset" in str(type(dataset))
    assert "red" in dataset.data_vars
    assert "green" in dataset.data_vars
    assert "blue" in dataset.data_vars
    assert "nir08" in dataset.data_vars
    assert len(dataset.time) > 0 