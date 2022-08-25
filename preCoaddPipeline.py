import glob
import numpy as np
import pandas as pd
import os
import shutil

# # Pre-Coadd Pipeline
# This notebook creates the 1d and 2d coadd files and slurm scripts for 2d
# coadding on lux.
#
# Prerequisites:
# * pypeit reduction has been ran, here I used the mosaic option for DEIMOS but
#   this should work either way

# ### Create slit tags files
# The slit tags files take the info from `pypeit_parse_slits` and synthesize it
# into one file per mask. This is useful for checking which slits/objects have
# data and is used later in the creation of 2d coadd files.
#
# The script `pypeit_parse_slits` is a little slow, so this part will take a
# couple of minutes
#
# NOTE: all paths must be absolute paths
mosaic=True
sciDirs = [
    '/data/groups/leauthaud/Merian/spectroscopy/Keck/Keck_data_2022/KOA_103052/DEIMOS/processed/keck_deimos_C/Science_M/',
    '/data/groups/leauthaud/Merian/spectroscopy/Keck/Keck_data_2022/KOA_103052/DEIMOS/processed/keck_deimos_D/Science_M/',
    '/data/groups/leauthaud/Merian/spectroscopy/Keck/Keck_data_2022/KOA_103052/DEIMOS/processed/keck_deimos_E/Science_M/',
    '/data/groups/leauthaud/Merian/spectroscopy/Keck/Keck_data_2022/KOA_103052/DEIMOS/processed/keck_deimos_F/Science_M/',
    '/data/groups/leauthaud/Merian/spectroscopy/Keck/Keck_data_2022/KOA_103504/DEIMOS/processed/mask5_allSci_M/',
    '/data/groups/leauthaud/Merian/spectroscopy/Keck/Keck_data_2022/KOA_103504/DEIMOS/processed/keck_deimos_G/Science_M/',
    '/data/groups/leauthaud/Merian/spectroscopy/Keck/Keck_data_2022/KOA_103504/DEIMOS/processed/keck_deimos_H/Science_M/',
    '/data/groups/leauthaud/Merian/spectroscopy/Keck/Keck_data_2022/KOA_103504/DEIMOS/processed/keck_deimos_E/Science_M/',
    '/data/groups/leauthaud/Merian/spectroscopy/Keck/Keck_data_2022/KOA_103937/DEIMOS/processed/keck_deimos_F/Science_M/',
    '/data/groups/leauthaud/Merian/spectroscopy/Keck/Keck_data_2022/KOA_103937/DEIMOS/processed/keck_deimos_G/Science_M/',
    '/data/groups/leauthaud/Merian/spectroscopy/Keck/Keck_data_2022/KOA_103937/DEIMOS/processed/keck_deimos_H/Science_M/',
    '/data/groups/leauthaud/Merian/spectroscopy/Keck/Keck_data_2022/KOA_103937/DEIMOS/processed/keck_deimos_I/Science_M/',
    '/data/groups/leauthaud/Merian/spectroscopy/Keck/Keck_data_2022/KOA_103937/DEIMOS/processed/keck_deimos_J/Science_M/'
]

# define method for parsing `pypeit_parse_slits` output into "slitTags" files
def makeSlitTag(idir, odir, maskNum):
    fin = idir+'/slitInfo.txt'
    fout= odir+'/slitTags_M%.2d.txt'%maskNum

    lines = open(fin).readlines()

    # one dictionary for each detector/mosaic
    slitInfo = [{}, {}, {}, {}, {}, {}, {}, {}]

    # read line by line
    currentDet = -1
    for line in lines:
        if line[0] == '=':
            currentDet = int(line[35])-1
        elif line[0] != 'S':
            # get slit id
            spatID = line[0:4]

            # maskdef ID
            mID = line[9:16]
            # manually added slits have no maskID
            if '-099' in mID:
                mID = str(currentDet+1) + '_' + line[0:4]

            # get flags
            idx = line.find('          ')
            t1 = line[33:-1].split(' ')
            t2 = []
            for t in t1:
                if t != '':
                    if t[-1] == ',':
                        t2.append(t[:-1])
                    else:
                        t2.append(t)

            # assign flags to slit in dictionary
            if  mID in slitInfo[currentDet].keys():
                slitInfo[currentDet][mID].append(t2)
            else:
                slitInfo[currentDet][mID] = [spatID, t2]


    M = maskNum

    outpt = open(fout, 'w')

    for i,det in enumerate(slitInfo):
        for maskID in det.keys():
            slitID = 'M'+'%.2d'%M + 'D' + '%.2d'%(i+1) + '_' + det[maskID][0]
            identifier = maskID
            shortflags = []
            for j,flags in enumerate(det[maskID]):
                if j == 0: continue
                if 'SHORTSLIT' in flags: shortflags.append('SHRT')
                elif 'BOXSLIT' in flags: shortflags.append(' BOX')
                elif 'BADWVCALIB' in flags: shortflags.append('WAVE')
                elif 'BADREDUCE' in flags: shortflags.append(' BR ')
                elif 'None' or 'Non' in flags: shortflags.append('GOOD')
                else: shortflags.append('????')
            l = str(identifier) + '\t' + slitID
            for flag in shortflags:
                l += '\t'+flag
            l += '\n'

            outpt.write(l)
    outpt.close()


