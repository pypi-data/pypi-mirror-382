#!/usr/bin/env python3
"""GeoParquet export format implementation.

This module provides GeoParquet export functionality for geospatial census data.
"""

import logging
from pathlib import Path

import geopandas as gpd
import pandas as pd

from socialmapper.constants import CATEGORICAL_CONVERSION_THRESHOLD

from ..base import BaseExporter, ExportError

logger = logging.getLogger(__name__)


class GeoParquetExporter(BaseExporter):
    """GeoParquet format exporter for geospatial census data.

    Exports GeoDataFrames to GeoParquet files with geometry support,
    automatic dtype optimization, and configurable compression.
    Falls back to standard Parquet for non-spatial data.
    """

    def export(
        self,
        data: pd.DataFrame | gpd.GeoDataFrame,
        output_path: str | Path,
        compression: str = "snappy",
        **kwargs,
    ) -> str:
        """Export GeoDataFrame to GeoParquet file with spatial support.

        Preserves geometry columns using the GeoParquet specification.
        Automatically converts DataFrames to GeoDataFrames when
        geometry column is present. Falls back to standard Parquet
        for non-spatial data.

        Parameters
        ----------
        data : pd.DataFrame or gpd.GeoDataFrame
            DataFrame or GeoDataFrame containing data to export.
        output_path : str or Path
            File path where the GeoParquet file should be saved.
        compression : str, optional
            Compression algorithm to use. Options: 'snappy', 'gzip',
            'brotli', or None for no compression. By default 'snappy'.
        **kwargs : dict, optional
            Additional keyword arguments passed to
            geopandas.to_parquet().

        Returns:
        -------
        str
            Absolute path to the saved GeoParquet file.

        Raises:
        ------
        ExportError
            If the file cannot be saved to the specified path.

        Examples:
        --------
        >>> import geopandas as gpd
        >>> exporter = GeoParquetExporter(config)
        >>> gdf = gpd.read_file('census_tracts.geojson')
        >>> path = exporter.export(gdf, 'census.geoparquet',
        ...                        compression='gzip')
        """
        output_path = self.validate_output_path(output_path)

        try:
            # Ensure we have a GeoDataFrame
            if not isinstance(data, gpd.GeoDataFrame):
                if "geometry" in data.columns:
                    logger.info("Converting DataFrame to GeoDataFrame")
                    data = gpd.GeoDataFrame(data)
                else:
                    logger.warning("No geometry column found, using standard Parquet instead")
                    from .parquet import ParquetExporter

                    parquet_exporter = ParquetExporter(self.config)
                    return parquet_exporter.export(data, output_path, compression, **kwargs)

            # Optimize data types for better compression
            data = self._optimize_geodataframe(data)

            # Default GeoParquet options
            geoparquet_options = {
                "compression": compression,
                "index": False,
            }
            geoparquet_options.update(kwargs)

            # Save to GeoParquet
            data.to_parquet(output_path, **geoparquet_options)
            logger.info(f"Successfully saved GeoParquet to {output_path}")

            return str(output_path)

        except Exception as e:
            raise ExportError(f"Could not save GeoParquet: {e}") from e

    def _optimize_geodataframe(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Optimize GeoDataFrame column types for better compression.

        Converts object columns to categorical types for low-cardinality
        data and downcasts numeric types while preserving geometry.

        Parameters
        ----------
        gdf : gpd.GeoDataFrame
            GeoDataFrame to optimize.

        Returns:
        -------
        gpd.GeoDataFrame
            Optimized GeoDataFrame with reduced memory footprint.
        """
        gdf_optimized = gdf.copy()

        # Optimize non-geometry columns
        for col in gdf_optimized.columns:
            if col != gdf_optimized.geometry.name:
                col_type = gdf_optimized[col].dtype

                if col_type == "object":
                    # Try to convert to categorical for better compression
                    unique_ratio = gdf_optimized[col].nunique() / len(gdf_optimized)
                    if (
                        unique_ratio < CATEGORICAL_CONVERSION_THRESHOLD
                    ):  # Less than 50% unique values
                        gdf_optimized[col] = gdf_optimized[col].astype("category")

                elif col_type in ["int64", "float64"]:
                    # Downcast numeric types
                    if "int" in str(col_type):
                        gdf_optimized[col] = pd.to_numeric(gdf_optimized[col], downcast="integer")
                    else:
                        gdf_optimized[col] = pd.to_numeric(gdf_optimized[col], downcast="float")

        return gdf_optimized

    def get_file_extension(self) -> str:
        """Get the standard file extension for GeoParquet format.

        Returns:
        -------
        str
            The file extension '.geoparquet'.
        """
        return ".geoparquet"

    def supports_geometry(self) -> bool:
        """Check if GeoParquet format supports geometry columns.

        Returns:
        -------
        bool
            Always True. GeoParquet natively supports spatial geometry.
        """
        return True
