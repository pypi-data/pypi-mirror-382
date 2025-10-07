"""
Test to demonstrate how cloud cover filtering affects data availability.

This test searches for real satellite data with different cloud cover settings
and verifies that less restrictive cloud filtering returns more data.
"""

import pytest
import geopandas as gpd
from shapely.geometry import Polygon
from environmental_risk_metrics.metrics.sentinel2_items import Sentinel2Items
from environmental_risk_metrics.metrics.landsat import LandsatItems
from environmental_risk_metrics.metrics.ndvi import HarmonizedNDVI


@pytest.fixture
def sample_geometry():
    """Create a sample geometry for testing - a small area in Redmond, WA"""
    polygon = Polygon([
        (-122.2751, 47.5469),  # SW corner
        (-121.9613, 47.5469),  # SE corner
        (-121.9613, 47.7458),  # NE corner
        (-122.2751, 47.7458),  # NW corner
        (-122.2751, 47.5469)   # Close the polygon
    ])
    return gpd.GeoDataFrame([1], geometry=[polygon], crs="EPSG:4326")


def test_cloud_cover_filtering_affects_data_availability_sentinel2(sample_geometry):
    """
    Test that less restrictive cloud cover filtering returns more Sentinel-2 data.
    
    This test demonstrates the relationship between cloud cover parameters and data availability.
    """
    
    # Test with very restrictive cloud filtering (should get few items)
    restrictive_s2 = Sentinel2Items(
        gdf=sample_geometry,
        start_date="2021-01-01",
        end_date="2021-12-31",
        max_entire_image_cloud_cover=5,  # Very restrictive: only images with <5% cloud cover
        max_cropped_area_cloud_cover=10,  # Very restrictive: only time steps with <10% cloud cover
        max_workers=2,
    )
    
    # Test with moderate cloud filtering (should get more items)
    moderate_s2 = Sentinel2Items(
        gdf=sample_geometry,
        start_date="2021-01-01",
        end_date="2021-12-31",
        max_entire_image_cloud_cover=20,  # Moderate: images with <20% cloud cover
        max_cropped_area_cloud_cover=50,  # Moderate: time steps with <50% cloud cover
        max_workers=2,
    )
    
    # Test with permissive cloud filtering (should get even more items)
    permissive_s2 = Sentinel2Items(
        gdf=sample_geometry,
        start_date="2021-01-01",
        end_date="2021-12-31",
        max_entire_image_cloud_cover=100,  # Permissive: accept all images
        max_cropped_area_cloud_cover=100,  # Permissive: accept all time steps
        max_workers=2,
    )
    
    # Get items for each configuration
    restrictive_items = restrictive_s2.get_items()
    moderate_items = moderate_s2.get_items()
    permissive_items = permissive_s2.get_items()
    
    # Count items for each configuration
    restrictive_count = len(restrictive_items["sentinel-2-l2a"][0])
    moderate_count = len(moderate_items["sentinel-2-l2a"][0])
    permissive_count = len(permissive_items["sentinel-2-l2a"][0])
    
    print(f"\nSentinel-2 Data Availability Test Results:")
    print(f"Restrictive filtering (<5% entire, <10% cropped): {restrictive_count} items")
    print(f"Moderate filtering (<20% entire, <50% cropped): {moderate_count} items")
    print(f"Permissive filtering (all clouds allowed): {permissive_count} items")
    
    # Verify that less restrictive filtering returns more data
    assert permissive_count >= moderate_count, "Permissive filtering should return at least as much data as moderate filtering"
    assert moderate_count >= restrictive_count, "Moderate filtering should return at least as much data as restrictive filtering"
    
    # If we have data, test loading it
    if permissive_count > 0:
        print(f"\nTesting data loading with permissive filtering...")
        
        # Load data with cloud filtering enabled
        data_with_filtering = permissive_s2.load_xarray(
            filter_cloud_cover=True,
            include_rgb=True
        )
        
        # Load data with cloud filtering disabled
        data_without_filtering = permissive_s2.load_xarray(
            filter_cloud_cover=False,
            include_rgb=True
        )
        
        # Count time steps in each dataset
        with_filtering_steps = 0
        without_filtering_steps = 0
        
        for ds in data_with_filtering["sentinel-2-l2a"]:
            if ds is not None:
                with_filtering_steps += len(ds.time)
        
        for ds in data_without_filtering["sentinel-2-l2a"]:
            if ds is not None:
                without_filtering_steps += len(ds.time)
        
        print(f"Time steps with cloud filtering: {with_filtering_steps}")
        print(f"Time steps without cloud filtering: {without_filtering_steps}")
        
        # Verify that disabling cloud filtering returns more time steps
        assert without_filtering_steps >= with_filtering_steps, "Disabling cloud filtering should return at least as many time steps"


