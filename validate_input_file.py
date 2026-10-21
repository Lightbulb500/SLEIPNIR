"""
Checks a SLEIPNIR sample (input) file against Input_File_Specification.md before a run.

    python validate_input_file.py path/to/Example_InputFile.ascii

Each spectrum's flux scale is checked against its Flux_Scaled_Flag (0 = erg/s/cm^2/Angstrom, 1 = units of 1e-17).

Run it from the same folder as the notebooks, because relative Spectrum_Path values are resolved from the working directory.
Exits with status 1 if any ERROR is found (warnings do not change the exit status).
"""

import os
import sys

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = [
	'Target', 'Spectrum_Path', 'SpecType', 'MJD', 'RA', 'DEC', 'Redshift', 'Redshift_Err',
	'Redshift_Corrected_Flag', 'Extinction', 'Extinction_Corrected_Flag', 'Flux_Scaled_Flag'
]
NUMERIC_COLUMNS = [
	'MJD', 'RA', 'DEC', 'Redshift', 'Redshift_Err', 'Redshift_Corrected_Flag', 'Extinction', 'Extinction_Corrected_Flag', 'Flux_Scaled_Flag'
]


def check_spectrum_file(path, flux_units=None):
	"""
	Returns a list of (level, message) for one spectrum file, using the same read rules as Spectra_Functions.spec_reader_ascii
	flux_units is 'cgs' (Flux_Scaled_Flag 0), '1e-17' (Flux_Scaled_Flag 1) or None to skip the flux scale check
	"""

	if path[-5:] == 'ascii':
		separator = r'\s+'
	elif path[-3:] == 'csv':
		separator = ','
	elif path[-3:] == 'tsv':
		separator = '\t'
	else:
		separator = None

	try:
		spectrum = pd.read_csv(
			path, comment='#', skip_blank_lines=True, sep=separator, header=None, names=['wave', 'flux', 'fluxerr'], engine='python'
		)
	except Exception as err:
		return [('ERROR', f'cannot be read ({type(err).__name__}: {err})')]

	problems = []

	for column in ('wave', 'flux', 'fluxerr'):
		if not pd.api.types.is_numeric_dtype(spectrum[column]):
			problems.append(('ERROR', f"column '{column}' is not numeric - is there an uncommented header line? (start header lines with #)"))

	if problems:
		return problems

	if len(spectrum) < 2:
		problems.append(('ERROR', 'fewer than two rows'))
		return problems

	if spectrum['wave'].isna().any() or not (np.diff(spectrum['wave'].values) > 0).all():
		problems.append(('ERROR', 'wavelengths are not finite and strictly ascending'))

	# Real spectra have a median flux of roughly 1e-21 to 1e-13 in cgs, i.e. 1e-4 to 1e4 in units of 1e-17 - 1e-8 splits the two
	finite_flux = np.abs(spectrum['flux'].values[np.isfinite(spectrum['flux'].values) & (spectrum['flux'].values != 0)])
	if len(finite_flux) > 0:
		typical_flux = np.median(finite_flux)
		if flux_units == 'cgs' and typical_flux > 1e-8:
			problems.append(('WARNING', f'median flux is {typical_flux:.3g}, which looks like units of 1e-17 erg/s/cm^2/Angstrom, but Flux_Scaled_Flag is 0 (cgs)'))
		elif flux_units == '1e-17' and typical_flux < 1e-8:
			problems.append(('WARNING', f'median flux is {typical_flux:.3g}, which looks like cgs (erg/s/cm^2/Angstrom), but Flux_Scaled_Flag is 1 (units of 1e-17)'))

	if spectrum['fluxerr'].isna().all():
		problems.append(('ERROR', 'no error column - the line scoring needs the error spectrum, so no line can score without it'))
	elif (spectrum['fluxerr'].dropna() < 0).any():
		problems.append(('ERROR', 'negative flux errors - the third column must be a 1 sigma error, not inverse variance'))
	elif (spectrum['fluxerr'] == 0).mean() > 0.1:
		problems.append(('WARNING', 'more than 10% of the errors are exactly zero (zero errors are treated as missing)'))

	return problems


