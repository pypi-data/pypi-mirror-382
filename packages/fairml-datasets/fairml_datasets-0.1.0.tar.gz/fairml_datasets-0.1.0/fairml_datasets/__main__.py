"""
Command-line interface module for the fairml_datasets package.

This module provides a CLI for common operations on fairness datasets, including:
- Generating and exporting metadata
- Exporting datasets in various processing stages
- Exporting dataset citations in .bib format
"""

import json
import traceback
import click
import logging
from pathlib import Path

import pandas as pd
from fairml_datasets.processing import annotations
from fairml_datasets import Datasets
from rich.progress import Progress


ANNOTATIONS_PREFIX = "ann_"

logger = logging.getLogger(__name__)


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging.")
def cli(debug):
    """Command-line interface for the fairml datasets package."""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.command()
@click.option(
    "-f",
    "--file",
    default="fairml_datasets/data/final/datasets_meta.csv",
    help="Which file to write the metadata to, the ending will determine the format (csv and json supported).",
)
@click.option(
    "--id",
    default=None,
    help="Generate metadata for only a single dataset.",
)
@click.option(
    "--inclue-large-datasets",
    is_flag=True,
    help="Include large datasets in the metadata generation (only used if descriptives are computed).",
)
@click.option(
    "--type",
    default="descriptives",
    type=click.Choice(["annotations", "descriptives", "all"]),
    help="Type of metadata to generate (annotations, descriptives, or both).",
)
def metadata(file, id, inclue_large_datasets, type):
    """
    Generate and save metadata for the datasets.
    """
    # Prepare filepath
    target_file = Path(file)
    target_dir = target_file.parent
    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)

    # Load annotations
    annotations_df = annotations.load()
    annotations_df_prep = annotations_df.reset_index().add_prefix(ANNOTATIONS_PREFIX)

    # Generate metadata based on type
    if type == "annotations":
        # Just use the annotations as metadata
        df_meta = annotations_df_prep
    elif type == "descriptives":
        # Generate descriptive metadata based on contents of datasets
        datasets = Datasets(
            df_info=annotations_df, inclue_large_datasets=inclue_large_datasets
        )

        if id:
            try:
                dataset = datasets[id]
                df_meta = pd.DataFrame.from_records(data=[dataset.generate_metadata()])
            except KeyError:
                logger.error(f"No dataset found with id '{id}'")
                return
        else:
            df_meta = datasets.generate_metadata()
    elif type == "all":
        # Generate both and merge them
        # First get descriptives
        datasets = Datasets(
            df_info=annotations_df, inclue_large_datasets=inclue_large_datasets
        )

        if id:
            try:
                dataset = datasets[id]
                descriptives = pd.DataFrame.from_records(
                    data=[dataset.generate_metadata()]
                )
            except KeyError:
                logger.error(f"No dataset found with id '{id}'")
                return
        else:
            descriptives = datasets.generate_metadata()

        # Join the two dataframes on dataset ID
        df_meta = pd.merge(
            descriptives,
            annotations_df_prep,
            left_on="id",
            right_on=ANNOTATIONS_PREFIX + "new_dataset_id",
            how="left",
        )

    # Save metadata
    logger.info(f"Writing {type} metadata to {target_file}")
    file_format = target_file.suffix.lower()
    if file_format == ".csv":
        df_meta.to_csv(target_file, index=False)
    elif file_format == ".json":
        df_meta.to_json(target_file, orient="records", indent=2)
    else:
        raise ValueError(f"Unsupported file format: {file_format}")


