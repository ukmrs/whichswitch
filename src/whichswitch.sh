#!/usr/bin/sh

cd $(dirname $0)

ribos=32
window=6

while getopts "w:?r:?" opt; do
  case "$opt" in
    r)  ribos=$OPTARG
      ;;
    w)  window=$OPTARG
      ;;
  esac
done

outdir=$(./broom.py -r $ribos -w $window) || { echo "broom failed"; exit 1; }

cd $outdir

vw --oaa $ribos trainset -f whichswitch.vw
vw -d testset -i whichswitch.vw -p predictions

../summary.py -r $ribos > summary
echo "\n---saved_in---\n$outdir"
echo "\n---summary---\n"
cat summary
