#!/usr/bin/env python3
"""Build the QTLS dataset page (website/index.html).

A simple, light "catalog" page: one row per experiment with its type, total
size, per-file download links and its full README documentation, plus a
"Data at a glance" gallery of the overview figures in website/figures/.

* Experiment docs come from ../src/dataset_creation_scripts/NN_*/README.md
* Data files come from ../dataset/experiment_N/  (stored with Git LFS)

GitHub Pages cannot serve Git LFS objects, so every download link points at
GitHub's LFS media endpoint for the repository instead. File sizes are read
from the LFS pointer files, so the build works on a checkout without LFS
objects (as in CI). Uses only the Python standard library.
"""

import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DOCS = os.path.join(ROOT, "src", "dataset_creation_scripts")
DATA = os.path.join(ROOT, "dataset")
OUT = os.path.join(HERE, "index.html")

# owner/repo and branch the download links point at. GITHUB_REPOSITORY is set
# automatically inside GitHub Actions; override DATA_BRANCH if needed.
REPO = os.environ.get("GITHUB_REPOSITORY", "Dartmouth-RIT/TLS-Data-Paper")
BRANCH = os.environ.get("DATA_BRANCH", "main")
REPO_URL = f"https://github.com/{REPO}"
MEDIA_URL = f"https://media.githubusercontent.com/media/{REPO}/{BRANCH}/"  # LFS files
RAW_URL = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/"  # regular files

PRIOR_WORK_TEXT = (
    "Q. Wang, J. S. Salcedo-Gallo, S. Bedkihal, T. Xia, M. W. Olszewski, V. Fatemi and "
    "M. Fitzpatrick, \u201cSpectroscopy and coherent control of two-level system defect "
    "ensembles using a broadband 3D waveguide,\u201d Materials for Quantum Technology "
    "5(4), 045201 (2025)."
)
PRIOR_WORK_BIBTEX = """@article{wang2025spectroscopy,
  title={Spectroscopy and coherent control of two-level system defect ensembles using a broadband 3D waveguide},
  author={Wang, Qianxu and Salcedo-Gallo, Juan S and Bedkihal, Salil and Xia, Tian and Olszewski, Maciej W and Fatemi, Valla and Fitzpatrick, Mattias},
  journal={Materials for Quantum Technology},
  volume={5},
  number={4},
  pages={045201},
  year={2025},
  publisher={IOP Publishing}
}"""
# Rows (records) per released experiment: traces x 1,000 samples each. Kept here
# because CI checks out LFS pointers only and cannot count rows in the pickles.
# Update when an experiment's data changes.
RECORDS = {2: 21_000_000, 3: 1_800_000, 4: 2_178_000, 5: 1_089_000,
           11: 42_506_000, 12: 15_246_000, 13: 6_000_000, 14: 33_000_000}
SIMS = {6, 7, 8, 9, 10, 15, 16}  # simulation experiments; the rest are measured

esc = html.escape


def file_size(path):
    """Real size of a file, reading it from the LFS pointer when it is one."""
    with open(path, "rb") as fh:
        head = fh.read(200)
    if head.startswith(b"version https://git-lfs"):
        with open(path, encoding="utf-8") as fh:
            m = re.search(r"^size (\d+)", fh.read(), re.M)
        if m:
            return int(m.group(1))
    return os.path.getsize(path)


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit in ("B", "KB") else f"{n:.1f} {unit}"
        n /= 1024


def records(n):
    return f"{n / 1e6:.1f}M"


def amount(num, size):
    """'21.0M records (400.5 MB)' style label; size only when the count is unknown."""
    if num in RECORDS:
        return f"{records(RECORDS[num])} ({human(size)})"
    return human(size)


def clean_title(h1):
    t = re.sub(r"^[^\w(]+", "", h1).strip()  # drop leading emoji/symbols
    m = re.match(r"Experiment\s+\d+\s*[—\-:]\s*(.*)", t)
    return m.group(1).strip() if m else t


def short_desc(md):
    para, seen_h1 = [], False
    for line in md.splitlines():
        s = line.strip()
        if not seen_h1:
            seen_h1 = s.startswith("# ")
            continue
        if not s:
            if para:
                break
            continue
        if s.startswith(("#", ">", "|", "```", "-", "*", "---", "===")):
            if para:
                break
            continue
        para.append(s)
    d = " ".join(para)
    d = re.sub(r"\*\*(.+?)\*\*", r"\1", d)
    d = re.sub(r"`(.+?)`", r"\1", d)
    d = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", d)
    if len(d) > 260:
        d = d[:260].rsplit(" ", 1)[0] + "…"
    return d


