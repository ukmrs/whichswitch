#!/usr/bin/sh

cd $(dirname $0)

BROOMOUT=$(./broom.py "$@") || { echo "broom failed"; exit 1; }
RIBOS=$(echo $BROOMOUT | cut -f1 -d ' ')
OUTDIR=$(echo $BROOMOUT | cut -f2 -d ' ')

cd $OUTDIR

vw --oaa $RIBOS trainset -f whichswitch.vw
vw -d testset -i whichswitch.vw -p predictions

../summary.py > summary
echo "\n---summary---\n"
cat summary