# run `pypeit_parse_slits` for each mask and create slitTags files
for i,d in enumerate(sciDirs):
    os.chdir(d)
    if os.path.exists('slitInfo.txt'):
        os.remove('slitInfo.txt')
    os.system('for f in $(ls spec2d*.fits); do pypeit_parse_slits $f >> slitInfo.txt; done')

    makeSlitTag(d,d,i+1)


# ### Make 1d coadd files
# I ran the 1d coadds locally, so the produced slurm script isn't strictly
# necessary. 1d coadding can be run with the shell command:
# `for f in $(ls coadd1dFiles_M00/*); do pypeit_coadd_1dspec $f; done`
#
# 1d coadd files are created in the directory `scidir/coadd1dFiles_M00/` and
# follow the naming convention `MASKID_DETNUM_coadd1dFiles.txt`. In the case of
# mosaics, `DETNUM` is replaced with the mosaic number

slitCol = ' slit '
nameCol = '                    name '
maskidCol = ' maskdef_id '

for i in range(len(sciDirs)):
    # read through spec1d.txt files
    scidir = sciDirs[i]
    outdir = scidir+'/coadd1dFiles_M%.2d/'%(i+1)
    fitsdir = scidir+'/coadd1dFits_M%.2d/'%(i+1)

    if os.path.exists(outdir):
        shutil.rmtree(outdir)
    os.mkdir(outdir)

    files = glob.glob(scidir + '/spec1d*.txt')

    dets = [{} for _ in range(8)]
    noRaDec = []

    # slurm header
    slurmFile = scidir+'/coadd1d_M%.2d.slurm'%(i+1)
    with open(slurmFile, 'w') as slrm:
        slrm.write('#!/bin/bash\n')
        slrm.write('#SBATCH --job-name=MSK'+str(i+1)+'c1\n')
        slrm.write('#SBATCH --partition=cpuq\n')
        slrm.write('#SBATCH --account=cpuq\n')
        slrm.write('#SBATCH --mail-type=END,FAIL\n')
        slrm.write('#SBATCH --mail-user=jmwick@ucsc.edu\n')
        slrm.write('#SBATCH --ntasks=20\n')
        slrm.write('#SBATCH --nodes=1\n')
        slrm.write('#SBATCH --ntasks-per-node=20\n')
        slrm.write('#SBATCH --time=12:00:00\n')
        slrm.write('#SBATCH --output=MSK'+str(i+1)+'c1.out\n\n')
        slrm.close()

    for file in files:
        df = pd.read_csv(file, sep='|')
        for j,a in enumerate(df[nameCol]):
            det = int(a[-2:])
            #slit = a[14:18]
            slit = df[maskidCol][j]
            if slit not in dets[det-1].keys():
                dets[det-1][slit] = [[(file, a[1:-1])], 1]
                if df[maskidCol][j] == -99:
                    noRaDec.append(a)
            else:
                dets[det-1][slit][1] += 1
                dets[det-1][slit][0].append( (file, a[1:-1]) )

    # write coadd1d files
    for j,det in enumerate(dets):
        for k in det.keys():
            basename = str(k)+'_'+str(j+1)
            fname = basename + '_coadd1dFile.txt'
            cname = basename + '_coadd1d.fits'

            with open(outdir+fname, 'w') as f:
                f.write('[coadd1d]\n')
                f.write('  coaddfile = ' + fitsdir+cname + '\n')
                f.write('  flux_value = False\n\n')
                f.write('# data block\n')
                f.write('coadd1d read\n')
                f.write('  path '+ scidir+'\n\n')
                f.write('  filename | obj_id\n')
                for pair in det[k][0]:
                    f.write('  ' + pair[0][len(scidir):-3] + 'fits | ' + pair[1] + '\n')
                f.write('coadd1d end')
                f.close()
            # add to slurm file
            with open(slurmFile, 'a') as slrm:
                slrm.write('srun pypeit_coadd_1dspec coadd1dFiles_M%.2d/'%(i+1) +fname+ ' &\n')
                slrm.close()

    # finish slurm
    with open(slurmFile, 'a') as slrm:
        slrm.write('wait')
        slrm.close()


