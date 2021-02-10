# -*- coding: utf-8 -*-
from __future__ import unicode_literals
'''
    gvSIG Online.
    Copyright (C) 2007-2015 gvSIG Association.

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
import re
import os
from .basetypes import GdalToolsError, Wrapper, ConnectionString, FileConnectionString
import io

def gdalsrsinfo(raster_path, **flags):
    """
    Returns the output of gdalsrsinfo command on the provided raster.
    
    :param raster_path: The path to the raster file
    :param flags: flags for the gdalinfo command. See GdalInfo.set_flags for accepted parameters
    """
    gi = GdalSrsInfo()
    gi.set_input(raster_path)
    if flags:
        gi.set_flags(**flags)
    return gi.execute()

class GdalSrsInfo(Wrapper):
    """
    Wrapper for the gdalsrsinfo command
    """
    CMD = 'gdalsrsinfo'
    
    def __init__(self, version=1, command_path=None):
        Wrapper.__init__(self, version, command_path)
        self.set_flags()
        self.output = None
    
    def set_input(self, input_raster):
        if isinstance(input_raster, ConnectionString):
            self.in_ds = input_raster
        else:
            self.in_ds = FileConnectionString(input_raster)
        return self

    def set_flags(
            self,
            single_line=False, validate=False, output_type=None, search_epsg=False):
        """
        :param mdd: None, "all" or a list of metadata domains to report
        :param sd: None or the number of subdataset to get info from
        """
        self.single_line = single_line
        self.validate = validate
        self.output_type = output_type
        return self
    
    def _get_flag_array(self):
        result = []
        if self.single_line:
            result.append("--single-line")
        if self.validate:
            result.append("-V")
        if self.output_type:
            result.extend(["-o", self.output_type])
        if self.search_epsg:
            result.append("-e")
        return result
    
    def execute(self):
        cmd = self._get_command()
        args = [cmd] + self._get_flag_array() + [self.in_ds.encode()]
        safe_args = [cmd] + self._get_flag_array() + [unicode(self.in_ds)]
        logging.debug(" ".join(safe_args))
        self.safe_args = safe_args
        self.output = self._do_execute(args)
        return self.output