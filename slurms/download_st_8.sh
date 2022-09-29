#!/bin/bash
#SBATCH --job-name=gcc_12m
#SBATCH --partition=hipri
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --cpus-per-task=10
#SBATCH --account=all

srun python download_gcc_12m.py --start 8000000 --store_path /datasets01/gcc12m/8000000