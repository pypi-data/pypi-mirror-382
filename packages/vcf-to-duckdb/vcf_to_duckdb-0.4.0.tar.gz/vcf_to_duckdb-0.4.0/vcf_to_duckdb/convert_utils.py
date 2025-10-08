import logging
import os
import re
import subprocess
from math import ceil
from pathlib import Path

import bgzip
import duckdb
import pandas as pd
from caseconverter import snakecase
from duckdb import DuckDBPyConnection


def convert(
    vcf_path: Path,
    db_path: Path,
    parquet_dir_path: Path,
    db_tmp_dir_path: Path,
    multiallelics: bool,
    compound_info_field_map: dict[str, list[dict[str, str]]],
    url_encoded_col_name_regexes: list[str],
    tab_path: Path | None = None,
    batch_size: int = 100000,
) -> None:
    """
    Convert a VCF file to a DuckDB database exported as Parquet files.

    :param vcf_path: Path to input VCF file
    :param db_path: Path to output DuckDB database file
    :param parquet_dir_path: Directory to output Parquet files
    :param db_tmp_dir_path: path to a temporary directory to use for DuckDB offloading
    :param multiallelics: Whether the VCF file contains multiallelic variants
    :param compound_info_field_map: Dictionary of annotation INFO names and steps to
    extract their data, where each step is itself a dictionary of keys/instructions
    ("split" or "extract") and values/compiled regexes (e.g. "/\\s*\\|\\s*/")
    :param url_encoded_col_name_regexes: List of regexes matching columns to URL-decode
    :param tab_path: Optional path to intermediate TSV file
    :param batch_size: number of variants to process at a time
    """

    val_info_types = get_vcf_val_info_types(
        vcf_path, multiallelics, compound_info_field_map
    )

    if tab_path is None:
        # use the same name as the VCF file but without the .gz extension
        tab_path = vcf_path.with_suffix("").with_suffix(".tsv")

    try:
        # remove the existing database file if it exists
        os.remove(db_path)
    except OSError:
        pass

    with duckdb.connect(db_path) as db:
        # set up the database schema and tables
        set_up_db(db, val_info_types, db_tmp_dir_path)

        # convert the VCF file to a tab-delimited file
        write_tab_vcf(vcf_gz_path=vcf_path, tab_path=tab_path)

        logging.info(f"Reading {vcf_path} into {db_path}")
        populate_db(
            db,
            tab_path,
            val_info_types,
            compound_info_field_map,
            url_encoded_col_name_regexes,
            batch_size,
        )

        logging.info(f"Exporting schema and Parquet files to {parquet_dir_path}")
        db.sql(f"EXPORT DATABASE '{parquet_dir_path}' (FORMAT PARQUET)")


