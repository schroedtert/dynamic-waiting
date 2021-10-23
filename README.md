# Cellular automata for waiting pedestrians at platforms

Trying to model waiting behavior of pedestrians on train station platforms via Cellular Automaton.

## Publications
A more detailed explanation of the model is given in the [paper](paper.pdf) and in the [talk](https://youtu.be/-2onk8QIA2g) at the FEMTC 2020.

- Paper: https://juser.fz-juelich.de/record/887683/
- Talk: https://youtu.be/-2onk8QIA2g

[![](https://img.youtube.com/vi/-2onk8QIA2g/0.jpg)](https://youtu.be/-2onk8QIA2g "Video to conference talk")

The results presented there are computed with the [FEMTC2020](https://github.com/schroedtert/dynamic-waiting/releases/tag/femtc2020) release from this repository.

## Requirements
Python 3.6 with following packages is required:
- descartes
- matplotlib
- numpy
- pandas
- scikit-fmm
- scipy
- Shapely
- VisiLibity

 They can by installed by:
```bash
pip install -r requirements.txt

```
## Usage
```bash
python waiting_ca.py <optional arguments>
```

| option             	| default value                 	| description                                                                   	|
|--------------------	|-------------------------------	|-------------------------------------------------------------------------------	|
| -h, --help         	|                               	| show this help message and exit                                               	|
| --max_agents       	| 100                           	| max number of pedestrians                                                     	|
| --init_agents      	| 20                            	| number of pedestrians at start of simulation                                  	|
| --standing_agents  	| 0                             	| number of pedestrian which will not move during simulation (only init agents) 	|
| --steps            	| 180                           	| number of simulation steps                                                    	|
| --file             	| './geometries/simplified.xml' 	| geometry used for simulation                                                  	|
| --seed             	| 124                           	| used random seed                                                              	|
| --w_exit           	| 1                             	| weight of exit potential                                                      	|
| --w_wall           	| 1                             	| weight of wall potential                                                      	|
| --door_b, --door_c 	| 1, 1                          	| sigmoid parameter for door decay                                              	|
| --exit_b, --exit_c 	| 1, 1                          	| sigmoid parameter for exit decay                                              	|
| --wall_b, --wall_c 	| 1, 1                          	| sigmoid parameter for wall decay                                              	|
| --ped_b, --ped_c   	| 1, 1                          	| sigmoid parameter for ped decay                                               	|
| --plot             	| False                         	| plot the static ff, and peds in each step                                     	|
| --output_path      	| 'results'                     	| directory where the results are stored                                        	|