def validate_input_file(path):
	"""Returns a list of (level, message) tuples for the sample file at 'path'"""

	problems = []

	def report(level, message):
		problems.append((level, message))

	try:
		table = pd.read_csv(path, comment='#', sep='\t')
	except Exception as err:
		return [('ERROR', f'cannot be read as a tab separated file ({type(err).__name__}: {err})')]

	missing = [column for column in REQUIRED_COLUMNS if column not in table.columns]
	if missing:
		return [('ERROR', f'missing column(s): {", ".join(missing)} (names are case sensitive, all {len(REQUIRED_COLUMNS)} are needed)')]

	extra = [column for column in table.columns if column not in REQUIRED_COLUMNS]
	if extra:
		report('WARNING', f'unused column(s) will be ignored: {", ".join(extra)}')

	# Numeric columns - anything that is not a number (other than a blank) is an error
	numbers = {}
	for column in NUMERIC_COLUMNS:
		numbers[column] = pd.to_numeric(table[column], errors='coerce')
		bad = table[column].notna() & numbers[column].isna()
		for row in table.index[bad]:
			report('ERROR', f"row {row + 1} ({table.at[row, 'Target']}): {column} = '{table.at[row, column]}' is not a number")

	for row in table.index:

		name = table.at[row, 'Target']
		label = f'row {row + 1} ({name})'

		def row_report(level, message):
			report(level, f'{label}: {message}')

		if pd.isna(name):
			row_report('ERROR', 'Target is blank')
		elif not all(character.isalnum() or character in '._-+' for character in str(name)):
			row_report('WARNING', 'Target has characters other than letters, numbers and . _ - + - it is used in file names')

		spec_type = table.at[row, 'SpecType']
		if not isinstance(spec_type, str) or spec_type.strip().upper() != 'ASCII':
			row_report('ERROR', f"SpecType '{spec_type}' is not supported - only ASCII is currently implemented")

		flux_units = {0: 'cgs', 1: '1e-17'}.get(numbers['Flux_Scaled_Flag'][row])  # None if the flag is invalid (reported below)

		spec_path = table.at[row, 'Spectrum_Path']
		if not isinstance(spec_path, str) or not os.path.isfile(spec_path):
			row_report('ERROR', f"Spectrum_Path '{spec_path}' does not exist (relative paths start from the current folder)")
		else:
			for level, message in check_spectrum_file(spec_path, flux_units):
				row_report(level, f'spectrum file: {message}')

		for column, low, high in (('RA', 0, 360), ('DEC', -90, 90)):
			value = numbers[column][row]
			if not np.isfinite(value) or not low <= value <= high:
				row_report('ERROR', f'{column} = {table.at[row, column]} must be decimal degrees between {low} and {high}')

		z_flag = numbers['Redshift_Corrected_Flag'][row]
		ext_flag = numbers['Extinction_Corrected_Flag'][row]
		for column, flag in (('Redshift_Corrected_Flag', z_flag), ('Extinction_Corrected_Flag', ext_flag)):
			if flag not in (0, 1):
				row_report('ERROR', f'{column} must be exactly 0 or 1 (found {table.at[row, column]}) - anything else is treated as 1')

		if numbers['Flux_Scaled_Flag'][row] not in (0, 1):
			row_report('ERROR', f"Flux_Scaled_Flag must be exactly 0 or 1 (found {table.at[row, 'Flux_Scaled_Flag']}) - SLEIPNIR_Analysis stops with an error otherwise")

		redshift = numbers['Redshift'][row]
		if pd.isna(table.at[row, 'Redshift']):
			row_report('WARNING', 'Redshift is blank - z = 0 will be assumed and the spectrum treated as already rest-frame')
		elif np.isfinite(redshift) and redshift < 0:
			row_report('WARNING', 'Redshift is negative')

		extinction = numbers['Extinction'][row]
		if pd.isna(table.at[row, 'Extinction']):
			if ext_flag == 1:
				row_report('WARNING', 'Extinction is blank - it is not needed for an already corrected spectrum, but the dust map will still be queried; use 0 to avoid that')
			else:
				row_report('WARNING', 'Extinction is blank - it will be looked up from the SFD dust map (the map files must be installed)')
		elif np.isfinite(extinction) and (extinction < 0 or extinction > 1):
			row_report('WARNING', f'Extinction (E(B-V)) = {extinction} is outside 0 - 1 mag, check the units')

	duplicated = table['Target'][table['Target'].duplicated(keep=False) & table['Target'].notna()].unique()
	for name in duplicated:
		report('ERROR', f"Target '{name}' appears more than once - Targets must be unique (output files are named from them)")

	return problems


if __name__ == '__main__':

	if len(sys.argv) != 2:
		sys.exit('usage: python validate_input_file.py <sample file>')

	found = validate_input_file(sys.argv[1])

	for level, message in found:
		print(f'{level}: {message}')

	errors = sum(level == 'ERROR' for level, _ in found)
	print(f'\n{errors} error(s), {len(found) - errors} warning(s)')
	sys.exit(1 if errors else 0)
