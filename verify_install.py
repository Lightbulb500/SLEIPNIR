"""
Checks a SLEIPNIR environment: Python version, required packages, the pylick index mapping, the dustmaps SFD data and the
project imports. Run it from the repository root (the folder containing Modules/ and Configuration_Files/):

    python verify_install.py

Exits with status 1 if anything fails.
"""

import importlib
import os
import sys

failures = []


def report(ok, label, detail=''):
	print(f"  [{'OK' if ok else 'FAIL'}] {label}" + (f' - {detail}' if detail else ''))
	if not ok:
		failures.append(label)


import platform

print(f'Python {sys.version.split()[0]} ({sys.executable}) - {platform.system()} {platform.machine()}')
report(sys.version_info[:2] == (3, 12), 'Python 3.12', f'found {sys.version_info.major}.{sys.version_info.minor}')

print('\nPackages')
for module in (
		'ssl', 'numpy', 'scipy', 'pandas', 'astropy', 'matplotlib', 'PIL', 'tqdm', 'colorama', 'str2bool', 'requests',
		'ipywidgets', 'dust_extinction', 'dustmaps', 'spectres', 'pylick'
):
	try:
		mod = importlib.import_module(module)
		report(True, module, getattr(mod, '__version__', ''))
	except Exception as err:
		report(False, module, f'{type(err).__name__}: {err}')

print('\nFunctional checks')
try:
	import numpy as np
	from astropy import units as u
	from dust_extinction.parameter_averages import F99

	factor = F99(Rv=3.1).extinguish(np.array([4000.0, 6000.0]) * u.AA, Ebv=0.05)
	report(bool(np.all((factor > 0) & (factor < 1))), 'F99 extinction (dust_extinction)')
except Exception as err:
	report(False, 'F99 extinction (dust_extinction)', f'{type(err).__name__}: {err}')

try:
	from spectres import spectres

	new_flux = spectres(np.arange(4010.0, 4090.0, 20.0), np.arange(4000.0, 4100.0, 5.0), np.ones(20))
	report(bool(np.allclose(new_flux, 1.0)), 'Rebinning (spectres)')
except Exception as err:
	report(False, 'Rebinning (spectres)', f'{type(err).__name__}: {err}')

try:
	from pylick.indices import IndexLibrary

	names = [str(name) for name in IndexLibrary(index_keys=np.array([24, 26, 32])).names]
	report(names == ['D4000', 'Hdelta_A', 'Hgamma_A'], 'pylick index numbers 24, 26, 32', str(names))
except Exception as err:
	report(False, 'pylick index numbers 24, 26, 32', f'{type(err).__name__}: {err}')

try:
	from dustmaps.config import config
	from dustmaps.sfd import SFDQuery

	data_dir = config.get('data_dir')
	SFDQuery()  # Raises if the SFD map files have not been downloaded
	report(True, 'dustmaps SFD data', str(data_dir))
except Exception as err:
	report(False, 'dustmaps SFD data', f'{type(err).__name__}: {err} - see step 5 of INSTALL.md')

"""
print('\nProject imports')
sys.path.insert(0, os.getcwd())
if not os.path.isdir('Modules'):
	report(False, 'Modules/ folder found', 'run this from the repository root')
else:
	for module in (
			'Modules.Core.Config_Readers', 'Modules.Core.Core_Functions', 'Modules.Spectra.Line_Lists',
			'Modules.Spectra.Spectra_Functions', 'Modules.Plotting.Plotting_Functions'
	):
		try:
			importlib.import_module(module)
			report(True, module)
		except SystemExit:
			report(False, module, 'exited on import - a configuration file was not found (run from the repository root)')
		except Exception as err:
			hint = ' - see step 6 of INSTALL.md' if "'Core'" in str(err) else ''
			report(False, module, f'{type(err).__name__}: {err}{hint}')
"""

print('\n' + ('All checks passed.' if not failures else f'{len(failures)} check(s) failed: ' + ', '.join(failures)))
sys.exit(1 if failures else 0)