# ### Make 2d coadd files
# I ran the 2d coadds on lux, so there will be a slurm script produced

# In[81]:


# if science directories on the machine the scripts will be ran on are different
# than those local, specify the cluster scidirs here
# if clusterSci is set to [], then the above sciDirs are used
clusterScis = []

for i in range(len(sciDirs)):
    masknum = i+1
    sciDir = sciDirs[i]
    slitinfo = sciDir+'/slitTags_M%.2d.txt'%masknum

    luxSci = sciDir
    if len(clusterScis)>0:
        luxSci = clusterScis[i]

    outdir=sciDir+'/coadd2dFiles_M%.2d/'%masknum
    if os.path.exists(outdir):
        shutil.rmtree(outdir)
    os.mkdir(outdir)


    files = glob.glob(sciDir + '/spec2d*.fits')
    tags = pd.read_csv(slitinfo, sep='\t', header=None)
    n = len(tags.columns)-2

    slurmFile = sciDir+'/coadd2d_M%.2d'%masknum+'.slurm'
    # write slurm header
    with open(slurmFile, 'w') as slrm:
        slrm.write('#!/bin/bash\n')
        slrm.write('#SBATCH --job-name=MSK'+str(masknum)+'c2\n')
        slrm.write('#SBATCH --partition=cpuq\n')
        slrm.write('#SBATCH --account=cpuq\n')
        slrm.write('#SBATCH --mail-type=END,FAIL\n')
        slrm.write('#SBATCH --mail-user=jmwick@ucsc.edu\n')
        slrm.write('#SBATCH --ntasks=20\n')
        slrm.write('#SBATCH --nodes=1\n')
        slrm.write('#SBATCH --ntasks-per-node=20\n')
        slrm.write('#SBATCH --time=12:00:00\n')
        slrm.write('#SBATCH --output=MSK'+str(masknum)+'c2.out\n\n')
        slrm.close()

    for s, slitID in enumerate(tags[1]):
        slitNum = slitID[-4:]
        detNum = int(slitID[4:6])
        maskID = tags[0][s]
        # figure out which files are okay
        incFiles = []
        for j in range(2, n):
            if tags[j][s] == 'GOOD':
                incFiles.append(j-2)

        # write coadd2dfile
        if len(incFiles)>0:
            fname = str(maskID)+'_'+str(detNum)+'_coadd2dFile.txt'
            with open(outdir+fname, 'w') as f:
                f.write('# auto generated 2Dcoadd by Joseph Wick\n')
                f.write('[rdx]\n')
                f.write('  spectrograph = keck_deimos\n')
                if mosaic:
                    if detNum == 1:
                        f.write('  detnum = (1,5)\n')
                    elif detNum == 2:
                        f.write('  detnum = (2,6)\n')
                    elif detNum == 3:
                        f.write('  detnum = (3,7)\n')
                    elif detNum == 4:
                        f.write('  detnum = (4,8)\n')
                else:
                    f.write('  detnum = %d\n' %detNum)
                f.write('[reduce]\n')
                f.write('  [[findobj]]\n')
                f.write('    snr_thresh = 1.0\n')
                f.write('    maxnumber_sci = 1\n')
                f.write('[coadd2d]\n')
                f.write('  offsets = maskdef_offsets\n')
                f.write('  only_slits = '+str(int(slitNum))+'\n\n')
                f.write('# data block\n')
                f.write('spec2d read\n')
                f.write('path ' + luxSci + '\n')
                f.write('filename\n')
                for file in incFiles:
                    f.write(files[file][len(sciDir):]+'\n')
                f.write('spec2d end' )
                f.close()
            # write to slurm file
            with open(slurmFile, 'a') as slrm:
                slrm.write('srun pypeit_coadd_2dspec --file coadd2dFiles_M%.2d/%s --basename %s &\n' %(masknum, fname, str(str(maskID)+'_'+str(detNum))))
                slrm.close()

    # finish slurm file
    with open(slurmFile, 'a') as slrm:
        slrm.write('wait')
        slrm.close()
