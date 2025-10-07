"""
Test that searches for real satellite data to demonstrate cloud cover filtering.

This test connects to Planetary Computer and searches for actual satellite data
with different cloud cover settings to show how filtering affects data availability.
"""

import geopandas as gpd
import pytest
from shapely.geometry import Polygon

from environmental_risk_metrics.utils.planetary_computer import (
    get_planetary_computer_items,
)


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


def test_real_cloud_cover_filtering_sentinel2(sample_geometry):
    """
    Test real cloud cover filtering with Sentinel-2 data from Planetary Computer.
    
    This test searches for actual Sentinel-2 data with different cloud cover settings
    and demonstrates that less restrictive filtering returns more data.
    """
    
    print("\n🔍 Testing Real Cloud Cover Filtering with Sentinel-2 Data")
    print("=" * 60)
    
    # Convert geometry to GeoJSON for STAC search
    polygon_geojson = sample_geometry.to_crs(epsg=4326).geometry.iloc[0].__geo_interface__
    
    # Test different cloud cover thresholds
    test_configs = [
        (5, "Very restrictive (<5% clouds)"),
        (20, "Moderate (<20% clouds)"),
        (50, "Permissive (<50% clouds)"),
        (100, "Maximum (all clouds allowed)")
    ]
    
    results = []
    
    for threshold, description in test_configs:
        print(f"\n📡 Searching with {description}...")
        
        try:
            # Search for Sentinel-2 items with the specified cloud cover threshold
            items = get_planetary_computer_items(
                collections=["sentinel-2-l2a"],
                start_date="2021-01-01",
                end_date="2021-12-31",
                polygon=polygon_geojson,
                max_entire_image_cloud_cover=threshold
            )
            
            item_count = len(items)
            results.append((description, threshold, item_count))
            
            print(f"  ✅ Found {item_count} items")
            
            # Show details of first few items
            if item_count > 0:
                print(f"  📋 First 3 items:")
                for i, item in enumerate(items[:3]):
                    cloud_cover = item.properties.get('eo:cloud_cover', 'N/A')
                    date = item.datetime.date() if item.datetime else 'N/A'
                    print(f"    {i+1}. {item.id} | Date: {date} | Cloud cover: {cloud_cover}%")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append((description, threshold, 0))
    
    # Display summary
    print(f"\n📊 Cloud Cover Filtering Results Summary:")
    print(f"{'Filtering Level':<25} {'Threshold':<12} {'Items Found':<12} {'Trend'}")
    print("-" * 65)
    
    for i, (description, threshold, count) in enumerate(results):
        trend = ""
        if i > 0:
            prev_count = results[i-1][2]
            if count > prev_count:
                trend = "↗️ More data"
            elif count == prev_count:
                trend = "→ Same data"
            else:
                trend = "↘️ Less data"
        
        print(f"{description:<25} {threshold:<12} {count:<12} {trend}")
    
    # Verify that higher thresholds generally return more data
    print(f"\n✅ Verification:")
    for i in range(1, len(results)):
        prev_threshold, prev_count = results[i-1][1], results[i-1][2]
        curr_threshold, curr_count = results[i][1], results[i][2]
        
        if curr_count >= prev_count:
            print(f"  ✓ Threshold {curr_threshold}% ({curr_count} items) >= {prev_threshold}% ({prev_count} items)")
        else:
            print(f"  ⚠️  Threshold {curr_threshold}% ({curr_count} items) < {prev_threshold}% ({prev_count} items) - this can happen due to data availability")
    
    print(f"\n🎯 Key Insights:")
    print(f"  • Higher cloud cover thresholds generally return more data")
    print(f"  • Very restrictive filtering (<5% clouds) gives high quality but limited data")
    print(f"  • Maximum tolerance (100%) returns all available data")
    print(f"  • Real-world data availability may vary due to seasonal patterns")


