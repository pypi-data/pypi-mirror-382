import os
import pandas as pd
from quantselect.loader import Loader


def load_and_process_data(output_path, filename="pg.matrix.normalized.tsv"):
    """Load and process protein group data from specified output path."""
    # Load selectLFQ data
    filepath = os.path.join(output_path, filename)
    selectlfq_data = pd.read_csv(filepath, sep="\t", index_col=0)

    # Load directLFQ data
    directlfq_data = Loader().load_pg_data(output_path).set_index("pg")
    directlfq_data = directlfq_data[sorted(directlfq_data.columns.unique())]

    return selectlfq_data, directlfq_data


def standardize_column_names(data):
    """Standardize column names by removing prefixes and suffixes."""
    return data.columns.str.split("30min_").str[1].str.split("_180K").str[0]


def extract_species_info(data):
    """Extract species information from protein group indices."""
    return (
        data.index.str.split("_")
        .str[1]
        .str.split(";")
        .str[0]
        .str.replace("ECOBW", "ECOLI")
        .str.replace("ECODH", "ECOLI")
        .values
    )


def align_datasets(selectlfq_data, directlfq_data, directlfq_data_nofilt=None):
    """Align selectLFQ and directLFQ datasets to common proteins."""
    # Standardize column names
    selectlfq_data.columns = standardize_column_names(selectlfq_data)
    directlfq_data.columns = standardize_column_names(directlfq_data)
    if directlfq_data_nofilt is not None:
        directlfq_data_nofilt.columns = standardize_column_names(directlfq_data_nofilt)

    # Find common proteins across all datasets
    common_proteins = set(directlfq_data.index).intersection(set(selectlfq_data.index))
    if directlfq_data_nofilt is not None:
        common_proteins = common_proteins.intersection(set(directlfq_data_nofilt.index))

    # Filter to common proteins and sort
    directlfq_data = directlfq_data[
        directlfq_data.index.isin(common_proteins)
    ].sort_index()
    selectlfq_data = selectlfq_data[
        selectlfq_data.index.isin(common_proteins)
    ].sort_index()
    if directlfq_data_nofilt is not None:
        directlfq_data_nofilt = directlfq_data_nofilt[
            directlfq_data_nofilt.index.isin(common_proteins)
        ].sort_index()

    # Extract species information
    species = extract_species_info(directlfq_data)

    if directlfq_data_nofilt is not None:
        return selectlfq_data, directlfq_data, directlfq_data_nofilt, species
    else:
        return selectlfq_data, directlfq_data, species
