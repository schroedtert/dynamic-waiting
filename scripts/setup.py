#!/usr/bin/env python3

from jinja2 import Template, Environment, FileSystemLoader
import glob
import subprocess
import numpy as np
import re
import math

max_agents = [200, 300, 500]
wall_time = {200: '00:30:00',
             300: '01:00:00',
             500: '01:30:00'}
template_loader = FileSystemLoader(searchpath="./")
template_env = Environment(loader=template_loader)

template_file = 'template_jureca.sh'
template = template_env.get_template(template_file)
                             
num_simulations = 1152  # 8748
num_processors_per_node = 48
num_task_per_processor = 1

tasks_per_node = math.ceil(num_simulations / num_processors_per_node)
jobs = math.ceil(tasks_per_node / num_task_per_processor)


range_per_job = math.ceil(num_simulations / jobs)
for agents in max_agents:
    for i in range(jobs):
        start = i * range_per_job
        end = min(num_simulations, (i+1)*range_per_job - 1)
        job_name = 'femtc-{:04d}-{:02d}'.format(agents, i)

        output = template.render(min=start, max=end, max_agents=agents, wall_time=wall_time[agents], jobname=job_name)
        file_name = 'jureca_run_{:04d}_{:02d}.sh'.format(agents, i)
        with open(file_name, 'w') as fh:
            fh.write(output)

