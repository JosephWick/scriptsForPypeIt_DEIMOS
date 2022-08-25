import glob
import numpy as np
import pandas as pd
from astropy.io import fits
import os
import shutil


# # Post Coadd Pipeline
# Creates an object list and science files for pypeit data
#
# Prerequisites:
# * pypeit reduction, 1d and 2d coadds have been run
# * slitTags files have been created
# * mask design files are available

# ### Directories
# User should not have to change anything beyond this line

# In[4]:


# mask file directories
masksDir = '/Users/josephwick/Documents/College/GalBreathMode/reduction/masks_2022'

sciDirs = [
    '/Volumes/Joe2TB/Data/KeckDwarfs2022/Keck_data_2022/KOA_103052/DEIMOS/processedEdges/keck_deimos_C/Science_M',
    '/Volumes/Joe2TB/Data/KeckDwarfs2022/Keck_data_2022/KOA_103052/DEIMOS/processedEdges/keck_deimos_D/Science_M',
    '/Volumes/Joe2TB/Data/KeckDwarfs2022/Keck_data_2022/KOA_103052/DEIMOS/processedEdges/keck_deimos_E/Science_M',
    '/Volumes/Joe2TB/Data/KeckDwarfs2022/Keck_data_2022/KOA_103052/DEIMOS/processedEdges/keck_deimos_F/Science_M',
    '/Volumes/Joe2TB/Data/KeckDwarfs2022/Keck_data_2022/KOA_103504/DEIMOS/processed/mask5_allSci_M',
    '/Volumes/Joe2TB/Data/KeckDwarfs2022/Keck_data_2022/KOA_103504/DEIMOS/processed/keck_deimos_G/Science_M',
    '/Volumes/Joe2TB/Data/KeckDwarfs2022/Keck_data_2022/KOA_103504/DEIMOS/processed/keck_deimos_H/Science_M',
    '/Volumes/Joe2TB/Data/KeckDwarfs2022/Keck_data_2022/KOA_103504/DEIMOS/processed/keck_deimos_E/Science_M',
    '/Volumes/Joe2TB/Data/KeckDwarfs2022/Keck_data_2022/KOA_103937/DEIMOS/processed/keck_deimos_F/Science_M',
    '/Volumes/Joe2TB/Data/KeckDwarfs2022/Keck_data_2022/KOA_103937/DEIMOS/processed/keck_deimos_G/Science_M',
    '/Volumes/Joe2TB/Data/KeckDwarfs2022/Keck_data_2022/KOA_103937/DEIMOS/processed/keck_deimos_H/Science_M',
    '/Volumes/Joe2TB/Data/KeckDwarfs2022/Keck_data_2022/KOA_103937/DEIMOS/processed/keck_deimos_I/Science_M',
    '/Volumes/Joe2TB/Data/KeckDwarfs2022/Keck_data_2022/KOA_103937/DEIMOS/processed/keck_deimos_J/Science_M'
]

outDir = '/Users/josephwick/Documents/College/GalBreathMode/reduction/notebooks/pipelineOutput'


# ### 1) Create object list from mask design files

# In[45]:


# first let's compile a list of objects and their ra/dec  from the mask files
maskfiles = glob.glob(masksDir+'/*')
mf_ras = []
mf_decs= []
mf_objs= []
mf_mags= []
for mf in maskfiles:
    data = fits.open(mf)[1].data
    for i,t in enumerate(data['ObjClass']):
        if 'Program_Target' in t:
            mf_ras.append(data['RA_OBJ'][i])
            mf_decs.append(data['DEC_OBJ'][i])
            mf_objs.append(data['OBJECT'][i])
            mf_mags.append(data['mag'][i])

# export a catalog based on this
mf_colRA = fits.Column(name='RA_OBJ', array=mf_ras, format='E')
mf_colDEC = fits.Column(name='DEC_OBJ', array=mf_decs, format='E')
mf_colObj = fits.Column(name='OBJNAME', array=mf_objs, format='20A')
mf_colMag = fits.Column(name='mag', array=mf_mags, format='E')

mf_t = fits.BinTableHDU.from_columns([mf_colRA, mf_colDEC, mf_colObj, mf_colMag])
mf_t.writeto('pipelineOutput/objList.fits', overwrite=True)


# In[46]:


# can we figure out how many and what objects are missing from the object list

# get all present objects
presentSciMaskIDs = []
presentObjs = []
missingObjs = []
missingMags = []
presentNonSci = []
for directory in sciDirs:
    files = glob.glob(directory+'/spec1d*.txt')
    for file in files:
        df = pd.read_csv(file, sep='|')
        objs = df[df.columns[4]]
        for i,obj in enumerate(objs):
            if obj.strip() not in presentObjs and '_' not in obj and 'S' not in obj and 'N' not in obj:
                presentObjs.append(obj.strip())
                presentSciMaskIDs.append(df[df.columns[3]][i])
            else:
                presentNonSci.append(obj.strip())

# figure out what's missing
for i,obj in enumerate(mf_objs):
    if obj not in presentObjs and obj not in presentNonSci:
        missingObjs.append(obj)
        missingMags.append(mf_mags[i])

