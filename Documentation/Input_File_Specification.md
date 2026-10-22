# SLEIPNIR input (sample) file specification

The input file lists the spectra for `SLEIPNIR_Analysis` to process: one row per spectrum, one column per variable described here.
Its path is set by `Sample_Meta_File` in the first cell of the notebook. `validate_input_file.py` checks a file against everything below:

```bash
python validate_input_file.py path/to/Example_InputFile.ascii     # run from the folder the notebooks run in
```

## File format

* **Tab separated text** with a **header row**. The notebook reads it with `pd.read_csv(Sample_Meta_File, comment='#', sep='\t')`.
* Column names are case sensitive and must match exactly. The column order does not matter, but **all 12 columns must be present** - a missing
  column is a `KeyError` even if you would have left its values blank.
* `#` starts a comment **anywhere on a line** (not just at the start), so `#` must not appear in a `Target` or a `Spectrum_Path`.
  Blank lines are skipped.
* Columns must be separated by a single tab. Spaces between columns will not work.
* A blank value is read as missing (`NaN`). `NaN`, `nan` and `NA` are also read as missing.
* Rows are processed in file order, and the results file keeps that order.

## Column reference

| Column | Type | Units / allowed values | Blank allowed? | Used for |
|---|---|---|---|---|
| `Target` | text | Unique identifier | No | `ID` in the results file; names the processed spectrum and plot files |
| `Spectrum_Path` | text | Path to the spectrum file | No | Where the spectrum is read from |
| `SpecType` | text | `ASCII` (any case) | No | Selects the spectrum reader; only `ASCII` is implemented |
| `MJD` | number | Modified Julian Date | Yes (informational) | Written to the results file and shown on the plots |
| `RA` | number | Decimal degrees (ICRS) | No | SFD dust map lookup, sample sky plot, results file, Legacy Survey cutout |
| `DEC` | number | Decimal degrees (ICRS) | No | As `RA` |
| `Redshift` | number | z | Yes (see below) | Rest-frame shift, redshift cuts, skyline positions |
| `Redshift_Err` | number | z | Yes (becomes 0) | Bookkeeping only - not used by SLEIPNIR |
| `Redshift_Corrected_Flag` | integer | `0` or `1` | No | Whether the spectrum is already in the rest frame |
| `Extinction` | number | E(B-V), magnitudes | Yes (see below) | Galactic extinction correction |
| `Extinction_Corrected_Flag` | integer | `0` or `1` | No | Whether the spectrum is already corrected for Galactic extinction |
| `Flux_Scaled_Flag` | integer | `0` or `1` | No (checked strictly) | Whether the flux and error are already in units of 1e-17 erg/s/cm^2/Angstrom |

## Column details

### `Target`
A unique name for the spectrum. It becomes the `ID` column of the results file and part of the file names `<Target>_Processed_Spectrum.ascii`
and the classification plot names, and `SLEIPNIR_Plots` finds the processed spectra by this name. Duplicates overwrite each other's files.
Stick to letters, numbers and `. _ - +`; no slashes, tabs or `#`. Several spectra of one object need different `Target` values
(for example `AT2018dyk_epoch1`).

### `Spectrum_Path`
Absolute, or relative to the folder the notebook runs from. **Every file must exist and be readable, including those of objects that the
redshift cut will reject**, because the spectrum is read before the cut. A missing file ends the run. See 'Spectrum files' below for the format.

### `SpecType`
Only `ASCII` is currently supported, in any case. Every row needs a value. `SLEIPNIR_Analysis` stops with an error for anything else.

### `MJD`
Observation date. It is not used in any calculation, only written out and shown on the plots, so a blank is harmless (it appears as `nan`).

### `RA`, `DEC`
Decimal degrees (for example `150.1234`, not `10:00:29.6`), in ICRS (J2000). A sky position is built for every object, so both must be numbers.

### `Redshift` and `Redshift_Err`
Redshift of the object. If `Redshift` is blank, SLEIPNIR warns, assumes z = 0 and **forces `Redshift_Corrected_Flag` to 1**, meaning the
spectrum is treated as already being in the rest frame. Check that this is true for any row you leave blank. `Redshift_Err` is not currently directly used by
SLEIPNIR; a blank becomes 0 and the value is only carried into the results file.

The cuts come from `Initial_Cuts.config`: `Redshift < High_z_Cut` is applied to every spectrum, and `Redshift > Low_z_Cut` only when
`Redshift_Corrected_Flag` is 0. Objects that fail are skipped and listed as rejected.

### `Redshift_Corrected_Flag`
| Value | Meaning | What SLEIPNIR does |
|---|---|---|
| `0` | Wavelengths in the file are **observed frame** | Shifts them to the rest frame, wavelength / (1 + z); applies both redshift cuts |
| `1` | Wavelengths in the file are **already rest frame** | Leaves the wavelengths alone; skips the low-z cut only |

It must be exactly `0` or `1`: any other value, including a blank, behaves as `1`. With flag `1` you should **still give the true redshift**,
because it is also used for the high-z cut, to place the skylines in the rest frame, and to evaluate the extinction correction at the observed wavelengths.

### `Extinction`
Galactic reddening E(B-V) in magnitudes, on the Schlafly & Finkbeiner (2011) scale (that is, the SFD value multiplied by 0.86). The correction
uses the Fitzpatrick (1999) law with Rv = 3.1. If it is blank, SLEIPNIR warns and looks the value up from the SFD dust map at `RA`, `DEC`
(multiplied by 0.86), which needs the map files from step 5 of `INSTALL.md`.

