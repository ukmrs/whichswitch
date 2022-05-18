#!/usr/bin/sh


cd $(dirname $0)

OUTDIR=$(./broom.py) || { echo "broom failed"; exit 1; }

cd $OUTDIR

vw --oaa 3 trainset -f whichswitch.vw
vw -d testset -i whichswitch.vw -p predictions

../summary.py > summary
cat summary
