import json
import logging
import sys
from pathlib import Path
from typing import Annotated

import pandas as pd
import typer

import vcf_to_duckdb.convert_utils

pd.set_option("display.max_columns", 30)
pd.set_option("display.max_colwidth", 50)
pd.set_option("display.max_info_columns", 30)
pd.set_option("display.max_info_rows", 20)
pd.set_option("display.max_rows", 20)
pd.set_option("display.max_seq_items", None)
pd.set_option("display.width", 200)
pd.set_option("expand_frame_repr", True)
pd.set_option("mode.chained_assignment", "warn")

app = typer.Typer()


# noinspection PyUnusedLocal
def done(*args, **kwargs):
    logging.info("Done.")


def set_up_gcp_friendly_logging(level: int = logging.INFO) -> None:
    """
    Configure logging so that logs are routed to stdout/stderr based on severity,
    for compatibility with Google Cloud Logging, and are prepended by timestamps.

    :param level: log level to set
    """

    logger = logging.getLogger()
    logger.setLevel(level)
    logger.handlers.clear()

    # formatter for all log levels
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    # handler for DEBUG and INFO → stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(lambda x: x.levelno < logging.WARNING)
    stdout_handler.setFormatter(formatter)

    # handler for WARNING and above → stderr
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(formatter)

    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)


@app.callback(result_callback=done)
def main():
    set_up_gcp_friendly_logging()


@app.command()
def convert(
    vcf: Annotated[Path, typer.Option(exists=True)],
    db: Annotated[Path, typer.Option()],
    parquet_dir: Annotated[Path, typer.Option()],
    multiallelics: Annotated[bool, typer.Option()] = True,
    config: Annotated[Path | None, typer.Option()] = None,
    tab: Annotated[Path | None, typer.Option()] = None,
    db_tmp_dir_path: Annotated[Path, typer.Option()] = Path("/tmp/duckdb"),
    batch_size: Annotated[int | None, typer.Option()] = 100000,
) -> None:
    compound_info_field_map = {}
    url_encoded_col_name_regexes = []

    if config is not None:
        with open(config, "r") as f:
            config_data = json.load(f)
            compound_info_field_map = config_data["compound_info_field_map"]
            url_encoded_col_name_regexes = config_data["url_encoded_col_name_regexes"]

    vcf_to_duckdb.convert_utils.convert(
        vcf_path=vcf,
        db_path=db,
        parquet_dir_path=parquet_dir,
        db_tmp_dir_path=db_tmp_dir_path,
        multiallelics=multiallelics,
        compound_info_field_map=compound_info_field_map,
        url_encoded_col_name_regexes=url_encoded_col_name_regexes,
        tab_path=tab,
        batch_size=batch_size,
    )


@app.command()
def merge(
    db: Annotated[list[Path], typer.Option(exists=True)],
    parquet_dir: Annotated[Path, typer.Option()],
) -> None:
    vcf_to_duckdb.merge_utils.merge_dbs(db_paths=db, parquet_dir_path=parquet_dir)


if __name__ == "__main__":
    app()
