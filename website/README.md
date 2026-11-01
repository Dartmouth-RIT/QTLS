# QTLS — Dataset Website

A simple, single-page catalog for the QTLS coherent-control dataset. Each
experiment is one row showing its type (measured / simulated), its total data
size, a download button for every data file, and its full documentation.

## Where the content comes from

| Content | Source |
|---|---|
| Experiment list, titles, descriptions, documentation | `../src/dataset_creation_scripts/NN_*/README.md` |
| Data files and sizes | `../dataset/experiment_N/*` (Git LFS) |

To publish data for a new experiment, add its files under
`dataset/experiment_N/` (tracked with Git LFS). The page picks them up on the
next build.

## Files

| File | Purpose |
|---|---|
| `build_site.py` | Generates `index.html` and `dataset_urls.txt` |
| `index.html` | The built page (generated, not committed) |
| `dataset_urls.txt` | Plain list of every data-file URL, for bulk download (generated, not committed) |

## How downloads work

GitHub Pages cannot serve Git LFS files, so each download link points at
GitHub's LFS media URL for the repository, e.g.

```
https://media.githubusercontent.com/media/Dartmouth-RIT/TLS-Data-Paper/main/dataset/experiment_3/experiment_3_dataset_long.pkl
```

File sizes are read from the LFS pointer files, so the build works on a
checkout that has not downloaded the LFS objects (as in CI). Downloads count
against the repository owner's Git LFS bandwidth quota.

The whole release (several GB) is too large for one zip on Pages or a GitHub
Release asset (2 GB limit per file), so the page offers two bulk options
instead: `git lfs` clone, or `wget -i dataset_urls.txt`. For a single
archive with a DOI, consider depositing the data on Zenodo and linking it.

The repository and branch used in the links default to
`Dartmouth-RIT/TLS-Data-Paper` and `main`. In GitHub Actions the repository
comes from `GITHUB_REPOSITORY`; set `DATA_BRANCH` to point at another branch.

## Rebuild and view locally

```bash
python website/build_site.py          # standard library only
cd website && python -m http.server 8000   # then open http://localhost:8000
```

## Deploy to GitHub Pages

`.github/workflows/deploy-pages.yml` rebuilds the page and publishes it on
every push to `main` that touches `website/`, an experiment README or
`dataset/` (and can be run manually from the **Actions** tab).

One-time setup: **Settings → Pages → Build and deployment → Source:
GitHub Actions**.
