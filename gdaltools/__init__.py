# -*- coding: utf-8 -*-
"""Python library providing wrappers for the most common Gdal/OGR command
line tools"""

from . import metadata

__version__ = metadata.version
__author__ = metadata.authors[0]
__license__ = metadata.license
__copyright__ = metadata.copyright

from .api import ogr2ogr
from .basetypes import ConnectionString, PgConnectionString, FileConnectionString, GdalToolsError
from .gdalinfocmd import get_raster_stats, gdalinfo
from .gdalinfocmd import GdalInfo
from .ogr2ogrcmd import Ogr2ogr
