# TLS-Data-Paper

A dataset of **Broadband Cryogenic Transient Dielectric Spectroscopy (BCTDS)**
measurements and simulations of two-level-system (TLS) defect ensembles, with
the scripts that build each dataset from the raw files.

The dataset website (built from this repository and deployed with GitHub
Pages) lists every experiment with its documentation and per-file download
links. See [`website/README.md`](website/README.md) for how it is built.

---

## Prior work

This dataset builds on earlier BCTDS work on the same measurement platform:

> Wang et al., *Spectroscopy and coherent control of two-level system defect
> ensembles using a broadband 3D waveguide*, Materials for Quantum Technology
> **5**(4), 045201 (2025).

Code for that paper: <https://github.com/fitz-lab/BCTDS-Coherent-Control-Manuscript-Codebase>

---

## Experiments

Each experiment has a folder under `src/dataset_creation_scripts/` with a
README (full documentation, column descriptions, loading example), the
creation script, and `metadata.json` / `column_info.json` where applicable.

### Published in this release

| # | Experiment | Type | Data file(s) | Size |
|---|---|---|---|---|
| 2 | [Pulse-width sweep](src/dataset_creation_scripts/02_pulse_width_sweep/README.md) | measured | `experiment_2_dataset_long.pkl` | 420 MB |
| 3 | [Amplitude control (two-pulse)](src/dataset_creation_scripts/03_amplitude_control/README.md) | measured | `experiment_3_dataset_long.pkl` | 50 MB |
| 4 | [Phase control (two-pulse)](src/dataset_creation_scripts/04_phase_control/README.md) | measured | `experiment_4_dataset_long.pkl` | 61 MB |
| 5 | [Phase control at long inter-pulse spacing](src/dataset_creation_scripts/05_phase_control_long_spacing/README.md) | measured | `experiment_5_dataset_long.pkl` | 26 MB |
| 11 | [Temperature dependence during warm-up](src/dataset_creation_scripts/11_temperature_sweep_warmup/README.md) | measured | `experiment_11_dataset_long.pkl` | 1.36 GB |
| 12 | [Phase control at different temperatures](src/dataset_creation_scripts/12_phase_control_temperature/README.md) | measured | `experiment_12_dataset_long.pkl` | 488 MB |
| 13 | [Thermal cycle (before and after)](src/dataset_creation_scripts/13_thermal_cycle/README.md) | measured | `experiment_13_dataset_long.pkl` | 120 MB |
| 14 | [Pulse-amplitude sweep spectroscopy](src/dataset_creation_scripts/14_phase_v_amplitude_sweep/README.md) | measured | `figure14_dataset_long.pkl` + 3 small derived files | 1.29 GB |

Total: about 3.8 GB, stored with Git LFS under `dataset/experiment_N/`.

### Not yet published

The simulated results are not released yet. Their creation scripts and
documentation are in the repository.

| # | Experiment |
|---|---|
| 6 | [Floquet spectroscopy of a two-TLS system](src/dataset_creation_scripts/06_floquet/README.md) |
| 8 | [Amplitude and multi-pulse control (N = 4)](src/dataset_creation_scripts/08_amplitude_control/README.md) |
| 9 | [Separation and relative-phase control (N = 2)](src/dataset_creation_scripts/09_separation_phase_sweep/README.md) |
| 10 | [Ring-down and phase sharpening vs pulse duration](src/dataset_creation_scripts/10_sharpening_physics/README.md) |
| 15 | [Interaction strength characterization](src/dataset_creation_scripts/15_j_ij_characterization/README.md) |
| 16 | [Degenerate and non-degenerate TLS dynamics](src/dataset_creation_scripts/16_tls_braiding/README.md) |

---

## Downloading the data

The data files are Git LFS objects, so a plain `git clone` without LFS only
fetches small pointer files. Three ways to get the real data:

**One file.** Use its LFS media URL, for example:

```bash
wget https://media.githubusercontent.com/media/Dartmouth-RIT/TLS-Data-Paper/main/dataset/experiment_3/experiment_3_dataset_long.pkl
```

**Everything, with the code.** Clone with Git LFS:

```bash
git lfs install
git clone https://github.com/Dartmouth-RIT/TLS-Data-Paper.git
```

To fetch only some experiments: `GIT_LFS_SKIP_SMUDGE=1 git clone ...`, then
`git lfs pull --include="dataset/experiment_3/*"`.

**Everything, data only.** Download `dataset_urls.txt` from the dataset
website (one URL per data file) and run:

```bash
wget -x -nH --cut-dirs=4 -i dataset_urls.txt
```

---

## Loading a dataset

For experiments 2–5 and 11–13, each `.pkl` file holds a dict with the rows
under `"data"` and the column names under `"columns"`:

```python
import pickle
import pandas as pd

with open("dataset/experiment_3/experiment_3_dataset_long.pkl", "rb") as fh:
    payload = pickle.load(fh)
df = pd.DataFrame(payload["data"], columns=payload["columns"])
```

Experiment 14 uses a different layout; see its README. Each experiment's
README describes its columns and how to select a single trace. Only unpickle files from a source you trust.

---

## Rebuilding a dataset from raw data

Each creation script takes the folder of raw files and an output folder, and
runs sanity checks after building. For example:

```bash
python src/dataset_creation_scripts/02_pulse_width_sweep/experiment_2_dataset_creation.py \
    --data_dir   /path/to/raw/npy \
    --output_dir /path/to/output
```

See each experiment's README for its exact inputs and options.

---

## Installation

Python 3.10 or newer.

```bash
pip install -e .                 # numpy, pandas, tqdm, flake8, black: enough to load the data and run the measured-data scripts
pip install -e ".[simulation]"   # adds scipy and qutip for the simulation scripts
```

`src/dataset_creation_scripts/requirements.txt` lists the same packages for a
plain `pip install -r`. numpy 2 or newer is needed to load the `.pkl` files.

---

## Repository layout

```
dataset/
  experiment_N/                 data files (Git LFS)
src/dataset_creation_scripts/
  NN_<name>/                    one folder per experiment
    README.md                   documentation (also shown on the website)
    *_dataset_creation.py       builds the dataset from raw files
    metadata.json, column_info.json
  requirements.txt
website/                        dataset website (build_site.py, see its README)
.github/workflows/              GitHub Pages deployment
Data_Documentation.pdf
```
