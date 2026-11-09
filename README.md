# QTLS

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

Experiment numbers follow that paper's figure numbers: Experiment *N*
corresponds to Figure *N*. Several released experiments cover more settings
than the corresponding figure shows (see
[Differences from the figures](#differences-from-the-paper-figures)).

---

## How the measurements work

A sample chip (27.5 × 5.5 mm) sits between two WR-229 waveguide adaptors (3–6
GHz passband, TE₁₀ mode) on the mixing-chamber stage of a Bluefors LD400
dilution refrigerator, below 10 mK unless stated. An RFSoC 4×2 board
synthesises square microwave pulses and performs homodyne readout with the
local oscillator at the drive frequency. After a pulse switches off, the TLS
ensemble rings down, and the in-phase (I) and quadrature (Q) signals of that
ring-down are recorded: 1,000 samples at about 1.81 ns per sample.

Two derived views are used throughout, and both can be computed from the
stored I and Q:

- **Transient spectrum:** log |I + iQ| against drive frequency and time.
- **Phase FFT:** the FFT of arg(I + iQ). It shows V-shaped features whose
  base sits at a bare TLS eigenfrequency. The V bases do not move when the
  pulse length or amplitude changes, which is why they are read as the defect
  frequencies.

Measured samples, as described in the paper:

| Sample | Used in | Paper section |
|---|---|---|
| Si(111) with native oxide | Exps 2, 3, 4 | Section 3.1, Appendix A.1 |
| Sapphire with 2 nm ALD AlOx | Exps 3, 4 | Section 3.2, Appendix A.2 |
| Sapphire with spin-coated Shipley 1813 photoresist | Exps 5, 11, 12, 13 | Appendices B and C |

---

## Experiments

The measured experiments fall into three families:

1. **Single-pulse spectroscopy** (Exps 2, 14, 13) locates the TLS defects. One
   pulse is swept across frequency while one drive setting is varied.
2. **Two-pulse coherent control** (Exps 3, 4, 5) tests whether the defect
   bath remembers an earlier pulse. The second pulse never changes, so any
   change in the ring-down after it comes from the first pulse.
3. **Temperature and thermal history** (Exps 11, 12, 13) repeat families 1
   and 2 while the fridge warms up, at fixed raised temperatures, or after a
   warm-up to room temperature.

The simulations (Exps 6–10, 15, 16) use a driven tunnelling model of N = 2 or
4 TLS with dipole–dipole coupling J and collective decay (Lindblad master
equation). Each reproduces one measured result qualitatively.

### Published in this release

| # | Experiment | What is swept | What it shows | Data file(s) | Size |
|---|---|---|---|---|---|
| 2 | [Pulse-width sweep](src/dataset_creation_scripts/02_pulse_width_sweep/README.md) | Si(111); pulse duration (42 values, ~5–214 ns) × drive frequency (4100–4599 MHz, 1 MHz steps) | Ring-downs sharpen with longer pulses while the V bases stay fixed. Counting them gives a TLS density of about 84 GHz⁻¹. | `experiment_2_dataset_long.pkl` | 420 MB |
| 3 | [Amplitude control (two-pulse)](src/dataset_creation_scripts/03_amplitude_control/README.md) | AlOx at 3657 MHz and Si(111) at 4254 MHz; first-pulse amplitude (100 values, up to 30,000 a.u.) × spacing (6 values, 0–50 ns); second pulse fixed at ~10,000 a.u. | The ring-down after the second pulse shifts with the first pulse's amplitude: the bath keeps a memory of the first pulse. | `experiment_3_dataset_long.pkl` | 50 MB |
| 4 | [Phase control (two-pulse)](src/dataset_creation_scripts/04_phase_control/README.md) | Same samples and frequencies as Exp 3; first-pulse phase (0–360°, 3° steps) × spacing (6 values, 0–50 ns); first pulse 3× the second | Phase-dependent interference fringes in both samples. | `experiment_4_dataset_long.pkl` | 61 MB |
| 5 | [Phase control at long inter-pulse spacing](src/dataset_creation_scripts/05_phase_control_long_spacing/README.md) | Shipley, 3400 MHz; first-pulse phase × spacing (9 values, 10–600 ns) | The single-pulse ring-down lasts ~100 ns. Phase control fades once the spacing is well past that. | `experiment_5_dataset_long.pkl` | 26 MB |
| 11 | [Temperature dependence during warm-up](src/dataset_creation_scripts/11_temperature_sweep_warmup/README.md) | Shipley; 106 back-to-back single-pulse sweeps (3–5 GHz, 5 MHz steps) during an uncontrolled warm-up from base to ~250 K | Ring-down lifetimes collapse near 1 K and the response vanishes at high temperature, consistent with a quantum origin. | `experiment_11_dataset_long.pkl` | 1.36 GB |
| 12 | [Phase control at different temperatures](src/dataset_creation_scripts/12_phase_control_temperature/README.md) | Shipley; Exp 5's protocol (phase × 9 spacings) at 3400 and 3560 MHz, at 7 set points (8, 95, 200, 307, 400, 600, 750 mK), each thermalised > 1 h | Interference contrast fades as temperature rises. The jump in lifetime between 95 and 200 mK is attributed to spectral diffusion. | `experiment_12_dataset_long.pkl` | 488 MB |
| 13 | [Thermal cycle (before and after)](src/dataset_creation_scripts/13_thermal_cycle/README.md) | Shipley at ~22 mK; single-pulse sweep (2000–4999 MHz, 1 MHz steps) in two cooldowns 3 days apart, with a warm-up to room temperature between | The ring-down patterns and V positions change: thermal cycling reconfigures the TLS population. | `experiment_13_dataset_long.pkl` | 120 MB |
| 14 | [Pulse-amplitude sweep spectroscopy](src/dataset_creation_scripts/14_phase_v_amplitude_sweep/README.md) | 200 ns pulse; amplitude (66 values, 0–30,000 a.u.) × 500 drive frequencies. Amplitude 0 is an undriven noise reference. | V bases stay fixed as amplitude grows, and the response saturates. | `figure14_dataset_long.pkl` + 3 small derived files | 1.29 GB |

Total: about 3.8 GB, stored with Git LFS under `dataset/experiment_N/`.

### Not yet published

The simulated results are not released yet. Their creation scripts and
documentation are in the repository.

| # | Experiment | Model | Reproduces |
|---|---|---|---|
| 6 | [Floquet spectroscopy of a two-TLS system](src/dataset_creation_scripts/06_floquet/README.md) | N = 2, master equation and Floquet quasi-energies | V features of Exp 2; V bases line up with quasi-energy dips |
| 7 | [Analytical phase-V spectroscopy](src/dataset_creation_scripts/07_perturbation_theory_spectra/README.md) | Two TLS, second-order perturbation theory | V bases at the bare frequencies, plus weaker sideband lines (Exp 2) |
| 8 | [Amplitude and multi-pulse control (N = 4)](src/dataset_creation_scripts/08_amplitude_control/README.md) | N = 4, amplitude sweep and two-pulse protocol | Exp 3 |
| 9 | [Separation and relative-phase control (N = 2)](src/dataset_creation_scripts/09_separation_phase_sweep/README.md) | N = 2, sweeps of the gap between pulses and their relative phase | Exps 4 and 5 |
| 10 | [Ring-down and phase sharpening vs pulse duration](src/dataset_creation_scripts/10_sharpening_physics/README.md) | N = 2 at 4.0 and 4.1 GHz, pulse duration swept | Sharpening with pulse length in Exp 2 |
| 15 | [Interaction strength characterization](src/dataset_creation_scripts/15_j_ij_characterization/README.md) | N = 4, coupling J from 5 MHz to 0.5 GHz | Why strongly coupled clusters can show a single V |
| 16 | [Degenerate and non-degenerate TLS dynamics](src/dataset_creation_scripts/16_tls_braiding/README.md) | N = 2, detuned vs identical frequencies | Braided vs single-line ring-downs in Exp 2 |

### How the experiments connect

- **Exps 2 and 14** vary the two single-pulse drive settings: duration and
  amplitude. The V bases stay fixed under both, which identifies them as the
  bare TLS frequencies.
- **Exp 13** is the check on that result. A thermal cycle does move the V
  features, so they follow the actual defects rather than the waveguide or
  electronics.
- **Exp 2 leads to Exps 3–5.** Pulse length changes how sidebands interfere,
  which suggests that pulse shape can steer the response. Exps 3–5 test this
  with two pulses, turning one setting at a time: first-pulse amplitude (3),
  first-pulse phase (4), then the spacing out to 600 ns to measure how long
  the memory lasts (5). Each sample's drive frequency was picked from its
  broadband single-pulse map, at a long ring-down.
- **Exps 11 and 12** add temperature. Exp 11 does single-pulse spectroscopy
  while the fridge warms. Exp 12 repeats Exp 5's phase-control protocol at
  fixed temperatures. Both lose coherent features above roughly the
  kT = hf crossover (144 mK at 3 GHz, 240 mK at 5 GHz).

### Differences from the paper figures

- **Exps 3 and 4** contain six spacings (0–50 ns). The paper shows three
  (10, 30, 50 ns).
- **Exp 5** is byte-for-byte the 8 mK, 3400 MHz slice of Exp 12, so Figure 5
  and the 8 mK row of Figure 12 come from the same acquisition.
- **Exp 12** has nine spacings and two frequencies at each temperature.
  Figure 12 shows only 3400 MHz at 100 ns.
- **Exp 11** has 106 sweeps and runs to ~250 K; Figure 11 shows sweeps 0–50 (up to ~88 K). The mixing-chamber
  temperature is missing (NaN) for sweeps 83–105.
- **Exp 13** spans 2000–4999 MHz; Figure 13 shows 3.3–3.8 GHz.
- Built-in repeats include the 0° and 360° phase pairs (Exps 4, 5, 12),
  first-pulse amplitude 0 (Exp 3) and amplitude 0 (Exp 14).

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
python3 -m venv .venv && source .venv/bin/activate   # create and activate a virtual environment (Windows: .venv\Scripts\activate)
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
