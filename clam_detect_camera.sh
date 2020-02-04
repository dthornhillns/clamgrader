ORIG_DIR=`pwd`

source ${CLAM_HOME}/venv/bin/activate

python ${CLAM_HOME}/camera_detect.py \
  -m=${CLAM_MODEL} \
  -l=${CLAM_LABELS} \
  -W=${CLAM_WIDTH} \
  -H=${CLAM_HEIGHT} \
  -c=$1 \
  -s=${CLAM_SCORE} \
  -b=4 \
  -f=2 \
  -cr=0.03

cd $ORIG_DIR
