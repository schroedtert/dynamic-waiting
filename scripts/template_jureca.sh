#!/bin/bash
#SBATCH --account=jias72
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=48
#SBATCH --job-name={{jobname}}
#SBATCH --time={{ wall_time }}
#SBATCH --output=outs/out.%j
#SBATCH --error=outs/out.%j

module load GCC
module load MPFR
module load OpenMPI
module load Python/3.6.8
module load Boost/1.69.0-Python-3.6.8

python3 run_simulations.py {{max_agents}} {{min}} {{max}}
