#!/bin/bash

shopt -s nullglob
for i in scripts/jureca_run*.sh; do
    sbatch $i
    done
