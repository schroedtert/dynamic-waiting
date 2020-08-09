#!/bin/bash
#SBATCH --account=ias-7
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=48
#SBATCH --job-name=femtc2020-waiting-ca
#SBATCH --time=10:00:00
#SBATCH --output=outs/out.%j
#SBATCH --error=outs/err.%j

module load GCC
module load MPFR
module load OpenMPI
module load Python/3.6.8
module load Boost/1.69.0-Python-3.6.8

python3 run_simulations.py
