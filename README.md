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

Pypeit has several scripts that we use to organize data, test calibrations, and reduce the data. Each of these when ran with the flag `-h` provides a summary of the script and the input options. 

## Initial setup
The first thing we want to do is let Pypeit sort through the data and determine what calibrations are associated with what science images. Pypeit is pretty good at this, I didn't find any errors, but it is still best to double check once we're done with this step.

The data I reduced was broked up by nights, each night with its own directory. Put all of the data for a given night, science _and_ calibrations, into one directory. I called this directory `allraw`. We want to create a separate directory for all of our reduction, I called this directory `processed`. Enter into the `processed` directory and call the script
`pypeit_setup -r RAWPATH -s keck_deimos -c all`

This will generate a series of folders organized by instrument configuration. Each folder has name along the lines of `keck_deimos_A`. You'll have to figure out which folder is associated with which mask. Each directory will have a `.pypeit` folder in it, which is what we will use to configure our reduction. For the masks that we want to reduce, read through the table at the bottom of the `.pypeit` file and make sure that all of the files have been correctly designated and nothing is missing.

Now, we want to modify our `.pypeit` files for the masks we want to reduce. There is an example `.pypeit` file in this repo, and for DEIMOS on dwarf galaxies, you can pretty much just copy those paramters. There are however, a couple of parameters I want to call attention to, as they may vary between runs. 

The first is `minimum_slit_length`, which defined the shortest slit that Pypeit will automatically identify. I think 4.0 arcseconds is accurate for the Merian Keck runs but wouldn't hurt to check with one of the observers. The other is `snr_thresh`. This will come into play after the reduction is done. Pypeit will try and automatically identify the object in the slit and use this information to extract spectra. One issue that I ran into was Pypeit being unable to find objects, which is why `snr_thresh` is set so low. Looking through the object finding QA images can help find a good value for this parameter. 

## Edge Tracing 
Before running the reduction, we want to make sure that Pypeit can capture the slit edges accurately. To do so, we use the script `pypeit_trace_edges`. After the script ends, we can use the script `pypeit_chk_edges` on the output of the edge tracing. You can compare the ginga window to a raw science image to conform that all (or at least nearly all) slits were well captured. 

If the edge tracing is poor, we can modify `slitedge` parameters: https://pypeit.readthedocs.io/en/release/calibrations/slit_tracing.html 

## Main Run 
When the edge tracing is satisfactory, we can move on to the main run, called by the `run_pypeit` script. There's a slurm script in this repo `reduceMask1_M.slurm` that I used to reduce on lux. That script only reduce one mask, but a slurm file could be made to reduce several at once. I made different pypeit files for each mosaic, but one could also use the `-d` flag when calling the script. 

## Checking QA

Pypeit produces several different QA images for each reduced galaxy. It is important to look through all of them, information on what consitututes a "good" reduction is available [here](https://pypeit.readthedocs.io/en/release/qa.html). 

I had the most problems with object finding, so spent the most time with those QA files. Looking at the objecting finding and sky subtraction QA images can give an idea of if the `snr_thresh` parameter in the pypeit file needs to be adjusted. I reduced the data multiple times to find an adequate `snr_thresh`, so it may be a good idea to run one mask to test this parameter before doing a full reduction. 

## Coadding
Once the data is reduced adequately, we want to coadd out multiple exposures to produce a single spectra. 

This is where the two python scripts in this repository come in. First run `preCoaddPypeline.py`, which will produce slurm scripts for coadding. After running those scripts to coadd the data, run `postCoaddPypeline.py`. Before running each script, you will need to modify the code so that the file paths at the top of the file point toward your data. 
