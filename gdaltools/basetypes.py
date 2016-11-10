# -*- coding: utf-8 -*-

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

import subprocess
import logging

class GdalToolsError(Exception):
    def __init__(self, code=-1, message=None):
        self.code = code
        self.message=message

class ConnectionString():
    def encode(self):
        pass

class PgConnectionString(ConnectionString):
    conn_string_tpl = u"PG:host='{host}' port='{port}' user='{user}' dbname='{dbname}' password='{password}'"
    def __init__(self, host=None, port=None, dbname=None, schema=None, user=None, password=None):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.schema = schema
        self.user = user
        self.password = password

    def encode(self):
        return self.conn_string_tpl.format(host=self.host, port=self.port, user=self.user, dbname=self.dbname, password=self.password, schema=self.schema)

    def __unicode__(self):
        return '"' + self.conn_string_tpl.format(host=self.host, port=self.port, user=self.user, dbname=self.dbname, password='xxxxxx', schema=self.schema) + '"'

    def __str__(self):
        return self.__unicode__().encode('utf-8') 

class FileConnectionString():
    
    def __init__(self, file_path):
        self.file_path = file_path

    def encode(self):
        return self.file_path

    def __unicode__(self):
        return '"' + self.file_path + '"'


class Wrapper():
    def __init__(self, version=1, command_path=None):
        self.version = version
        if command_path:
            self.command = command_path
        else:
            self.command = self._get_default_command()
    
    def _get_default_command(self):
        pass
    
    def _do_execute(self, args):
        p = subprocess.Popen(args, stdin=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=-1)
        output, err = p.communicate()
        rc = p.returncode
        print "return code: " + str(rc)
        if rc>0:
            logging.error(msg)
            raise GdalToolsError(rc, err)
        return output