def get_vcf_val_info_types(
    vcf_path: Path,
    multiallelics: bool,
    compound_info_field_map: dict[str, list[dict[str, str]]],
) -> pd.DataFrame:
    """
    Extract value and info field types from VCF header. This creates a DataFrame with
    rows like:

    [{'id': 'AF',
      'number': '1',
      'type': 'FLOAT',
      'description': 'Allele fractions of alternate alleles in the tumor',
      'kind': 'value',
      'has_children': False,
      'parent_id': None,
      'ix': None,
      'col_def': 'FLOAT',
      'is_list': False,
      'v_col_name': 'v_float'},
     {'id': 'CSQ',
      'number': '.',
      'type': 'JSON',
      'description': 'Consequence annotations from Ensembl VEP. Format: '
                     'Allele|Consequence|IMPACT|SYMBOL|Gene|<snip>|am_pathogenicity',
      'kind': 'info',
      'has_children': True,
      'parent_id': None,
      'ix': None,
      'col_def': 'JSON[]',
      'is_list': True,
      'v_col_name': 'v_json_arr'},
     {'id': 'SYMBOL',
      'number': '1',
      'type': 'VARCHAR',
      'description': None,
      'kind': 'sub_info',
      'has_children': False,
      'parent_id': 'CSQ',
      'ix': 4,
      'col_def': 'VARCHAR',
      'is_list': False,
      'v_col_name': 'v_varchar'}]

    :param vcf_path: Path to VCF file
    :param multiallelics: Whether the VCF file contains multiallelic variants
    :param compound_info_field_map: Dictionary of annotation INFO names and steps to
    extract their data, where each step is itself a dictionary of keys/instructions
    ("split" or "extract") and values/compiled regexes (e.g. "/\\s*\\|\\s*/")
    :return: DataFrame containing field type information
    """

    # get the header lines from the VCF file
    header_lines = get_header_lines(vcf_path)

    # filter out lines that are not relevant to values or info fields
    header_lines = [
        x for x in header_lines if x.startswith("##FORMAT") or x.startswith("##INFO")
    ]

    # map VCF field types to DuckDB types
    type_map = {
        "Integer": "INTEGER",
        "Float": "FLOAT",
        "String": "VARCHAR",
        "Character": "VARCHAR",
        "Flag": "BOOLEAN",
    }

    # initialize arrays for storing field types
    arr = []
    sub_arr = []

    # iterate over the header lines
    for x in header_lines:
        # extract the kind of field (value or info)
        kind = re.search(r"^##(\w+)", x).group(1).lower()  # pyright: ignore

        # extract the key-value pairs from the interior
        interior = re.search(r"<(.+)>$", x).group(1)  # pyright: ignore
        parts = re.findall(r'([A-Za-z0-9_]+)=(".*?"|[^,]+)', interior)

        # normalize the key-value pairs
        d = {k.lower(): v.strip('"') for k, v in parts}

        d["kind"] = kind if kind == "info" else "value"

        if d["id"] in compound_info_field_map.keys():
            # we'll store this kind of info field as a JSON object
            d["has_children"] = True
            d["type"] = "JSON"

            # extract the subfield names from the description
            desc = re.search(
                r"^.+:['\s]*([^']+)['\s]*$",
                d["description"],
            ).group(1)  # pyright: ignore
            subfields = re.split(r"\s*\|\s*", desc)

            # iterate over the subfields (we have to assume they're all strings) and
            # store the order they appear in `ix`, which we'll use to match subfield
            # names and values later
            for ix, s in enumerate(subfields):
                dsub = {
                    "id": s,
                    "has_children": False,
                    "number": "1",
                    "type": "VARCHAR",
                    "kind": "sub_info",
                    "parent_id": d["id"],
                    "ix": ix + 1,
                }

                sub_arr.append(dsub)

        else:
            d["has_children"] = False
            d["type"] = type_map[d["type"]]

        arr.append(d)

    # create a properly-typed DataFrame from the collected field types
    df = pd.DataFrame(arr + sub_arr).astype(
        {
            "id": "string",
            "number": "string",
            "type": "string",
            "description": "string",
            "kind": "string",
            "has_children": "boolean",
            "parent_id": "string",
            "ix": "UInt64",
        }
    )

    if not multiallelics:
        # force single value if we're assuming multiallelics have already been split to
        # separate rows (TODO: detect incorrect assumption)
        df.loc[df["number"].eq("A"), "number"] = "1"

    # define a DuckDB column type for each item, appending "[]" if the field is a list
    df["col_def"] = df["type"]
    df["is_list"] = ~df["number"].isin(["0", "1"])
    df.loc[df["is_list"], "col_def"] += "[]"

    # define the name of the column to store the value
    df["v_col_name"] = "v_" + df["type"].str.lower()
    df.loc[df["is_list"], "v_col_name"] += "_arr"

    return df


def get_header_lines(vcf_path: Path) -> list[str]:
    """
    Read all of the header lines in a list of VCF files and return their union,
    retaining their order.

    :param vcf_path: a path to a VCF file
    :return: a list of the distinct header lines in their original order
    """

    header_lines = []
    col_header_line = None

    # don't read more lines than necessary to get the entire header
    break_next_time = False

    with open(vcf_path, "rb") as raw:
        logging.info(f"Reading {os.path.basename(vcf_path)} header")
        this_header_texts = ""  # start collecting header text

        # assume file is bgzipped
        with bgzip.BGZipReader(raw) as f:
            while True:
                # read a small block of bytes at a time
                if not (d := f.read(10 * 1024)):
                    break

                # concat the latest chunk of text
                text = d.tobytes().decode()
                d.release()
                this_header_texts += text

                # check if we've reached the end of the header section and get one
                # more chunk
                if break_next_time:
                    break
                elif "\n#CHROM" in this_header_texts:
                    break_next_time = True

        # extract the header lines and the column headers
        this_header_lines = this_header_texts.split("\n")

        if col_header_line is None:
            # extract the line with column names
            col_header_line = [x for x in this_header_lines if x.startswith("#CHROM")][
                0
            ]

        this_header_lines = [x for x in this_header_lines if x.startswith("##")]

        # add to the collected header lines
        header_lines.extend(this_header_lines)

    # de-dup but keep original order of lines
    return (
        pd.Series([*header_lines, col_header_line])
        .astype("string")
        .drop_duplicates()
        .tolist()
    )


