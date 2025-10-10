"""Test catalog information is valid"""

import os
import shutil

import pytest

from hats.catalog import PartitionInfo
from hats.io.validation import is_valid_catalog


def test_is_valid_catalog(tmp_path, small_sky_catalog):
    """Tests if the catalog_info and partition_info files are valid"""
    # An empty directory means an invalid catalog
    assert not is_valid_catalog(tmp_path)

    # Having the catalog_info file is not enough
    small_sky_catalog.catalog_info.to_properties_file(tmp_path)
    assert not is_valid_catalog(tmp_path)

    # The catalog is valid if both the catalog_info and _metadata files exist,
    # and the catalog_info is in a valid format
    (tmp_path / "dataset").mkdir()
    shutil.copy(small_sky_catalog.catalog_path / "dataset" / "_metadata", tmp_path / "dataset" / "_metadata")
    assert is_valid_catalog(tmp_path)

    # A partition_info file alone is also not enough
    os.remove(tmp_path / "properties")
    os.remove(tmp_path / "hats.properties")
    assert not is_valid_catalog(tmp_path)

    # The catalog_info file needs to be in the correct format
    small_sky_catalog.catalog_info.catalog_type = "invalid"
    small_sky_catalog.catalog_info.to_properties_file(tmp_path)
    assert not is_valid_catalog(tmp_path)


def test_is_valid_catalog_strict(tmp_path, small_sky_catalog, small_sky_pixels, small_sky_order1_pixels):
    """Tests if the catalog_info and partition_info files are valid"""
    # Set up our arguments once, just to be sure we're calling validation
    # the same way throughout this test scene.
    flags = {
        "strict": True,  # more intensive checks
        "fail_fast": False,  # check everything, and just return true/false
        "verbose": False,  # don't print, throw warnings.
    }
    # An empty directory means an invalid catalog
    with pytest.warns():
        assert not is_valid_catalog(tmp_path, **flags)

    # Having the catalog_info file is not enough
    small_sky_catalog.catalog_info.to_properties_file(tmp_path)
    with pytest.warns():
        assert not is_valid_catalog(tmp_path, **flags)

    # Adds the _metadata and _common_metadata, but that's not enough.
    (tmp_path / "dataset").mkdir()
    shutil.copy(small_sky_catalog.catalog_path / "dataset" / "_metadata", tmp_path / "dataset" / "_metadata")
    with pytest.warns():
        assert not is_valid_catalog(tmp_path, **flags)

    # Adds the partition_info.csv, but that's STILL not enough
    PartitionInfo.from_healpix(small_sky_pixels).write_to_file(catalog_path=tmp_path)
    with pytest.warns():
        assert not is_valid_catalog(tmp_path, **flags)

    # This outta do it! Add parquet files that match the _metadata pixels.
    shutil.copytree(small_sky_catalog.catalog_path / "dataset", tmp_path / "dataset", dirs_exist_ok=True)

    assert is_valid_catalog(tmp_path, **flags)

    # Uh oh! Now the sets of pixels don't match between _metadata and partition_info.csv!
    PartitionInfo.from_healpix(small_sky_order1_pixels).write_to_file(catalog_path=tmp_path)
    with pytest.warns():
        assert not is_valid_catalog(tmp_path, **flags)


def test_is_valid_catalog_fail_fast(tmp_path, small_sky_catalog, small_sky_pixels):
    """Tests if the catalog_info and partition_info files are valid"""
    # Set up our arguments once, just to be sure we're calling validation
    # the same way throughout this test scene.
    flags = {
        "strict": True,  # more intensive checks
        "fail_fast": True,  # raise an error at the first problem.
        "verbose": False,  # don't bother printing anything.
    }
    # An empty directory means an invalid catalog
    with pytest.raises(ValueError, match="properties file"):
        is_valid_catalog(tmp_path, **flags)

    # Having the catalog_info file is not enough
    small_sky_catalog.catalog_info.to_properties_file(tmp_path)
    with pytest.raises(ValueError, match="_metadata"):
        is_valid_catalog(tmp_path, **flags)

    (tmp_path / "dataset").mkdir()
    shutil.copy(small_sky_catalog.catalog_path / "dataset" / "_metadata", tmp_path / "dataset" / "_metadata")
    shutil.copy(
        small_sky_catalog.catalog_path / "dataset" / "_common_metadata",
        tmp_path / "dataset" / "_common_metadata",
    )
    with pytest.raises(ValueError, match="partition_info.csv"):
        is_valid_catalog(tmp_path, **flags)

    PartitionInfo.from_healpix(small_sky_pixels).write_to_file(catalog_path=tmp_path)

    shutil.copytree(small_sky_catalog.catalog_path / "dataset", tmp_path / "dataset", dirs_exist_ok=True)
    assert is_valid_catalog(tmp_path, **flags)


def test_is_valid_catalog_verbose_fail(tmp_path, capsys):
    """Tests if the catalog_info and partition_info files are valid"""
    # Set up our arguments once, just to be sure we're calling validation
    # the same way throughout this test scene.
    flags = {
        "strict": True,  # more intensive checks
        "fail_fast": False,  # check everything, and just return true/false
        "verbose": True,  # print messages along the way
    }
    # An empty directory means an invalid catalog
    assert not is_valid_catalog(tmp_path, **flags)

    captured = capsys.readouterr().out
    assert "Validating catalog at path" in captured
    assert "properties file does not exist or is invalid" in captured
    assert "_metadata file does not exist" in captured
    assert "_common_metadata file does not exist" in captured


def test_is_valid_catalog_verbose_success(small_sky_dir, capsys):
    """Tests if the catalog_info and partition_info files are valid"""
    # Set up our arguments once, just to be sure we're calling validation
    # the same way throughout this test scene.
    flags = {
        "strict": True,  # more intensive checks
        "fail_fast": False,  # check everything, and just return true/false
        "verbose": True,  # print messages along the way
    }
    assert is_valid_catalog(small_sky_dir, **flags)
    captured = capsys.readouterr().out
    assert "Validating catalog at path" in captured
    assert "Found 1 partition" in captured
    assert "Approximate coverage is 8" in captured


def test_valid_catalog_strict_all(
    small_sky_source_dir,
    small_sky_order1_dir,
    small_sky_dir,
    small_sky_source_object_index_dir,
    margin_catalog_path,
):
    """Check that all of our object catalogs in test data are valid, using strict mechanism"""
    flags = {
        "strict": True,  # more intensive checks
        "fail_fast": False,  # check everything, and just return true/false
        "verbose": False,  # don't bother printing anything.
    }
    assert is_valid_catalog(small_sky_source_dir, **flags)
    assert is_valid_catalog(small_sky_order1_dir, **flags)
    assert is_valid_catalog(small_sky_dir, **flags)
    assert is_valid_catalog(small_sky_source_object_index_dir, **flags)
    assert is_valid_catalog(margin_catalog_path, **flags)


def test_is_valid_catalog_fail_with_missing_partitions(small_sky_source_dir, tmp_path):
    """Test that if some files are missing an error is raised"""
    flags = {
        "strict": True,  # more intensive checks
        "fail_fast": True,  # check everything, and just return true/false
        "verbose": False,  # don't bother printing anything.
    }
    # copy all partitions but two
    shutil.copytree(
        small_sky_source_dir, tmp_path / "copy", ignore=lambda _, f: ["Npix=4.parquet", "Npix=176.parquet"]
    )
    with pytest.raises(ValueError, match="partition is missing"):
        assert is_valid_catalog(tmp_path / "copy", **flags)
