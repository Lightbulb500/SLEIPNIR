# SLEIPNIR - references and attribution

SLEIPNIR makes use of multiple software packages and additional sources of data as detailed here.

The BibTeX entries for everything below are in `references.bib` (keys are shown in brackets).

### Utilised Software packages

| Package | Used for | Cite |
|---|---|---|
| NumPy | Array handling throughout | Harris et al. 2020 [`Harris2020`] |
| SciPy | Filtering (median, Savitzky-Golay, FFT), integration, constants | Virtanen et al. 2020 [`Virtanen2020`] |
| pandas | Reading the input file and writing results | McKinney 2010 [`McKinney2010`]; The pandas development team 2020 [`pandas2020`] |
| Matplotlib | The classification and summary plots | Hunter 2007 [`Hunter2007`] |
| Astropy | Units, coordinates, convolution smoothing | Astropy Collaboration 2013, 2018, 2022 [`Astropy2013`, `Astropy2018`, `Astropy2022`] |
| SpectRes | Rebinning the spectra | Carnall 2017 [`Carnall2017`] |
| dust_extinction | Galactic extinction correction (Fitzpatrick 1999 law) | Gordon 2024 [`Gordon2024`] |
| dustmaps | SFD dust map lookup when no extinction is supplied | Green 2018 [`Green2018`] |
| pyLick | D4000 and Lick index measurements | Borghi et al. 2022 [`Borghi2022`] |

### Models, calibrations and index definitions

| Reference | What it is for |
|---|---|
| Schlegel, Finkbeiner & Davis 1998 [`Schlegel1998`] | The SFD dust map queried by dustmaps |
| Schlafly & Finkbeiner 2011 [`Schlafly2011`] | The recalibration of SFD (E(B-V) multiplied by 0.86) that SLEIPNIR applies to the map value |
| Fitzpatrick 1999 [`Fitzpatrick1999`] | The R_V = 3.1 extinction law used for the correction |
| Bruzual 1983 [`Bruzual1983`] | The D4000 definition (blue 3750-3950, red 4050-4250 Angstrom) used by pyLick |
| Worthey & Ottaviani 1997 [`WortheyOttaviani1997`] | The H-delta A and H-gamma A index definitions |
| Cardiel et al. 1998 [`Cardiel1998`] | The signal-to-noise method pyLick uses for the index uncertainties |


### Imaging services

DESI Legacy Imaging Surveys - (Dey et al. 2019 [`Dey2019`])

The Legacy Surveys consist of three individual and complementary projects: the Dark Energy Camera Legacy Survey (DECaLS; Proposal ID #2014B-0404; PIs: David Schlegel and Arjun Dey), the Beijing-Arizona Sky Survey (BASS; NOAO Prop. ID #2015A-0801; PIs: Zhou Xu and Xiaohui Fan), and the Mayall z-band Legacy Survey (MzLS; Prop. ID #2016A-0453; PI: Arjun Dey). DECaLS, BASS and MzLS together include data obtained, respectively, at the Blanco telescope, Cerro Tololo Inter-American Observatory, NSF’s NOIRLab; the Bok telescope, Steward Observatory, University of Arizona; and the Mayall telescope, Kitt Peak National Observatory, NOIRLab. Pipeline processing and analyses of the data were supported by NOIRLab and the Lawrence Berkeley National Laboratory (LBNL). The Legacy Surveys project is honored to be permitted to conduct astronomical research on Iolkam Du’ag (Kitt Peak), a mountain with particular significance to the Tohono O’odham Nation.

NOIRLab is operated by the Association of Universities for Research in Astronomy (AURA) under a cooperative agreement with the National Science Foundation. LBNL is managed by the Regents of the University of California under contract to the U.S. Department of Energy.

This project used data obtained with the Dark Energy Camera (DECam), which was constructed by the Dark Energy Survey (DES) collaboration. Funding for the DES Projects has been provided by the U.S. Department of Energy, the U.S. National Science Foundation, the Ministry of Science and Education of Spain, the Science and Technology Facilities Council of the United Kingdom, the Higher Education Funding Council for England, the National Center for Supercomputing Applications at the University of Illinois at Urbana-Champaign, the Kavli Institute of Cosmological Physics at the University of Chicago, Center for Cosmology and Astro-Particle Physics at the Ohio State University, the Mitchell Institute for Fundamental Physics and Astronomy at Texas A&M University, Financiadora de Estudos e Projetos, Fundacao Carlos Chagas Filho de Amparo, Financiadora de Estudos e Projetos, Fundacao Carlos Chagas Filho de Amparo a Pesquisa do Estado do Rio de Janeiro, Conselho Nacional de Desenvolvimento Cientifico e Tecnologico and the Ministerio da Ciencia, Tecnologia e Inovacao, the Deutsche Forschungsgemeinschaft and the Collaborating Institutions in the Dark Energy Survey. The Collaborating Institutions are Argonne National Laboratory, the University of California at Santa Cruz, the University of Cambridge, Centro de Investigaciones Energeticas, Medioambientales y Tecnologicas-Madrid, the University of Chicago, University College London, the DES-Brazil Consortium, the University of Edinburgh, the Eidgenossische Technische Hochschule (ETH) Zurich, Fermi National Accelerator Laboratory, the University of Illinois at Urbana-Champaign, the Institut de Ciencies de l’Espai (IEEC/CSIC), the Institut de Fisica d’Altes Energies, Lawrence Berkeley National Laboratory, the Ludwig Maximilians Universitat Munchen and the associated Excellence Cluster Universe, the University of Michigan, NSF’s NOIRLab, the University of Nottingham, the Ohio State University, the University of Pennsylvania, the University of Portsmouth, SLAC National Accelerator Laboratory, Stanford University, the University of Sussex, and Texas A&M University.

BASS is a key project of the Telescope Access Program (TAP), which has been funded by the National Astronomical Observatories of China, the Chinese Academy of Sciences (the Strategic Priority Research Program “The Emergence of Cosmological Structures” Grant # XDB09000000), and the Special Fund for Astronomy from the Ministry of Finance. The BASS is also supported by the External Cooperation Program of Chinese Academy of Sciences (Grant # 114A11KYSB20160057), and Chinese National Natural Science Foundation (Grant # 12120101003, # 11433005).

The Legacy Survey team makes use of data products from the Near-Earth Object Wide-field Infrared Survey Explorer (NEOWISE), which is a project of the Jet Propulsion Laboratory/California Institute of Technology. NEOWISE is funded by the National Aeronautics and Space Administration.

The Legacy Surveys imaging of the DESI footprint is supported by the Director, Office of Science, Office of High Energy Physics of the U.S. Department of Energy under Contract No. DE-AC02-05CH1123, by the National Energy Research Scientific Computing Center, a DOE Office of Science User Facility under the same contract; and by the U.S. National Science Foundation, Division of Astronomical Sciences under Contract No. AST-0950945 to NOAO.

### Skyline List

`Line_Lists.py` uses a slightly modified skyline list obtained from <https://www.astro.keele.ac.uk/jkt/GrSpInstructions/skylines.dat>. 

### Other Infrastructure packages

tqdm, colorama, str2bool, Pillow, requests, and Jupyter / IPython