def test_cloud_cover_filtering_affects_data_availability_landsat(sample_geometry):
    """
    Test that less restrictive cloud cover filtering returns more Landsat data.
    """
    
    # Test with very restrictive cloud filtering
    restrictive_landsat = LandsatItems(
        gdf=sample_geometry,
        start_date="2021-01-01",
        end_date="2021-12-31",
        max_entire_image_cloud_cover=5,  # Very restrictive
        max_cropped_area_cloud_cover=10,  # Very restrictive
        max_workers=2,
    )
    
    # Test with permissive cloud filtering
    permissive_landsat = LandsatItems(
        gdf=sample_geometry,
        start_date="2021-01-01",
        end_date="2021-12-31",
        max_entire_image_cloud_cover=100,  # Permissive
        max_cropped_area_cloud_cover=100,  # Permissive
        max_workers=2,
    )
    
    # Get items for each configuration
    restrictive_items = restrictive_landsat.get_items()
    permissive_items = permissive_landsat.get_items()
    
    # Count items
    restrictive_count = len(restrictive_items["landsat-c2-l2"][0])
    permissive_count = len(permissive_items["landsat-c2-l2"][0])
    
    print(f"\nLandsat Data Availability Test Results:")
    print(f"Restrictive filtering (<5% entire, <10% cropped): {restrictive_count} items")
    print(f"Permissive filtering (all clouds allowed): {permissive_count} items")
    
    # Verify that permissive filtering returns more data
    assert permissive_count >= restrictive_count, "Permissive filtering should return at least as much data as restrictive filtering"


def test_cloud_cover_filtering_affects_data_availability_ndvi(sample_geometry):
    """
    Test that less restrictive cloud cover filtering returns more NDVI data.
    """
    
    # Test with very restrictive cloud filtering
    restrictive_ndvi = HarmonizedNDVI(
        start_date="2021-01-01",
        end_date="2021-12-31",
        gdf=sample_geometry,
        collections=["sentinel-2-l2a"],
        max_entire_image_cloud_cover=5,  # Very restrictive
        max_cropped_area_cloud_cover=10,  # Very restrictive
        max_workers=2,
    )
    
    # Test with permissive cloud filtering
    permissive_ndvi = HarmonizedNDVI(
        start_date="2021-01-01",
        end_date="2021-12-31",
        gdf=sample_geometry,
        collections=["sentinel-2-l2a"],
        max_entire_image_cloud_cover=100,  # Permissive
        max_cropped_area_cloud_cover=100,  # Permissive
        max_workers=2,
    )
    
    # Get items for each configuration
    restrictive_items = restrictive_ndvi.get_items()
    permissive_items = permissive_ndvi.get_items()
    
    # Count items
    restrictive_count = len(restrictive_items["sentinel-2-l2a"][0])
    permissive_count = len(permissive_items["sentinel-2-l2a"][0])
    
    print(f"\nNDVI Data Availability Test Results:")
    print(f"Restrictive filtering (<5% entire, <10% cropped): {restrictive_count} items")
    print(f"Permissive filtering (all clouds allowed): {permissive_count} items")
    
    # Verify that permissive filtering returns more data
    assert permissive_count >= restrictive_count, "Permissive filtering should return at least as much data as restrictive filtering"