def set_up_db(
    db: DuckDBPyConnection, val_info_types: pd.DataFrame, db_tmp_dir_path: Path
) -> None:
    """
    Set up the DuckDB database schema and tables.

    :param db: DuckDB database connection
    :param val_info_types: DataFrame containing VCF value and info field types
    :param db_tmp_dir_path: path to a temporary directory to use for DuckDB offloading
    """

    # misc. DuckDB settings
    db.sql("""
        SET preserve_insertion_order = false;
        SET enable_progress_bar = false;
    """)

    db.execute(f"PRAGMA temp_directory='{db_tmp_dir_path.name}'")

    # register the val_info_types table in the database
    val_info_types_tbl = val_info_types.copy()
    val_info_types_tbl["id_snake"] = val_info_types_tbl["id"]
    db.register("val_info_types_view", val_info_types_tbl)

    # persist val_info_types as a regular table in the database
    db.sql("""
        CREATE TABLE IF NOT EXISTS
            val_info_types
        AS
            SELECT * from val_info_types_view
    """)

    db.unregister("val_info_types_view")

    # convert the id column to snake case
    snake_case_col(db, tbl="val_info_types", col="id_snake")

    # create all the temp tables for variants and generic key-value data
    db.sql("""
        CREATE TABLE IF NOT EXISTS vcf_lines (
            chrom VARCHAR NOT NULL,
            pos UINTEGER NOT NULL,
            id VARCHAR,
            ref VARCHAR,
            alt VARCHAR,
            qual VARCHAR,
            filters VARCHAR,
            info VARCHAR,
            format VARCHAR,
            values VARCHAR
        );
    """)

    db.sql("""
        CREATE TABLE IF NOT EXISTS kv (
            vid VARCHAR,
            k VARCHAR,
            v VARCHAR
        );
    """)

    db.sql("""
        CREATE TABLE IF NOT EXISTS kv_compound_info (
            vid VARCHAR,
            k VARCHAR,
            k_ix INTEGER,
            k_sub VARCHAR,
            ix INTEGER,
            v VARCHAR
        );
    """)

    db.sql("""
        CREATE TABLE IF NOT EXISTS vals_info_tmp (
            vid VARCHAR,
            kind VARCHAR,
            k VARCHAR,
            v_boolean BOOLEAN,
            v_varchar VARCHAR,
            v_integer INTEGER,
            v_float FLOAT,
            v_json JSON,
            v_boolean_arr BOOLEAN[],
            v_varchar_arr VARCHAR[],
            v_integer_arr INTEGER[],
            v_float_arr FLOAT[],
            v_json_arr JSON[]
        );
    """)

    # create all the persistent tables for variants and their data
    db.sql("""
        CREATE TABLE IF NOT EXISTS variants (
            vid VARCHAR PRIMARY KEY,
            chrom VARCHAR NOT NULL,
            pos UINTEGER NOT NULL,
            id VARCHAR,
            ref VARCHAR,
            alt VARCHAR,
            qual VARCHAR,
            filters VARCHAR[]
        );
    """)

    db.sql("""
        CREATE TABLE IF NOT EXISTS vals_info (
            vid VARCHAR REFERENCES variants (vid),
            kind VARCHAR,
            k VARCHAR NOT NULL,
            v_boolean BOOLEAN,
            v_varchar VARCHAR,
            v_integer INTEGER,
            v_float FLOAT,
            v_json JSON,
            v_boolean_arr BOOLEAN[],
            v_varchar_arr VARCHAR[],
            v_integer_arr INTEGER[],
            v_float_arr FLOAT[],
            v_json_arr JSON[]
        );
    """)

    # register a sub_fields table for compound info fields
    info_types = val_info_types.loc[val_info_types["kind"].eq("info")]

    sub_fields = val_info_types.loc[
        val_info_types["parent_id"].isin(info_types["id"]),
        ["ix", "parent_id", "id"],
    ].rename(columns={"parent_id": "k", "id": "k_sub"})

    db.register("sub_fields", sub_fields)