# ---- data files ------------------------------------------------------------
files = {}  # experiment number -> [(repo-relative path, size)]
if os.path.isdir(DATA):
    for d in sorted(os.listdir(DATA)):
        m = re.match(r"^experiment_(\d+)$", d)
        if not m:
            continue
        rows = []
        for f in sorted(os.listdir(os.path.join(DATA, d))):
            p = os.path.join(DATA, d, f)
            if os.path.isfile(p) and not f.startswith("."):
                rows.append((f"dataset/{d}/{f}", file_size(p)))
        if rows:
            files[int(m.group(1))] = rows

# ---- experiments -----------------------------------------------------------
experiments = []
for folder in sorted(os.listdir(DOCS)):
    if not re.match(r"^\d\d_", folder):
        continue
    path = os.path.join(DOCS, folder, "README.md")
    if not os.path.exists(path):
        continue
    num = int(folder[:2])
    md = open(path, encoding="utf-8").read()
    # TEMPORARY: hide institution attribution lines on the site (README untouched).
    md = re.sub(r"(?m)^.*Fitzpatrick Lab, Dartmouth College.*\n?", "", md)
    h1 = next((m.group(1).strip() for m in re.finditer(r"(?m)^#\s+(.*)", md)), folder)
    experiments.append(
        {
            "num": num,
            "id": f"{num:02d}",
            "title": clean_title(h1),
            "desc": short_desc(md),
            "kind": "sim" if num in SIMS else "meas",
            "md": md,
            "files": files.get(num, []),
        }
    )

all_files = [f for e in experiments for f in e["files"]]
total = sum(s for _, s in all_files)
total_records = sum(RECORDS.get(e["num"], 0) for e in experiments if e["files"])


def row_html(e):
    kind = "Simulated" if e["kind"] == "sim" else "Measured"
    size = amount(e["num"], sum(s for _, s in e["files"])) if e["files"] else "—"
    if e["files"]:
        dl = "".join(
            f'<a class="btn" href="{MEDIA_URL}{p}" download>'
            f'<span aria-hidden="true">↓</span> {esc(os.path.basename(p))} '
            f'<span class="sz">{human(s)}</span></a>'
            for p, s in e["files"]
        )
    else:
        dl = '<span class="na">Data not yet published for this experiment.</span>'
    return f"""<details class="row" id="exp-{e['id']}">
  <summary><span class="n">{e['id']}</span><span class="t">{esc(e['title'])}</span><span class="tag {e['kind']}">{kind}</span><span class="s">{size}</span></summary>
  <div class="body">
    <p>{esc(e['desc'])}</p>
    <div class="btns">{dl}</div>
    <button class="doc" type="button" data-exp="{e['id']}">Read full documentation →</button>
  </div>
</details>"""


rows_html = "\n".join(row_html(e) for e in experiments)
url_list = "\n".join(MEDIA_URL + p for p, _ in all_files)
readmes = {
    e["id"]: {"title": e["title"], "kind": e["kind"], "md": e["md"]}
    for e in experiments
}
readmes_json = json.dumps(readmes).replace("</", "<\\/")