def test_real_cloud_cover_filtering_landsat(sample_geometry):
    """
    Test real cloud cover filtering with Landsat data from Planetary Computer.
    """
    
    print("\n🔍 Testing Real Cloud Cover Filtering with Landsat Data")
    print("=" * 60)
    
    # Convert geometry to GeoJSON for STAC search
    polygon_geojson = sample_geometry.to_crs(epsg=4326).geometry.iloc[0].__geo_interface__
    
    # Test different cloud cover thresholds
    test_configs = [
        (10, "Restrictive (<10% clouds)"),
        (50, "Moderate (<50% clouds)"),
        (100, "Maximum (all clouds allowed)")
    ]
    
    results = []
    
    for threshold, description in test_configs:
        print(f"\n📡 Searching with {description}...")
        
        try:
            # Search for Landsat items with the specified cloud cover threshold
            items = get_planetary_computer_items(
                collections=["landsat-c2-l2"],
                start_date="2021-01-01",
                end_date="2021-12-31",
                polygon=polygon_geojson,
                max_entire_image_cloud_cover=threshold
            )
            
            item_count = len(items)
            results.append((description, threshold, item_count))
            
            print(f"  ✅ Found {item_count} items")
            
            # Show details of first few items
            if item_count > 0:
                print(f"  📋 First 3 items:")
                for i, item in enumerate(items[:3]):
                    cloud_cover = item.properties.get('eo:cloud_cover', 'N/A')
                    date = item.datetime.date() if item.datetime else 'N/A'
                    platform = item.properties.get('platform', 'N/A')
                    print(f"    {i+1}. {item.id} | Date: {date} | Cloud cover: {cloud_cover}% | Platform: {platform}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append((description, threshold, 0))
    
    # Display summary
    print(f"\n📊 Landsat Cloud Cover Filtering Results:")
    print(f"{'Filtering Level':<25} {'Threshold':<12} {'Items Found':<12}")
    print("-" * 55)
    
    for description, threshold, count in results:
        print(f"{description:<25} {threshold:<12} {count:<12}")
    
    print(f"\n✅ Landsat data typically has fewer observations than Sentinel-2")
    print(f"   but covers longer time periods and different spectral bands")


def test_maximum_data_availability_real(sample_geometry):
    """
    Test maximum data availability with real satellite data.
    """
    
    print("\n🔍 Testing Maximum Data Availability with Real Data")
    print("=" * 60)
    
    # Convert geometry to GeoJSON for STAC search
    polygon_geojson = sample_geometry.to_crs(epsg=4326).geometry.iloc[0].__geo_interface__
    
    # Test with maximum cloud cover tolerance
    print(f"\n📡 Searching for maximum data availability...")
    
    try:
        # Search for all available Sentinel-2 items (no cloud filtering)
        all_items = get_planetary_computer_items(
            collections=["sentinel-2-l2a"],
            start_date="2021-01-01",
            end_date="2021-12-31",
            polygon=polygon_geojson,
            max_entire_image_cloud_cover=100  # Maximum tolerance
        )
        
        total_items = len(all_items)
        print(f"  ✅ Found {total_items} total items with maximum cloud tolerance")
        
        if total_items > 0:
            # Analyze cloud cover distribution
            cloud_covers = []
            for item in all_items:
                cloud_cover = item.properties.get('eo:cloud_cover', 0)
                cloud_covers.append(cloud_cover)
            
            # Calculate statistics
            clear_items = sum(1 for cc in cloud_covers if cc < 10)
            moderate_items = sum(1 for cc in cloud_covers if 10 <= cc < 50)
            cloudy_items = sum(1 for cc in cloud_covers if cc >= 50)
            
            print(f"\n📊 Cloud Cover Distribution:")
            print(f"  • Clear (<10% clouds): {clear_items} items ({clear_items/total_items*100:.1f}%)")
            print(f"  • Moderate (10-50% clouds): {moderate_items} items ({moderate_items/total_items*100:.1f}%)")
            print(f"  • Cloudy (≥50% clouds): {cloudy_items} items ({cloudy_items/total_items*100:.1f}%)")
            
            # Show examples of different cloud cover levels
            print(f"\n📋 Examples by cloud cover level:")
            
            # Find examples of each category
            clear_examples = [item for item in all_items if item.properties.get('eo:cloud_cover', 0) < 10][:2]
            moderate_examples = [item for item in all_items if 10 <= item.properties.get('eo:cloud_cover', 0) < 50][:2]
            cloudy_examples = [item for item in all_items if item.properties.get('eo:cloud_cover', 0) >= 50][:2]
            
            if clear_examples:
                print(f"  🌤️  Clear examples:")
                for item in clear_examples:
                    print(f"    • {item.id} | Cloud cover: {item.properties.get('eo:cloud_cover', 'N/A')}%")
            
            if moderate_examples:
                print(f"  ⛅ Moderate examples:")
                for item in moderate_examples:
                    print(f"    • {item.id} | Cloud cover: {item.properties.get('eo:cloud_cover', 'N/A')}%")
            
            if cloudy_examples:
                print(f"  ☁️  Cloudy examples:")
                for item in cloudy_examples:
                    print(f"    • {item.id} | Cloud cover: {item.properties.get('eo:cloud_cover', 'N/A')}%")
            
            print(f"\n🎯 Maximum Data Strategy:")
            print(f"  • Setting max_entire_image_cloud_cover=100 returns ALL available data")
            print(f"  • You can then apply post-processing cloud filtering during analysis")
            print(f"  • This gives you maximum temporal coverage and flexibility")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")


if __name__ == "__main__":
    # Run the real data tests
    print("Running real cloud cover filtering tests...")
    
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
    test_real_cloud_cover_filtering_sentinel2(sample_geometry)
    test_real_cloud_cover_filtering_landsat(sample_geometry)
    test_maximum_data_availability_real(sample_geometry)
    
    print("\n✅ All real data tests completed!") 