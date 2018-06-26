
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
from .basetypes import Wrapper, ConnectionString, FileConnectionString


def ogrinfo(datasource, *layer_names, **flags):
    """
    Returns the output of ogrinfo command on the provided vector layer(s).
    
    Examples:
    ogrinfo("thelayer.shp", "thelayer", geom=False)
    ogrinfo("thedb.sqlite")
    ogrinfo("thedb.sqlite", "layer1", "layer2", geom="SUMMARY")
    ogrinfo("thedb.sqlite", sql="SELECT UpdateLayerStatistics()")
    
    :param datasource: The path to the data source (e.g. a SHP file) or a database
    connection string
    :param layer_names: The name(s) of the layer(s) to query
    :param flags: flags for the ogrinfo command. See Ogrinfo.set_flags for accepted parameters
    """
    oinfo = OgrInfo()
    oinfo.set_input(datasource, *layer_names)
    if flags:
        oinfo.set_flags(**flags)
    return oinfo.execute()

class OgrInfo(Wrapper):
    """
    Wrapper for the ogrinfo command
    """
    CMD = 'ogrinfo'
    
    def __init__(self, version=1, command_path=None):
        Wrapper.__init__(self, version, command_path)
        self.set_input(None)
        self.set_flags()
    
    def set_input(self, input_ds, *layer_names):
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
        self.in_tables = layer_names
        return self


    def set_flags(
            self,
            readonly=False, alltables=False, summary=False, quiet=False,
            where=None, sql=None, dialect=None, spat=None, geomfield=None,
            fid=None, fields=True, geom=True, formats=False):
                self.readonly = readonly
                self.alltables = alltables
                self.summary=summary
                self.quiet = quiet
                self.where = where
                self.sql = sql
                self.dialect = dialect
                self.spat = spat
                self.geomfield = geomfield
                self.fid = fid
                self.fields = fields
                self.geom = geom
                self.formats = formats


    def execute(self):
        args = [self._get_command()]

        if self.formats:
            args.append("--formats")
        elif self.sql:
            args.extend(["-sql", self.sql])
        else:
            if self.readonly:
                args.append("-ro")
            if self.alltables:
                args.append("-al")
            if self.summary:
                args.append("-so")
            if self.quiet:
                args.append("-q")
            if self.where:
                args.extend(["-where", self.where])
            if self.dialect:
                args.extend(["-dialect", self.dialect])
            if self.spat and len(self.spat)==4:
                args.append("-spat")
                args.extend(spat)
            if self.geomfield:
                args.extend(["-geomfield", self.geomfield])
            if self.fid:
                args.extend(["-fid", self.fid])
            if not self.fields:
                args.append("-fields=NO")
            if not self.geom:
                args.append("-geom=NO")
            elif self.geom == "SUMMARY":
                args.append("-geom=SUMMARY")

        # log the command, excluding password for db connection strings
        safe_args = list(args)
        safe_args.append(unicode(self.in_ds))
        safe_args.extend(self.in_tables)
        logging.debug(" ".join(safe_args))
        
        args.append(self.in_ds.encode())
        args.extend(self.in_tables)
        self.safe_args = safe_args
        return self._do_execute(args)
