#!/usr/bin/env python3

from jinja2 import Template, Environment, FileSystemLoader
import glob
import subprocess
import numpy as np
import re
import math

max_agents = [50, 100, 200, 300, 400, 500, 1000]
wall_time = {50: '00:10:00',
             100: '00:30:00',
             200: '00:45:00',
             300: '01:00:00',
             400: '01:15:00',
             500: '02:00:00',
             1000: '05:00:00'}
template_loader = FileSystemLoader(searchpath="./")
template_env = Environment(loader=template_loader)

template_file = 'template_jureca.sh'
template = template_env.get_template(template_file)
                             
num_simulations = 240 #8748
num_processors_per_node = 48
num_task_per_processor = 1

tasks_per_node = math.ceil(num_simulations / num_processors_per_node)
jobs = math.ceil(tasks_per_node / num_task_per_processor)


range_per_job = math.ceil(num_simulations / jobs)
for agents in max_agents:
    for i in range(jobs):
        start = i * range_per_job
        end = min(num_simulations, (i+1)*range_per_job - 1)
        job_name = 'femtc-{:03d}-{:02d}'.format(agents, i)

        output = template.render(min=start, max=end, max_agents=agents, wall_time=wall_time[agents], jobname=job_name)
        file_name = 'jureca_run_{:03d}_{:02d}.sh'.format(agents, i)
        print(output)
        with open(file_name, 'w') as fh:
            fh.write(output)

