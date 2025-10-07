import logging
from concurrent.futures import ThreadPoolExecutor

import geopandas as gpd
import odc.stac
import planetary_computer
import pystac
import xarray as xr
from tqdm.auto import tqdm

from environmental_risk_metrics.base import BaseEnvironmentalMetric
from environmental_risk_metrics.utils.planetary_computer import (
    get_planetary_computer_items,
)

logger = logging.getLogger(__name__)


class LandsatItems(BaseEnvironmentalMetric):
    """
    A class for accessing Landsat Collection 2 Level 2 items from Planetary Computer.
    This class is focused on retrieving items and loading them as xarray Datasets.
    
    This class provides access to Landsat Collection 2 Level 2 data which includes
    surface reflectance and surface temperature products from multiple Landsat platforms
    (Landsat 4, 5, 7, 8, and 9).
    
    Key Features:
    - Supports landsat-c2-l2 collection
    - Automatic cloud filtering using qa_pixel band
    - Concurrent data loading for improved performance
    - Supports multiple geometries
    - Includes bands: red, green, blue, nir08, swir16, swir22, lwir11, qa_pixel
    
    Example:
    --------
    >>> import geopandas as gpd
    >>> from shapely.geometry import Polygon
    >>> from environmental_risk_metrics.metrics.landsat import LandsatItems
    >>> 
    >>> # Create a sample geometry
    >>> polygon = Polygon([(-122.2751, 47.5469), (-121.9613, 47.5469), 
    ...                    (-121.9613, 47.7458), (-122.2751, 47.7458), 
    ...                    (-122.2751, 47.5469)])
    >>> gdf = gpd.GeoDataFrame([1], geometry=[polygon], crs="EPSG:4326")
    >>> 
    >>> # Initialize the LandsatItems class
    >>> landsat = LandsatItems(
    ...     gdf=gdf,
    ...     start_date="2021-01-01",
    ...     end_date="2021-12-31",
    ...     max_entire_image_cloud_cover=10
    ... )
    >>> 
    >>> # Get items
    >>> items = landsat.get_items()
    >>> 
    >>> # Load data as xarray Dataset
    >>> data = landsat.load_xarray(include_rgb=True, filter_cloud_cover=True)
    >>> 
    >>> # Access the dataset
    >>> dataset = data["landsat-c2-l2"][0]
    >>> print(dataset.data_vars)
    """

    BAND_MAPPINGS = {
        "landsat-c2-l2": {
            "red": "red",
            "green": "green",
            "blue": "blue",
            "nir": "nir08",
            "swir1": "swir16",
            "swir2": "swir22",
            "thermal": "lwir11",
            "cloud_mask": "qa_pixel",
            "cloud_clear_values": [21824, 21888],  # Clear pixels (bit 6 set)
        },
    }

    def __init__(
        self,
        gdf: gpd.GeoDataFrame,
        start_date: str,
        end_date: str,
        resolution: int = 30,
        max_entire_image_cloud_cover: int = 100,
        max_cropped_area_cloud_cover: int = 80,
        max_workers: int = 10,
    ):
        sources = ["https://planetarycomputer.microsoft.com/api/stac/v1"]
        description = "Landsat Collection 2 Level 2 items from Planetary Computer."

        super().__init__(sources=sources, description=description)

        self.collections = ["landsat-c2-l2"]
        self.resolution = resolution
        self.max_entire_image_cloud_cover = max_entire_image_cloud_cover
        self.max_cropped_area_cloud_cover = max_cropped_area_cloud_cover
        self.max_workers = max_workers
        self.start_date = start_date
        self.end_date = end_date
        self.gdf = gdf.to_crs(epsg=4326)
        self.items = None
        self.xarray_data = None
        logger.debug("Initializing LandsatItems client")

    def get_items(
        self,
        max_entire_image_cloud_cover: int = None,
    ) -> dict[str, list[pystac.Item]]:
        """
        Search for items from Landsat within a given date range and polygon.
        Args:
            max_entire_image_cloud_cover: Maximum cloud cover percentage allowed for entire image (excludes images with higher cloud cover)
        Returns:
            Dictionary with collection name as key and list of pystac.Item objects as values
        """
        if self.items is not None:
            return self.items

        if max_entire_image_cloud_cover is None:
            max_entire_image_cloud_cover = self.max_entire_image_cloud_cover

        gdf = self.gdf.to_crs(epsg=4326)
        items_by_collection = {"landsat-c2-l2": []}
        collection = "landsat-c2-l2"

        def fetch_items_for_collection(collection_polygon_pair):
            collection, polygon = collection_polygon_pair
            return collection, get_planetary_computer_items(
                collections=[collection],
                start_date=self.start_date,
                end_date=self.end_date,
                polygon=polygon,
                max_entire_image_cloud_cover=max_entire_image_cloud_cover,
            )

        collection_polygon_pairs = [(collection, geom) for geom in gdf.geometry]

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(
                tqdm(
                    executor.map(fetch_items_for_collection, collection_polygon_pairs),
                    total=len(collection_polygon_pairs),
                    desc=f"Fetching {collection} items",
                )
            )

        for i, (_, items_list) in enumerate(results):
            if i >= len(items_by_collection[collection]):
                items_by_collection[collection].extend(
                    [[] for _ in range(i + 1 - len(items_by_collection[collection]))]
                )
            items_by_collection[collection][i] = items_list

        self.items = items_by_collection
        return self.items

    def _get_bands_for_collection(
        self, collection: str, include_rgb: bool = False
    ) -> list[str]:
        """Get the required bands for a collection"""
        mapping = self.BAND_MAPPINGS[collection]
        bands = [mapping["nir"], mapping["red"]]
        if include_rgb:
            bands.extend([mapping["green"], mapping["blue"]])
        if mapping["cloud_mask"]:
            bands.append(mapping["cloud_mask"])
        return bands

    def load_xarray(
        self,
        bands: dict[str, list[str]] = None,
        show_progress: bool = True,
        filter_cloud_cover: bool = True,
        include_rgb: bool = False,
    ) -> dict[str, list[xr.Dataset]]:
        """Load data for all collections into xarray Datasets.
        Args:
            bands: Dictionary with collection names as keys and band lists as values
            show_progress: Whether to show a progress bar
            filter_cloud_cover: Whether to filter the data based on cloud cover
            include_rgb: Whether to include RGB bands for visualization
        Returns:
            Dictionary with collection names as keys and lists of xarray Datasets as values
        """
        if self.xarray_data is not None:
            return self.xarray_data

        logger.debug(
            f"Loading data for collections {self.collections} at {self.resolution}m resolution"
        )

        items_dict = self.get_items()

        if not any(items_dict.values()):
            logger.error(
                "No items found for any collection in the given date range and polygon"
            )
            raise ValueError(
                "No items found for any collection in the given date range and polygon"
            )

        self.xarray_data = {}

        for collection in self.collections:
            self.xarray_data[collection] = []
            items_list = items_dict.get(collection, [])

            if not items_list:
                logger.warning(f"No items found for collection {collection}")
                continue

            if bands and collection in bands:
                collection_bands = bands[collection]
            else:
                collection_bands = self._get_bands_for_collection(
                    collection, include_rgb
                )

            mapping = self.BAND_MAPPINGS[collection]

            for geometry_idx, (items, geometry) in enumerate(
                zip(items_list, self.gdf.geometry)
            ):
                if not items:
                    logger.warning(
                        f"No items for geometry {geometry_idx} in collection {collection}"
                    )
                    self.xarray_data[collection].append(None)
                    continue

                logger.debug(f"Signing {len(items)} items for collection {collection}")
                signed_items = [planetary_computer.sign(i) for i in items]

                thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)

                logger.debug(f"Loading data into xarray Dataset for {collection}")
                progress = tqdm if show_progress else None

                try:
                    ds = odc.stac.load(
                        items=signed_items,
                        bands=collection_bands,
                        resolution=self.resolution,
                        pool=thread_pool,
                        geopolygon=geometry,
                        progress=progress,
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to load data for {collection}, geometry {geometry_idx}: {e}"
                    )
                    self.xarray_data[collection].append(None)
                    continue

                if (
                    self.max_cropped_area_cloud_cover
                    and filter_cloud_cover
                    and mapping["cloud_mask"]
                ):
                    logger.debug(
                        f"Filtering data based on cloud cover using {mapping['cloud_mask']} band"
                    )

                    # For Landsat qa_pixel, bit 6 indicates clear pixels
                    # We check if bit 6 is set (clear pixel)
                    cloud_clear_mask = (ds[mapping["cloud_mask"]] & 64) == 64

                    cloud_cover_pct = (1 - cloud_clear_mask.mean(dim=["x", "y"])) * 100
                    logger.debug(
                        f"Cloud cover percentage: {cloud_cover_pct}. Filtering based on {self.max_cropped_area_cloud_cover}% threshold"
                    )

                    logger.debug(f"Dataset time steps before filtering: {len(ds.time)}")
                    ds = ds.sel(
                        time=cloud_cover_pct <= self.max_cropped_area_cloud_cover
                    )
                    logger.debug(f"Filtered dataset to {len(ds.time)} time steps")

                    if filter_cloud_cover:
                        ds = ds.where(cloud_clear_mask, drop=False)

                logger.debug(f"Successfully loaded {collection} data")
                self.xarray_data[collection].append(ds)

        return self.xarray_data 