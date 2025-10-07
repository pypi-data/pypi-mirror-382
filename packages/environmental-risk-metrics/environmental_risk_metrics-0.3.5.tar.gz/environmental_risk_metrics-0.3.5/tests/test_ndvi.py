from unittest.mock import Mock, patch

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from shapely.geometry import box

from environmental_risk_metrics.metrics.ndvi import HarmonizedNDVI, Sentinel2


@pytest.fixture
def sample_geometry():
    """Create a sample geometry for testing"""
    bbox = [-117.8, 33.65, -117.65, 33.8]  # Orange County, California area
    geometry = box(*bbox)
    return gpd.GeoDataFrame([1], geometry=[geometry], crs="EPSG:4326")


@pytest.fixture
def ndvi_client(sample_geometry):
    """Create a HarmonizedNDVI client for testing"""
    return HarmonizedNDVI(
        start_date="2021-01-01",
        end_date="2021-12-31",
        gdf=sample_geometry,
        collections=["sentinel-2-l2a"],
        max_entire_image_cloud_cover=10,
        max_cropped_area_cloud_cover=50,
        max_workers=2,
    )


def test_init(ndvi_client):
    """Test initialization of HarmonizedNDVI client"""
    assert ndvi_client.start_date == "2021-01-01"
    assert ndvi_client.end_date == "2021-12-31"
    assert len(ndvi_client.collections) == 1
    assert "sentinel-2-l2a" in ndvi_client.collections


@patch('environmental_risk_metrics.metrics.ndvi.HarmonizedNDVI.calculate_mean_ndvi')
def test_multiple_collections(mock_calculate_mean_ndvi, ndvi_client):
    """Test working with multiple satellite collections"""
    # Mock the mean NDVI data
    mock_data = {
        "sentinel-2-l2a": [pd.DataFrame({
            'ndvi': [0.1, 0.2, 0.3],
            'timestamp': pd.date_range('2023-01-01', periods=3)
        })],
        "hls2-s30": [pd.DataFrame({
            'ndvi': [0.2, 0.3, 0.4],
            'timestamp': pd.date_range('2023-01-01', periods=3)
        })],
        "hls2-l30": [pd.DataFrame({
            'ndvi': [0.3, 0.4, 0.5],
            'timestamp': pd.date_range('2023-01-01', periods=3)
        })]
    }
    mock_calculate_mean_ndvi.return_value = mock_data

    mean_ndvi_data = ndvi_client.calculate_mean_ndvi()

    assert isinstance(mean_ndvi_data, dict)
    assert len(mean_ndvi_data) == 3
    for collection in ["sentinel-2-l2a", "hls2-s30", "hls2-l30"]:
        assert collection in mean_ndvi_data
        assert len(mean_ndvi_data[collection]) == 1
        assert isinstance(mean_ndvi_data[collection][0], pd.DataFrame)


@patch('environmental_risk_metrics.metrics.ndvi.HarmonizedNDVI.rgb_ndvi_images')
def test_rgb_ndvi_images(mock_rgb_ndvi_images, ndvi_client):
    """Test generation of RGB+NDVI side-by-side images"""
    # Mock the RGB+NDVI images
    mock_images = {
        "sentinel-2-l2a": [{
            "2023-06-01": b"mock_image_data",
            "2023-06-15": b"mock_image_data"
        }]
    }
    mock_rgb_ndvi_images.return_value = mock_images

    rgb_ndvi_images = ndvi_client.rgb_ndvi_images()

    assert isinstance(rgb_ndvi_images, dict)
    assert "sentinel-2-l2a" in rgb_ndvi_images
    assert len(rgb_ndvi_images["sentinel-2-l2a"]) == 1
    assert len(rgb_ndvi_images["sentinel-2-l2a"][0]) == 2


@patch('environmental_risk_metrics.metrics.ndvi.HarmonizedNDVI.generate_ndvi_gif')
def test_gif_generation(mock_generate_gif, ndvi_client):
    """Test generation of animated GIF"""
    mock_gif_data = b"mock_gif_data"
    mock_generate_gif.return_value = mock_gif_data

    gif_bytes = ndvi_client.generate_ndvi_gif(
        collection="hls2-s30",
        geometry_index=0,
        duration=0.8,
        vmin=-0.2,
        vmax=0.8
    )

    assert isinstance(gif_bytes, bytes)
    mock_generate_gif.assert_called_once_with(
        collection="hls2-s30",
        geometry_index=0,
        duration=0.8,
        vmin=-0.2,
        vmax=0.8
    )


def test_backward_compatibility(sample_geometry):
    """Test backward compatibility with Sentinel2 class"""
    sentinel2_client = Sentinel2(
        start_date="2023-07-01",
        end_date="2023-07-31",
        gdf=sample_geometry,
        resolution=10,
    )

    assert isinstance(sentinel2_client, Sentinel2)
    assert sentinel2_client.start_date == "2023-07-01"
    assert sentinel2_client.end_date == "2023-07-31"
    assert sentinel2_client.resolution == 10