def write_tab_vcf(vcf_gz_path: Path, tab_path: Path) -> None:
    """
    Convert a bgzipped VCF file to a header-less, tab-delimited format using bcftools.

    :param vcf_gz_path: Path to input bgzipped VCF file
    :param tab_path: Path to output tab-delimited file
    """

    logging.info(f"Converting {vcf_gz_path} to TSV")
    subprocess.run(["bcftools", "view", vcf_gz_path, "--no-header", "-o", tab_path])


def populate_db(
    db: DuckDBPyConnection,
    tab_path: Path,
    val_info_types: pd.DataFrame,
    compound_info_field_map: dict[str, list[dict[str, str]]],
    url_encoded_col_name_regexes: list[str],
    batch_size: int = 100000,
) -> None:
    """
    Populate the DuckDB database with VCF data.

    :param db: DuckDB database connection
    :param tab_path: Path to tab-delimited VCF file
    :param val_info_types: DataFrame containing VCF value and info field types
    :param compound_info_field_map: Dictionary of annotation INFO names and steps to
    extract their data, where each step is itself a dictionary of keys/instructions
    ("split" or "extract") and values/compiled regexes (e.g. "/\\s*\\|\\s*/")
    :param url_encoded_col_name_regexes: List of regexes matching columns to URL-decode
    :param batch_size: number of variants to process at a time
    """

    # copy the tab-delimited VCF file to the vcf_lines raw data table
    db.sql(f"""
        COPY
            vcf_lines
        FROM
            '{tab_path}' (DELIMITER '\\t', AUTO_DETECT false);
    """)

    # handle missing values
    db.sql("""
        UPDATE vcf_lines SET id = NULL where id = '.';
        UPDATE vcf_lines SET ref = NULL where ref = '.';
        UPDATE vcf_lines SET alt = NULL where alt = '.';
        UPDATE vcf_lines SET qual = NULL where qual = '.';
        UPDATE vcf_lines SET filters = NULL where filters = '.';
        UPDATE vcf_lines SET info = NULL where info = '.';
        UPDATE vcf_lines SET format = NULL where format = '.';
        UPDATE vcf_lines SET values = NULL where values = '.';
    """)

    # populate the variants table with data from vcf_lines, which has a vid column now
    db.sql("""
        INSERT INTO
            variants (
                vid,
                chrom,
                pos,
                id,
                ref,
                alt,
                qual,
                filters
            )
        SELECT
            concat(chrom, ':', pos, '|', ref, '>', alt),
            chrom,
            pos,
            id,
            ref,
            alt,
            qual,
            str_split(filters, ';')
        FROM
            vcf_lines;
    """)

    # split the variants into evenly sized batches
    n_variants = db.table("vcf_lines").shape[0]
    n_batches = 1 + n_variants // batch_size
    chosen_batch_size = ceil(n_variants / n_batches)

    for i in range(n_batches):
        logging.info(f"Loading batch {i + 1} of {n_batches}")
        offset = i * chosen_batch_size

        # populate the kv table with values and info
        populate_vals(db, val_info_types, limit=chosen_batch_size, offset=offset)
        populate_info(
            db,
            val_info_types,
            compound_info_field_map,
            limit=chosen_batch_size,
            offset=offset,
        )

    # drop temporary tables
    db.sql("DROP TABLE IF EXISTS kv;")
    db.sql("DROP TABLE IF EXISTS kv_compound_info;")
    db.sql("DROP TABLE IF EXISTS vcf_lines;")
    db.unregister("sub_fields")

    # finish creating the vals_info table
    make_constraints(db)
    snake_case_col(db, tbl="vals_info", col="k")

    # URL-decode text from the requested info fields that might appear in v_varchar and
    # v_varchar_arr columns
    urldecode_cols(db, url_encoded_col_name_regexes)


def make_constraints(db: DuckDBPyConnection) -> None:
    """
    Apply constraints to the `vals_info` table by copying from a temporary table into
    one with constraints.

    :param db: DuckDB database connection
    """

    logging.info(f"Applying constraints to vals_info")

    db.sql("""
        INSERT INTO
            vals_info
        BY NAME
        SELECT
            *
        FROM
            vals_info_tmp;
    """)

    db.sql("DROP TABLE vals_info_tmp;")