### `Extinction_Corrected_Flag`
| Value | Meaning | What SLEIPNIR does |
|---|---|---|
| `0` | Fluxes are **not** corrected for Galactic extinction | Divides flux and error by the F99 transmission for `Extinction` |
| `1` | Fluxes are **already** corrected | No correction. `Extinction` is not used in the analysis. However the `Extinction` value is propagated to the output file |

As with the redshift flag, it must be exactly `0` or `1`. For a corrected spectrum it is preferred to still include the value used in the correction as
this value is propagated as is to the output file, regardless if it is used directly by SLEIPNIR.

### `Flux_Scaled_Flag`
The units of the flux and flux error columns in this spectrum's file:

| Value | Meaning | What SLEIPNIR does |
|---|---|---|
| `0` | **Not scaled**: erg/s/cm^2/Angstrom (cgs, values typically around 1e-18 to 1e-15) | Multiplies flux and error by 1e17 as it reads the file |
| `1` | **Already scaled**: units of 1e-17 erg/s/cm^2/Angstrom (as native DESI and SDSS products are) | No conversion |

This follows the convention of the other two flags (0 = SLEIPNIR does it, 1 = already done), so a raw spectrum, in the observed frame, in cgs and
uncorrected for extinction, is `0` in all three. Unlike those, it is **checked strictly**: a blank or any value other than 0 or 1 makes
`SLEIPNIR_Analysis` stop before it processes anything, naming the offending `Target` values, because a wrong value would put the flux
out by a factor of 1e17. Because it is set per spectrum, one sample can mix both conventions.

Whatever the input units, everything downstream is in units of 1e-17 erg/s/cm^2/Angstrom: the analysis, the line fluxes in the results
file, the saved processed spectra, and the plots (which label their axes with that unit). The notebook prints a warning for any
spectrum whose median flux, after conversion, falls outside 1e-4 to 1e5 (which points to a wrong flag), and `validate_input_file.py` makes
the same check on each file before you run.

## Spectrum files (the files named by `Spectrum_Path`)

* **Columns:** wavelength, flux, flux error, in that order, with **no header row**. Put any header text on lines starting with `#`.
  An uncommented header line makes the columns non-numeric and the read will fail.
* **Delimiter:** chosen by the end of the file name. `ascii` means whitespace separated, `csv` comma separated and `tsv` tab separated
  (all lower case). For other file types, an attempt at determining the delimited is made.
* **Wavelength:** Angstroms, strictly ascending, in the observed frame if `Redshift_Corrected_Flag` is 0. The line list is labelled as air
  wavelengths, so the spectrum wavelengths are expected to be on the same system.
* **Flux and flux error units:** erg/s/cm^2/Angstrom (flag `0`) or units of 1e-17 erg/s/cm^2/Angstrom (flag `1`), as set by that
  spectrum's `Flux_Scaled_Flag` (see above). The flux and the error must use the same units. The line detection works on continuum
  normalised flux, so the thresholds do not depend on the scale.
* **Flux error:** a 1 sigma error in the same units as the flux. It is **not** inverse variance: convert such values first
  (error = 1 / sqrt(IVAR)). **Treat this column as required.** With only two columns the pEQW is still measured, but the error spectrum SNR cuts
  can never be met, so no line scores (in a test the same spectrum scored 11 with errors and 0 without). Exactly zero errors are
  treated as missing - under the assumption of flagged pixels.
* **Gaps and bad pixels:** `NaN` fluxes are allowed and are interpolated over.
* **Coverage:** the scoring lines lie between 3759 and 7894 Angstroms (rest frame). A line the spectrum does not cover is not scored, and if
  that is `[FeXI]7894` the candidate threshold is lowered by 2 (see `ECLE_Scoring.config`).

## Example

Columns separated by tabs. `ExampleObject_1` is a raw spectrum: observed frame, uncorrected, in cgs units. `ExampleObject_2` is already rest frame,
extinction corrected and in units of 1e-17. `ExampleObject_3` is in cgs units and has no redshift or extinction, so it would be treated as z = 0
with the dust map queried.

```
# Lines starting with # are ignored
Target	Spectrum_Path	SpecType	MJD	RA	DEC	Redshift	Redshift_Err	Redshift_Corrected_Flag	Extinction	Extinction_Corrected_Flag	Flux_Scaled_Flag
ExampleObject_1	Example_Inputs/ExampleObject_1/spec_a.ascii	ASCII	59000.5	150.1234	2.2345	0.1000	0.0001	0	0.0200	0	0
ExampleObject_2	Example_Inputs/ExampleObject_2/spec_b.csv	ASCII	59010.2	210.5000	-5.1000	0.0550	0.0002	1	0	1	1
ExampleObject_3	Example_Inputs/ExampleObject_3/spec_c.ascii	ASCII	59020.0	33.3333	12.0000			1		1	0
```

## Quick checklist

1. All 12 column names present and spelled exactly; tab separated; no `#` in names or paths.
2. `Target` unique and filename safe.
3. Every `Spectrum_Path` exists (even for objects you expect to be rejected) and `SpecType` is `ASCII`.
4. `RA` / `DEC` in decimal degrees.
5. All three flags exactly 0 or 1 (`Flux_Scaled_Flag` is enforced; a wrong value is a factor of 1e17), and a real redshift even when the spectrum is already rest frame.
6. Spectra: no uncommented header, ascending wavelengths in Angstrom, flux and error in the units the `Flux_Scaled_Flag` says, error column present as 1 sigma.
7. Run `validate_input_file.py` on the file.
