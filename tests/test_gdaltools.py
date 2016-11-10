# -*- coding: utf-8 -*-
import pytest


@pytest.yield_fixture
def ogr():
    import gdaltools
    ogr = gdaltools.ogr2ogr()
    yield ogr


@pytest.yield_fixture
def tmpdir():
    import tempfile
    tmp_path = tempfile.mkdtemp()
    yield tmp_path
    import shutil
    shutil.rmtree(tmp_path)


@pytest.fixture
def tmp_sqlite(tmpdir):
    import os
    return os.path.join(tmpdir, "db.sqlite")


def test_spatialite_output(ogr, tmp_sqlite):
    ogr.set_input("tests/data/areas.shp", srs="EPSG:4258")
    ogr.set_encoding("UTF-8")
    ogr.set_output(tmp_sqlite)
    ogr.execute()
    import os
    assert os.path.isfile(tmp_sqlite)


def test_creation_mode(ogr, tmp_sqlite):
    import os
    print os.getcwd()

    ogr.set_input("tests/data/areas.shp", srs="EPSG:4258")
    ogr.set_encoding("UTF-8")
    ogr.set_output(tmp_sqlite)
    # create areas layer in tmp_sqlite
    ogr.execute()

    # should fail now, as it already exists
    from gdaltools import GdalToolsError
    with pytest.raises(GdalToolsError):
        ogr.execute()

    # should also fail if explicitly using MODE_LAYER_CREATE and MODE_DS_CREATE_OR_UPDATE
    ogr.set_output_mode(
            layer_mode=ogr.MODE_LAYER_CREATE,
            data_source_mode=ogr.MODE_DS_CREATE_OR_UPDATE)
    with pytest.raises(GdalToolsError):
        ogr.execute()

    # should work with MODE_LAYER_OVERWRITE
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_OVERWRITE, data_source_mode=ogr.MODE_DS_CREATE_OR_UPDATE)
    ogr.execute()

    # should fail with MODE_LAYER_CREATE & MODE_DS_UPDATE
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_CREATE, data_source_mode=ogr.MODE_DS_UPDATE)
    with pytest.raises(GdalToolsError):
        ogr.execute()

    # should work
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_OVERWRITE, data_source_mode=ogr.MODE_DS_UPDATE)
    ogr.execute()

    # I think it should fail according ogr2ogr docs, but works at least in ogr 1.11 so excluding from testing
    #ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_OVERWRITE, data_source_mode=ogr.MODE_DS_CREATE)
    #ogr.execute()

    # should fail
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_CREATE, data_source_mode=ogr.MODE_DS_CREATE)
    with pytest.raises(GdalToolsError):
        ogr.execute()

    # should fail because the db exist and using MODE_DS_CREATE
    ogr.set_output(tmp_sqlite, table_name="areas01")
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_CREATE, data_source_mode=ogr.MODE_DS_CREATE)
    with pytest.raises(GdalToolsError):
        ogr.execute()

    # should work
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_CREATE, data_source_mode=ogr.MODE_DS_CREATE_OR_UPDATE)
    ogr.execute()

    # should work
    ogr.set_output(tmp_sqlite, table_name="areas02")
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_CREATE, data_source_mode=ogr.MODE_DS_UPDATE)
    ogr.execute()

    # should work
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_APPEND, data_source_mode=ogr.MODE_DS_UPDATE)
    ogr.execute()

    # should work
    ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_APPEND, data_source_mode=ogr.MODE_DS_CREATE_OR_UPDATE)
    ogr.execute()

    # I think it should fail according ogr2ogr docs, but works at least in ogr 1.11 so excluding from testing
    #ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_APPEND, data_source_mode=ogr.MODE_DS_CREATE)
    #with pytest.raises(GdalToolsError):
    #    ogr.execute()
