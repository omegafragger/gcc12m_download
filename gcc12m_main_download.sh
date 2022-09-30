#!/bin/bash

# Clone git repo
echo "Cloning git repo"
git clone https://github.com/omegafragger/gcc12m_download.git
echo "Git repo cloned"


# Download meta data file
echo "Downloading GCC meta-data"
wget https://storage.googleapis.com/conceptual_12m/cc12m.tsv
echo "Meta data downloaded"


# Move meta data into repo dir
mv cc12m.tsv ./gcc12m_download/


# Make dirs in /datasets01
echo "Making directory structure inside /datasets01"
mkdir /datasets01/gcc12m
for i in 0 1000000 2000000 3000000 4000000 5000000 6000000 7000000 8000000 9000000 10000000 11000000 12000000; do mkdir /datasets01/gcc12m/$i; done


# Run slurm jobs
echo "Kicking off slurm scripts"
for i in gcc12m_download/slurms/*.sh; do sbatch $i; done
echo "Done!"