def snake_case_col(db: DuckDBPyConnection, tbl: str, col: str) -> None:
    """
    Convert values in a camelCased or PascalCased column to snake_case.

    :param db: DuckDB database connection
    :param tbl: Name of table containing the column
    :param col: Name of column to convert to snake case
    """

    # create a map of the distinct values in the column to their snake_case equivalents
    # (there are many repeated values, so this is more efficient than snake_casing the
    # values directly)
    snake_map = db.table(tbl)[col].distinct().df()
    snake_map[f"{col}_snake"] = snake_map[col].apply(snakecase)

    db.register("snake_map", snake_map)

    db.sql(f"""
        UPDATE
            {tbl}
        SET
            {col} = snake_map.{col}_snake
        FROM
            snake_map
        WHERE
            {tbl}.{col} = snake_map.{col};
    """)

    db.unregister("snake_map")


def populate_vals(
    db: DuckDBPyConnection,
    val_info_types: pd.DataFrame,
    limit: int = 0,
    offset: int = 0,
) -> None:
    """
    Populate the kv table with values (non-info fields) from the VCF file.

    :param db: DuckDB database connection
    :param val_info_types: DataFrame containing VCF value and info field types
    :param limit: Number of rows to process
    :param offset: Number of rows to skip
    """

    db.sql("TRUNCATE kv;")

    # parse the format and values columns into key-value pairs and populate the kv table
    db.sql(
        """
        INSERT INTO
            kv (
                vid,
                k,
                v
            )
        SELECT
            vid,
            unnest(str_split(format, ':')) AS k,
            unnest(str_split(values, ':')) AS v
        FROM (
            SELECT
                vid: concat(chrom, ':', pos, '|', ref, '>', alt),
                format,
                values
            FROM
                vcf_lines
            ORDER BY
                chrom,
                pos,
                ref,
                alt
            LIMIT
                $limit
            OFFSET
                $offset
        );
        """,
        params={"limit": limit, "offset": offset},
    )

    # collect the value types observed in the current batch
    val_types = val_info_types.loc[
        val_info_types["kind"].eq("value")
        & val_info_types["id"].isin(db.table("kv")["k"].distinct().df()["k"])
    ].copy()

    # copy the values to the vals_info_tmp table
    cast_and_insert_v(db=db, types_df=val_types, kind="val")


