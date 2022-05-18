#!/usr/bin/sh


cd $(dirname $0)

IFS=-


BROOMOUT=$(./broom.py "$@") || { echo "broom failed"; exit 1; }
WINDOW=$(echo $BROOMOUT | cut -f1)
OUTDIR=$(echo $BROOMOUT | cut -f2)


cd $OUTDIR

vw --oaa $WINDOW trainset -f whichswitch.vw
vw -d testset -i whichswitch.vw -p predictions

../summary.py > summary
cat summary
