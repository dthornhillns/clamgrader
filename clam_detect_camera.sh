#!/bin/bash

CLAM_HOME=/home/cockle/projects/Clam_Grader

ORIG_DIR=`pwd`

source ${CLAM_HOME}/venv/bin/activate

python ${CLAM_HOME}/camera_detect.py \
  -f=${CLAM_HOME}/camera_config.json \
  -n

cd $ORIG_DIR
