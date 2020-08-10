#!/usr/bin/env python3

from jinja2 import Template, Environment, FileSystemLoader
import glob
import subprocess
import numpy as np
import re
import math

template_loader = FileSystemLoader(searchpath="./")
template_env = Environment(loader=template_loader)

template_file = 'template_jureca.sh'
template = template_env.get_template(template_file)
                             
num_simulations = 4374#8748
num_processors_per_node = 48
num_task_per_processor = 4

tasks_per_node = math.ceil(num_simulations / num_processors_per_node)
jobs = math.ceil(tasks_per_node / num_task_per_processor)

range_per_job = math.ceil(num_simulations / jobs)

for i in range(jobs):
    start = i * range_per_job
    end = min(num_simulations, (i+1)*range_per_job - 1)
    
    output = template.render(min=start, max=end)

    file_name = 'jureca_run_{:02d}.sh'.format(i)
    with open(file_name, 'w') as fh:
        fh.write(output)