def populate_info(
    db: DuckDBPyConnection,
    val_info_types: pd.DataFrame,
    compound_info_field_map: dict[str, list[dict[str, str]]],
    limit: int = 0,
    offset: int = 0,
) -> None:
    """
    Populate the kv table with values from the VCF file's info fields.

    :param db: DuckDB database connection
    :param val_info_types: DataFrame containing VCF value and info field types
    :param compound_info_field_map: Dictionary of annotation INFO names and steps to
    extract their data, where each step is itself a dictionary of keys/instructions
    ("split" or "extract") and values/compiled regexes (e.g. "/\\s*\\|\\s*/")
    :param limit: Number of rows to process
    :param offset: Number of rows to skip
    """

    db.sql("TRUNCATE kv;")
    db.sql("TRUNCATE kv_compound_info;")

    # collect the info types as a list of field types
    info_types = val_info_types.loc[val_info_types["kind"].eq("info")].copy()
    info_types_ids = info_types["id"].tolist()

    # populate the kv table with info field data
    db.sql(
        """
        INSERT INTO
            kv (
                vid,
                k,
                v
            )
        SELECT
            vid,
            annot[1] AS k,
            annot[2] AS v
        FROM (
            SELECT
                vid,
                str_split(unnest(str_split(info, ';')), '=') AS annot
            FROM (
                SELECT
                    vid: concat(chrom, ':', pos, '|', ref, '>', alt),
                    info
                FROM
                    vcf_lines
                ORDER BY
                    chrom,
                    pos,
                    ref,
                    alt
                LIMIT
                    $limit
                OFFSET
                    $offset
            )
        )
        WHERE
            k IN $info_types_ids;
        """,
        params={"limit": limit, "offset": offset, "info_types_ids": info_types_ids},
    )

    # collect the info types observed in the current batch
    info_types = info_types.loc[
        info_types["id"].isin(db.table("kv")["k"].distinct().df()["k"])
    ].copy()

    # deal with flag/boolean field types
    assign_flags_as_bool(db, info_types)

    # need to treat simple and compound info fields differently
    simple_info_types = info_types.loc[~info_types["has_children"]].copy()
    compound_info_types = info_types.loc[info_types["has_children"]].copy()

    # copy the simple (non-compound) info fields to the vals_info_tmp table
    cast_and_insert_v(db=db, types_df=simple_info_types, kind="info")

    # create a list of the compound info types
    compound_info_types_ids = compound_info_types["id"].tolist()

    # delete the non-compound info fields from the kv table now that we've populated the
    # vals_info_tmp table with them
    db.sql(
        """
        DELETE FROM
            kv
        WHERE
            k NOT IN $compound_info_types_ids;
        """,
        params={"compound_info_types_ids": compound_info_types_ids},
    )

    for cif_id in compound_info_types_ids:
        # start constructing a subquery of CTEs for the provided splitting instructions
        cte_name = f"{cif_id}_base"

        # wee need to keep track of col names used in splitting
        select_col_names = ["vid", "k"]
        split_col_names = []

        # the initial select can be the same for any annotation type
        ctes = [
            f"""
                WITH {cte_name} AS (
                    SELECT
                        {", ".join(select_col_names)},
                        v
                    FROM
                        kv
                    WHERE
                        k='{cif_id}'
                )
            """
        ]

        for i, step in enumerate(compound_info_field_map[cif_id]):
            # get the instruction type and regex
            ((cmd, regex),) = step.items()

            # determine the latest CTE to select from and name the current one
            last_cte_name = cte_name
            cte_name = f"step{i}_{cmd}"

            if cmd == "split":
                # just need any distinct column name to store the ordinals of the
                # splitted values
                split_col_name = f"{cte_name}_ix"

                cte = f"""
                    -- split to an array
                    {cte_name}_to_unnest AS (
                        SELECT
                            {", ".join(select_col_names)},
                            regexp_split_to_array(v, '{regex}') AS v
                        FROM
                            {last_cte_name}
                    ),
                    -- explode the array to rows along with an ordinal for this split
                    {cte_name} AS (
                        SELECT
                            {", ".join(select_col_names)},
                            unnest(v) AS v,
                            generate_subscripts(v, 1) AS {split_col_name}
                        FROM
                            {cte_name}_to_unnest
                    )
                """

                split_col_names.append(split_col_name)
                select_col_names.append(split_col_name)

            elif cmd == "extract":
                # extract the singular value from the current `v`
                cte = f"""
                    {cte_name} AS (
                        SELECT
                            {", ".join(select_col_names)},
                            regexp_extract(v, '{regex}', 1) AS v
                        FROM
                            {last_cte_name}
                    )
                """

            else:
                raise NotImplementedError(
                    f"Unsupported compound info parse command: {cmd}"
                )

            ctes.append(cte)

        # did we split just once (standard) or was there an initial split for
        # multi-valued compound values?
        k_ordinal_ordinal_col_name = split_col_names[0]
        ksub_ordinal_col_name = split_col_names[-1]

        if k_ordinal_ordinal_col_name == ksub_ordinal_col_name:
            # there is only one set of split annotations for this vid+k
            ctes.append(f"""
                {cif_id}_done AS (
                    SELECT
                        vid,
                        k,
                        1 AS k_ix,
                        {ksub_ordinal_col_name} AS ksub_ix,
                        v
                    FROM
                        {cte_name}
                ) 
            """)
        else:
            # there might be many sets of split annotations for this vid+k, so we need
            # to keep k_ix
            ctes.append(f"""
                {cif_id}_done AS (
                    SELECT
                        vid,
                        k,
                        {k_ordinal_ordinal_col_name} AS k_ix,
                        {ksub_ordinal_col_name} AS ksub_ix,
                        v
                    FROM
                        {cte_name}
                ) 
            """)

        # construct the subquery
        subq = ", ".join(ctes)

        # populate the kv_compound_info table (same as kv but with k_sub and ix columns
        # for joining subfield names to values)
        db.sql(f"""
            INSERT INTO
                kv_compound_info (
                    vid,
                    k,
                    k_ix,
                    k_sub,
                    ix,
                    v
                )
            SELECT
               vid,
               k,
               k_ix,
               k_sub,
               ix,
               v
            FROM (
                {subq}
                -- join subfield names using the common ordinal column
                SELECT
                    vid,
                    {cif_id}_done.k,
                    {cif_id}_done.k_ix,
                    sub_fields.k_sub,
                    sub_fields.ix,
                    CASE
                        WHEN
                            v IN ('', '.')
                        THEN
                            NULL
                        ELSE
                            v
                    END AS v
                FROM
                    {cif_id}_done
                INNER JOIN
                    sub_fields
                ON
                    {cif_id}_done.k = sub_fields.k
                    AND
                    {cif_id}_done.ksub_ix = sub_fields.ix
            )
        """)

    # convert the subfield names to snake_case
    snake_case_col(db, tbl="kv_compound_info", col="k_sub")

    db.sql("TRUNCATE kv;")

    # we need to treat JSON and JSON[] type values differently
    compound_info_types_scalar = compound_info_types.loc[
        ~compound_info_types["is_list"]
    ].copy()
    compound_info_types_arr = compound_info_types.loc[
        compound_info_types["is_list"]
    ].copy()

    compound_info_types_scalar_ids = compound_info_types_scalar["id"].tolist()
    compound_info_types_arr_ids = compound_info_types_arr["id"].tolist()

    # populate the kv table with compound_info field data
    db.sql(
        """
        INSERT INTO
            kv (
                vid,
                k,
                v
            )
        SELECT
            vid,
            k,
            v
        FROM (
            WITH compound_info_maps AS (
                -- collect compound info keys and values as string-casted JSON
                SELECT
                    vid,
                    k,
                    k_ix,
                    MAP(
                        list(k_sub ORDER BY ix),
                        list(v ORDER BY ix)
                    )::JSON::VARCHAR AS v
                FROM
                    kv_compound_info
                GROUP BY
                    vid,
                    k,
                    k_ix
            ),
            -- we already have strings to insert into v_json
            compound_info_maps_scalar AS (
                SELECT
                    vid,
                    k,
                    v
                FROM
                    compound_info_maps
                WHERE
                    k IN $compound_info_types_scalar_ids
            ),
            -- aggregate string JSON values into arrays to insert into v_json_arr
            compound_info_maps_arr AS (
                -- 
                SELECT
                    vid,
                    k,
                    '[' || string_agg(v, ',') || ']' AS v
                FROM
                    compound_info_maps
                WHERE
                    k IN $compound_info_types_arr_ids
                GROUP BY
                    vid,
                    k
            )
            SELECT
                vid,
                k,
                v
            FROM
                compound_info_maps_scalar
            UNION
            SELECT
                vid,
                k,
                v
            FROM
                compound_info_maps_arr
        )
        """,
        params={
            "compound_info_types_scalar_ids": compound_info_types_scalar_ids,
            "compound_info_types_arr_ids": compound_info_types_arr_ids,
        },
    )

    db.sql("TRUNCATE kv_compound_info;")

    cast_and_insert_v(db=db, types_df=compound_info_types, kind="info")


