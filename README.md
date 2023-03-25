# scriptsForPypeIt_DEIMOS

Pypeit Documentation: https://pypeit.readthedocs.io/en/release/ 

This repo contains scripts to assist in reduction of DEIMOS slit masks with PypeIt. The scripts are designed to be ran on UCSC's Lux cluster, and handle creation of PypeIt files for 1d and 2d coadding, as well as reformatting the resulting coadded files. I reduced data from DEIMOS using PypeIt 1.10, and these scripts should be compatible with reduction done with mosaics or individual detectors. It should be noted that these scripts were not designed for use with fluxing 

There are two main scripts: `preCoaddPipeline.py` and `postCoaddPipeline.py`; for a more detailed walkthrough of my entire PypeIt process, see the bottom of this document. 

### `preCoaddPipeline`
This script uses the files in the `Science/` directory that PypeIt outputs during reduction to create parameter files for 1d and 2d coadding, and a respective slurm scripts. As an auxiliary output, the script also creates "slit tag" files that synthesize the output of `pypeit_parse_slits` for each reduced fits file into one text file. I found these useful in optimizing the reduction parameters, and they are used in the creation oof 2d coadd files. 

### `postCoaddPipeline`
This script reformats the coadded files into a specific format and naming convention, and creates an object list. The naming convention is `keck_IdxInObjList_Objname.fits` for 1d spectra and is the same for 2d spectra with an added suffix: `_spec2D`. 

# General Pypeit
The PypeIt read the docs site can be found [here](https://pypeit.readthedocs.io) and has a [DEIMOS specific how to](https://pypeit.readthedocs.io/en/release/tutorials/deimos_howto.html), which is what I roughly followed. There is an example pypeit file as well as a slurm script in the `PypeIt/` directory. 

## Initial setup
The first thing we want to do is let Pypeit sort through the data and determine what calibrations are associated with what science images. Pypeit is pretty good at this, I didn't find any errors, but it is still best to double check once we're done with this step.

The data I reduced was broked up by nights, each night with its own directory. Put all of the data for a given night, science _and_ calibrations, into one directory. I called this directory `allraw`. We want to create a separate directory for all of our reduction, I called this directory `processed`. Enter into the `processed` directory and call the script
`pypeit_setup -r RAWPATH -s keck_deimos -c all`

This will generate a series of folders organized by instrument configuration. Each folder has name along the lines of `keck_deimos_A`. You'll have to figure out which folder is associated with which mask. Each directory will have a `.pypeit` folder in it, which is what we will use to configure our reduction. For the masks that we want to reduce, read through the table at the bottom of the `.pypeit` file and make sure that all of the files have been correctly designated and nothing is missing.

Now, we want to modify our `.pypeit` files for the masks we want to reduce. There is an example `.pypeit` file in this repo, and for DEIMOS on dwarf galaxies, you can pretty much just copy those paramters. There are however, a couple of parameters I want to call attention to, as they may vary between runs. 

The first is `minimum_slit_length`, which defined the shortest slit that Pypeit will automatically identify. I think 4.0 arcseconds is accurate for the Merian Keck runs but wouldn't hurt to check with one of the observers. The other is `snr_thresh`. This will come into play after the reduction is done. Pypeit will try and automatically identify the object in the slit and use this information to extract spectra. One issue that I ran into was Pypeit being unable to find objects, which is why `snr_thresh` is set so low. Looking through the object finding QA images can help find a good value for this parameter. 

## Edge Tracing 
Before running the reduction, we want to make sure that Pypeit can capture the slit edges accurately. To do so, we use the script 

---
To use these scripts with PypeIt, first call `pypeit_setup`, then reduce all of the data with `run_pypeit`. Then the script `preCoaddPipeline.py` can be used to create configuration flies for 1D and 2D coadds and respective slurm scripts. After running all of the coadds, `postCoaddPipeline.py` can be used to reformat the data into one directory. 

I found that a mosaic reduction and detector reduction sometimes failed for different objects. So by running PypeIt in both mosaic and detector modes, I was able to have a larger dataset of succesfully reduced objects. The scripts in this repository do not reassemble the detector mode data, but the script 'combineByPriority.py` can be used to assemble a dataset of all reduced objects. 
