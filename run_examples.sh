#!/usr/bin/env bash

python cachesim.py -t traces/basic.trace -b 64 -l 2 -s [512,2048] -c [1,4] -a [4,4] -d 2 -m 5
python cachesim.py -t traces/basic.trace -b 64 -l 3 -s [512,2048,6500] -c [1,10,15] -a [1,2,4] -d 2 -m 0
python cachesim.py -t traces/basic.trace -b 64 -l 7 -s [512,2048,6500,10000,2000000,10000000,4000000] -c [1,10,15,20,25,30,35] -a [1,1,2,2,4,4,4] -d 1 -m 10