def assign_flags_as_bool(db: DuckDBPyConnection, info_types: pd.DataFrame) -> None:
    """
    Flag fields in a VCF are keys without values (i.e. booleans), so populate the `v`
    column manually by assigning the string 'true' for all these records. These are
    converted to BOOL columns later.

    :param db: DuckDB database connection
    :param info_types: DataFrame containing the info field types
    """

    flag_fields_ids = list(
        info_types.loc[
            info_types["kind"].eq("info") & info_types["number"].eq("0"), "id"
        ]
    )

    db.sql(
        """
        UPDATE
            kv
        SET
            v = 'true'
        WHERE
            k in $flag_fields_ids
        """,
        params={"flag_fields_ids": flag_fields_ids},
    )


def cast_and_insert_v(
    db: DuckDBPyConnection, types_df: pd.DataFrame, kind: str
) -> None:
    """
    Cast and insert values into the `vals_info_tmp` table. This effectively converts
    the long `kv` table into a wide table having separate columns for each value type
    (v_boolean, v_varchar, ..., v_boolean_arr, v_varchar_arr, etc.).

    :param db: DuckDB database connection
    :param types_df: DataFrame containing the types of the source table
    :param kind: Kind of values to insert ('val' or 'info')
    """

    # iterate over the types of values to insert:
    # - `v_col_name` is the column to insert into (e.g. `v_varchar`)
    # - `is_list` indicates whether we are inserting into a column like `v_varchar_arr`
    #   and need to split values by commas before inserting
    # - `the_type` is the DuckDB column type (e.g. `VARCHAR`)
    # - `g` is all the val/info types belonging to the above group
    for (v_col_name, is_list, the_type), g in types_df.groupby(
        ["v_col_name", "is_list", "type"]
    ):
        # create a comma-separated list of the `kv.k` values to select and copy
        k_ids = g["id"].tolist()

        if is_list and the_type != "JSON":
            # inserting lists, so we need to split the values by commas first
            db.sql(
                f"""
                INSERT INTO
                    vals_info_tmp (
                        vid,
                        kind,
                        k,
                        {v_col_name}
                    )
                SELECT
                    vid,
                    '{kind}',
                    k,
                    str_split(v, ',') AS {v_col_name}
                FROM
                    kv
                WHERE
                    k IN $k_ids;
                """,
                params={"k_ids": k_ids},
            )
        else:
            # it's not a list or it's a JSON[] column we're inserting into, in which
            # case we've already concatenated the values
            db.sql(
                f"""
                INSERT INTO
                    vals_info_tmp (
                        vid,
                        kind,
                        k,
                        {v_col_name}
                    )
                SELECT
                    vid,
                    '{kind}',
                    k,
                    v
                FROM
                    kv
                WHERE
                    k IN $k_ids;
                """,
                params={"k_ids": k_ids},
            )


