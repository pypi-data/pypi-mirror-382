import hashlib
import logging
import shutil
from pathlib import Path

import duckdb


def merge_dbs(db_paths: list[Path], parquet_dir_path: Path) -> None:
    """
    Merge the databases created by a split/scattered VCF-to-DuckDB conversion.

    :param db_paths: Path to output DuckDB database folders
    :param parquet_dir_path: Directory to output Parquet files
    """

    logging.info(f"Merging {len(db_paths)} databases")

    parquet_dir_path.mkdir(parents=True, exist_ok=True)

    logging.info("Checking file hashes of files that are identical between shards")

    reference = db_paths[0]  # choose first shard
    identical_files = ["schema.sql", "load.sql", "val_info_types.parquet"]

    def file_hash(path: Path) -> str:
        """
        Compute a SHA256 checksum of a file's contents.

        :param path: Path to the file to hash.
        :returns: Hexadecimal SHA256 digest of the file.
        """

        h = hashlib.sha256()

        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)

        return h.hexdigest()

    ref_hashes = {fname: file_hash(reference / fname) for fname in identical_files}

    for db_path in db_paths[1:]:
        for fname in identical_files:
            if file_hash(db_path / fname) != ref_hashes[fname]:
                raise ValueError(f"File {fname} differs across shards: {db_path}")

    # copy the verified identical files from the first shard
    for fname in identical_files:
        _ = shutil.copy2(reference / fname, parquet_dir_path / fname)

    def concat_parquets(table_name: str) -> None:
        """
        Concatenate identically structured Parquet files from all shards using DuckDB
        streaming.

        :param table_name: Base name of the table (without extension).
        """

        logging.info(f"Concatenating {table_name} parquet files")

        parquet_files = [str(p / f"{table_name}.parquet") for p in db_paths]

        for f in parquet_files:
            if not Path(f).exists():
                raise FileNotFoundError(f"Missing {f}")

        out_path = parquet_dir_path / f"{table_name}.parquet"

        with duckdb.connect() as db:
            db.sql("SET enable_progress_bar = false;")
            db.execute(
                f"""
                COPY (
                    SELECT * FROM read_parquet({parquet_files})
                ) TO '{out_path}' (FORMAT 'parquet');
                """
            )

    concat_parquets("variants")
    concat_parquets("vals_info")
