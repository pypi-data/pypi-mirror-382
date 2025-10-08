vcf-to-duckdb
---

This is a Python package to convert a VCF (Variant Call Format) file to a DuckDB database (exported as Parquet files and accompanying SQL schema). 

## Features

- Processes large VCF files efficiently using multithreaded batch processing.
- Infers data types from VCF headers.
- Parses and separates data in compound INFO fields (e.g. from VEP, SnpEFF, etc.).
- URL-decodes specified fields and detects fields still needing decoding.

## Installation

1. Install the required system dependencies:
    - [pyenv](https://github.com/pyenv/pyenv)
    - [Poetry](https://python-poetry.org/)
    - [bcftools](https://samtools.github.io/bcftools/bcftools.html)

2. Install the required Python version (developed with 3.12.3, but other 3.12+ versions should work):
   ```shell
   pyenv install "$(cat .python-version)"
   ```

3. Confirm that `python` maps to the correct version:
   ```
   python --version
   ```

4. Set the Poetry interpreter and install the Python dependencies:
   ```shell
   poetry env use "$(pyenv which python)"
   poetry install
   ```

A `requirements.txt` file is also available and kept in sync with Poetry dependencies in case you don't want to use Poetry, or you can use vcf-to-duckdb via docker: `docker pull dmccabe606/vcf-to-duckdb:latest`.

## Usage

```python
from pathlib import Path
from vcf_to_duckdb.convert_utils import convert

convert(
    vcf_path=Path("input.vcf.gz"),
    tab_path=Path("tmp.tsv"),
    db_path=Path("tmp.db"),
    parquet_dir_path=Path("output_parquet"),
    multiallelics=False,
    compound_info_field_map={
        "ANN": [{"split": "\\s*\\|\\s*"}],
        "CSQ": [{"split": "\\s*\\|\\s*"}],
        "LOF": [
            {"split": ","},
            {"extract": "^\\((.+)\\)$"},
            {"split": "\\s*\\|\\s*"},
        ],
        "NMD": [
            {"split": ","},
            {"extract": "^\\((.+)\\)$"},
            {"split": "\\s*\\|\\s*"},
        ],
    },
    url_encoded_col_name_regexes=[
        "^civic_desc$",
        "^clndn$",
        "^clnvi$",
        "^oc_",
        "^oncokb_muteff$",
        "^oncokb_oncogenic$",
        "^hgnc",
    ],
)
```

Or using the CLI and the provided example `config.json`:

```shell
python -m vcf_to_duckdb convert \
    --vcf="input.vcf.gz" \
    --tab="tmp.tsv" \
    --db="tmp.duckdb" \
    --parquet-dir="output_parquet" \
    --no-multiallelics \
    --config="config.json"
```

## Database Schema

The resulting DuckDB database (and exported Parquet files) have the following schema:

```sql
-- value and info metadata (a structured form of the VCF header)
CREATE TABLE val_info_types (
    id VARCHAR,
    number VARCHAR,
    "type" VARCHAR,
    description VARCHAR,
    kind VARCHAR,
    has_children BOOLEAN,
    parent_id VARCHAR,
    ix UBIGINT,
    col_def VARCHAR,
    is_list BOOLEAN,
    v_col_name VARCHAR,
    id_snake VARCHAR
);

-- variants and their top-level fields
CREATE TABLE variants (
    vid UINTEGER PRIMARY KEY,
    chrom VARCHAR NOT NULL,
    pos UINTEGER NOT NULL,
    id VARCHAR,
    "ref" VARCHAR,
    alt VARCHAR,
    qual VARCHAR,
    filters VARCHAR[]
);

-- the variants' values and info field data
CREATE TABLE vals_info (
    vid UINTEGER,
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
    v_json_arr JSON[],
    FOREIGN KEY (vid) REFERENCES variants (vid)
);
```

Both values (i.e. data specified by the `FORMAT` column in the VCF) and INFO fields (e.g. annotations) are loaded into `vals_info`, where `k` is the key/name of the value and the value is present in exactly one of the `v_*` columns (depending on its type). Essentially, the schema treats the data in the VCF file as a typed key-value store.  

## Typing

The converter automatically maps VCF data types to appropriate DuckDB types:

- Integer → `INTEGER`
- Float → `FLOAT`
- String → `VARCHAR`
- Character → `VARCHAR`
- Flag → `BOOLEAN`

To handle fields that the header indicates contain multiple values (i.e. `Number=.`), these values are stored in columns like `v_varchar_arr` instead of `v_varchar`.

INFO fields identified as pipe-delimited compound fields via the `compound-info-field` argument are stored as `JSON` columns. The keys of the objects are identified by parsing the field's description in the header, e.g.

```
##INFO=<ID=LOF,Number=.,Type=String,Description="Predicted loss of function effects for this variant. Format: 'Gene_Name | Gene_ID | Number_of_transcripts_in_gene | Percent_of_transcripts_affected'">
```

will result in data like 

```json5
[
  {
    "gene_name": "PTEN",
    "gene_id": "123",
    // etc.
  },
  // etc.
]
```

being loaded into a row's `v_json_arr` column.

## Querying

The schema above was inspired by ELT data warehouses, and was thus designed to be universal and be able to store data from any VCF file, as opposed to a more explicit "wide" schema where values and INFO field data are populated directly into columns. This makes creating the database fast and reliable, but defers the responsibility of understanding and extracting the data to downstream tools.

So, after creating the database, it might be helpful to use CTEs and database views to make querying easier. For instance, to simulate a wide table containing variants' top-level values (defined in the `FORMAT` column of the VCF), one could define these views:

```python
import duckdb

with duckdb.connect("tmp.duckdb") as db:
    db.sql("IMPORT DATABASE './output_parquet'")

    # separate `vals_info` into views for values and INFO
    db.sql("""
        CREATE OR REPLACE VIEW vals AS (
            SELECT
                *
            FROM
                vals_info
            WHERE
                kind = 'val'
        )
    """)
    
    db.sql("""
        CREATE OR REPLACE VIEW info AS (
            SELECT
                *
            FROM
                vals_info
            WHERE
                kind = 'info'
        )
    """)
    
    # make a wide view for all top-level values
    db.sql("""
        CREATE OR REPLACE VIEW vals_wide AS (
            SELECT
                DISTINCT vals.vid,
                t_ad.ad[1] AS ref_count,
                t_ad.ad[2] AS alt_count,
                t_af.af,
                t_dp.dp,
                t_gt.gt,
                t_ps.ps
            FROM
                vals
    
            LEFT OUTER JOIN (
                SELECT
                    vid,
                    v_integer_arr AS ad
                FROM
                    vals
                WHERE
                    k = 'ad'
            ) t_ad ON vals.vid = t_ad.vid
    
            LEFT OUTER JOIN (
                SELECT
                    vid,
                    v_float AS af
                FROM
                    vals
                WHERE
                    k = 'af'
            ) t_af ON vals.vid = t_af.vid
    
            LEFT OUTER JOIN (
                SELECT
                    vid,
                    v_integer AS dp
                FROM
                    vals
                WHERE
                    k = 'dp'
            ) t_dp ON vals.vid = t_dp.vid
    
            LEFT OUTER JOIN (
                SELECT
                    vid,
                    v_varchar AS gt
                FROM
                    vals
                WHERE
                    k = 'gt'
            ) t_gt ON vals.vid = t_gt.vid
    
            LEFT OUTER JOIN (
                SELECT
                    vid,
                    v_integer AS ps
                FROM
                    vals
                WHERE
                    k = 'ps'
            ) t_ps ON vals.vid = t_ps.vid
        )
    """)
```

## Limitations

- No test suite (yet)
- This isn't tested on VCFs containing structural variants and is unlikely to work as expected.
- The JSON objects used to store compound info fields use strings for all values, since the VCF header contains no information about these types. Tools like VEP arguably abuse the [VCF spec](https://samtools.github.io/hts-specs/VCFv4.2.pdf) by storing data like `foo|14.1|bar` in single fields, but there's nothing we can do about this.
- This package doesn't currently handle multi-allelic fields, so it's recommended to pre-process the VCF with `bcftools norm --multiallelics=-` and supply the `--no-multiallelics` argument here.
- Which column (`v_boolean`, `v_varchar_arr`, etc.) each kind of data is stored in is determined by what's in the VCF header, which might not be reliable.