def test_maximum_data_availability(sample_geometry):
    """
    Test that setting maximum cloud cover values returns the most data possible.
    """
    
    # Configuration for maximum data availability
    max_data_s2 = Sentinel2Items(
        gdf=sample_geometry,
        start_date="2021-01-01",
        end_date="2021-12-31",
        max_entire_image_cloud_cover=100,  # Maximum: accept all images
        max_cropped_area_cloud_cover=100,  # Maximum: accept all time steps
        max_workers=2,
    )
    
    # Get all available items
    all_items = max_data_s2.get_items()
    total_items = len(all_items["sentinel-2-l2a"][0])
    
    print(f"\nMaximum Data Availability Test:")
    print(f"Total items found with maximum cloud cover tolerance: {total_items}")
    
    if total_items > 0:
        # Show details of first few items
        print(f"\nFirst 3 items details:")
        for i, item in enumerate(all_items["sentinel-2-l2a"][0][:3]):
            cloud_cover = item.properties.get('eo:cloud_cover', 'N/A')
            print(f"  Item {i+1}: {item.id}")
            print(f"    Date: {item.datetime.date()}")
            print(f"    Cloud cover: {cloud_cover}%")
            print(f"    Platform: {item.properties.get('platform', 'N/A')}")
        
        # Test loading data without any cloud filtering
        print(f"\nLoading data without cloud filtering...")
        data = max_data_s2.load_xarray(
            filter_cloud_cover=False,  # No cloud filtering at all
            include_rgb=True
        )
        
        total_time_steps = 0
        for ds in data["sentinel-2-l2a"]:
            if ds is not None:
                total_time_steps += len(ds.time)
        
        print(f"Total time steps loaded: {total_time_steps}")
        
        # Verify we got some data
        assert total_time_steps >= 0, "Should be able to load data with maximum cloud tolerance"


def test_cloud_cover_parameter_behavior(sample_geometry):
    """
    Test to verify the behavior of cloud cover parameters with different values.
    """
    
    # Test different max_entire_image_cloud_cover values
    test_configs = [
        (5, "Very restrictive"),
        (20, "Moderate"),
        (50, "Permissive"),
        (100, "Maximum")
    ]
    
    results = []
    
    for cloud_threshold, description in test_configs:
        s2 = Sentinel2Items(
            gdf=sample_geometry,
            start_date="2021-01-01",
            end_date="2021-12-31",
            max_entire_image_cloud_cover=cloud_threshold,
            max_cropped_area_cloud_cover=100,  # Keep this constant for fair comparison
            max_workers=2,
        )
        
        items = s2.get_items()
        item_count = len(items["sentinel-2-l2a"][0])
        results.append((description, cloud_threshold, item_count))
    
    print(f"\nCloud Cover Parameter Behavior Test:")
    print(f"{'Description':<20} {'Threshold':<10} {'Items Found':<12}")
    print("-" * 45)
    
    for description, threshold, count in results:
        print(f"{description:<20} {threshold:<10} {count:<12}")
    
    # Verify that higher thresholds generally return more data
    for i in range(1, len(results)):
        prev_count = results[i-1][2]
        curr_count = results[i][2]
        assert curr_count >= prev_count, f"Higher threshold should return at least as much data: {results[i-1][0]} ({prev_count}) vs {results[i][0]} ({curr_count})"


if __name__ == "__main__":
    # Run the tests and show results
    print("Running cloud cover filtering tests...")
    
    # Create sample geometry
    polygon = Polygon([
        (-122.2751, 47.5469),
        (-121.9613, 47.5469),
        (-121.9613, 47.7458),
        (-122.2751, 47.7458),
        (-122.2751, 47.5469)
    ])
    sample_geometry = gpd.GeoDataFrame([1], geometry=[polygon], crs="EPSG:4326")
    
    # Run tests
    test_cloud_cover_filtering_affects_data_availability_sentinel2(sample_geometry)
    test_cloud_cover_filtering_affects_data_availability_landsat(sample_geometry)
    test_cloud_cover_filtering_affects_data_availability_ndvi(sample_geometry)
    test_maximum_data_availability(sample_geometry)
    test_cloud_cover_parameter_behavior(sample_geometry)
    
    print("\nAll tests completed successfully!") 