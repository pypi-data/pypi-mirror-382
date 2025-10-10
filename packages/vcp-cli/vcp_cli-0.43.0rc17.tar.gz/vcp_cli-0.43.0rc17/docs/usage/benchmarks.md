# Benchmarks

The VCP CLI provides commands to utilize the capabilities of the [Virtual Cells Platform](https://virtualcellmodels.cziscience.com/)

## Overview

Benchmarking in VCP allows comparison of different models across various tasks and datasets. The benchmarking system consists of three main components:

- **Models**: Pre-trained machine learning models (e.g., scVI, TRANSCRIPTFORMER)
- **Datasets**: Single-cell datasets for evaluation (e.g., Tabula Sapiens datasets)
- **Tasks**: Specific evaluation tasks (e.g., clustering, embedding, label prediction)

The Datasets and Task implementations are provided by the [cz-benchmarks](https://chanzuckerberg.github.io/cz-benchmarks/) package.

## Commands

### vcp benchmarks list

Lists the benchmarks that have been computed by and published on the [Virtual Cells Platform](https://virtualcellmodels.cziscience.com/benchmarks).
This output provides the combinations of datasets, models, and tasks for which benchmarks were computed.
See [`vcp benchmarks get`](#vcp-benchmarks-get) below for how to retrieve the benchmark metric results for specific benchmarks.

#### Basic Usage
```bash
vcp benchmarks list
```

See [Output Fields](#output-fields) for a description of the output fields.

#### Options

| Option | Short | Description | Example |
|--------|--------|-------------|---------|
| `--benchmark-key` | `-b` | Filter by specific benchmark key | `-b f47892309c571cdf` |
| `--model-filter` | `-m` | Filter by model key pattern | `-m "scvi*"` |
| `--dataset-filter` | `-d` | Filter by dataset key pattern | `-d "tsv2*blood"` |
| `--task-filter` | `-t` | Filter by task key pattern | `-t "embed*"` |
| `--format` | `-f` | Output format (table or json) | `-f json` |

* A benchmark key is a unique identifier that combines a specific model, dataset, and task. For example, `f47892309c571cdf` represents a specific combination of TRANSCRIPTFORMER model, tsv2_blood dataset, and embedding task. It is returned in results when using the filter options and can be used to identify a specific benchmark when using the `vcp benchmarks get` and `vcp benchmarks list` commands.

The filter options allow use of `*` as a wildcard. Filters use substring matching and are case-insensitive. Filter values match across both the name and key of a given entity type (model, dataset, entity).


#### Examples

**List all available benchmarks:**
```bash
vcp benchmarks list
```

**Filter by dataset, model, and task with table output:**
```bash
vcp benchmarks list -d tsv2_blood -m TRANSCRIPT -t embedding
```

**Find specific benchmark by key:**
```bash
vcp benchmarks list -b f47892309c571cdf
```

**Search for scVI models on any dataset with JSON output:**
```bash
vcp benchmarks list -m "scvi*" -f json
```

### vcp benchmarks run

Executes a benchmark task and generates performance metrics using a specific model and dataset.

#### Basic Usage

To reproduce a benchmark published on the Virtual Cells Platform:
```bash
vcp benchmarks run -m MODEL_KEY -d DATASET_KEY -t TASK_KEY
```

#### Options

| Option | Short | Description | Example |
|--------|--------|-------------|---------|
| `--benchmark-key` | `-b` | Use predefined benchmark combination | `-b f47892309c571cdf` |
| `--model-key` | `-m` | Specify model from registry | `-m SCVI-v1-homo_sapiens` |
| `--dataset-key` | `-d` | Specify dataset from registry | `-d tsv2_blood` |
| `--task-key` | `-t` | Specify benchmark task | `-t clustering` |
| `--user-dataset` | `-u` | Use custom dataset file | See user dataset section |
| `--cell-representation` | `-c` | Use precomputed embeddings | `-c embeddings.npy` |
| `--baseline-args` | `-l` | Parameters for baseline computation | `-l '{}'` |
| `--random-seed` | `-r` | Set random seed for reproducibility | `-r 42` |
| `--no-cache` | `-n` | Disable caching, run from scratch | `-n` |

#### Task-Specific Options

**Embedding Task:**
| Option | Description | Example |
|--------|-------------|---------|
| `--labels` | Cell type labels column (also supports '@obs:column' format) | `--labels cell_type` |

**Clustering Task:**
| Option | Description | Example |
|--------|-------------|---------|
| `--labels` | Cell type labels column (also supports '@obs:column' format) | `--labels cell_type` |
| `--use-rep` | Representation to use for clustering (default: 'X') | `--use-rep X` |
| `--n-iterations` | Number of Leiden algorithm iterations (default: 2) | `--n-iterations 3` |
| `--flavor` | Leiden algorithm flavor: 'leidenalg' or 'igraph' (default: 'igraph') | `--flavor igraph` |
| `--key-added` | Key for storing cluster assignments (default: 'leiden') | `--key-added my_clusters` |

**Label Prediction Task:**
| Option | Description | Example |
|--------|-------------|---------|
| `--labels` | Cell type labels column (also supports '@obs:column' format) | `--labels cell_type` |
| `--n-folds` | Number of cross-validation folds (default: 5) | `--n-folds 3` |
| `--min-class-size` | Minimum samples per class for inclusion (default: 10) | `--min-class-size 5` |

**Batch Integration Task:**
| Option | Description | Example |
|--------|-------------|---------|
| `--labels` | Cell type labels column (also supports '@obs:column' format) | `--labels cell_type` |
| `--batch-column` | Batch information column (default: 'batch') | `--batch-column batch_id` |

**Cross-Species Integration Task:**
| Option | Description | Example |
|--------|-------------|---------|
| `--organisms` | Organism specification for cross-species (format: `name:prefix`; see [supported values](https://github.com/chanzuckerberg/cz-benchmarks/blob/76712bc768cac6c65d4bdbfc02203da74ac405a9/src/czbenchmarks/datasets/types.py#L6)) | `--organisms homo_sapiens:ENSG` |
| `--cross-species-labels` | Cell type labels column for each dataset in cross-species tasks | `--cross-species-labels "@0:obs:cell_type"` |

#### Examples

**Run benchmark using a VCP benchmark key:**
```bash
vcp benchmarks run -b 40e2c4837bf36ae1
```

**Embedding task with custom labels:**
```bash
vcp benchmarks run -m SCVI-v1-homo_sapiens -d tsv2_blood -t embedding --labels cell_type -r 42 -n
```

**Clustering task with advanced options:**
```bash
vcp benchmarks run -m SCVI-v1-homo_sapiens -d tsv2_blood -t clustering \
  --labels cell_type --use-rep X --n-iterations 3 --flavor igraph --key-added my_clusters -r 42 -n
```

**Label prediction with cross-validation settings:**
```bash
vcp benchmarks run -m SCVI-v1-homo_sapiens -d tsv2_blood -t label_prediction \
  --labels cell_type --n-folds 3 --min-class-size 5 -r 42 -n
```

**Batch integration with custom batch column:**
```bash
vcp benchmarks run -m SCVI-v1-homo_sapiens -d tsv2_blood -t batch_integration \
  --batch-column batch_id --labels cell_type -r 42 -n
```

**Cross-species integration:**
```bash
  vcp benchmarks run -t cross-species_integration -m UCE-v1-4l \
    -d mouse_spermatogenesis --organisms mus_musculus:ENSMUSG --cross-species-labels "@0:obs:cell_type"  \
    -d rhesus_macaque_spermatogenesis  --organisms macaca_mulatta:ENSMMUG --cross-species-labels "@1:obs:cell_type" \
    -r 42 -n
```

**Use precomputed cell representations with reference format:**
```bash
vcp benchmarks run -c './user_model_output.npy' \
  -u '{"dataset_class": "czbenchmarks.datasets.SingleCellLabeledDataset", "organism": "HUMAN", "path": "~/user_dataset.h5ad"}' \
  -t label_prediction --labels @obs:cell_type --n-folds 5 --min-class-size 10 -r 100 -n
```

#### User Dataset Format
When using `--user-dataset`, provide a JSON string with the following keys:
- `dataset_class`: The dataset class to use (typically `czbenchmarks.datasets.SingleCellLabeledDataset`)
- `organism`: The organism type (`HUMAN`, `MOUSE`, etc.)
- `path`: Path to the .h5ad file

Example:
```json
{
  "dataset_class": "czbenchmarks.datasets.SingleCellLabeledDataset",
  "organism": "HUMAN",
  "path": "~/mydata.h5ad"
}
```

#### Task Arguments and Reference Format

Task-specific arguments can be provided via command-line options or through the `--baseline-args` JSON parameter. The `--labels` option supports both direct column names and AnnData reference format:

**Direct format:** `--labels cell_type`
**Reference format:** `--labels @obs:cell_type`

**For embedding tasks:**
```bash
# Command-line options (recommended)
--labels cell_type

# Via baseline-args
--baseline-args '{"input_labels": "@obs:cell_type"}'
```

**For clustering tasks:**
```bash
# Command-line options (recommended)
--labels cell_type --use-rep X --n-iterations 2 --flavor igraph --key-added leiden

# Via baseline-args
--baseline-args '{"obs": "@obs", "input_labels": "@obs:cell_type", "use_rep": "X", "n_iterations": 2, "flavor": "igraph", "key_added": "leiden"}'
```

**For label prediction tasks:**
```bash
# Command-line options (recommended)
--labels cell_type --n-folds 5 --min-class-size 10

# Via baseline-args
--baseline-args '{"labels": "@obs:cell_type", "n_folds": 5, "min_class_size": 10}'
```

**For batch integration tasks:**
```bash
# Command-line options (recommended)
--batch-column batch --labels cell_type

# Via baseline-args
--baseline-args '{"batch_labels": "@obs:batch", "labels": "@obs:cell_type"}'
```

**For cross-species integration tasks:**
```bash
# Command-line options (recommended)
--cross-species-organisms homo_sapiens:ENSG --cross-species-organisms mus_musculus:ENSMUSG
--cross-species-labels "@0:obs:cell_type" --cross-species-labels "@1:obs:cell_type"

# Via baseline-args
--baseline-args '{"organism_list": [["homo_sapiens", "ENSG"], ["mus_musculus", "ENSMUSG"]], "labels": ["@0:obs:cell_type", "@1:obs:cell_type"]}'
```

### vcp benchmarks get

Retrieves and displays benchmark results that have been computed by and published by either the the Virtual Cells Platform or computed locally by the user using the `vcp benchmarks run` command.
If filters match benchmarks from both the VCP and a user's locally run benchmarks, all of the matching benchmarks will be output together. This supports comparison of user benchmarks against VCP benchmarks.

#### Basic Usage
```bash
vcp benchmarks get
```

See [Output Fields](#output-fields) for a description of the output fields.

#### Options

| Option | Short | Description | Example |
|--------|--------|-------------|---------|
| `--benchmark-key` | `-b` | Filter by benchmark key pattern | `-b "scvi*v1-tsv2*liver"` |
| `--model-filter` | `-m` | Filter by model key pattern | `-m "scvi*"` |
| `--dataset-filter` | `-d` | Filter by dataset key pattern | `-d "tsv2*liver"` |
| `--task-filter` | `-t` | Filter by task key pattern | `-t "label*pred"` |
| `--format` | `-f` | Output format (table or json) | `-f json` |

The filter options allow use of `*` as a wildcard. Filters use substring matching and are case-insensitive. Filter values match across both the name and key of a given entity type (model, dataset, entity).

#### Examples

**Get all available results:**
```bash
vcp benchmarks get
```

**Filter results by model and dataset:**
```bash
vcp benchmarks get -m test -d tsv2_blood
```

**Get results for specific benchmark:**
```bash
vcp benchmarks get -b f47892309c571cdf
```

**Filter by task and model with JSON output:**
```bash
vcp benchmarks get -m scvi -d tsv2_blood -t clustering -f json
```

## Output Fields

The `vcp benchmarks get` and `vcp benchmarks list` commands output the following attributes:

- **Benchmark Key**: Unique identifier for the benchmark
- **Model Key/Name**: Model identifier and display name
- **Dataset Keys/Names**: Dataset identifier and display name
- **Task Key/Name**: Task identifier and display name
- **Metric**: Metric name (for `get` results only).
- **Value**: Metric value (for `get` results only)

For further details about the supported Tasks and Metrics see the [cz-benchmarks Tasks documentation](https://chanzuckerberg.github.io/cz-benchmarks/assets.html#task-details).

## Advanced Usage Patterns

### Reproducible Experiments
Always use the `--random-seed` option for reproducible results:
```bash
vcp benchmarks run -m SCVI-v1-homo_sapiens -d tsv2_blood -t clustering -r 42
```

### Bypassing Cache
Use `--no-cache` to ensure fresh computation:
```bash
vcp benchmarks run -m SCVI-v1-homo_sapiens -d tsv2_blood -t clustering --no-cache
```

### Reproducing VCP Results
Combine `list` and `run` commands for systematic evaluation:
```bash
# First, list available benchmarks
vcp benchmarks list -m "scvi*" -f json > available_benchmarks.json

# Then run specific benchmarks
vcp benchmarks run -b BENCHMARK_KEY_FROM_LIST
```

### User Datasets
Evaluate models on user datasets while comparing to existing benchmarks:
```bash
# Specify a user's local dataset file with custom labels
vcp benchmarks run -m SCVI-v1-homo_sapiens \
  -u '{"dataset_class": "czbenchmarks.datasets.SingleCellLabeledDataset", "organism": "HUMAN", "path": "~/custom.h5ad"}' \
  -t embedding --labels custom_cell_type

# Compare with existing results
vcp benchmarks get -m SCVI-v1-homo_sapiens -t embedding
```

### Task-Specific Workflows
Use specialized options for different benchmark tasks:
```bash
# Advanced clustering with custom parameters
vcp benchmarks run -m SCVI-v1-homo_sapiens -d tsv2_blood -t clustering \
  --labels cell_type --use-rep X --n-iterations 5 --flavor leidenalg --key-added custom_clusters -r 42

# Cross-validation with custom settings for label prediction
vcp benchmarks run -c embeddings.npy \
  -u '{"dataset_class": "czbenchmarks.datasets.SingleCellLabeledDataset", "organism": "HUMAN", "path": "~/data.h5ad"}' \
  -t label_prediction --labels @obs:cell_type --n-folds 10 --min-class-size 3 -r 42

# Batch integration with alternative column names
vcp benchmarks run -m SCVI-v1-homo_sapiens -d tsv2_blood -t batch_integration \
  --batch-column sample_id --labels cell_type -r 42
```

## Best Practices

- **Use specific filters**: Narrow down results with appropriate filters to find relevant benchmarks quickly
- **Set random seeds**: Ensure reproducibility by always setting random seeds for experiments
- **Reference format**: Use `@obs:column_name` format when your dataset uses non-standard column names
- **Cache management**: Use `--no-cache` sparingly, as caching significantly speeds up repeated experiments
- **Output format selection**: Use JSON format for programmatic processing, table format for human review
- **Task-specific tuning**: Adjust parameters like `--n-folds`, `--n-iterations` based on dataset size and requirements
- **Progressive filtering**: Start with broad filters and progressively narrow down to find specific benchmarks

