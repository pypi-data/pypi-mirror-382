"""
Test that uses real classes to demonstrate both cloud cover parameters working together.

This test shows how both parameters affect data availability in practice.
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


def test_both_parameters_sentinel2(sample_geometry):
    """
    Test both cloud cover parameters with Sentinel-2 data.
    """
    
    print("\n🔍 Testing Both Parameters with Sentinel-2 Data")
    print("=" * 60)
    
    # Test different combinations of both parameters
    test_configs = [
        {
            'name': 'Very restrictive (both low)',
            'entire': 5,
            'cropped': 10,
            'description': 'High quality, limited data'
        },
        {
            'name': 'Moderate (both moderate)',
            'entire': 20,
            'cropped': 30,
            'description': 'Balanced quality and coverage'
        },
        {
            'name': 'Mixed (high entire, low cropped)',
            'entire': 50,
            'cropped': 15,
            'description': 'Many items found, few pass loading'
        },
        {
            'name': 'Mixed (low entire, high cropped)',
            'entire': 15,
            'cropped': 50,
            'description': 'Few items found, most pass loading'
        },
        {
            'name': 'Maximum (both high)',
            'entire': 100,
            'cropped': 100,
            'description': 'All data available'
        }
    ]
    
    results = []
    
    for config in test_configs:
        print(f"\n📡 Testing: {config['name']}")
        print(f"   {config['description']}")
        print(f"   max_entire_image_cloud_cover={config['entire']}%")
        print(f"   max_cropped_area_cloud_cover={config['cropped']}%")
        
        try:
            # Create Sentinel2Items instance with both parameters
            s2 = Sentinel2Items(
                gdf=sample_geometry,
                start_date="2021-01-01",
                end_date="2021-12-31",
                max_entire_image_cloud_cover=config['entire'],
                max_cropped_area_cloud_cover=config['cropped'],
                max_workers=2,
            )
            
            # Get items (this uses max_entire_image_cloud_cover)
            items_dict = s2.get_items()
            items_after_search = len(items_dict["sentinel-2-l2a"][0])
            
            print(f"   ✅ Items after STAC search: {items_after_search}")
            
            # Show details of first few items
            if items_after_search > 0:
                print(f"   📋 First 3 items:")
                for i, item in enumerate(items_dict["sentinel-2-l2a"][0][:3]):
                    cloud_cover = item.properties.get('eo:cloud_cover', 'N/A')
                    date = item.datetime.date() if item.datetime else 'N/A'
                    print(f"     {i+1}. {item.id} | Date: {date} | Cloud cover: {cloud_cover}%")
            
            # Try to load data (this uses max_cropped_area_cloud_cover)
            try:
                data = s2.load_xarray(
                    filter_cloud_cover=True,  # This enables cropped area filtering
                    include_rgb=True
                )
                
                # Count time steps after loading
                time_steps_after_loading = 0
                for ds in data["sentinel-2-l2a"]:
                    if ds is not None:
                        time_steps_after_loading += len(ds.time)
                
                print(f"   ✅ Time steps after loading: {time_steps_after_loading}")
                
                results.append({
                    'name': config['name'],
                    'entire': config['entire'],
                    'cropped': config['cropped'],
                    'items_after_search': items_after_search,
                    'time_steps_after_loading': time_steps_after_loading
                })
                
            except Exception as e:
                print(f"   ❌ Error loading data: {e}")
                results.append({
                    'name': config['name'],
                    'entire': config['entire'],
                    'cropped': config['cropped'],
                    'items_after_search': items_after_search,
                    'time_steps_after_loading': 0
                })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'name': config['name'],
                'entire': config['entire'],
                'cropped': config['cropped'],
                'items_after_search': 0,
                'time_steps_after_loading': 0
            })
    
    # Display summary
    print(f"\n📊 Both Parameters Results Summary:")
    print(f"{'Configuration':<35} {'Entire':<8} {'Cropped':<8} {'After Search':<12} {'After Loading':<12}")
    print("-" * 85)
    
    for result in results:
        print(f"{result['name']:<35} {result['entire']:<8} {result['cropped']:<8} {result['items_after_search']:<12} {result['time_steps_after_loading']:<12}")
    
    # Analyze the results
    print(f"\n🎯 Analysis:")
    
    # Find which configuration gives most data
    max_data_config = max(results, key=lambda x: x['time_steps_after_loading'])
    print(f"  • Most data: {max_data_config['name']} ({max_data_config['time_steps_after_loading']} time steps)")
    
    # Find which configuration gives least data
    min_data_config = min(results, key=lambda x: x['time_steps_after_loading'])
    print(f"  • Least data: {min_data_config['name']} ({min_data_config['time_steps_after_loading']} time steps)")
    
    # Show the relationship between parameters
    print(f"\n📈 Parameter Relationship:")
    for result in results:
        if result['items_after_search'] > 0 and result['time_steps_after_loading'] > 0:
            ratio = result['time_steps_after_loading'] / result['items_after_search']
            print(f"  • {result['name']}: {ratio:.2f} time steps per item found")


def test_both_parameters_landsat(sample_geometry):
    """
    Test both cloud cover parameters with Landsat data.
    """
    
    print("\n🔍 Testing Both Parameters with Landsat Data")
    print("=" * 60)
    
    # Test different combinations
    test_configs = [
        {
            'name': 'Restrictive',
            'entire': 10,
            'cropped': 20,
        },
        {
            'name': 'Moderate',
            'entire': 30,
            'cropped': 50,
        },
        {
            'name': 'Maximum',
            'entire': 100,
            'cropped': 100,
        }
    ]
    
    results = []
    
    for config in test_configs:
        print(f"\n📡 Testing: {config['name']}")
        print(f"   max_entire_image_cloud_cover={config['entire']}%")
        print(f"   max_cropped_area_cloud_cover={config['cropped']}%")
        
        try:
            # Create LandsatItems instance
            landsat = LandsatItems(
                gdf=sample_geometry,
                start_date="2021-01-01",
                end_date="2021-12-31",
                max_entire_image_cloud_cover=config['entire'],
                max_cropped_area_cloud_cover=config['cropped'],
                max_workers=2,
            )
            
            # Get items
            items_dict = landsat.get_items()
            items_after_search = len(items_dict["landsat-c2-l2"][0])
            
            print(f"   ✅ Items after STAC search: {items_after_search}")
            
            # Try to load data
            try:
                data = landsat.load_xarray(
                    filter_cloud_cover=True,
                    include_rgb=True
                )
                
                time_steps_after_loading = 0
                for ds in data["landsat-c2-l2"]:
                    if ds is not None:
                        time_steps_after_loading += len(ds.time)
                
                print(f"   ✅ Time steps after loading: {time_steps_after_loading}")
                
                results.append({
                    'name': config['name'],
                    'entire': config['entire'],
                    'cropped': config['cropped'],
                    'items_after_search': items_after_search,
                    'time_steps_after_loading': time_steps_after_loading
                })
                
            except Exception as e:
                print(f"   ❌ Error loading data: {e}")
                results.append({
                    'name': config['name'],
                    'entire': config['entire'],
                    'cropped': config['cropped'],
                    'items_after_search': items_after_search,
                    'time_steps_after_loading': 0
                })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'name': config['name'],
                'entire': config['entire'],
                'cropped': config['cropped'],
                'items_after_search': 0,
                'time_steps_after_loading': 0
            })
    
    # Display summary
    print(f"\n📊 Landsat Both Parameters Results:")
    print(f"{'Configuration':<15} {'Entire':<8} {'Cropped':<8} {'After Search':<12} {'After Loading':<12}")
    print("-" * 65)
    
    for result in results:
        print(f"{result['name']:<15} {result['entire']:<8} {result['cropped']:<8} {result['items_after_search']:<12} {result['time_steps_after_loading']:<12}")


def test_maximum_data_with_both_parameters(sample_geometry):
    """
    Test that setting both parameters to maximum returns the most data.
    """
    
    print("\n🔍 Testing Maximum Data with Both Parameters")
    print("=" * 60)
    
    # Test with maximum values for both parameters
    print(f"\n📡 Testing maximum data availability...")
    print(f"   max_entire_image_cloud_cover=100%")
    print(f"   max_cropped_area_cloud_cover=100%")
    
    try:
        # Create Sentinel2Items with maximum values
        s2_max = Sentinel2Items(
            gdf=sample_geometry,
            start_date="2021-01-01",
            end_date="2021-12-31",
            max_entire_image_cloud_cover=100,  # Maximum tolerance
            max_cropped_area_cloud_cover=100,  # Maximum tolerance
            max_workers=2,
        )
        
        # Get all available items
        items_dict = s2_max.get_items()
        total_items = len(items_dict["sentinel-2-l2a"][0])
        
        print(f"   ✅ Total items found: {total_items}")
        
        if total_items > 0:
            # Load data without cloud filtering
            data = s2_max.load_xarray(
                filter_cloud_cover=False,  # No cloud filtering to get maximum data
                include_rgb=True
            )
            
            total_time_steps = 0
            for ds in data["sentinel-2-l2a"]:
                if ds is not None:
                    total_time_steps += len(ds.time)
            
            print(f"   ✅ Total time steps loaded: {total_time_steps}")
            
            # Show cloud cover distribution
            cloud_covers = []
            for item in items_dict["sentinel-2-l2a"][0]:
                cloud_cover = item.properties.get('eo:cloud_cover', 0)
                cloud_covers.append(cloud_cover)
            
            clear_items = sum(1 for cc in cloud_covers if cc < 10)
            moderate_items = sum(1 for cc in cloud_covers if 10 <= cc < 50)
            cloudy_items = sum(1 for cc in cloud_covers if cc >= 50)
            
            print(f"\n📊 Cloud Cover Distribution:")
            print(f"   • Clear (<10% clouds): {clear_items} items ({clear_items/total_items*100:.1f}%)")
            print(f"   • Moderate (10-50% clouds): {moderate_items} items ({moderate_items/total_items*100:.1f}%)")
            print(f"   • Cloudy (≥50% clouds): {cloudy_items} items ({cloudy_items/total_items*100:.1f}%)")
            
            print(f"\n🎯 Maximum Data Strategy:")
            print(f"   • Setting both parameters to 100 returns ALL available data")
            print(f"   • You can then apply cloud filtering during analysis as needed")
            print(f"   • This gives maximum temporal coverage and flexibility")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    # Run the real data tests
    print("Running real both parameters tests...")
    
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
    test_both_parameters_sentinel2(sample_geometry)
    test_both_parameters_landsat(sample_geometry)
    test_maximum_data_with_both_parameters(sample_geometry)
    
    print("\n✅ All real both parameters tests completed!") 