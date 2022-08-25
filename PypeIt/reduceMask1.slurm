#!/bin/bash
#SBATCH --job-name=MSK01M
#SBATCH --partition=cpuq
#SBATCH --account=cpuq
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=jmwick@ucsc.edu
#SBATCH --ntasks=4
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --time=48:00:00
#SBATCH --output=MSK01M.out

srun --ntasks 1 run_pypeit keck_deimos_C_M1.pypeit -o &
srun --ntasks 1 run_pypeit keck_deimos_C_M2.pypeit -o &
srun --ntasks 1 run_pypeit keck_deimos_C_M3.pypeit -o &
srun --ntasks 1 run_pypeit keck_deimos_C_M4.pypeit -o &
wait