def urldecode_cols(
    db: DuckDBPyConnection, url_encoded_col_name_regexes: list[str]
) -> None:
    """
    URL-decode specified columns in the vals_info table:
    1. URL-decodes varchar and varchar_arr columns matching the provided regexes
    2. Only decodes values containing '%' characters (indicating URL encoding)
    3. Logs a warning if other columns appear to contain URL encoded values

    :param db: DuckDB database connection
    :param url_encoded_col_name_regexes: List of regular expressions matching column
    names to URL-decode
    """

    if len(url_encoded_col_name_regexes) == 0:
        logging.info("Not URL-decoding any columns")

        still_encoded = db.sql(
            """
            SELECT
                vid,
                k,
                v_varchar,
                v_varchar_arr
            FROM
                vals_info
            WHERE
                kind = 'info'
                AND (
                    contains(v_varchar, '%')
                    OR
                    contains(v_varchar_arr::VARCHAR, '%')
                )
            ORDER BY
                random()
            """,
        )

    else:
        url_encoded_col_name_regex = "|".join(url_encoded_col_name_regexes)
        logging.info(
            f"URL-decoding info fields matching /{url_encoded_col_name_regex}/"
        )

        db.sql(
            """
            UPDATE
                vals_info
            SET
                v_varchar = url_decode(v_varchar)
            WHERE
                kind = 'info'
                AND
                regexp_matches(k, $url_encoded_col_name_regex)
                AND
                contains(v_varchar, '%')
            """,
            params={"url_encoded_col_name_regex": url_encoded_col_name_regex},
        )

        db.sql(
            """
            UPDATE
                vals_info
            SET
                v_varchar_arr = list_transform(v_varchar_arr, x -> url_decode(x))
            WHERE
                kind = 'info'
                AND
                regexp_matches(k, $url_encoded_col_name_regex)
                AND
                contains(v_varchar_arr::VARCHAR, '%')
            """,
            params={"url_encoded_col_name_regex": url_encoded_col_name_regex},
        )

        still_encoded = db.sql(
            """
            SELECT
                vid,
                k,
                v_varchar,
                v_varchar_arr
            FROM
                vals_info
            WHERE
                kind = 'info'
                AND
                NOT regexp_matches(k, $url_encoded_col_name_regex)
                AND (
                    contains(v_varchar, '%')
                    OR
                    contains(v_varchar_arr::VARCHAR, '%')
                )
            ORDER BY
                random()
            """,
            params={"url_encoded_col_name_regex": url_encoded_col_name_regex},
        )

    if still_encoded.shape[0] > 0:
        still_encoded_k = ", ".join(
            [x[0] for x in still_encoded["k"].distinct().fetchall()]
        )

        logging.warning(
            f"{still_encoded.shape[0]} values for annotations [{still_encoded_k}] "
            f"might need to be URL_decoded:\n{still_encoded}"
        )
