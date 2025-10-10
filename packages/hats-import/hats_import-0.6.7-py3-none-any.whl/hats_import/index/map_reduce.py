"""Create columnar index of hats table using dask for parallelization"""

import dask.dataframe as dd
import numpy as np
from hats.io import file_io, paths
from hats.pixel_math.spatial_index import SPATIAL_INDEX_COLUMN


def read_leaf_file(
    input_file_and_pixel, include_columns, include_healpix_29, drop_duplicates, schema, include_order_pixel
):
    """Mapping function called once per input file.

    Reads the leaf parquet file, and returns with appropriate columns and duplicates dropped."""
    input_file, input_pixel = input_file_and_pixel
    data = file_io.read_parquet_file_to_pandas(
        input_file,
        columns=include_columns,
        schema=schema,
    )

    if data.index.name == SPATIAL_INDEX_COLUMN:
        data = data.reset_index()
    if not include_healpix_29 and SPATIAL_INDEX_COLUMN in data.columns:
        data = data.drop(columns=[SPATIAL_INDEX_COLUMN])
    if include_order_pixel:
        length = len(data)
        data["Norder"] = np.full(length, fill_value=input_pixel.order, dtype=np.uint8)
        data["Npix"] = np.full(length, fill_value=input_pixel.pixel, dtype=np.uint64)

    if drop_duplicates:
        data = data.drop_duplicates()
    return data


def create_index(args, client):
    """Read primary column, indexing column, and other payload data,
    and write to catalog directory."""
    include_columns = [args.indexing_column]
    if args.extra_columns:
        include_columns.extend(args.extra_columns)
    if args.include_healpix_29:
        include_columns.append(SPATIAL_INDEX_COLUMN)

    index_dir = file_io.get_upath(args.catalog_path / "dataset" / "index")

    data = dd.from_map(
        read_leaf_file,
        [
            (
                paths.pixel_catalog_file(catalog_base_dir=args.input_catalog.catalog_base_dir, pixel=pixel),
                pixel,
            )
            for pixel in args.input_catalog.get_healpix_pixels()
        ],
        include_columns=include_columns,
        include_healpix_29=args.include_healpix_29,
        drop_duplicates=args.drop_duplicates,
        schema=args.input_catalog.schema,
        include_order_pixel=args.include_order_pixel,
    )

    if args.division_hints is not None and len(args.division_hints) > 2:
        data = data.set_index(args.indexing_column, divisions=args.division_hints)
    else:
        # Try to avoid this! It's expensive! See:
        # https://docs.dask.org/en/latest/generated/dask.dataframe.DataFrame.set_index.html
        data = data.set_index(args.indexing_column)

    data = data.repartition(partition_size=args.compute_partition_size)

    # Now just write it out to leaf parquet files!
    result = data.to_parquet(
        path=index_dir.path,
        engine="pyarrow",
        compute_kwargs={"partition_size": args.compute_partition_size},
        filesystem=index_dir.fs,
    )
    client.compute(result)
    return len(data)
