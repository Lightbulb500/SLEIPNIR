# SLEIPNIR - environment set up

A fresh Anaconda / Miniconda environment on Python 3.12, with everything possible installed through conda (conda-forge) and
`pylick` installed through pip without its dependency pins.

Commands are for a bash / zsh shell (macOS, Linux, WSL). On Windows use the Anaconda Prompt and run the commands in step 3 one at a time
instead of the `for` loop.

## 1. Create the environment

```bash
# macOS only: check the architecture first - 'uname -m' and conda's 'platform' should agree
uname -m                                # arm64 = Apple Silicon, x86_64 = Intel
conda info | grep platform              # osx-arm64 = native Apple Silicon, osx-64 = Intel (or Rosetta)
echo "CONDA_SUBDIR=[$CONDA_SUBDIR]"     # normally empty

# Apple Silicon (osx-arm64). On an Intel Mac use osx-64 in both places. On Linux / Windows leave out the CONDA_SUBDIR prefix and the 'subdir' line.
CONDA_SUBDIR=osx-arm64 conda create -n sleipnir --override-channels -c conda-forge python=3.12 -y
conda activate sleipnir
conda config --env --set subdir osx-arm64
conda config --env --set channel_priority strict

# Check inside the activated environment - all three must agree and the python line must run without an error
conda info | grep platform              # must still say osx-arm64
python -c "import ssl, platform; print(platform.machine())"     # must print arm64
conda config --show-sources             # look for any 'subdir' or 'channels' left over from an older set up
```

The `subdir` line pins the environment to one architecture so later installs can never pull in packages built for the other one.

Every `conda` command below carries `--override-channels -c conda-forge` explicitly. Your global conda configuration (`~/.condarc`) can
list other channels (`defaults`, `astroconda`, `conda-pypi`...), and `conda config --env` only adds to those rather than replacing them.
Mixing Python from one channel with libraries such as OpenSSL from another is a well known way to end up with a Python whose `ssl` module
doesn't load - which in turn stops `pip` from reaching PyPI. Keep the old `astroconda` channel out of this environment.

## 2. Core stack (all conda)

```bash
conda install -y --override-channels -c conda-forge numpy scipy pandas astropy matplotlib pillow tqdm colorama requests jupyterlab ipywidgets ipykernel
```

`ipywidgets` is only needed so the `tqdm.notebook` progress bars render in the notebooks; `requests` is installed here because
`pylick` needs it and step 4 skips pylick's own dependencies.

## 3. Domain packages (conda where available, pip as the fallback)

```bash
for pkg in dust_extinction dustmaps spectres str2bool; do
    conda install -y --override-channels -c conda-forge $pkg || python -m pip install $pkg
done
```

Each package is tried on conda-forge first and only falls back to pip if conda cannot find it. `str2bool` is not on conda-forge, so it
always comes from pip, and conda printing `PackagesNotFoundInChannelsError` for it just before the pip install is expected. (The conda
dependencies of the others are pulled in automatically; `dustmaps` brings `healpy`, `h5py` and `progressbar2`.) Afterwards,
`conda list | grep pypi` shows which packages came from pip.

Before relying on pip, make sure it can reach PyPI: `python -c "import ssl"` must print nothing. If it raises an error see
'Troubleshooting' below.

## 4. pylick (pip, ignoring its dependency pins)

```bash
python -m pip install pylick --no-deps
```

Do this after everything above. `--no-deps` stops pip from replacing the conda packages: pylick 1.0.2 declares `astropy>=5.2,<6.0`,
which would otherwise drag astropy (and through it numpy) back to old versions. Its remaining requirements (numpy, scipy, astropy,
requests) are all installed in steps 2-3.

* Tested on Python 3.12 with numpy 2.4.4, scipy 1.17.1 and astropy 8.0.1: `pylick.indices` and `pylick.analysis` import,
  index numbers 24, 26 and 32 resolve to D4000, Hdelta_A and Hgamma_A (the names SLEIPNIR_Analysis asserts), and a Lick index
  calculation through `Spectra_Functions.lick_index_calculation` runs.
* `pip check` will now report the pylick / astropy conflict. That is expected and can be ignored.
* Don't use `pip install --upgrade pylick` later without `--no-deps`.

## 5. Download the SFD dust map (one-off)

