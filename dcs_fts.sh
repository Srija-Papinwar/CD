#!/bin/bash
:'
This is script is helper script which helps executing the python script called dcs_fts
'
python3 -m pip install --upgrade robotframework-sshlibrary
cd scripts
python3 dcs_fts.py 