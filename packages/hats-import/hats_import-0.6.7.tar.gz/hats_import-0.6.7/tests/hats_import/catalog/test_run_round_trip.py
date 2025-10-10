"""Test end-to-end execution of pipeline with different formats and configurations.

Please add a brief description in the docstring of the features or specific
regression the test case is exercising.
"""

# pylint: disable=too-many-lines
import glob
import os
from pathlib import Path

import numpy as np
import numpy.testing as npt
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as pds
import pyarrow.parquet as pq
import pytest
from hats import read_hats
from hats.io.skymap import read_skymap
from hats.pixel_math import HealpixPixel
from hats.pixel_math.spatial_index import SPATIAL_INDEX_COLUMN, spatial_index_to_healpix
from pyarrow import csv

import hats_import.catalog.run_import as runner
from hats_import.catalog.arguments import ImportArguments
from hats_import.catalog.file_readers import CsvReader, get_file_reader
from hats_import.catalog.file_readers.csv import CsvPyarrowReader
from hats_import.catalog.file_readers.parquet import ParquetPyarrowReader


@pytest.mark.dask
def test_import_snappy_source_table(
    dask_client,
    small_sky_source_dir,
    tmp_path,
):
    """Test basic execution, using a larger source file.
    - catalog type should be source
    - will have larger partition info than the corresponding object catalog
    """
    args = ImportArguments(
        output_artifact_name="small_sky_source_catalog.parquet",
        input_path=small_sky_source_dir,
        file_reader="csv",
        catalog_type="source",
        ra_column="source_ra",
        dec_column="source_dec",
        sort_columns="source_id",
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=2,
        pixel_threshold=3_000,
        progress_bar=False,
        # Sneak in a test of setting a non-default compression scheme.
        write_table_kwargs={"compression": "SNAPPY"},
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path
    assert catalog.catalog_info.ra_column == "source_ra"
    assert catalog.catalog_info.dec_column == "source_dec"
    assert len(catalog.get_healpix_pixels()) == 14

    output_file = os.path.join(args.catalog_path, "dataset", "Norder=1", "Dir=0", "Npix=47.parquet")
    metadata = pq.read_metadata(output_file)
    assert metadata.num_row_groups == 1
    assert metadata.row_group(0).column(0).compression == "SNAPPY"

    # Check that the pixels have been sorted by the default _healpix_29 values
    pixel_data = pq.read_table(output_file)
    sorting_columns = metadata.row_group(0).sorting_columns
    ordering_tuples = pq.SortingColumn.to_ordering(pixel_data.schema, sorting_columns)[0]
    assert ordering_tuples[0] == (SPATIAL_INDEX_COLUMN, "ascending")
    assert pixel_data.equals(pixel_data.sort_by(SPATIAL_INDEX_COLUMN))


@pytest.mark.dask
def test_import_with_num_row_groups(
    dask_client,
    small_sky_source_dir,
    tmp_path,
):
    """The row group size will be specified in `row_group_kwargs`"""
    args = ImportArguments(
        output_artifact_name="small_sky_source_catalog",
        input_path=small_sky_source_dir,
        file_reader="csv",
        catalog_type="source",
        ra_column="source_ra",
        dec_column="source_dec",
        sort_columns="source_id",
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=2,
        pixel_threshold=3_000,
        progress_bar=False,
        # Sneak in a test of custom row group size
        row_group_kwargs={"num_rows": 100},
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path
    assert catalog.catalog_info.ra_column == "source_ra"
    assert catalog.catalog_info.dec_column == "source_dec"
    assert len(catalog.get_healpix_pixels()) == 14

    output_file = os.path.join(args.catalog_path, "dataset", "Norder=1", "Dir=0", "Npix=47.parquet")
    pixel = pq.ParquetFile(output_file)
    data = pixel.read()
    assert len(pixel.read()) == 2395

    # Check that the number of row groups is the one expected
    metadata = pixel.metadata
    assert metadata.num_rows == 2395
    # 24 = math.ceil(metadata.num_rows / 100)
    assert metadata.num_row_groups == 24
    # The last row group has fewer number of rows, which is fine
    assert all(metadata.row_group(i).num_rows == 100 for i in range(metadata.num_row_groups - 1))

    # Check that the sorting columns were saved in the parquet metadata
    sorting_columns = metadata.row_group(0).sorting_columns
    ordering_tuples = pq.SortingColumn.to_ordering(data.schema, sorting_columns)[0]
    assert ordering_tuples[0] == (SPATIAL_INDEX_COLUMN, "ascending")
    assert ordering_tuples[1] == ("source_id", "ascending")

    # And that the data is indeed sorted
    sorted_data = data.sort_by([(SPATIAL_INDEX_COLUMN, "ascending"), ("source_id", "ascending")])
    assert data.equals(sorted_data)


@pytest.mark.dask
def test_import_with_subtile_row_groups(
    dask_client,
    small_sky_source_dir,
    tmp_path,
):
    """The row group subtile splitting will be specified in `row_group_kwargs`"""
    args = ImportArguments(
        output_artifact_name="small_sky_source_catalog",
        input_path=small_sky_source_dir,
        file_reader="csv",
        catalog_type="source",
        ra_column="source_ra",
        dec_column="source_dec",
        sort_columns="source_id",
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=2,
        pixel_threshold=3_000,
        progress_bar=False,
        # Sneak in a test of custom subtile splitting
        row_group_kwargs={"subtile_order_delta": 2},
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path
    assert catalog.catalog_info.ra_column == "source_ra"
    assert catalog.catalog_info.dec_column == "source_dec"
    assert len(catalog.get_healpix_pixels()) == 14

    output_file = os.path.join(args.catalog_path, "dataset", "Norder=1", "Dir=0", "Npix=47.parquet")

    pixel = pq.ParquetFile(output_file)
    assert len(pixel.read()) == 2395

    # Check that the number of row groups is the one expected
    metadata = pixel.metadata
    assert metadata.num_rows == 2395
    child_pixels = HealpixPixel(1, 47).convert_to_higher_order(delta_order=2)
    # The empty sub-tiles are not kept
    assert pixel.num_row_groups <= len(child_pixels)

    seen_pixels = []

    for i in range(metadata.num_row_groups):
        row_group = metadata.row_group(i)

        # Check that the row group statistics are correct
        assert row_group.num_rows > 0
        min_healpix29 = row_group.column(0).statistics.min
        max_healpix29 = row_group.column(0).statistics.max
        pixel_min, pixel_max = spatial_index_to_healpix([min_healpix29, max_healpix29], target_order=3)
        assert pixel_min == pixel_max and HealpixPixel(3, pixel_min) in child_pixels

        # The row group contains data that does in fact belong to the pixel
        row_group_healpix29 = pixel.read_row_group(i)[SPATIAL_INDEX_COLUMN].to_numpy()
        assert all(row_group_healpix29 >= min_healpix29)
        assert all(row_group_healpix29 <= max_healpix29)
        seen_pixels.append(pixel_min)

    # Make sure there was no overlap between row group pixels
    assert list(set(seen_pixels)) == seen_pixels


@pytest.mark.dask
def test_import_mixed_schema_csv(
    dask_client,
    mixed_schema_csv_dir,
    mixed_schema_csv_parquet,
    assert_parquet_file_ids,
    tmp_path,
):
    """Test basic execution, with a mixed schema.
    - the two input files in `mixed_schema_csv_dir` have different *implied* schemas
        when parsed by pandas. this verifies that they end up with the same schema
        and can be combined into a single parquet file.
    - this additionally uses pathlib.Path for all path inputs.
    """
    args = ImportArguments(
        output_artifact_name="mixed_csv_bad",
        input_file_list=[
            Path(mixed_schema_csv_dir) / "input_01.csv",
            Path(mixed_schema_csv_dir) / "input_02.csv",
            Path(mixed_schema_csv_dir) / "input_03.csv",
        ],
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=1,
        file_reader=get_file_reader(
            "csv",
            chunksize=1,
            schema_file=Path(mixed_schema_csv_parquet),
        ),
        progress_bar=False,
    )

    runner.run(args, dask_client)

    # Check that the catalog parquet file exists
    output_file = os.path.join(args.catalog_path, "dataset", "Norder=0", "Dir=0", "Npix=11.parquet")

    assert_parquet_file_ids(output_file, "id", [*range(700, 708)])

    # Check that the schema is correct for leaf parquet and _metadata files
    expected_parquet_schema = pa.schema(
        [
            pa.field("_healpix_29", pa.int64()),
            pa.field("id", pa.int64()),
            pa.field("ra", pa.float64()),
            pa.field("dec", pa.float64()),
            pa.field("ra_error", pa.int64()),
            pa.field("dec_error", pa.int64()),
            pa.field("comment", pa.string()),
            pa.field("code", pa.string()),
        ]
    )
    schema = pq.read_metadata(output_file).schema.to_arrow_schema()
    assert schema.equals(expected_parquet_schema)
    schema = pq.read_metadata(args.catalog_path / "dataset" / "_metadata").schema.to_arrow_schema()
    assert schema.equals(expected_parquet_schema)


@pytest.mark.dask
def test_import_mixed_schema_csv_pyarrow(
    dask_client,
    mixed_schema_csv_dir,
    mixed_schema_csv_parquet,
    assert_parquet_file_ids,
    tmp_path,
):
    """Test basic execution, with a mixed schema, reading with pyarrow's CSV reader.
    - the two input files in `mixed_schema_csv_dir` have different *implied* schemas
        when parsed by pandas. this verifies that they end up with the same schema
        and can be combined into a single parquet file.
    - this additionally uses pathlib.Path for all path inputs.
    """
    input_files = list(Path(mixed_schema_csv_dir).glob("*.csv"))
    input_files.sort()
    args = ImportArguments(
        output_artifact_name="mixed_csv_bad",
        # Pyarrow CSV reader isn't happy about empty files.
        # See https://github.com/apache/arrow/discussions/46429
        input_file_list=input_files[0:2],
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=1,
        file_reader=CsvPyarrowReader(
            schema_file=mixed_schema_csv_parquet,
            read_options=csv.ReadOptions(
                column_names=["id", "ra", "dec", "ra_error", "dec_error", "comment", "code"],
                skip_rows=1,
            ),
        ),
        progress_bar=False,
    )

    runner.run(args, dask_client)

    # Check that the catalog parquet file exists
    output_file = os.path.join(args.catalog_path, "dataset", "Norder=0", "Dir=0", "Npix=11.parquet")

    assert_parquet_file_ids(output_file, "id", [*range(700, 708)])

    # Check that the schema is correct for leaf parquet and _metadata files
    expected_parquet_schema = pa.schema(
        [
            pa.field("_healpix_29", pa.int64()),
            pa.field("id", pa.int64()),
            pa.field("ra", pa.float64()),
            pa.field("dec", pa.float64()),
            pa.field("ra_error", pa.int64()),
            pa.field("dec_error", pa.int64()),
            pa.field("comment", pa.string()),
            pa.field("code", pa.string()),
        ]
    )
    schema = pq.read_metadata(output_file).schema.to_arrow_schema()
    assert schema.equals(expected_parquet_schema)
    schema = pq.read_metadata(args.catalog_path / "dataset" / "_metadata").schema.to_arrow_schema()
    assert schema.equals(expected_parquet_schema)


@pytest.mark.dask
def test_import_preserve_index(
    dask_client,
    formats_pandasindex,
    assert_parquet_file_ids,
    assert_parquet_file_index,
    tmp_path,
):
    """Test basic execution, with input with pandas metadata.
    - the input file is a parquet file with some pandas metadata.
        this verifies that the parquet file at the end also still has the
        contents of that column.
    """

    expected_indexes = [
        "star1_1",
        "star1_2",
        "star1_3",
        "star1_4",
        "galaxy1_1",
        "galaxy1_2",
        "galaxy2_1",
        "galaxy2_2",
    ]
    assert_parquet_file_index(formats_pandasindex, expected_indexes)
    data_frame = pd.read_parquet(formats_pandasindex, engine="pyarrow")
    assert data_frame.index.name == "obs_id"
    npt.assert_array_equal(
        data_frame.columns,
        ["obj_id", "band", "ra", "dec", "mag"],
    )

    ## Don't generate a hats spatial index. Verify that the original index remains.
    args = ImportArguments(
        output_artifact_name="pandasindex",
        input_file_list=[formats_pandasindex],
        file_reader="parquet",
        sort_columns="obs_id",
        add_healpix_29=False,
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=1,
        progress_bar=False,
    )

    runner.run(args, dask_client)

    # Check that the catalog parquet file exists
    output_file = os.path.join(args.catalog_path, "dataset", "Norder=1", "Dir=0", "Npix=46.parquet")

    data_frame = pd.read_parquet(output_file, engine="pyarrow")
    npt.assert_array_equal(
        data_frame.columns,
        ["obs_id", "obj_id", "band", "ra", "dec", "mag"],
    )

    ## DO generate a hats spatial index. Verify that the original index is preserved in a column.
    args = ImportArguments(
        output_artifact_name="pandasindex_preserve",
        input_file_list=[formats_pandasindex],
        file_reader="parquet",
        sort_columns="obs_id",
        add_healpix_29=True,
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=1,
        progress_bar=False,
    )

    runner.run(args, dask_client)

    # Check that the catalog parquet file exists
    output_file = os.path.join(args.catalog_path, "dataset", "Norder=1", "Dir=0", "Npix=46.parquet")

    data_frame = pd.read_parquet(output_file, engine="pyarrow")
    npt.assert_array_equal(
        data_frame.columns,
        ["_healpix_29", "obs_id", "obj_id", "band", "ra", "dec", "mag"],
    )
    assert_parquet_file_ids(output_file, "obs_id", expected_indexes)


@pytest.mark.dask
def test_import_constant_healpix_order(
    dask_client,
    small_sky_parts_dir,
    tmp_path,
):
    """Test basic execution.
    - tests that all the final tiles are at the same healpix order,
        and that we don't create tiles where there is no data.
    """
    args = ImportArguments(
        output_artifact_name="small_sky_object_catalog",
        input_path=small_sky_parts_dir,
        file_reader="csv",
        output_path=tmp_path,
        dask_tmp=tmp_path,
        constant_healpix_order=2,
        progress_bar=False,
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path
    # Check that the partition info file exists - all pixels at order 2!
    assert all(pixel.order == 2 for pixel in catalog.partition_info.get_healpix_pixels())

    # Pick a parquet file and make sure it contains as many rows as we expect
    output_file = os.path.join(args.catalog_path, "dataset", "Norder=2", "Dir=0", "Npix=178.parquet")

    data_frame = pd.read_parquet(output_file, engine="pyarrow")
    assert len(data_frame) == 14
    ids = data_frame["id"]
    assert np.logical_and(ids >= 700, ids < 832).all()

    assert catalog.catalog_info.skymap_alt_orders is None
    assert catalog.catalog_info.skymap_order == 2


@pytest.mark.dask
def test_import_keep_intermediate_files(
    dask_client,
    small_sky_parts_dir,
    tmp_path,
):
    """Test that ALL intermediate files are still around on-disk after
    successful import, when setting the appropriate flags.
    """
    temp = tmp_path / "intermediate_files"
    temp.mkdir(parents=True)
    args = ImportArguments(
        output_artifact_name="small_sky_object_catalog",
        input_path=small_sky_parts_dir,
        file_reader="csv",
        output_path=tmp_path,
        tmp_dir=temp,
        dask_tmp=temp,
        progress_bar=False,
        highest_healpix_order=2,
        delete_intermediate_parquet_files=False,
        delete_resume_log_files=False,
    )
    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path

    # Check that both stage level and intermediate parquet files exist
    base_intermediate_dir = temp / "small_sky_object_catalog" / "intermediate"
    assert_stage_level_files_exist(base_intermediate_dir)
    assert_intermediate_parquet_files_exist(base_intermediate_dir)


@pytest.mark.dask
def test_import_delete_provided_temp_directory(
    dask_client,
    small_sky_parts_dir,
    tmp_path_factory,
):
    """Test that ALL intermediate files (and temporary base directory) are deleted
    after successful import, when both `delete_intermediate_parquet_files` and
    `delete_resume_log_files` are set to True."""
    output_dir = tmp_path_factory.mktemp("catalogs")
    # Provided temporary directory, outside `output_dir`
    temp = tmp_path_factory.mktemp("intermediate_files")

    # When at least one of the delete flags is set to False we do
    # not delete the provided temporary base directory.
    args = ImportArguments(
        output_artifact_name="keep_log_files",
        input_path=small_sky_parts_dir,
        file_reader="csv",
        output_path=output_dir,
        tmp_path=temp,
        dask_tmp=temp,
        progress_bar=False,
        highest_healpix_order=2,
        delete_intermediate_parquet_files=True,
        delete_resume_log_files=False,
    )
    runner.run(args, dask_client)
    assert_stage_level_files_exist(temp / "keep_log_files" / "intermediate")

    args = ImportArguments(
        output_artifact_name="keep_parquet_intermediate",
        input_path=small_sky_parts_dir,
        file_reader="csv",
        output_path=output_dir,
        tmp_path=temp,
        dask_tmp=temp,
        progress_bar=False,
        highest_healpix_order=2,
        delete_intermediate_parquet_files=False,
        delete_resume_log_files=True,
        resume=False,
    )
    runner.run(args, dask_client)
    assert_intermediate_parquet_files_exist(temp / "keep_parquet_intermediate" / "intermediate")

    # The temporary directory is deleted.
    args = ImportArguments(
        output_artifact_name="remove_all_intermediate",
        input_path=small_sky_parts_dir,
        file_reader="csv",
        output_path=output_dir,
        tmp_path=temp,
        dask_tmp=temp,
        progress_bar=False,
        highest_healpix_order=2,
        delete_intermediate_parquet_files=True,
        delete_resume_log_files=True,
        resume=False,
    )
    runner.run(args, dask_client)
    assert not os.path.exists(temp / "remove_all_intermediate")


def assert_stage_level_files_exist(base_intermediate_dir):
    # Check that stage-level done files are still around for the import of
    # `small_sky_object_catalog` at order 0.
    expected_contents = [
        "alignment.pickle",
        "histograms",  # directory containing sub-histograms
        "input_paths.txt",  # original input paths for subsequent comparison
        "mapping_done",  # stage-level done file
        "mapping_histogram.npz",  # concatenated histogram file
        "order_0",  # all intermediate parquet files
        "reader.pickle",  # pickled InputReader
        "reducing",  # directory containing task-level done files
        "reducing_done",  # stage-level done file
        "splitting",  # directory containing task-level done files
        "splitting_done",  # stage-level done file
    ]
    assert_directory_contains(base_intermediate_dir, expected_contents)

    checking_dir = base_intermediate_dir / "histograms"
    assert_directory_contains(
        checking_dir, ["map_0.npz", "map_1.npz", "map_2.npz", "map_3.npz", "map_4.npz", "map_5.npz"]
    )
    checking_dir = base_intermediate_dir / "splitting"
    assert_directory_contains(
        checking_dir,
        ["split_0_done", "split_1_done", "split_2_done", "split_3_done", "split_4_done", "split_5_done"],
    )

    checking_dir = base_intermediate_dir / "reducing"
    assert_directory_contains(checking_dir, ["0_11_done"])


def assert_intermediate_parquet_files_exist(base_intermediate_dir):
    # Check that all the intermediate parquet shards are still around for the
    # import of `small_sky_object_catalog` at order 0.
    checking_dir = base_intermediate_dir / "order_0" / "dir_0" / "pixel_11"
    assert_directory_contains(
        checking_dir,
        [
            "shard_split_0_0.parquet",
            "shard_split_1_0.parquet",
            "shard_split_2_0.parquet",
            "shard_split_3_0.parquet",
            "shard_split_4_0.parquet",
        ],
    )


def assert_directory_contains(dir_name, expected_contents):
    assert os.path.exists(dir_name)
    actual_contents = os.listdir(dir_name)
    actual_contents.sort()
    npt.assert_array_equal(actual_contents, expected_contents)


@pytest.mark.dask
def test_import_lowest_healpix_order(
    dask_client,
    small_sky_parts_dir,
    tmp_path,
):
    """Test basic execution.
    - tests that all the final tiles are at the lowest healpix order,
        and that we don't create tiles where there is no data.
    """
    args = ImportArguments(
        output_artifact_name="small_sky_object_catalog",
        input_path=small_sky_parts_dir,
        file_reader="csv",
        output_path=tmp_path,
        dask_tmp=tmp_path,
        lowest_healpix_order=2,
        highest_healpix_order=4,
        skymap_alt_orders=[3, 1],
        progress_bar=False,
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path
    # Check that the partition info file exists - all pixels at order 2!
    assert all(pixel.order >= 2 for pixel in catalog.get_healpix_pixels())
    assert len(catalog.get_healpix_pixels()) == 14

    # Pick a parquet file and make sure it contains as many rows as we expect
    output_file = os.path.join(args.catalog_path, "dataset", "Norder=2", "Dir=0", "Npix=178.parquet")

    data_frame = pd.read_parquet(output_file, engine="pyarrow")
    assert len(data_frame) == 14
    ids = data_frame["id"]
    assert np.logical_and(ids >= 700, ids < 832).all()

    point_map_file = args.catalog_path / "point_map.fits"
    assert point_map_file.exists()

    skymap_file = args.catalog_path / "skymap.fits"
    assert skymap_file.exists()

    assert len(read_skymap(catalog, None)) == 3_072

    skymap_file = args.catalog_path / "skymap.1.fits"
    assert skymap_file.exists()
    skymap_file = args.catalog_path / "skymap.2.fits"
    assert not skymap_file.exists()
    skymap_file = args.catalog_path / "skymap.3.fits"
    assert skymap_file.exists()

    assert catalog.catalog_info.skymap_alt_orders == [1, 3]
    assert catalog.catalog_info.skymap_order == 4

    old_properties_file = args.catalog_path / "properties"
    assert old_properties_file.exists()
    new_properties_file = args.catalog_path / "hats.properties"
    assert new_properties_file.exists()

    with open(old_properties_file, "r", encoding="utf-8") as old_file:
        old_contents = old_file.readlines()

    with open(new_properties_file, "r", encoding="utf-8") as new_file:
        new_contents = new_file.readlines()

    assert old_contents == new_contents


class StarrReader(CsvReader):
    """Shallow subclass"""

    def read(self, input_file, read_columns=None):
        files = glob.glob(f"{input_file}/*.starr")
        files.sort()
        for file in files:
            return super().read(file, read_columns)


@pytest.mark.dask
def test_import_starr_file(
    dask_client,
    formats_dir,
    assert_parquet_file_ids,
    tmp_path,
):
    """Test basic execution.
    - tests that we can run pipeline with a totally unknown file type, so long
      as a valid InputReader implementation is provided.
    """

    args = ImportArguments(
        output_artifact_name="starr",
        input_file_list=[formats_dir],
        file_reader=StarrReader(),
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=2,
        pixel_threshold=3_000,
        progress_bar=False,
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path
    assert catalog.catalog_info.total_rows == 131
    assert len(catalog.get_healpix_pixels()) == 1

    # Check that the catalog parquet file exists and contains correct object IDs
    output_file = os.path.join(args.catalog_path, "dataset", "Norder=0", "Dir=0", "Npix=11.parquet")

    expected_ids = [*range(700, 831)]
    assert_parquet_file_ids(output_file, "id", expected_ids)


class PyarrowCsvReader(CsvReader):
    """Use pyarrow for CSV reading, and force some pyarrow dtypes.
    Return a pyarrow table instead of pd.DataFrame."""

    def read(self, input_file, read_columns=None):
        table = csv.read_csv(input_file)
        extras = pa.array([[True, False, True]] * len(table), type=pa.list_(pa.bool_(), 3))
        table = table.append_column("extras", extras)
        yield table


@pytest.mark.dask
def test_import_pyarrow_types(
    dask_client,
    small_sky_single_file,
    assert_parquet_file_ids,
    tmp_path,
):
    """Test basic execution.
    - tests that we can run pipeline with a totally unknown file type, so long
      as a valid InputReader implementation is provided.
    """

    args = ImportArguments(
        output_artifact_name="pyarrow_dtype",
        input_file_list=[small_sky_single_file],
        file_reader=PyarrowCsvReader(),
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=2,
        pixel_threshold=3_000,
        progress_bar=False,
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path
    assert catalog.catalog_info.total_rows == 131
    assert len(catalog.get_healpix_pixels()) == 1

    # Check that the catalog parquet file exists and contains correct object IDs
    output_file = args.catalog_path / "dataset" / "Norder=0" / "Dir=0" / "Npix=11.parquet"

    expected_ids = [*range(700, 831)]
    assert_parquet_file_ids(output_file, "id", expected_ids)

    expected_parquet_schema = pa.schema(
        [
            pa.field("_healpix_29", pa.int64()),
            pa.field("id", pa.int64()),
            pa.field("ra", pa.float64()),
            pa.field("dec", pa.float64()),
            pa.field("ra_error", pa.int64()),
            pa.field("dec_error", pa.int64()),
            pa.field("extras", pa.list_(pa.bool_(), 3)),  # The 3 is the length for `fixed_size_list`
        ]
    )
    schema = pq.read_metadata(output_file).schema.to_arrow_schema()
    assert schema.equals(expected_parquet_schema)
    schema = pq.read_metadata(args.catalog_path / "dataset" / "_metadata").schema.to_arrow_schema()
    assert schema.equals(expected_parquet_schema)


@pytest.mark.dask
def test_import_healpix_29_pyarrow_table_csv(
    dask_client,
    small_sky_single_file,
    assert_parquet_file_ids,
    tmp_path,
):
    """Should be identical to the above test, but uses the CsvPyarrowReader."""
    args = ImportArguments(
        output_artifact_name="small_sky_pyarrow",
        input_file_list=[small_sky_single_file],
        file_reader=CsvPyarrowReader(),
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=2,
        pixel_threshold=3_000,
        progress_bar=False,
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path
    assert catalog.catalog_info.total_rows == 131
    assert len(catalog.get_healpix_pixels()) == 1

    # Check that the catalog parquet file exists and contains correct object IDs
    output_file = args.catalog_path / "dataset" / "Norder=0" / "Dir=0" / "Npix=11.parquet"

    expected_ids = [*range(700, 831)]
    assert_parquet_file_ids(output_file, "id", expected_ids)
    data_frame = pd.read_parquet(output_file, engine="pyarrow")
    assert data_frame.index.name is None
    npt.assert_array_equal(
        data_frame.columns,
        ["_healpix_29", "id", "ra", "dec", "ra_error", "dec_error"],
    )


@pytest.mark.dask
def test_import_healpix_29_pyarrow_table_parquet(
    dask_client,
    formats_dir,
    assert_parquet_file_ids,
    tmp_path,
):
    """Should be identical to the above test, but uses the ParquetPyarrowReader."""
    input_file = formats_dir / "healpix_29_index.parquet"
    args = ImportArguments(
        output_artifact_name="using_healpix_index",
        input_file_list=[input_file],
        file_reader=ParquetPyarrowReader(),
        output_path=tmp_path,
        dask_tmp=tmp_path,
        use_healpix_29=True,
        highest_healpix_order=2,
        pixel_threshold=3_000,
        progress_bar=False,
        ## Sneak in a test for custom extension
        npix_suffix=".pq",
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path
    assert catalog.catalog_info.total_rows == 131
    assert len(catalog.get_healpix_pixels()) == 1

    # Check that the catalog parquet file exists and contains correct object IDs
    output_file = args.catalog_path / "dataset" / "Norder=0" / "Dir=0" / "Npix=11.pq"

    expected_ids = [*range(700, 831)]
    assert_parquet_file_ids(output_file, "id", expected_ids)
    data_frame = pd.read_parquet(output_file, engine="pyarrow")

    npt.assert_array_equal(
        data_frame.columns,
        ["id", "_healpix_29"],
    )


@pytest.mark.dask
def test_import_healpix_29(
    dask_client,
    formats_dir,
    assert_parquet_file_ids,
    tmp_path,
):
    """Test basic execution, using a previously-computed _healpix_29 column for spatial partitioning."""
    ## First, let's just check the assumptions we have about our input file:
    ## - should have _healpix_29 as the indexed column
    ## - should NOT have any columns like "ra" or "dec"
    input_file = formats_dir / "healpix_29_index.parquet"

    expected_ids = [*range(700, 831)]
    assert_parquet_file_ids(input_file, "id", expected_ids)

    data_frame = pd.read_parquet(input_file, engine="pyarrow")
    assert data_frame.index.name == "_healpix_29"
    npt.assert_array_equal(data_frame.columns, ["id"])

    args = ImportArguments(
        output_artifact_name="using_healpix_29",
        input_file_list=[input_file],
        file_reader="parquet",
        output_path=tmp_path,
        dask_tmp=tmp_path,
        use_healpix_29=True,
        highest_healpix_order=2,
        pixel_threshold=3_000,
        progress_bar=False,
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path
    assert catalog.catalog_info.total_rows == 131
    assert len(catalog.get_healpix_pixels()) == 1

    # Check that the catalog parquet file exists and contains correct object IDs
    output_file = os.path.join(args.catalog_path, "dataset", "Norder=0", "Dir=0", "Npix=11.parquet")

    expected_ids = [*range(700, 831)]
    assert_parquet_file_ids(output_file, "id", expected_ids)
    data_frame = pd.read_parquet(output_file, engine="pyarrow")
    npt.assert_array_equal(
        data_frame.columns,
        ["_healpix_29", "id"],
    )


@pytest.mark.dask
def test_import_healpix_29_no_pandas(
    dask_client,
    formats_dir,
    assert_parquet_file_ids,
    tmp_path,
):
    """Test basic execution, using a previously-computed _healpix_29 column for spatial partitioning."""
    input_file = formats_dir / "spatial_index.csv"
    args = ImportArguments(
        output_artifact_name="using_healpix_29",
        input_file_list=[input_file],
        file_reader="csv",
        output_path=tmp_path,
        dask_tmp=tmp_path,
        use_healpix_29=True,
        highest_healpix_order=2,
        pixel_threshold=3_000,
        progress_bar=False,
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path
    assert catalog.catalog_info.total_rows == 131
    assert len(catalog.get_healpix_pixels()) == 1

    # Check that the catalog parquet file exists and contains correct object IDs
    output_file = os.path.join(args.catalog_path, "dataset", "Norder=0", "Dir=0", "Npix=11.parquet")

    expected_ids = [*range(700, 831)]
    assert_parquet_file_ids(output_file, "id", expected_ids)
    data_frame = pd.read_parquet(output_file, engine="pyarrow")
    npt.assert_array_equal(
        data_frame.columns,
        ["id", "_healpix_29", "magnitude", "nobs"],
    )


@pytest.mark.dask
def test_import_gaia_minimum(
    dask_client,
    formats_dir,
    tmp_path,
):
    """Test end-to-end import, using a representative chunk of gaia data."""
    input_file = formats_dir / "gaia_minimum.csv"
    schema_file = formats_dir / "gaia_minimum_schema.parquet"

    args = ImportArguments(
        output_artifact_name="gaia_minimum",
        input_file_list=[input_file],
        file_reader=CsvReader(
            comment="#",
            schema_file=schema_file,
        ),
        ra_column="ra",
        dec_column="dec",
        sort_columns="solution_id",
        use_schema_file=schema_file,
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=2,
        pixel_threshold=3_000,
        progress_bar=False,
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path
    assert catalog.catalog_info.total_rows == 5
    assert len(catalog.get_healpix_pixels()) == 3

    # Pick an output file, and make sure it has valid columns:
    first_pixel = catalog.get_healpix_pixels()[0]
    output_file = (
        args.catalog_path
        / "dataset"
        / f"Norder={first_pixel.order}"
        / "Dir=0"
        / f"Npix={first_pixel.pixel}.parquet"
    )
    data_frame = pd.read_parquet(output_file)

    # Make sure that the spatial index values match the pixel for the partition (0,5)
    spatial_index_pixels = spatial_index_to_healpix(data_frame["_healpix_29"].values, 0)
    npt.assert_array_equal(spatial_index_pixels, [5, 5, 5])


@pytest.mark.dask
def test_import_issue_538(
    dask_client,
    reproducers_dir,
    tmp_path,
):
    """Test end-to-end import, using a reproducible chunk of data."""
    args = ImportArguments(
        output_artifact_name="numpy_unique",
        input_file_list=[reproducers_dir / "issue_538.csv"],
        file_reader="csv",
        ra_column="RA",
        dec_column="DEC",
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=2,
        pixel_threshold=3_000,
        progress_bar=False,
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path
    assert catalog.catalog_info.total_rows == 132
    assert len(catalog.get_healpix_pixels()) == 12


@pytest.mark.dask
def test_gaia_ecsv(
    dask_client,
    formats_dir,
    tmp_path,
    assert_parquet_file_ids,
):
    input_file = formats_dir / "gaia_epoch.ecsv"

    args = ImportArguments(
        output_artifact_name="gaia_e_astropy",
        input_file_list=[input_file],
        file_reader="ecsv",
        ra_column="ra",
        dec_column="dec",
        sort_columns="solution_id,source_id",
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=2,
        pixel_threshold=3_000,
        progress_bar=False,
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path
    assert catalog.catalog_info.total_rows == 3
    assert len(catalog.get_healpix_pixels()) == 1

    first_pixel = catalog.get_healpix_pixels()[0]
    output_file = (
        args.catalog_path
        / "dataset"
        / f"Norder={first_pixel.order}"
        / "Dir=0"
        / f"Npix={first_pixel.pixel}.parquet"
    )
    assert_parquet_file_ids(output_file, "source_id", [10655814178816, 10892037246720, 14263587225600])

    # Check that the schema is correct for leaf parquet and _metadata files
    expected_parquet_schema = pa.schema(
        [
            pa.field("_healpix_29", pa.int64()),
            pa.field("solution_id", pa.int64()),
            pa.field("source_id", pa.int64()),
            pa.field("ra", pa.float64()),
            pa.field("dec", pa.float64()),
            pa.field("n_transits", pa.int16()),
            pa.field("transit_id", pa.list_(pa.int64())),
            pa.field("g_transit_time", pa.list_(pa.float64())),
            pa.field("g_transit_flux", pa.list_(pa.float64())),
            pa.field("g_transit_flux_error", pa.list_(pa.float64())),
            pa.field("g_transit_flux_over_error", pa.list_(pa.float32())),
            pa.field("g_transit_mag", pa.list_(pa.float64())),
            pa.field("g_transit_n_obs", pa.list_(pa.int8())),
            pa.field("bp_obs_time", pa.list_(pa.float64())),
            pa.field("bp_flux", pa.list_(pa.float64())),
            pa.field("bp_flux_error", pa.list_(pa.float64())),
            pa.field("bp_flux_over_error", pa.list_(pa.float32())),
            pa.field("bp_mag", pa.list_(pa.float64())),
            pa.field("rp_obs_time", pa.list_(pa.float64())),
            pa.field("rp_flux", pa.list_(pa.float64())),
            pa.field("rp_flux_error", pa.list_(pa.float64())),
            pa.field("rp_flux_over_error", pa.list_(pa.float32())),
            pa.field("rp_mag", pa.list_(pa.float64())),
            pa.field("photometry_flag_noisy_data", pa.list_(pa.bool_())),
            pa.field("photometry_flag_sm_unavailable", pa.list_(pa.bool_())),
            pa.field("photometry_flag_af1_unavailable", pa.list_(pa.bool_())),
            pa.field("photometry_flag_af2_unavailable", pa.list_(pa.bool_())),
            pa.field("photometry_flag_af3_unavailable", pa.list_(pa.bool_())),
            pa.field("photometry_flag_af4_unavailable", pa.list_(pa.bool_())),
            pa.field("photometry_flag_af5_unavailable", pa.list_(pa.bool_())),
            pa.field("photometry_flag_af6_unavailable", pa.list_(pa.bool_())),
            pa.field("photometry_flag_af7_unavailable", pa.list_(pa.bool_())),
            pa.field("photometry_flag_af8_unavailable", pa.list_(pa.bool_())),
            pa.field("photometry_flag_af9_unavailable", pa.list_(pa.bool_())),
            pa.field("photometry_flag_bp_unavailable", pa.list_(pa.bool_())),
            pa.field("photometry_flag_rp_unavailable", pa.list_(pa.bool_())),
            pa.field("photometry_flag_sm_reject", pa.list_(pa.bool_())),
            pa.field("photometry_flag_af1_reject", pa.list_(pa.bool_())),
            pa.field("photometry_flag_af2_reject", pa.list_(pa.bool_())),
            pa.field("photometry_flag_af3_reject", pa.list_(pa.bool_())),
            pa.field("photometry_flag_af4_reject", pa.list_(pa.bool_())),
            pa.field("photometry_flag_af5_reject", pa.list_(pa.bool_())),
            pa.field("photometry_flag_af6_reject", pa.list_(pa.bool_())),
            pa.field("photometry_flag_af7_reject", pa.list_(pa.bool_())),
            pa.field("photometry_flag_af8_reject", pa.list_(pa.bool_())),
            pa.field("photometry_flag_af9_reject", pa.list_(pa.bool_())),
            pa.field("photometry_flag_bp_reject", pa.list_(pa.bool_())),
            pa.field("photometry_flag_rp_reject", pa.list_(pa.bool_())),
            pa.field("variability_flag_g_reject", pa.list_(pa.bool_())),
            pa.field("variability_flag_bp_reject", pa.list_(pa.bool_())),
            pa.field("variability_flag_rp_reject", pa.list_(pa.bool_())),
        ]
    )

    # In-memory schema uses list<item> naming convention, but pyarrow converts to
    # the parquet-compliant list<element> convention when writing to disk.
    # Round trip the schema to get a schema with compliant nested naming convention.
    schema_path = tmp_path / "temp_schema.parquet"
    pq.write_table(expected_parquet_schema.empty_table(), where=schema_path)
    expected_parquet_schema = pq.read_metadata(schema_path).schema.to_arrow_schema()

    schema = pq.read_metadata(output_file).schema.to_arrow_schema()
    assert schema.equals(expected_parquet_schema)
    schema = pq.read_metadata(args.catalog_path / "dataset" / "_metadata").schema.to_arrow_schema()
    assert schema.equals(expected_parquet_schema)
    schema = pq.read_metadata(args.catalog_path / "dataset" / "_common_metadata").schema.to_arrow_schema()
    assert schema.equals(expected_parquet_schema)
    schema = pds.dataset(args.catalog_path, format="parquet").schema
    assert schema.equals(expected_parquet_schema)


@pytest.mark.dask
def test_import_indexed_csv(
    dask_client,
    indexed_files_dir,
    tmp_path,
):
    """Use indexed-style CSV reads. There are two index files, and we expect
    to have two batches worth of intermediate files."""
    temp = tmp_path / "intermediate_files"
    os.makedirs(temp)

    args = ImportArguments(
        output_artifact_name="indexed_csv",
        input_file_list=[
            indexed_files_dir / "csv_list_double_1_of_2.txt",
            indexed_files_dir / "csv_list_double_2_of_2.txt",
            indexed_files_dir / "csv_list_empty.txt",
        ],
        output_path=tmp_path,
        file_reader="indexed_csv",
        sort_columns="id",
        tmp_dir=temp,
        dask_tmp=temp,
        highest_healpix_order=2,
        delete_intermediate_parquet_files=False,
        delete_resume_log_files=False,
        pixel_threshold=3_000,
        progress_bar=False,
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path
    assert len(catalog.get_healpix_pixels()) == 1

    # Check that there are TWO intermediate parquet file (two index files).
    assert_directory_contains(
        temp / "indexed_csv" / "intermediate" / "order_0" / "dir_0" / "pixel_11",
        [
            "shard_split_0_0.parquet",
            "shard_split_1_0.parquet",
        ],
    )


@pytest.mark.dask
def test_import_healpix13(dask_client, formats_dir, tmp_path):
    """Use catalog data with an existing spatial index NOT at order 29."""

    args = ImportArguments(
        output_artifact_name="healpix13",
        input_file_list=formats_dir / "small_sky_healpix13.csv",
        output_path=tmp_path,
        file_reader="csv",
        sort_columns="id",
        pixel_threshold=3_000,
        highest_healpix_order=2,
        progress_bar=False,
        add_healpix_29=False,
        addl_hats_properties={"hats_col_healpix": "healpix13", "hats_col_healpix_order": 13},
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path
    assert len(catalog.get_healpix_pixels()) == 1
    assert catalog.has_healpix_column()
    assert catalog.catalog_info.healpix_column == "healpix13"


@pytest.mark.dask
def test_pickled_reader_class_issue542(
    dask_client,
    formats_dir,
    tmp_path,
):
    """Check if we can use reader class not imported from somewhere else,
    e.g. defined in a Jupyter notebook.
    """

    class MyReader(StarrReader):
        """My cool reader."""

    args = ImportArguments(
        output_artifact_name="starr",
        input_file_list=[formats_dir],
        file_reader=MyReader(),
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=2,
        pixel_threshold=3_000,
        progress_bar=False,
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.catalog_info.total_rows == 131