@cli.command()
@click.option(
    "-s",
    "--stage",
    default="prepared",
    type=click.Choice(
        ["downloaded", "loaded", "prepared", "binarized", "transformed", "split"]
    ),
    help="At which stage of processing to export the data.",
)
@click.option(
    "--id",
    default=None,
    help="Export only a single dataset.",
)
@click.option(
    "--inclue-large-datasets",
    is_flag=True,
    help="Include large datasets in the export.",
)
@click.option(
    "--include-usage-info",
    is_flag=True,
    help="Whether to also export information regarding the role of different columns e.g. which ones are features, sensitive and target.",
)
def export_datasets(stage, id, inclue_large_datasets, include_usage_info):
    """
    Export datasets as files.
    """
    target_dir = Path("./export")
    if target_dir.exists():
        logger.warning(f"Target directory '{target_dir}' already exists")
    target_dir.mkdir(exist_ok=True)

    datasets = Datasets(inclue_large_datasets=inclue_large_datasets)

    # Filter datasets if id is provided
    if id:
        datasets = [datasets[id]]

    with Progress() as progress:
        task = progress.add_task("Exporting datasets", total=len(datasets))

        # Export datasets one by one
        for dataset in datasets:
            progress.update(task, description=f"Exporting {dataset.dataset_id}")
            try:
                sensitive_cols = dataset.sensitive_columns
                if stage in ["downloaded", "loaded", "prepared", "binarized"]:
                    df = dataset.load(stage)
                elif stage in ["binarized", "transformed", "split"]:
                    df = dataset.load("prepared")
                    df, info = (
                        dataset.binarize(df=df)
                        if stage == "binarized"
                        else dataset.transform(df=df)
                    )
                    # Overwrite sensitive cols (as they may change during transformation)
                    sensitive_cols = info.sensitive_columns
                if stage == "split":
                    train, test, val = dataset.train_test_val_split(df)
                    df = None  # Reset df so nothing will be exported on top

                    train.to_csv(
                        target_dir / f"{dataset.dataset_id}--train.csv", index=False
                    )
                    test.to_csv(
                        target_dir / f"{dataset.dataset_id}--test.csv", index=False
                    )
                    val.to_csv(
                        target_dir / f"{dataset.dataset_id}--val.csv", index=False
                    )
                    logger.info(
                        f"Written files to {[target_dir / f'{dataset.dataset_id}--{suffix}.csv' for suffix in ['X', 'y', 's']]}"
                    )

                # Export file
                if "df" in locals() and df is not None:
                    filepath = target_dir / f"{dataset.dataset_id}.csv"
                    df.to_csv(filepath, index=False)
                    logger.info(f"Written file to {filepath}")

                # Export information on which roles columns have
                if include_usage_info:
                    column_roles = {
                        "features": dataset.get_feature_columns(df=df),
                        "target": dataset.get_target_column(),
                        "sensitive": sensitive_cols,
                    }
                    usage_filepath = target_dir / f"{dataset.dataset_id}--usage.json"
                    with open(usage_filepath, "w") as fp:
                        json.dumps(column_roles, fp, indent=2)

            except Exception as e:
                logger.error(
                    f"Export error in {dataset.dataset_id} ({e.__class__.__name__}): {e}"
                )
                logger.debug(traceback.format_exc())
            progress.advance(task)


@cli.command()
@click.option(
    "-o",
    "--output",
    default="dataset_citations.bib",
    help="Output file for the citations in .bib format.",
)
@click.option(
    "--ids",
    default=None,
    help="Comma-separated list of dataset IDs to export citations for. If not provided, exports citations for all datasets.",
)
def export_citations(output, ids):
    """
    Export dataset citations as a .bib file.

    This command collects all citations from either all datasets or the specified datasets
    and exports them to a .bib file, ensuring duplicate citations are only included once.
    """
    # Prepare output file path
    output_path = Path(output)
    if not output_path.suffix:
        output_path = output_path.with_suffix(".bib")

    # Create parent directories if they don't exist
    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load datasets
    datasets = Datasets()

    # Process dataset IDs if provided
    selected_datasets = datasets
    if ids:
        dataset_ids = [id.strip() for id in ids.split(",")]
        selected_datasets = [datasets[id] for id in dataset_ids if id in datasets]
        if not selected_datasets:
            logger.error("No valid dataset IDs provided")
            return

    # Collect citations
    citations = {}
    with Progress() as progress:
        task = progress.add_task("Collecting citations", total=len(selected_datasets))

        for dataset in selected_datasets:
            progress.update(task, description=f"Processing {dataset.dataset_id}")
            try:
                citation_text = dataset.citation()
                if citation_text:
                    # Add citation to the collection, using citation key as unique identifier
                    citation_text = citation_text.strip()
                    if citation_text:
                        # Simple extraction of citation key from BibTeX
                        lines = citation_text.split("\n")
                        if lines and "@" in lines[0]:
                            key_part = lines[0].split("{", 1)
                            if len(key_part) > 1:
                                citation_key = key_part[1].split(",")[0]
                                citations[citation_key] = citation_text
            except Exception as e:
                logger.error(f"Error getting citations for {dataset.dataset_id}: {e}")

            progress.advance(task)

    # Write citations to file
    if citations:
        with open(output_path, "w") as f:
            for citation in citations.values():
                f.write(citation + "\n\n")

        logger.info(f"Exported {len(citations)} unique citations to {output_path}")
    else:
        logger.warning("No citations found to export")


if __name__ == "__main__":
    cli()