`SLEIPNIR_Analysis` only queries the SFD map for objects that have no `Extinction` value in the sample file (the map is loaded the first
time that happens). If every object in your samples has one you can skip this step; otherwise:

```bash
python -c "from dustmaps.config import config; config['data_dir'] = '/path/to/dustmaps_data'"
python -c "import dustmaps.sfd; dustmaps.sfd.fetch()"
```

The first command stores the folder in `~/.dustmapsrc`, so it only has to be done once per machine. Use a folder outside the repository.

If the dustmaps auto download fails, you can download the required files manually from the Harvard Dataverse website directly.

https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/EWCNL5

Download the files:

	SFD_dust_4096_ngp.fits
	SFD_dust_4096_sgp.fits
	
Ensure these are placed in the defined dustmaps datafolder:

	'/path/to/dustmaps_data/sfd/*'

## 6. Project layout and the `Core` import

Run everything from the repository root:

```
<repo root>/
    SLEIPNIR_Analysis.ipynb
    SLEIPNIR_Plots.ipynb
    verify_install.py
    Configuration_Files/{Cuts,Processing,Scoring,Plots}/...
    Modules/{Core,Spectra,Plotting}/...
```

The notebooks and `Plotting_Functions` import `Modules.Core...`, but `Spectra_Functions` imports `Core.Core_Functions`, which fails
from a clean environment (`ModuleNotFoundError: No module named 'Core'`). Either:

## 7. Register the kernel and start Jupyter

```bash
python -m ipykernel install --user --name sleipnir --display-name "Python 3.12 (SLEIPNIR)"
jupyter lab        # from the repository root, then pick the 'Python 3.12 (SLEIPNIR)' kernel
```

## 8. Verify

```bash
python verify_install.py
```

It checks the Python version, every package, a quick functional test of extinction / rebinning / pylick, the SFD data, and that each
project module imports. It exits with status 1 and says which step to revisit if anything fails.

## Recording the environment

```bash
conda env export --no-builds > sleipnir_environment_snapshot.yml
```

This captures the versions used. If you rebuild from it, repeat step 4 afterwards, as the pylick `--no-deps` install can't be expressed
in an `environment.yml`.

## Troubleshooting

**`ssl module is unavailable` / `Could not fetch URL https://pypi.org/simple/...` from pip.** The environment's Python has a broken
`ssl` module, nearly always from mixed channels (e.g. Python from `defaults` with OpenSSL from conda-forge). Check with:

```bash
python -c "import ssl"
conda list --show-channel-urls | grep -E "^(python|openssl|libffi|ca-certificates|certifi) "
```

If `import ssl` fails, or `python` and `openssl` come from different channels or architectures, the quickest fix is to rebuild the environment using
the steps above rather than repair it:

```bash
conda deactivate
conda env remove -n sleipnir
```

then repeat from step 1.

**Mixed architectures on macOS (`ssl` broken even with conda-forge only).** An environment must contain packages for one architecture only.
The sign of a mix is conda reporting `Platform: osx-64` while the plan lists something like
`openssl conda-forge/osx-arm64::... --> conda-forge/osx-64::...`. That happens when the environment was created under a different
architecture from the one conda is now using, for example an Intel (osx-64) Miniconda running on an Apple Silicon Mac, a Terminal
opened under Rosetta, or `CONDA_SUBDIR` set at creation time. The result is a Python that cannot load its own libraries. Fix it by removing
the environment and recreating it with the explicit `CONDA_SUBDIR=... conda create` and `conda config --env --set subdir ...` lines in step 1.
A common source is two configuration files that disagree: `conda config --show-sources` can show `subdir: osx-64` in
`<miniconda root>/.condarc` and `subdir: osx-arm64` in `~/.condarc`. The per-environment pin from step 1 overrides both for this
environment, but the stray line will affect other environments; to remove it from the Miniconda root file:

```bash
conda config --file ~/miniconda3/.condarc --remove-key subdir
```

If conda reports a different platform inside the activated environment than outside it, something in the environment is forcing it - check `conda config --show-sources`, `conda env config vars list` and `cat $CONDA_PREFIX/.condarc`.
A native Apple Silicon install (Miniconda for osx-arm64, with `osx-arm64` in those lines) is the better long-term choice, but either works
as long as it is used consistently.

**`No module named 'Core'`.** See step 6.

**`pip check` reports a pylick conflict.** Expected after step 4 - see the notes there.
