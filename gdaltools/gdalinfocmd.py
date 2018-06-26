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


def get_raster_stats(raster_path):
    """
    Gets the statistics of the raster using gdalinfo command.
    Returns an array of tuples, containing the min, max, mean and stdev values
    for each band.
    
    Usage:
    import gdaltools
    stats = gdaltools.get_raster_stats('path_to_my_raster')
    (band0_ min, band0_max, band0_mean, band0_stdev) = stats[0]
    (band1_ min, band1_max, band1_mean, band1_stdev) = stats[1]
    """
    gi = GdalInfo()
    gi.set_input(raster_path)
    gi.set_flags(stats=True)
    gi.execute()
    return gi.get_raster_stats()
    

def gdalinfo(raster_path, **flags):
    """
    Returns the output of gdalinfo command on the provided raster.
    
    :param raster_path: The path to the raster file
    :param flags: flags for the gdalinfo command. See GdalInfo.set_flags for accepted parameters
    """
    gi = GdalInfo()
    gi.set_input(raster_path)
    if flags:
        gi.set_flags(**flags)
    return gi.execute()

class GdalInfo(Wrapper):
    """
    Wrapper for the gdalinfo command
    """
    CMD = 'gdalinfo'
    
    __BAND_PATTERN=re.compile("Band ([0-9]+).*")
    __BAND_STATS_PATTERN=re.compile("  Minimum=([-+]?\d*\.\d+|\d+), Maximum=([-+]?\d*\.\d+|\d+), Mean=([-+]?\d*\.\d+|\d+), StdDev=([-+]?\d*\.\d+|\d+).*")
    __BAND_NO_DATA_PATTERN=re.compile("  NoData Value=(.*)")
    
    def __init__(self, version=1, command_path=None):
        Wrapper.__init__(self, version, command_path)
        self.set_flags()
        self.output = None

    """
    def _get_default_command(self):
        return self.GDALINFO_PATH
    """
    
    def set_input(self, input_raster):
        if isinstance(input_raster, ConnectionString):
            self.in_ds = input_raster
        else:
            self.in_ds = FileConnectionString(input_raster)
        return self

    def set_flags(
            self,
            stats=False, mm=False, approx_stats=False, hist=False, nogcp=False,
            nomd=False, nrat=False, noct=False, checksum=False, listmdd=False, mdd=None,
            nofl=False, sd=None, proj4=False):
        """
        :param mdd: None, "all" or a list of metadata domains to report
        :param sd: None or the number of subdataset to get info from
        """
        self.stats = stats
        self.mm = mm
        self.approx_stats = approx_stats
        self.hist = hist
        self.nogcp = nogcp
        self.nomd = nomd
        self.nrat = nrat
        self.noct = noct
        self.checksum = checksum
        self.listmdd = listmdd
        self.mdd = mdd
        self.nofl = nofl
        self.sd = sd
        self.proj4 = proj4
        return self
    
    def _get_flag_array(self):
        result = []
        if self.stats:
            result.append("-stats")
        if self.mm:
            result.append("-mm")
        if self.approx_stats:
            result.append("-approx_stats")
        if self.hist:
            result.append("-hist")
        if self.nogcp:
            result.append("-nogcp")
        if self.nomd:
            result.append("-nomd")
        if self.nrat:
            result.append("-nrat")
        if self.noct:
            result.append("-noct")
        if self.checksum:
            result.append("-checksum")
        if self.listmdd:
            result.append("-listmdd")
        if self.mdd:
            if mdd=="all":
               result.extend(["-mdd", "all"])
            else:
                try:
                    for domain in mdd:
                        result.extend(["-mdd", domain])
                except:
                    raise GdalToolsError(-1, "mdd flag only accepts 'all' or a list of metadata domains to report about")
        if self.nofl:
            result.append("-nofl")
        if self.sd:
            result.extend(["-sd", self.sd])
        if self.proj4:
            result.append("-proj4")
        return result
    
    def execute(self):
        cmd = self._get_command()
        args = [cmd] + self._get_flag_array() + [self.in_ds.encode()]
        safe_args = [cmd] + self._get_flag_array() + [unicode(self.in_ds)]
        logging.debug(" ".join(safe_args))
        self.safe_args = safe_args
        self.output = self._do_execute(args)
        return self.output

    def get_raster_stats(self):
        """
        Gets the statistics of the raster using gdalinfo command.
        Returns an array of tuples, containing the min, max, mean and stdev values
        for each band.
        
        Usage:
        import gdal_tools
        stats = gdal_tools.get_raster_stats('path_to_my_raster')
        (band0_ min, band0_max, band0_mean, band0_stdev) = stats[0]
        (band1_ min, band1_max, band1_mean, band1_stdev) = stats[1]
        """
        stats_str = self.output
        buf = io.StringIO(stats_str)
        result = []
        band_results = self.__process_band(buf)
        while band_results != None:
            result.append(band_results)
            band_results = self.__process_band(buf)
        buf.close()
        return result

    def __process_band(self, buf):
        self.__find_band(buf)
        line = buf.readline()
        while line != "":
            m = self.__BAND_STATS_PATTERN.match(line)
            if m: # stats found
                return (float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)))
            line = buf.readline()
        return None
    
    def __find_band(self, buf):
        line = buf.readline()
        while line != "":
            m = self.__BAND_PATTERN.match(line)
            if m: # band found
                return
            line = buf.readline()
