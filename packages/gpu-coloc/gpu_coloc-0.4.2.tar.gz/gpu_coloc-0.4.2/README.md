# gpu-coloc

**gpu-coloc** is a GPU-accelerated Bayesian colocalization implementation (COLOC), delivering identical results to R's `coloc.bf_bf` approximately 1000 times faster.

If you have any questions or problems with `gpu-coloc`, please write to `mihkel.jesse@gmail.com`.

## Citation

If you use **gpu-coloc**, please cite: [https://doi.org/10.1101/2025.08.25.672103](https://doi.org/10.1101/2025.08.25.672103)

##

All of eQTL Catalogue ready for use with gpu-coloc can be found [here](https://tartuulikool-my.sharepoint.com/:f:/r/personal/a72094_ut_ee/Documents/eQTL_Catlogue_gpu-coloc?csf=1&web=1&e=U6OhP4).

## Installation

Install via pip (Python ≥3.12):

```bash
pip install gpu-coloc
```

If `pip` cannot find the package, it is probably do to an older version of `pip`. Thus to upgrade it run:

```bash

pip install --upgrade pip
```

You can set up `gpu-coloc` up in a virtual environment:

```bash
python -m venv [path_to_venv]
source [path_to_venv]/bin/activate
pip install gpu-coloc
```

This is prefered in production environments or if you are having trouble with package management.

## Verify Installation

To confirm installation, clone this repository:

```bash
git clone https://github.com/mjesse-github/gpu-coloc
cd gpu-coloc
bash test.sh
```

This creates an `example/` directory containing an `example_results.tsv` file.

## Workflow

**Note:** Paths assume gpu-coloc is in the working directory; adjust paths if necessary.

### Variant Naming Convention

Variants must follow the naming format: `chr[chromosome]_[position]_[ref]_[alt]`. Ensure renaming is completed before Step 1. Use chromosome X, not 23.

### 1. Prepare Signals and Summary Files

* **Signal Files:** Save signals as `[signal].pickle`, containing variants and their log Bayes Factors (lbf).

Example format:

```
variant	chrX_153412224_C_A	chrX_153412528_C_T	...
lbf	-0.060991	-1.508802	...
```

* **Summary File:** Tab-separated, structured as:

```
signal	chromosome	location_min	location_max	signal_strength	lead_variant
QTD000141_ENSG00000013563_L1	X	153412224	155341332	12.1069377174147	chrX_154403855_T_G
...
```

Naming examples:

* Summary: `gwas_summary.tsv`
* Signals directory: `gwas_signals/[signal].pickle`

See scripts in `summary_and_signals_examples/` for reference; modifications may be necessary.

### 2. Format Data

```bash
gpu-coloc --format --input [path_to_signals] --input_summary [summary_file] --output [output_folder]
```

#### Parameters for `gpu-coloc --format`

- `--input` (required): Path to the directory containing signal files (e.g., `gwas_signals/`). Supports `pickle` or `feather` files (see `--input_type`).
- `--output` (required): Path to the output directory where formatted parquet files will be saved.
- `--input_summary` (required): Path to the summary TSV file (e.g., `gwas_summary.tsv`).
- `--output_summary` (optional): Path to write the formatted summary as a parquet file.
- `--input_type` (optional): Type of input files, either `'pickle'` (default) or `'feather'`.

### 3. Run Colocalization

```bash
gpu-coloc --run --dir1 [formatted_dataset_1] --dir2 [formatted_dataset_2] --results [results_output] --p12 1e-6 --H4 0.8
```
#### Parameters for `gpu-coloc --run`

- `--dir1` (required): Path to the first formatted dataset directory.
- `--dir2` (required): Path to the second formatted dataset directory.
- `--results` (required): Path to the output file where colocalization results will be saved.
- `--p12` (optional): Prior probability that a variant is associated with both traits. Default: `1e-6`.
- `--H4` (optional): Posterior probability threshold for declaring colocalization (H4). Default: `0.8`.
