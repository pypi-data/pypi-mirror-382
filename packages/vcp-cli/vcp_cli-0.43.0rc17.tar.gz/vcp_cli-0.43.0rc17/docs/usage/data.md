# Data

## What is the Data CLI Tool?

A command-line interface for searching, exploring metadata, and downloading data registered in the Virtual Cells Platform ("VCP"). This tool allows you to search for data across multiple scientific domains, without needing to write code or scripts.

### Metadata Schemas

Registered data comes with rich metadata to streamline search. Learn about our data schemas including the cross modality schema that specifies the key metadata available for all registered datasets.

```{toctree}
:maxdepth: 1

data_schemas/cross_modality_schema
data_schemas/imaging_metadata_schema
data_schemas/sequencing_schema
data_schemas/mass_spectrometry_schema
```

## Getting Started

### Prerequisites

* Your Virtual Cells Platform account credentials ([register here](https://virtualcellmodels.cziscience.com/?register=true))
* Python version 3.10 or greater
* The [VCP CLI tool](https://pypi.org/project/vcp-cli/). See [Installation](installing) for instructions.

### Authentication

Some CLI commands will require that you have a user account on the Virtual Cells Platform website and that you login to your account using the CLI. If needed, you
can create a new account [in the Virtual Cells Platform website](https://virtualcellmodels.cziscience.com/).

#### Login via Web Browser

To log in to your Virtual Cells Platform account using your browser:

```bash
vcp login
```

Once you log in, you can go back to the command line and continue.

#### Login via the Command Line

To log in to your Virtual Cells Platform account from your terminal, specify the `--username` option:

```bash
vcp login --username your.name@example.org
```

You will be prompted for a password. Use the same one you use on [the
Virtual Cell Models web page](https://virtualcellmodels.cziscience.com).

### Get Help Using the CLI

The `--help` flag provides additional documentation and tips. You can add it to the end of any of the available commands for more information.

For example, to learn what data commands are available for this tool, run:

```bash
vcp data --help
```

You can also get help with learning how to use individual commands by adding it to a command, for example:

```bash
vcp data describe --help
```

## Overview of Data Commands

The CLI has 6 core data commands:

| Command | Description |
| ----- | ----- |
| `vcp data metadata-list`| List available metadata fields for searching datasets. |
| `vcp data summary <FIELD>` | Summarize metadata of matched datasets against a specified metadata field. |
| `vcp data search "<TERM>"` | Query datasets using terms for specific fields. [Lucene style queries](https://lucene.apache.org/core/10_3_0/queryparser/org/apache/lucene/queryparser/classic/package-summary.html#package.description) are supported. |
| `vcp data describe <DATASET_ID>` | View a summary of dataset metadata, including domain, species, tissues, and assets. |
| `vcp data preview <DATASET_ID>` | Generate a Neuroglancer preview URL for a dataset with zarr files. |
| `vcp data download <DATASET_ID>` | Download a dataset by ID to a local directory. |


The CLI also has the following flags that can be used to adjust commands:


| Flag | Purpose |
| ----- | ----- |
| `--download` | Download all datasets returned by the search. |
|`--exact`|    Match term exactly (no partial matches)|
| `--full` | Show detailed metadata for each dataset in the search results as a pretty-printed JSON  |
| `--raw` | Show the raw returned record |
| `--open` |  Automatically open the preview URL for Neuroglancer in your browser |
| `-o`, `--outdir` | Specify a directory for downloads (used with `--download` or `vcp data download`). |
| `-q`, `--query` | Search query to filter datasets. |
| `--help` | Show help message and usage information for the command. |


## Summary of Fields
To return the full list of searchable fields, run

```bash
vcp data metadata-list
```

Below is a table of searchable fields which includes terms from the [cross modality schema](./data_schemas/cross_modality_schema).

| **Field**                          | **Definition**                                                                                                                                                      |
|-----------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **assay**                         | Defines the assay that was used to create the dataset. Human-readable label.                                                                                        |
| **assay_ontology_term_id**        | Defines the assay used to create the dataset. MUST be an Experimental Factor Ontology (EFO) term, e.g., “EFO:0022605”.                                              |
| **tissue**                        | Defines the tissues from which assayed biosamples were derived. Human-readable label.                                                                               |
| **tissue_ontology_term_id**       | Defines the tissues from which assayed biosamples were derived. Allowed ontologies include CL, GO, UBERON, WBbt, ZFA, and FBbt.                                     |
| **tissue_type**                   | One of: 'cell culture', 'cell line', 'organelle', 'organoid', or 'tissue'.                                                                                          |
| **cell_type**                     | Cell Type as defined in this [Cellosaurus](https://www.cellosaurus.org/)                                                                                                         |
| **organism**                      | Defines the organism from which assayed biosamples were derived. Human-readable label.                                                                              |
| **organism_ontology_term_id**     | Defines the organism from which assayed biosamples were derived. MUST be an NCBI organismal classification term, e.g., 'NCBITaxon:9606'.                            |
| **disease**                       | Defines the disease of the patients or organisms from which biosamples were derived. Human-readable label.                                                          |
| **disease_ontology_term_id**      | Defines the disease. MUST be a descendant of 'MONDO:0000001' if disease, or 'PATO:0000461' for normal/healthy.                                                     |
| **development_stage**             | Defines the development stage of the patients or organisms. Human-readable label.                                                                                   |
| **development_stage_ontology_term_id** | Defines the development stage. Use 'na' for cell lines, 'unknown' if unknown, or otherwise an ontology term from an organism-specific ontology.              |
| **name**                          | Curator-provided name for the dataset.                                                                                                                              |
| **tags**                          | List of tags associated with the dataset, including 'namespace:<namespace>' which defines the source of the data.                                                                                        |
| **creator**                       | Stringified list of creators, usually a person (e.g., 'John Doe') or organization (e.g., 'CZI').                                                                    |

For any field, you can return a paginated table of all terms with registered data using vcp data summary <FIELD>. For example, the following returns a list of all tissue types: 

```bash
vcp data summary tissue_type
```

Use the `--query` flag to summarize a field along with a filter according to a specific term. For example, to get the counts of assays that have brain data, use:

```bash
vcp data summary assay --query brain
```


## Example Queries

### Search for Datasets

```bash
vcp data search cryoet
```

This will return an overall count of the datasets with `cryoet` in the dataset name or metadata and a paginated table of those datasets with their associated metadata. To automatically download the datasets returned by search add the flag `--download` to the end of your query.

The CLI supports Lucene-style search, so you can use:

* Field-specific search, like `”tissue:brain”`
* Quotation marks `" "` to group multiword terms and boolean expressions
* AND, OR, NOT boolean operators to combine terms (To use boolean operators with multiwords terms, use double quotation marks (`" "`) around the query and single quotation marks (`' '`) for the multiword expresssions within the query.)
* Wildcard terms with `*` and `?`
* Fuzzy search with `~`

Examples using each type of Lucene query are below.

#### Field-specific Terms

Use `field:value` pairs to search for specific metadata.

```bash
vcp data search "tissue:skeletal"
```

To search for ontology terms, use escape colons with a backslash (`\:`) in place of colons. For example,  

```bash
vcp data search "assay_ontology_term_id:EFO\:0030062"
``` 

#### Multiword Terms

Use double quotations (`" "`) around multiword search terms. 

```bash
vcp data search "cryoet data portal"
```

#### Combine Terms with Boolean Operators

The following returns CellxGene datasets of kidney samples.

```bash
vcp data search "tissue:kidney AND cellxgene"
```

To combine boolean operators with multiword search terms, use double quotes (`" "`) around the query, and single quotes (`' '`) around the multiword search terms. For example, to search for datasets on the [CryoET Data Portal](https://cryoetdataportal.czscience.com/) from the [Chan Zuckerberg Imaging Institute (CZII)](https://www.czimaginginstitute.org/), use:

```bash
vcp data search "'cryoet data portal' AND CZII"
```

#### Wildcard Terms

The `*` symbol can be used as a multicharacter wildcard and the `?` as a single character wildcard on terms within quotation marks. For example, to search for data from any 10x assay, use:

```bash
vcp data search "assay:10x*"
```

To search for cryoET or cryoEM data, you could use:

```bash
vcp data search "cryoe?"
```

#### Fuzzy Search

To do a fuzzy search, use a `~` symbol at the end of a single word term. This type of search accounts for simple typos and formatting differences.

```bash
vcp data search “Hpylori~”
```

### View Dataset Metadata

```bash
vcp data describe 688ab21b2f6b6186d8332644
```
This returns a table with additional metadata beyond what is displayed with the `search` command.

To show comprehensive metadata for a dataset add the flag `--full` to the end of your query, for example:

```bash
vcp data describe 688ab21b2f6b6186d8332644 --full
```

All of the metadata displayed can be used for field specific search, for example:

```bash
vcp data search namespace:cellxgene
```

### Preview an Imaging Zarr Dataset

For Imaging datasets with Zarr files, we support previewing the data in Neuroglancer. Check out this [Neuroglancer quickstart](https://chanzuckerberg.github.io/cryoet-data-portal/stable/neuroglancer_quickstart.html#neuroglancer-quickstart) and [Neuroglancer documentation](https://neuroglancer-docs.web.app/index.html) to familiarize yourself with the tool. 

```bash
vcp data preview 681a6a61200cf05759b5bf91
```
This will return a clickable URL for opening the dataset in Neuroglancer. Use the `--open` flag to automatically open the link in your browser.

```bash
vcp data preview 681a6a61200cf05759b5bf91 --open
```

### Download a Dataset

```bash
vcp data download 688ab21b2f6b6186d8332644
```

This will initiate a download in the current working directory. During the download, a progress bar is displayed along with the full file size in bytes.

You can use the following flags `-o` or `--outdir` followed by a path to a folder to specify the output directory for download. For example, to download a file to your Documents folder, run:

```bash
vcp data download -o ~/Documents 688ab21b2f6b6186d8332644
```
Or

```bash
vcp data download --outdir ~/Documents 688ab21b2f6b6186d8332644
```

#### Download All Datasets Based on Query

To download all datasets that match a query, use `vcp data download --query $QUERY`. For example, to download all CellxGene dataets with kidney samples, use: 

```bash
vcp data download --query "tissue:kidney AND cellxgene"
```

## Tips

* Put multiword terms in quotes: `"stem cell"` not `stem cell`.
* Start simple: Try `vcp data search cellxgene` to get a feel for results.
* Use `--help` often: Every command supports it!

For more information on the available commands and flags, see {ref}`cli-reference`.