@patch('environmental_risk_metrics.metrics.ndvi.HarmonizedNDVI.ndvi_thumbnails')
def test_hls2_specific(mock_thumbnails, ndvi_client):
    """Test HLS2-specific functionality"""
    # Mock the thumbnails
    mock_thumb_data = {
        "hls2-s30": [{"2023-01-01": b"mock_thumb"}],
        "hls2-l30": [{"2023-01-01": b"mock_thumb"}]
    }
    mock_thumbnails.return_value = mock_thumb_data

    thumbnails = ndvi_client.ndvi_thumbnails(image_format="png")

    assert isinstance(thumbnails, dict)
    assert "hls2-s30" in thumbnails
    assert "hls2-l30" in thumbnails
    assert len(thumbnails["hls2-s30"]) == 1
    assert len(thumbnails["hls2-l30"]) == 1


@patch('environmental_risk_metrics.metrics.ndvi.HarmonizedNDVI.load_xarray')
def test_ndvi_dataarrays_include_item_metadata(mock_load_xarray, ndvi_client):
    item_metadata = {
        "id": "test-item",
        "datetime": "2021-06-01T10:00:00Z",
        "assets": {
            "visual": {"href": "https://example.com/visual.tif"}
        }
    }

    times = pd.to_datetime(["2021-06-01T10:00:00Z"]).to_numpy()
    coords = {
        "time": ("time", times),
        "y": ("y", np.array([33.7])),
        "x": ("x", np.array([-117.7])),
    }
    data_vars = {
        "B08": (("time", "y", "x"), np.array([[[0.7]]], dtype=float)),
        "B04": (("time", "y", "x"), np.array([[[0.3]]], dtype=float)),
        "SCL": (("time", "y", "x"), np.array([[[4.0]]], dtype=float)),
    }
    ds = xr.Dataset(data_vars=data_vars, coords=coords)
    ds = ds.assign_coords(spatial_ref="EPSG:4326")

    mock_load_xarray.return_value = {"sentinel-2-l2a": [ds]}
    ndvi_client.xarray_item_metadata = {"sentinel-2-l2a": [[item_metadata]]}

    ndvi_outputs = ndvi_client.load_ndvi_images()
    ndvi_array = ndvi_outputs["sentinel-2-l2a"][0]
    metadata = ndvi_array.attrs.get("item_metadata")

    assert metadata is not None
    first_entry = metadata[0]
    assert first_entry["assets"]["visual"]["href"] == "https://example.com/visual.tif"


class DummyRioAccessor:
    def __init__(self, parent):
        self._parent = parent

    def write_crs(self, crs):
        return self._parent

    def clip(self, geometries, crs, all_touched):
        return self._parent


class DummyNDVI:
    def __init__(self, mean_value: float, metadata: list[dict], timestamps: np.ndarray):
        self.attrs = {"item_metadata": metadata.copy()}
        self.time = Mock(values=timestamps)
        self.coords = {
            "spatial_ref": Mock(values=np.array(["EPSG:4326"])),
        }
        self.rio = DummyRioAccessor(self)
        self._mean_value = mean_value

    def mean(self, dim=None):
        return Mock(values=np.array([[self._mean_value]]))


@patch('environmental_risk_metrics.metrics.ndvi.HarmonizedNDVI.load_ndvi_images')
def test_metadata_propagates_to_outputs(mock_load_ndvi_images, ndvi_client):
    metadata_entry = {
        "datetime": "2021-06-01T00:00:00Z",
        "assets": {"visual": {"href": "https://example.com/visual.tif"}},
    }

    timestamps = np.array([np.datetime64("2021-06-01")])
    dummy_ndvi = DummyNDVI(mean_value=0.5, metadata=[metadata_entry], timestamps=timestamps)
    mock_load_ndvi_images.return_value = {"sentinel-2-l2a": [dummy_ndvi]}

    mean_results = ndvi_client.calculate_mean_ndvi(interpolate=False)
    mean_df = mean_results["sentinel-2-l2a"][0]

    assert "metadata" in mean_df.columns
    first_metadata = mean_df.iloc[0]["metadata"]
    assert isinstance(first_metadata, list)
    assert first_metadata[0]["assets"]["visual"]["href"] == "https://example.com/visual.tif"

    data_output = ndvi_client.get_data(interpolate=False)
    records = data_output["sentinel-2-l2a"][0]
    metadata_record = records[0]["metadata"]
    assert isinstance(metadata_record, list)
    assert metadata_record[0]["assets"]["visual"]["href"] == "https://example.com/visual.tif"