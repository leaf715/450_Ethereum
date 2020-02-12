#!/bin/sh

python3 run_mapping.py 00469642.json 0 00469642.json 1 > comps/00469242_0-00469642_1.json &
python3 run_mapping.py 00469642.json 0 00469649.json 0 > comps/00469242_0-00469649_0.json &
python3 run_mapping.py 00469642.json 1 00469649.json 0 > comps/00469242_1-00469649_0.json &
python3 run_mapping.py 00499990.json 0 00499995.json 0 > comps/00499990_0-00499995_0.json &
python3 run_mapping.py 04501736.json 0 04501736.json 0 > comps/04501736_0-04501969_0.json
