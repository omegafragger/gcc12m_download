#!/bin/bash
#SBATCH --job-name=gcc_12m
#SBATCH --partition=hipri
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --cpus-per-task=10
#SBATCH --account=all

source activate pytorch_latest

srun python download_gcc_12m.py --start 6000000