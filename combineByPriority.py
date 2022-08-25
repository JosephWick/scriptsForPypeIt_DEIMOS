# combineByPriority.py
# Joseph Wick, 2022
#
# Synthesizes files from multiple directories into one directory based on
# order of input directories

import os
import glob
outdir = '/data/groups/leauthaud/Merian/spectroscopy/Keck/Keck_data_2022/dataProducts/spectra_opt'
indirs = [
    '/data/groups/leauthaud/Merian/spectroscopy/Keck/Keck_data_2022/dataProducts/spectra_M',
    '/data/groups/leauthaud/Merian/spectroscopy/Keck/Keck_data_2022/dataProducts/spectra_d'
    ]

shutil.rmtree(outdir)
os.mkdir(outdir)

for d in indirs:
    currFiles = glob.glob(outdir+'/*')
    currFiles_s []
    for f in currFiles:
        currFiles_s.append(f.split('/')[-1])
    for file in glob.glob(d+'/*'):
        fname = file.split('/')[-1]
        if fname not in currFiles_s:
            shutil.copyfile(file, outdir)
