# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytest


@pytest.yield_fixture
def ogr():
    import gdaltools
    ogr = gdaltools.ogr2ogr()
    yield ogr


"""
@pytest.yield_fixture
def tmpdir():
    import tempfile
    tmp_path = tempfile.mkdtemp()
    yield tmp_path
    import shutil
    shutil.rmtree(tmp_path)
"""


@pytest.yield_fixture
def tmp_sqlite(tmpdir):
    f = str(tmpdir.join("db.sqlite"))
    yield f
    import os
    if os.path.exists(f):
        os.remove(f)


def test_spatialite_output(ogr, tmp_sqlite):
    ogr.set_input("tests/data/areas.shp", srs="EPSG:4258")
    ogr.set_encoding("UTF-8")
    ogr.set_output(tmp_sqlite)
    ogr.execute()
    assert ogr.returncode == 0
    import os
    assert os.path.isfile(tmp_sqlite)


def test_creation_mode(ogr, tmp_sqlite):
    ogr.set_input("tests/data/areas.shp", srs="EPSG:4258")
    ogr.set_encoding("UTF-8")
    ogr.set_output(tmp_sqlite)
    # create areas layer in tmp_sqlite
    ogr.execute()
    assert ogr.returncode == 0

    # should fail now, as it already exists
    from gdaltools import GdalToolsError
    with pytest.raises(GdalToolsError):
        ogr.execute()
    assert ogr.returncode != 0

    # should also fail if explicitly using MODE_LAYER_CREATE and MODE_DS_CREATE_OR_UPDATE
    ogr.set_output_mode(
            layer_mode=ogr.MODE_LAYER_CREATE,
            data_source_mode=ogr.MODE_DS_CREATE_OR_UPDATE)
    with pytest.raises(GdalToolsError):
        ogr.execute()
    assert ogr.returncode != 0

    # should work with MODE_LAYER_OVERWRITE
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_OVERWRITE, data_source_mode=ogr.MODE_DS_CREATE_OR_UPDATE)
    ogr.execute()
    assert ogr.returncode == 0

    # should fail with MODE_LAYER_CREATE & MODE_DS_UPDATE
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_CREATE, data_source_mode=ogr.MODE_DS_UPDATE)
    with pytest.raises(GdalToolsError):
        ogr.execute()
    assert ogr.returncode != 0

    # should work
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_OVERWRITE, data_source_mode=ogr.MODE_DS_UPDATE)
    ogr.execute()
    assert ogr.returncode == 0

    # I think it should fail according ogr2ogr docs, but works at least in ogr 1.11 so excluding from testing
    # ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_OVERWRITE, data_source_mode=ogr.MODE_DS_CREATE)
    # ogr.execute()

    # should fail
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_CREATE, data_source_mode=ogr.MODE_DS_CREATE)
    with pytest.raises(GdalToolsError):
        ogr.execute()
    assert ogr.returncode != 0

    # should fail because the db exist and using MODE_DS_CREATE
    ogr.set_output(tmp_sqlite, table_name="areas01")
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_CREATE, data_source_mode=ogr.MODE_DS_CREATE)
    with pytest.raises(GdalToolsError):
        ogr.execute()
    assert ogr.returncode != 0

    # should work
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_CREATE, data_source_mode=ogr.MODE_DS_CREATE_OR_UPDATE)
    ogr.execute()
    assert ogr.returncode == 0

    # should work
    ogr.set_output(tmp_sqlite, table_name="areas02")
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_CREATE, data_source_mode=ogr.MODE_DS_UPDATE)
    ogr.execute()
    assert ogr.returncode == 0

    # should work
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_APPEND, data_source_mode=ogr.MODE_DS_UPDATE)
    ogr.execute()
    assert ogr.returncode == 0

    # should work
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_APPEND, data_source_mode=ogr.MODE_DS_CREATE_OR_UPDATE)
    ogr.execute()
    assert ogr.returncode == 0

    # I think it should fail according ogr2ogr docs, but works at least in ogr 1.11 so excluding from testing
    # ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_APPEND, data_source_mode=ogr.MODE_DS_CREATE)
    # with pytest.raises(GdalToolsError):
    #    ogr.execute()


def test_shape_encoding(ogr, tmpdir, tmp_sqlite):
    # import utf-8 and latin1 layers in s spatialite db
    ogr.set_input("tests/data/pointsutf8.shp", srs="EPSG:4258")
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_CREATE, data_source_mode=ogr.MODE_DS_CREATE_OR_UPDATE)
    ogr.set_encoding("UTF-8")
    ogr.set_output(tmp_sqlite)
    ogr.execute()
    assert ogr.returncode == 0
    ogr.set_input("tests/data/pointslatin1.shp", srs="EPSG:4258")
    ogr.set_encoding("ISO-8859-1")
    ogr.set_output(tmp_sqlite)
    ogr.execute()
    assert ogr.returncode == 0

    # export as utf8 a layer having utf8 chars
    ogr.set_input(tmp_sqlite, table_name="pointsutf8", srs="EPSG:4258")
    out_shp = tmpdir.join("pointsutf8_01.shp")
    ogr.set_output(str(out_shp))
    ogr.set_encoding("UTF-8")
    ogr.execute()
    assert ogr.returncode == 0
    assert out_shp.check(file=1)
    out_cpg = tmpdir.join("pointsutf8_01.cpg")
    assert out_cpg.read() =='UTF-8'
    

    # export as latin1 a layer having utf8 chars
    out_shp = tmpdir.join("pointsutf8_02.shp")
    ogr.set_output(str(out_shp))
    ogr.set_encoding("ISO-8859-1")
    output = ogr.execute()
    assert ogr.returncode == 0
    
    assert out_shp.check(file=1)
    assert "Warning" in ogr.stderr
    assert "One or several characters couldn't be converted correctly from UTF-8 to ISO-8859-1" in ogr.stderr
    
    out_cpg = tmpdir.join("pointsutf8_02.cpg")
    assert out_cpg.read() == "ISO-8859-1"