print('Total Objects  : ' + str(len(mf_ras)))
print('Present Objects: ' + str(len(presentSciMaskIDs)))
print('Missing Objects: ' + str(len(missingObjs)))


# ### Create Science Files
# first, correlate maskID and objname using the .txt sci files
mIDtoName = {}

for d in sciDirs:
    files = glob.glob(d+'/spec1d*.txt')
    for file in files:
        df = pd.read_csv(file, sep='|')
        mIDs = df[df.columns[3]]
        names = df[df.columns[4]]
        for i,m in enumerate(mIDs):
            if str(m) not in mIDtoName.keys() and '_' not in names[i]:
                mIDtoName[str(m)] = names[i].strip()

# go through 1d coadd 1d spec and see what's there
# see if any 2d coadd 1d specs add objects
# create scifile, using 1d coadd when available

# 1d spectra
# need to choose between 1d or 2d coadd here
#  - check if both are present, if only one present use that
#  - if both are present, use 1d coadd
outpath = outDir+'/objectSpectra'
shutil.rmtree(outpath)
os.mkdir(outpath)

# coadd1d fields
waveKey = 'wave'
fluxKey = 'flux'
ivarKey = 'ivar'

# figure out 1d or 2d coadd
mIDsPresent_1 = []
mIDsPresent_2 = []
for i,d in enumerate(sciDirs):
    masknum = i+1
    files = glob.glob(d+'/coadd1dFits_M%.2d/*.fits'%masknum)
    for file in files:
        mIDsPresent_1.append(file[-20:-13])

    files = glob.glob(d+'/Science_coadd/spec1d*.fits')
    for file in files:
        mID = file[-14:-7]
        if mID not in mIDsPresent_1:
            mIDsPresent_2.append(mID)

# reformat all coadd1d files present
# then do any necessary coadd2d files
for i,d in enumerate(sciDirs):
    maskNum = i+1

    # keys for 1d coadd
    waveKey = 'wave'
    fluxKey = 'flux'
    ivarKey = 'ivar'
    # do 1d coadds
    files = glob.glob(d+'/coadd1dFits_M%.2d/*.fits'%masknum)
    for file in files:
        # get objname
        obj = ''
        data = fits.open(file)[1].data
        mID = file[-20:-13]
        if mID in mIDtoName.keys():
            obj = mIDtoName[mID]
        else: continue

        # make new fits file
        idx = mf_objs.index(obj)+1
        outname = 'keck_'+str(idx)+'_'+obj+'.fits'

        col_wave = fits.Column(name='wave', array=data[waveKey], format='E')
        col_flux = fits.Column(name='flux', array=data[fluxKey], format='E')
        col_ivar = fits.Column(name='ivar', array=data[ivarKey], format='E')
        t = fits.BinTableHDU.from_columns([col_wave, col_flux, col_ivar])

        hdul = fits.HDUList([fits.PrimaryHDU(), t])
        hdul.writeto(outpath+'/'+outname)

    # keys for 2d coadd
    waveKey = 'OPT_WAVE'
    fluxKey = 'OPT_COUNTS'
    ivarKey = 'OPT_COUNTS_IVAR'
    files = glob.glob(d+'/Science_coadd/spec1d*.fits')
    for file in files:
        mID = file[-14:-7]
        if mID in mIDsPresent_2:
            obj = ''
            data = fits.open(file)[1].data
            if mID in mIDtoName.keys():
                obj = mIDtoName[mID]
            else: continue

            # make new fits file
            idx = mf_objs.index(obj)+1
            outname = 'keck_'+str(idx)+'_'+obj+'.fits'

            col_wave = fits.Column(name='wave', array=data[waveKey], format='E')
            col_flux = fits.Column(name='flux', array=data[fluxKey], format='E')
            col_ivar = fits.Column(name='ivar', array=data[ivarKey], format='E')
            t = fits.BinTableHDU.from_columns([col_wave, col_flux, col_ivar])

            hdul = fits.HDUList([fits.PrimaryHDU(), t])
            hdul.writeto(outpath+'/'+outname)

# 2d spectra
# naming convention: keck_objname_indexInObjList_spec2d.fits
for i,d in enumerate(sciDirs):
    files = glob.glob(d+'/Science_coadd/spec2d*.fits')
    for file in files:
        mID = file[-14:-7]
        if mID in mIDtoName.keys():
            obj = mIDtoName[mID]
        else:
            continue

        idx = mf_objs.index(obj)+1
        outname = 'keck_'+str(idx)+'_'+obj+'_spec2d.fits'

        f = fits.open(file)
        sciImg = f[1].data
        mdlImg = f[4].data
        errImg = f[5].data

        hdu0 = fits.PrimaryHDU()
        imgHDU_mdl = fits.ImageHDU(mdlImg)
        imgHDU_err = fits.ImageHDU(mdlErr)
        imgHDU_sci = fits.ImageHDU(sciImg)

        hdul = fits.HDUList([hdu0, imgHDU_mdl, imgHDU_err, imgHDU_sci])
        hdul.writeto(outdir+'/'+outname)