# ---- figures ---------------------------------------------------------------
# Static PNGs in website/figures/, made by the analysis scripts. A figure whose
# file is missing is skipped, so the page still builds without them.
FIGURES = [
    {
        "src": "experiment-overview.png",
        "title": "What each experiment sweeps",
        "shows": "Each row is one measured experiment. The grid gives the number of distinct values of each "
        "control setting (a dot means the setting is held fixed); the bars give the number of ring-down "
        "traces, each 1,000 records long.",
        "takeaways": [
            "Drive frequency is the most densely sampled setting (up to 3,000 tones); each experiment adds "
            "one to three other settings on top of it.",
            "Settings are swept on grids within an experiment, not across all experiments, so most "
            "combinations (for example amplitude and temperature together) are not measured.",
            "Experiment 5 is the 8 mK, 3400 MHz slice of Experiment 12, so use one or the other. The "
            "mixing-chamber thermometer column in Experiment 11 is empty for sweeps 83–105; I and Q are "
            "always present.",
        ],
    },
    {
        "src": "frequency-coverage.png",
        "title": "Drive frequencies",
        "shows": "The drive tones used in each experiment, coloured by sample. Bars are frequency sweeps; "
        "diamonds are a few fixed tones.",
        "takeaways": [
            "Together the experiments cover 2–5 GHz. Experiment 13 spans the whole range in 1 MHz steps and "
            "Experiment 11 covers 3–5 GHz.",
            "The Shipley 1813 sample has the broadest frequency coverage. Experiments 3 and 4 are the only "
            "places where several samples are measured under the same protocol.",
            "Neighbouring tones behave alike, so a model tested on held-out frequency bands gives a more "
            "honest score than one tested on randomly held-out traces.",
        ],
    },
    {
        "src": "signal-coverage.png",
        "title": "Where the signal is",
        "shows": "Ring-down signal-to-noise ratio (SNR) for every trace across four sweep grids: light is "
        "noise only (SNR ≈ 1.25), dark is strong signal. SNR is the mean ring-down amplitude 36–72 ns "
        "after the drive pulse ends, divided by the trace's noise level.",
        "takeaways": [
            "Vertical dark bands mark frequencies where the defects respond strongly, for example around "
            "4.3 GHz in Experiments 2 and 14.",
            "Experiment 2 has usable signal in every trace. In Experiment 14 the signal only rises above "
            "noise at higher drive amplitude, so the low-amplitude rows are close to noise.",
            "In the Experiment 11 warm-up the signal disappears as the sample heats: from sweep 8 onward the "
            "median trace is noise. Those traces are useful as noise examples or for detection tasks, but "
            "not for learning the ring-down shape.",
            "Experiment 13 has strong signal above about 2.5 GHz and weaker signal below it, in both "
            "cooldowns.",
        ],
    },
    {
        "src": "noise-and-snr.png",
        "title": "Noise floor and signal-to-noise",
        "shows": "(A) The readout noise of undriven traces. (B) The noise level of every trace, taken from its "
        "last 150 samples after the ring-down has decayed. (C) The share of traces below a given SNR, per "
        "experiment.",
        "takeaways": [
            "Readout noise is Gaussian with σ ≈ 0.098 ADC units in both I and Q, so a simple Gaussian "
            "noise model is appropriate.",
            "The noise floor differs between experiments by up to about 7× (about 0.1 for Experiments 2–4 "
            "and 14, up to 0.7 for Experiment 11). Normalise or weight per experiment before pooling them.",
            "Most traces are far above noise (median SNR 60–2,500). The exceptions are Experiment 11, where "
            "95% of traces have SNR below 3, and the low-amplitude part of Experiment 14.",
        ],
    },
]
figures = [f for f in FIGURES if os.path.exists(os.path.join(HERE, "figures", f["src"]))]


def fig_html(i, f):
    tk = "".join(f"<li>{esc(t)}</li>" for t in f["takeaways"])
    return f"""<figure class="fig">
  <button class="figbtn" type="button" data-fig="{i}" aria-label="Enlarge: {esc(f['title'])}"><img src="figures/{f['src']}" alt="{esc(f['title'])}" loading="lazy"></button>
  <figcaption>
    <h3>{esc(f['title'])}</h3>
    <p><b>What it shows.</b> {esc(f['shows'])}</p>
    <p class="tkh"><b>What to take from it</b></p>
    <ul>{tk}</ul>
  </figcaption>
</figure>"""


if figures:
    figs_html = (
        '<h2 id="overview">Data at a glance</h2>\n'
        '  <p class="sub">Click a figure to enlarge it.</p>\n'
        '  <div class="figs">\n' + "\n".join(fig_html(i, f) for i, f in enumerate(figures)) + "\n  </div>"
    )
else:
    figs_html = ""
figs_json = json.dumps(
    [{"src": "figures/" + f["src"], "title": f["title"], "shows": f["shows"], "takeaways": f["takeaways"]} for f in figures]
).replace("</", "<\\/")

TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>QTLS · Coherent Control Dataset</title>
<meta name="description" content="Open dataset of measured and simulated two-level-system ring-downs under coherent microwave control, with downloads.">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='22' fill='%232563eb'/><text x='50' y='70' font-size='60' text-anchor='middle' fill='white'>&#9672;</text></svg>">
<style>
*{box-sizing:border-box}
body{margin:0;font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;color:#1d2433;background:#f7f8fa}
a{color:#2563eb}
.w{max-width:920px;margin:0 auto;padding:0 20px}
header{background:#fff;border-bottom:1px solid #e5e7eb;padding:44px 0 32px}
h1{font-size:28px;line-height:1.2;margin:0 0 8px;letter-spacing:-.01em}
.lead{color:#5b6476;margin:0 0 20px}
.stats{display:flex;flex-wrap:wrap;gap:32px;color:#5b6476;font-size:13px}
.stats b{display:block;font-size:22px;color:#1d2433}
.stats small{font-size:15px;font-weight:500;color:#5b6476}
.top{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}
.pbtn,.gbtn{padding:9px 14px;border-radius:8px;text-decoration:none;font-weight:600;font-size:14px}
.pbtn{background:#2563eb;color:#fff}.pbtn:hover{background:#1d4ed8}
.gbtn{border:1px solid #d1d5db;color:#1d2433;background:#fff}.gbtn:hover{border-color:#9ca3af}
main{padding:28px 0 8px}
h2{font-size:19px;margin:28px 0 12px}
.row{background:#fff;border:1px solid #e5e7eb;border-radius:10px;margin-bottom:8px}
.row[open]{border-color:#c7d2fe}
summary{display:grid;grid-template-columns:36px 1fr auto 140px;gap:12px;align-items:center;padding:14px 16px;cursor:pointer;list-style:none}
summary::-webkit-details-marker{display:none}
summary:hover .t{color:#2563eb}
.n{color:#9aa3b2;font-variant-numeric:tabular-nums}
.t{font-weight:600}
.s{text-align:right;color:#5b6476;font-size:13px;font-variant-numeric:tabular-nums}
.tag{font-size:12px;padding:2px 9px;border-radius:99px;white-space:nowrap}
.meas{background:#e0f2fe;color:#075985}.sim{background:#ede9fe;color:#5b21b6}
.body{padding:0 16px 16px 64px;color:#4b5563}
.body p{margin:0 0 12px}
.btns{display:flex;flex-wrap:wrap;gap:8px}
.btn{border:1px solid #2563eb;color:#2563eb;padding:6px 11px;border-radius:7px;text-decoration:none;font-size:13px;word-break:break-all}
.btn:hover{background:#eff6ff}
.sz{color:#6b7280}.na{color:#9aa3b2;font-size:13px}
.doc{margin-top:12px;background:none;border:0;padding:0;color:#2563eb;font:inherit;font-size:13px;cursor:pointer}
.doc:hover{text-decoration:underline}
.card{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:18px 20px;color:#4b5563}
.card p{margin:0 0 10px}
pre{background:#0f172a;color:#e2e8f0;border-radius:8px;padding:14px;overflow:auto;font:12.5px/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.cite{color:#1d2433;border-left:3px solid #c7d2fe;padding-left:12px}
.bibhead{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.copy{border:1px solid #d1d5db;background:#fff;border-radius:7px;padding:4px 10px;cursor:pointer;font-size:13px}
.copy:hover{border-color:#9ca3af}
pre#bibtex{white-space:pre-wrap;word-break:break-word}
footer{color:#9aa3b2;font-size:13px;padding:28px 0 40px}
.sub{color:#5b6476;margin:-6px 0 12px;font-size:13px}
.figs{display:flex;flex-direction:column;gap:14px}
.fig{margin:0;background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px 18px}
.figbtn{display:block;width:100%;border:0;padding:0;background:#fff;cursor:zoom-in;border-radius:6px;overflow:hidden}
.figbtn img{display:block;width:100%;max-height:520px;object-fit:contain}
.figbtn:hover img{opacity:.85}
.fig figcaption{font-size:14px;color:#4b5563;margin-top:12px;line-height:1.55}
.fig h3{font-size:16px;color:#1d2433;margin:0 0 6px}
.fig figcaption p{margin:0 0 8px}
.fig figcaption b{color:#1d2433}
.fig ul,.about ul{margin:0;padding-left:20px}.fig li,.about li{margin-bottom:4px}
.tkh{margin-bottom:4px!important}
.about h3{font-size:15px;color:#1d2433;margin:16px 0 6px}
.about h3:first-child{margin-top:0}
.lb{position:fixed;inset:0;display:none;z-index:11}
.lb.open{display:block}
.lbp{position:absolute;inset:4vh 4vw;background:#fff;border-radius:10px;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 10px 40px rgba(0,0,0,.25)}
.lbimg{flex:1;min-height:0;overflow:auto;padding:12px 20px;display:flex;align-items:flex-start;justify-content:center}
.lbimg img{max-width:100%;height:auto}
.lbcap p{margin:0 0 6px}.lbcap ul{margin:0;padding-left:20px}
.lbcap{padding:12px 20px 18px;max-height:30vh;overflow:auto;border-top:1px solid #e5e7eb;color:#4b5563;font-size:14px}
.lbnav{display:flex;gap:8px}
/* reader */
.reader{position:fixed;inset:0;display:none;z-index:10}
.reader.open{display:block}
.rb{position:absolute;inset:0;background:rgba(15,23,42,.45)}
.rp{position:absolute;top:0;right:0;bottom:0;width:min(780px,100%);background:#fff;display:flex;flex-direction:column;box-shadow:-8px 0 30px rgba(0,0,0,.15)}
.rh{display:flex;justify-content:space-between;align-items:center;padding:14px 20px;border-bottom:1px solid #e5e7eb}
.rx{border:1px solid #d1d5db;background:#fff;border-radius:7px;padding:4px 10px;cursor:pointer;font-size:14px}
.md-body{overflow:auto;padding:8px 24px 40px;color:#374151}
.md-h{color:#111827;line-height:1.3}
.md-pre{background:#f3f4f6;color:#111827}
.md-tablewrap{overflow:auto}.md-table{border-collapse:collapse;font-size:13px;margin:10px 0}
.md-table th,.md-table td{border:1px solid #e5e7eb;padding:6px 9px;text-align:left;vertical-align:top}.md-table th{background:#f9fafb}
.md-quote{border-left:3px solid #c7d2fe;margin:10px 0;padding:2px 14px;color:#4b5563}
.md-hr{border:0;border-top:1px solid #e5e7eb;margin:20px 0}
code{background:#f3f4f6;border-radius:4px;padding:1px 5px;font-size:.9em}
pre code{background:none;padding:0}
@media (max-width:640px){
  .lbp{inset:0;border-radius:0}
  summary{grid-template-columns:28px 1fr auto;}
  summary .s{display:none}
  .body{padding:0 16px 16px}
  h1{font-size:23px}
}
</style>
</head>
<body>
<header>
  <div class="w">
    <h1>QTLS · Coherent Control Dataset</h1>
    <p class="lead">Measured ring-downs and matched simulations of two-level-system defects under pulsed microwave control.</p>
    <div class="stats">
      <span><b>__NEXP__</b>experiments</span>
      <span><b>__NDATA__</b>with downloadable data</span>
      <span><b>__NREC__ <small>(__TOTAL__)</small></b>records</span>
    </div>
    <div class="top">
      <a class="pbtn" href="#download-all">↓ Download everything</a>
      <a class="gbtn" href="__REPO__" target="_blank" rel="noopener">GitHub repository</a>
      <a class="gbtn" href="__RAW__Data_Documentation.pdf" target="_blank" rel="noopener">Data documentation (PDF)</a>
    </div>
  </div>
</header>

<main class="w">
  <h2 id="about">About the data</h2>
  <div class="card about">
    <p>Two-level-system (TLS) defects in the amorphous oxides and polymers on superconducting-circuit materials are a leading source of energy loss and decoherence in superconducting qubits. This dataset records how ensembles of these defects respond to pulsed microwave control. In each measurement a dielectric sample sits in a broadband 3D waveguide at millikelvin temperature and is driven by one or two microwave pulses. The microwave signal the excited defects re-emit as they relax afterwards (the <i>ring-down</i>) is recorded as raw homodyne I and Q samples.</p>
    <h3>What is in a record</h3>
    <p>Each record (one row) is a single time sample of one ring-down: the control settings, the time since the start of the trace (1.81 ns spacing) and the raw I and Q values. 1,000 consecutive records with the same settings form one ring-down trace. Across the measured experiments the swept settings are drive frequency (2–5 GHz), pulse width, drive amplitude, the relative phase and spacing of two pulses, and temperature (8 mK to about 250 K during a warm-up). Samples include Si(111) with native oxide, sapphire with ALD AlO<sub>x</sub>, and sapphire with Shipley 1813 photoresist. The data is released exactly as measured, without filtering or post-processing. The simulated and analytical experiments (6–10, 15 and 16) are documented with their generation code, but their data has not been published yet.</p>
    <h3>How it can be used</h3>
    <ul>
      <li><b>Learning the control-to-response map.</b> Train models that predict a ring-down from the drive settings, as fast surrogates for pulse design and optimal control.</li>
      <li><b>Testing physics models and simulators.</b> Compare TLS-ensemble or Bloch-equation simulations with raw measurements, including two-pulse phase and spacing effects and the temperature dependence.</li>
      <li><b>Spectroscopy and material comparison.</b> Find the frequency bands where defects respond strongly and compare dielectric samples.</li>
      <li><b>Signal-processing benchmarks.</b> Denoising, detecting weak signals and tracking drift, using traces that range from very strong signal to pure noise.</li>
    </ul>
    <h3>Before you start</h3>
    <ul>
      <li>Hold out whole frequency bands (or samples, or temperatures) for testing, not random traces. Neighbouring tones are strongly correlated, so random splits overstate accuracy (in one simple baseline, R² fell from 0.94 to 0.82).</li>
      <li>Noise levels differ between experiments by up to about 7×, so normalise per experiment before pooling them.</li>
      <li>Experiment 5 duplicates part of Experiment 12, and most of the Experiment 11 warm-up is noise-dominated. The figures below show where the signal is.</li>
    </ul>
  </div>

  __FIGS__

  <h2>Experiments</h2>
  __ROWS__

  <h2 id="download-all">Download everything</h2>
  <div class="card">
    <p>The full release is __NREC__ records (__TOTAL__), which is too large for a single zip. Choose one of these:</p>
    <p><b>Clone the repository with Git LFS</b> (includes the code and documentation):</p>
<pre>git lfs install
git clone __REPO__.git</pre>
    <p><b>Download only the data files</b>, keeping the <code>dataset/experiment_N/</code> folders:</p>
<p>Save <a href="dataset_urls.txt" download>dataset_urls.txt</a> (the list of every data file), then run:</p>
<pre>wget -x -nH --cut-dirs=4 -i dataset_urls.txt</pre>
    <details><summary style="display:block;padding:0;cursor:pointer;color:#2563eb">Show the list of file URLs</summary><pre>__URLS__</pre></details>
  </div>

  <h2>Loading a dataset</h2>
  <div class="card">
<pre>import pickle, pandas as pd
with open("experiment_3_dataset_long.pkl", "rb") as fh:
    payload = pickle.load(fh)
df = pd.DataFrame(payload["data"], columns=payload["columns"])</pre>
    <p style="margin:0">Each experiment's documentation describes its columns, units and how to rebuild it from the raw measurements.</p>
  </div>

  <h2 id="prior-work">Prior work</h2>
  <div class="card">
    <p>This dataset builds on the following earlier work.</p>
    <p class="cite">__CITE_TEXT__</p>
    <p>Code for that paper: <a href="https://github.com/fitz-lab/BCTDS-Coherent-Control-Manuscript-Codebase" target="_blank" rel="noopener">fitz-lab/BCTDS-Coherent-Control-Manuscript-Codebase</a></p>
    <div class="bibhead"><b>BibTeX</b><button class="copy" type="button" id="copy-bib">Copy</button></div>
<pre id="bibtex">__PRIOR_WORK_BIBTEX__</pre>
  </div>
</main>

<footer class="w">QTLS · Coherent Control Dataset · <a href="__REPO__">__REPO_NAME__</a></footer>

<div class="reader" id="reader" aria-hidden="true" role="dialog" aria-modal="true">
  <div class="rb" data-close></div>
  <div class="rp">
    <div class="rh"><span><span class="n" id="reader-id"></span> <span class="tag" id="reader-badge"></span></span><button class="rx" data-close aria-label="Close">Close ✕</button></div>
    <div class="md-body" id="reader-body"></div>
  </div>
</div>

<div class="lb" id="lb" aria-hidden="true" role="dialog" aria-modal="true" aria-labelledby="lb-title">
  <div class="rb" data-lbclose></div>
  <div class="lbp">
    <div class="rh"><b id="lb-title"></b><span class="lbnav"><button class="rx" type="button" id="lb-prev" aria-label="Previous figure">←</button><button class="rx" type="button" id="lb-next" aria-label="Next figure">→</button><a class="rx" id="lb-open" href="#" target="_blank" rel="noopener" style="text-decoration:none;color:inherit">Full size</a><button class="rx" type="button" data-lbclose aria-label="Close">Close ✕</button></span></div>
    <div class="lbimg"><img id="lb-img" alt=""></div>
    <div class="lbcap" id="lb-cap"></div>
  </div>
</div>

<script id="figs" type="application/json">__FIGS_JSON__</script>
<script id="readmes" type="application/json">__READMES__</script>
<script>
(function(){
  var DATA=JSON.parse(document.getElementById('readmes').textContent);
  /* ---- markdown renderer ---- */
  function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
  function inline(s){
    s=esc(s);
    s=s.replace(/`([^`]+)`/g,function(_,a){return '<code>'+a+'</code>';});
    s=s.replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>');
    s=s.replace(/(^|[^*])\*([^*]+)\*/g,'$1<em>$2</em>');
    s=s.replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>');
    return s;
  }
  function render(md){
    var lines=md.replace(/\r/g,'').split('\n'),out=[],i=0;
    function isBreak(l){return /^\s*(#|>|```)/.test(l)||/^\s*(---|\*\*\*|___)\s*$/.test(l)||/^\s*([-*]|\d+\.)\s+/.test(l)||/\|/.test(l);}
    while(i<lines.length){
      var ln=lines[i];
      if(/^```/.test(ln)){var b=[];i++;while(i<lines.length&&!/^```/.test(lines[i])){b.push(lines[i]);i++;}i++;out.push('<pre class="md-pre"><code>'+esc(b.join('\n'))+'</code></pre>');continue;}
      if(/\|/.test(ln)&&i+1<lines.length&&/^\s*\|?[\s:|-]+\|?\s*$/.test(lines[i+1])&&/-/.test(lines[i+1])){
        var head=ln,rows=[];i+=2;
        while(i<lines.length&&/\|/.test(lines[i])&&lines[i].trim()!==''){rows.push(lines[i]);i++;}
        var cells=function(r){r=r.trim().replace(/^\|/,'').replace(/\|$/,'');return r.split('|').map(function(c){return inline(c.trim());});};
        var th=cells(head).map(function(c){return '<th>'+c+'</th>';}).join('');
        var tb=rows.map(function(r){return '<tr>'+cells(r).map(function(c){return '<td>'+c+'</td>';}).join('')+'</tr>';}).join('');
        out.push('<div class="md-tablewrap"><table class="md-table"><thead><tr>'+th+'</tr></thead><tbody>'+tb+'</tbody></table></div>');continue;
      }
      if(/^\s*>/.test(ln)){var b=[];while(i<lines.length&&/^\s*>/.test(lines[i])){b.push(lines[i].replace(/^\s*>\s?/,''));i++;}out.push('<blockquote class="md-quote">'+render(b.join('\n'))+'</blockquote>');continue;}
      var h=/^(#{1,6})\s+(.*)$/.exec(ln);
      if(h){var lv=Math.min(h[1].length,3);out.push('<h'+lv+' class="md-h">'+inline(h[2])+'</h'+lv+'>');i++;continue;}
      if(/^\s*(---|\*\*\*|___)\s*$/.test(ln)){out.push('<hr class="md-hr">');i++;continue;}
      if(/^\s*[-*]\s+/.test(ln)||/^\s*\d+\.\s+/.test(ln)){
        var ord=/^\s*\d+\.\s+/.test(ln),it=[];
        while(i<lines.length&&(/^\s*[-*]\s+/.test(lines[i])||/^\s*\d+\.\s+/.test(lines[i]))){it.push('<li>'+inline(lines[i].replace(/^\s*(?:[-*]|\d+\.)\s+/,''))+'</li>');i++;}
        out.push('<'+(ord?'ol':'ul')+' class="md-list">'+it.join('')+'</'+(ord?'ol':'ul')+'>');continue;
      }
      if(ln.trim()===''){i++;continue;}
      var p=[ln];i++;
      while(i<lines.length&&lines[i].trim()!==''&&!isBreak(lines[i])){p.push(lines[i]);i++;}
      out.push('<p class="md-p">'+inline(p.join(' '))+'</p>');
    }
    return out.join('\n');
  }


  var reader=document.getElementById('reader'),body=document.getElementById('reader-body'),
      rid=document.getElementById('reader-id'),rbadge=document.getElementById('reader-badge'),last=null;
  function open(num){
    var e=DATA[num];if(!e)return;
    rid.textContent='Experiment '+num;
    rbadge.textContent=e.kind==='sim'?'Simulated':'Measured';rbadge.className='tag '+e.kind;
    body.innerHTML=render(e.md);body.scrollTop=0;
    last=document.activeElement;reader.classList.add('open');reader.setAttribute('aria-hidden','false');
    document.body.style.overflow='hidden';reader.querySelector('.rx').focus();
  }
  function close(){
    reader.classList.remove('open');reader.setAttribute('aria-hidden','true');
    document.body.style.overflow='';if(last)last.focus();
  }
  document.querySelectorAll('.doc').forEach(function(b){b.addEventListener('click',function(){open(b.getAttribute('data-exp'));});});
  reader.querySelectorAll('[data-close]').forEach(function(x){x.addEventListener('click',close);});
  document.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&reader.classList.contains('open'))close();});
  /* ---- figure lightbox ---- */
  var FIGS=JSON.parse(document.getElementById('figs').textContent),lb=document.getElementById('lb'),cur=0,lbLast=null;
  function showFig(i){
    cur=(i+FIGS.length)%FIGS.length;var f=FIGS[cur];
    document.getElementById('lb-img').src=f.src;document.getElementById('lb-img').alt=f.title;
    document.getElementById('lb-title').textContent=f.title;var cap=document.getElementById('lb-cap');cap.innerHTML='';var p=document.createElement('p');p.textContent=f.shows;cap.appendChild(p);var ul=document.createElement('ul');f.takeaways.forEach(function(t){var li=document.createElement('li');li.textContent=t;ul.appendChild(li);});cap.appendChild(ul);
    document.getElementById('lb-open').href=f.src;
  }
  function openFig(i){showFig(i);lbLast=document.activeElement;lb.classList.add('open');lb.setAttribute('aria-hidden','false');document.body.style.overflow='hidden';lb.querySelector('[data-lbclose].rx').focus();}
  function closeFig(){lb.classList.remove('open');lb.setAttribute('aria-hidden','true');document.body.style.overflow='';if(lbLast)lbLast.focus();}
  document.querySelectorAll('.figbtn').forEach(function(b){b.addEventListener('click',function(){openFig(+b.getAttribute('data-fig'));});});
  lb.querySelectorAll('[data-lbclose]').forEach(function(x){x.addEventListener('click',closeFig);});
  document.getElementById('lb-prev').addEventListener('click',function(){showFig(cur-1);});
  document.getElementById('lb-next').addEventListener('click',function(){showFig(cur+1);});
  document.addEventListener('keydown',function(ev){
    if(!lb.classList.contains('open'))return;
    if(ev.key==='Escape')closeFig();else if(ev.key==='ArrowLeft')showFig(cur-1);else if(ev.key==='ArrowRight')showFig(cur+1);
  });
  var cb=document.getElementById('copy-bib');
  cb.addEventListener('click',function(){
    var t=document.getElementById('bibtex').textContent;
    function done(){cb.textContent='Copied';setTimeout(function(){cb.textContent='Copy';},1500);}
    if(navigator.clipboard){navigator.clipboard.writeText(t).then(done,function(){});}
    else{var r=document.createRange();r.selectNodeContents(document.getElementById('bibtex'));var sel=getSelection();sel.removeAllRanges();sel.addRange(r);document.execCommand('copy');done();}
  });
  // open the experiment named in the URL hash, e.g. #exp-03
  var h=location.hash.match(/^#exp-(\d\d)$/);if(h){var d=document.getElementById('exp-'+h[1]);if(d)d.open=true;}
})();
</script>
</body>
</html>
"""

page = (
    TEMPLATE.replace("__FIGS_JSON__", figs_json)
    .replace("__FIGS__", figs_html)
    .replace("__ROWS__", rows_html)
    .replace("__READMES__", readmes_json)
    .replace("__URLS__", esc(url_list))
    .replace("__CITE_TEXT__", esc(PRIOR_WORK_TEXT))
    .replace("__PRIOR_WORK_BIBTEX__", esc(PRIOR_WORK_BIBTEX))
    .replace("__NEXP__", str(len(experiments)))
    .replace("__NDATA__", str(sum(1 for e in experiments if e["files"])))
    .replace("__NREC__", records(total_records))
    .replace("__TOTAL__", human(total))
    .replace("__REPO_NAME__", esc(REPO))
    .replace("__REPO__", REPO_URL)
    .replace("__RAW__", RAW_URL)
)
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(page)
with open(os.path.join(HERE, "dataset_urls.txt"), "w", encoding="utf-8") as fh:
    fh.write(url_list + "\n")
print(
    f"wrote {OUT} - {len(experiments)} experiments, {len(all_files)} data files ({human(total)}), {len(figures)} figures"
)
