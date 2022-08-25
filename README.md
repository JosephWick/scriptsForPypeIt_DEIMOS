# scriptsForPypeIt_DEIMOS
This repo contains scripts to assist in reduction of DEIMOS slit masks with PypeIt. The scripts are designed to be ran on UCSC's Lux cluster, and handle creation of PypeIt files for 1d and 2d coadding, as well as reformatting the resulting coadded files. I reduced data from DEIMOS using PypeIt 1.10, and these scripts should be compatible with reduction done with mosaics or individual detectors. It should be noted that these scripts were not designed for use with fluxing 

There are two main scripts: `preCoaddPipeline.py` and `postCoaddPipeline.py`; for a more detailed walkthrough of my entire PypeIt process, see the bottom of this document. 

### `preCoaddPipeline`
This script uses the files in the `Science/` directory that PypeIt outputs during reduction to create parameter files for 1d and 2d coadding, and a respective slurm scripts. As an auxiliary output, the script also creates "slit tag" files that synthesize the output of `pypeit_parse_slits` for each reduced fits file into one text file. I found these useful in optimizing the reduction parameters, and they are used in the creation oof 2d coadd files. 

### `postCoaddPipeline`
This script reformats the coadded files into a specific format and naming convention, and creates an object list. The naming convention is `keck_IdxInObjList_Objname.fits` for 1d spectra and is the same for 2d spectra with an added suffix: `_spec2D`. 

# General Pypeit
The PypeIt read the docs site can be found [here](https://pypeit.readthedocs.io) and has a [DEIMOS specific how to](https://pypeit.readthedocs.io/en/release/deimos_howto.html), which is what I roughly followed. There is an example pypeit file as well as a slurm script in the `PypeIt/` directory. 

To use these scripts with PypeIt, first call `pypeit_setup`, then reduce all of the data with `run_pypeit`. Then the script `preCoaddPipeline.py` can be used to create configuration flies for 1D and 2D coadds and respective slurm scripts. After running all of the coadds, `postCoaddPipeline.py` can be used to reformat the data into one directory. 

I found that a mosaic reduction and detector reduction sometimes failed for different objects. So by running PypeIt in both mosaic and detector modes, I was able to have a larger dataset of succesfully reduced objects. The scripts in this repository do not reassemble the detector mode data, but the script 'combineByPriority.py` can be used to assemble a dataset of all reduced objects. 
