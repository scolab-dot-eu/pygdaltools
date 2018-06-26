# -*- coding: utf-8 -*-
from __future__ import unicode_literals
'''
    gvSIG Online.
    Copyright (C) 2015-2016 gvSIG Association.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
'''
@author: Cesar Martinez Izquierdo - Scolab <http://scolab.es>
'''


import logging
import os
from .basetypes import Wrapper, ConnectionString, FileConnectionString, PgConnectionString


class Ogr2ogr(Wrapper):
    """
    Wrapper for the ogr2ogr command
    """
    MODE_LAYER_CREATE="CR"
    MODE_LAYER_APPEND="AP"
    MODE_LAYER_OVERWRITE="OW"
    
    MODE_DS_CREATE="CR"
    MODE_DS_UPDATE="UP"
    MODE_DS_CREATE_OR_UPDATE="CU"
    
    CMD = 'ogr2ogr'
    
    def __init__(self, version=1, command_path=None):
        Wrapper.__init__(self, version, command_path)
        self.set_output_mode()
        self._dataset_creation_options = {}
        self._layer_creation_options = {}
        self._dataset_creation_options_internal = {}
        self._layer_creation_options_internal = {}
        self._config_options = {}
        self._config_options_internal = {}
        self.geom_type = None
        self.encoding = None
        self.preserve_fid = None
    
    def set_input(self, input_ds, table_name=None, srs=None):
        """
        Sets the input layer
        
        :param input_ds: The path to the input data source (shapefile, spatialite, etc)
        or a ConnectionString object
        :param table_name: The name of the input table name in the data source. Can be
        omitted for some data source types such as Shapefiles or CSVs
        :param srs: Defines the SRS of the input layer, using a EPSG code string
        (e.g. "EPSG:4326"). Ogr will try to autodetect the SRS if this parameter is omitted,
        but autodetection will fail in a number of situations, so it is always recommended
        to explicitly set the SRS parameter
        """
        if isinstance(input_ds, ConnectionString):
            self.in_ds = input_ds
        else:
            self.in_ds = FileConnectionString(input_ds)
        self.in_table = table_name
        self.in_srs = srs
        return self
    
    def set_output(self, output_ds, file_type=None, table_name=None, srs=None):
        """
        Sets the output layer
        :param output_ds: The path to the output data source (shapefile, spatialite, etc)
        or a ConnectionString object (for Postgresql connections, etc)
        :param file_type: The output data source type (e.g. "ESRI Shapefile", "GML",
        "GeoJSON", "PostgreSQL", etc). See ogr2ogr documentation for the full list
        of valid types
        :param table_name: The name of the output table name in the data source. If omitted,
        the name of the input table will be used. It will be ignored for some data source types
        such as Shapefiles or CSVs which don't have the concept of table
        :param srs: Defines a transformation from the input SRS to this SRS.
        It expects a EPSG code string (e.g. "EPSG:4326"). If omitted and the input SRS
        has been defined, then the input SRS will also be used as output SRS
        """
        if isinstance(output_ds, ConnectionString):
            self.out_ds = output_ds
        else:
            self.out_ds = FileConnectionString(output_ds)

        if file_type:
            self.out_file_type = file_type
        else:
            dslower = self.out_ds.encode().lower()
            if dslower.endswith(".shp"):
                self.out_file_type = "ESRI Shapefile"
            elif dslower.startswith("pg:"):
                self.out_file_type = "PostgreSQL"
            elif dslower.endswith(".sqlite"):
                self.out_file_type = "SQLite"
            elif dslower.endswith(".json") or dslower.endswith(".geojson"):
                self.out_file_type = "GeoJSON"
            elif dslower.endswith(".gml"):
                self.out_file_type = "GML"
            elif dslower.endswith(".csv"):
                self.out_file_type = "CSV"
            elif dslower.endswith(".gpx"):
                self.out_file_type = "GPX"
            elif dslower.endswith(".kml"):
                self.out_file_type = "KML"
            else:
                self.out_file_type = "ESRI Shapefile"

        if self.out_file_type == "SQLite":
            self._dataset_creation_options_internal["SPATIALITE"] = "YES"
            self._layer_creation_options_internal["LAUNDER"] = "YES"
        elif self.out_file_type == "PostgreSQL":
            self._layer_creation_options_internal["LAUNDER"] = "YES"

        self.out_table = table_name
        self.out_srs = srs
        return self

    @property
    def geom_type(self):
        if self.out_file_type=="PostgreSQL" and not self._geom_type: 
            return "PROMOTE_TO_MULTI"
        else:
            return self._geom_type
    
    @geom_type.setter
    def geom_type(self, geom_type):
        self._geom_type = geom_type
    
    def set_output_mode(self, layer_mode=MODE_LAYER_CREATE, data_source_mode=MODE_DS_CREATE):
        self.layer_mode = layer_mode
        self.data_source_mode = data_source_mode

    @property
    def dataset_creation_options(self):
        """
        Dataset creation options, expressed as a dict of options such as
        such as {"SPATIALITE": "YES", "METADATA", "YES"}
        """
        result = self._dataset_creation_options_internal.copy()
        result.update(self._dataset_creation_options)
        return result

    @dataset_creation_options.setter
    def dataset_creation_options(self, ds_creation_options):
        self._dataset_creation_options = ds_creation_options

    @property
    def layer_creation_options(self):
        """
        Sets layer creation options, expressed as a dict of options such as
        {"SPATIAL_INDEX": "YES", "RESIZE": "YES"}
        """
        result = self._layer_creation_options_internal.copy()
        if self.encoding and self.out_file_type == "ESRI Shapefile":
            result["ENCODING"] = self.encoding
        result.update(self._layer_creation_options)
        return result

    @layer_creation_options.setter 
    def layer_creation_options(self, layer_creation_options):
        self._layer_creation_options = layer_creation_options

    def set_encoding(self, encoding):
        """
        Sets the encoding used to read and write Shapefiles. You MUST ALWAYS
        set the encoding when working with Shapefiles, unless you are only using ASCII
        characters. Note that the encoding is ignored for the rest of data sources.

        Ogr2ogr does not properly handle charset recoding for Shapefiles,
        so it is not possible to read from a Shapefile using enconding A and
        to write to another Shapefile using encoding B.

        However, it IS possible to read from a Shapefile using encoding A,
        write to a different format (such as Spatialite),
        and then do the reverse operation reading from Spatialite and writing
        to Shapefile using encoding B.

        :param encoding: A string defining the charset to use (e.g. "UTF-8" or
        "ISO-8859-1").
        """
        self.encoding = encoding
    
    def set_preserve_fid(self, preserve_fid):
        """
        Use the FID of the source features instead of letting the output driver to
        automatically assign a new one. It is True by default when output mode is
        not append.
        :param preserve_fid: True or False
        """
        self.preserve_fid = preserve_fid

    @property
    def config_options(self):
        """
        Gdal/ogr config options, expressed as a dict of options such as
        {"SHAPE_ENCODING": "latin1"}, {"OGR_ENABLE_PARTIAL_REPROJECTION": "YES"}
        """
        result = self._config_options_internal.copy()
        if self.encoding:
            result["SHAPE_ENCODING"] = self.encoding
        result.update(self._config_options)
        return result

    @config_options.setter
    def config_options(self, options):
        self._config_options = options

    def execute(self):
        args = [self._get_command()]
        config_options = self.config_options
        
        if self.data_source_mode == self.MODE_DS_UPDATE:
            args.extend(["-update"])
        elif self.data_source_mode == self.MODE_DS_CREATE_OR_UPDATE:
            if isinstance(self.out_ds, FileConnectionString):
                if os.path.exists(self.out_ds.encode()):
                    # if it is a FileConnectionString, only use -update if the file exists
                    args.extend(["-update"])
            else:
                args.extend(["-update"])

        if self.layer_mode == self.MODE_LAYER_APPEND:
            args.extend(["-append"])
        elif self.layer_mode == self.MODE_LAYER_OVERWRITE:
            if self.out_file_type ==  "PostgreSQL" and config_options.get("OGR_TRUNCATE") != "NO":
                # prefer truncate for PostgresSQL driver
                args.extend(['-append'])
                config_options["OGR_TRUNCATE"] = "YES"
            else:
                args.extend(['-overwrite'])

        if self.out_srs:
            args.extend(['-t_srs', self.out_srs])
        
        if self.preserve_fid is None:  # it may also be False
            if self.layer_mode != self.MODE_LAYER_APPEND:
                # automatically set preserve_fid when we are not in APPEND mode
                args.extend(['-preserve_fid'])
        elif self.preserve_fid:
            args.extend(['-preserve_fid'])

        if self.in_srs:
            if not self.out_srs:
                args.extend(['-a_srs', self.in_srs])
            args.extend(['-s_srs', self.in_srs])

        args.extend(["-f", self.out_file_type])

        for key, value in self.dataset_creation_options.items():
            args.extend(["-dsco", key+"="+value])
        for key, value in self.layer_creation_options.items():
            args.extend(["-lco", key+"="+value])
        for key, value in config_options.items():
            args.extend(["--config", key, value])

        if self.out_table:
            out_table = self.out_table
        elif self.in_table:
            out_table = self.in_table
        elif isinstance(self.in_ds, FileConnectionString):
            out_table = os.path.splitext(os.path.basename(self.in_ds.encode()))[0]
        else:
            out_table = None
        
        if out_table:
            if (isinstance(self.out_ds, PgConnectionString) and
                  self.out_ds.schema and
                  not out_table.startswith(self.out_ds.schema + ".")):
                schema = self.out_ds.schema + "."
            else:
                schema = ""
            args.extend(["-nln", schema + out_table])

        if self.geom_type:
            args.extend(["-nlt", self.geom_type])

        safe_args = list(args)
        if self.in_table:
            if (isinstance(self.in_ds, PgConnectionString) and
                  self.in_ds.schema and
                  not self.in_table.startswith(self.in_ds.schema + ".")):
                schema = self.in_ds.schema + "."
            else:
                schema = ""            
            args.extend([self.out_ds.encode(), self.in_ds.encode(), schema + self.in_table])
            safe_args.extend([str(self.out_ds), str(self.in_ds), schema + self.in_table])
        else:
            args.extend([self.out_ds.encode(), self.in_ds.encode()])
            safe_args.extend([str(self.out_ds), str(self.in_ds)])
        
        logging.debug(" ".join(safe_args))
        self.safe_args = safe_args
        return self._do_execute(args)
