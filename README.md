# scriptsForPypeIt_DEIMOS
This repo contains scripts to assist in reduction of DEIMOS slit masks with PypeIt. The scripts are designed to be ran on UCSC's Lux cluster, and handle creation of PypeIt files for 1d and 2d coadding, as well as reformatting the resulting coadded files. I reduced data from DEIMOS using PypeIt 1.10, and these scripts should be compatible with reduction done with mosaics or individual detectors. 

There are two main scripts: `preCoaddPipeline.py` and `postCoaddPipeline.py`

### `preCoaddPipeline`
This script uses the files in the `Science/` directory that PypeIt outputs during reduction to create parameter files for 1d and 2d coadding, and a respective slurm scripts. As an auxiliary output, the script also creates "slit tag" files that synthesize the output of `pypeit_parse_slits` for each reduced fits file into one text file. I found these useful in optimizing the reduction parameters, and they are used in the creation oof 2d coadd files. 

### `postCoaddPipeline`
This script reformats the coadded files into a specific format and naming convention, and creates an object list. The naming convention is `keck_IdxInObjList_Objname.fits` for 1d spectra and is the same for 2d spectra with an added suffix: `_spec2D`. 
