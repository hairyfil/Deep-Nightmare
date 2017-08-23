#!/bin/sh
export CAFFE_ROOT=/usr/local/caffe

#
# different layers to choose from
# layers = ("conv2/3x3", "inception_3b/5x5_reduce", "inception_4c/output")
#
# --guide-image
#
clear
rm logfile
rm timefile

for IMAGELIST in images/d*
do
echo "-----------------" "$IMAGELIST"
    for SEEDFILE in images-seed/*
    do
        IMAGE=`basename "$IMAGELIST"`
        SEED=`basename "$SEEDFILE"`
        echo "Processing <" "$IMAGE" "> with seed <" "$SEED" ">"
        echo "Processing <" "$IMAGE" "> with seed <" "$SEED" ">" >> logfile
        echo "started at  \t" `date` >> timefile
        python deepnightmare.py --base-model $CAFFE_ROOT/models/bvlc_googlenet -i "$IMAGELIST" -o images-out/"$IMAGE"-"$SEED"-1 --guide-image "$SEEDFILE" --layer inception_4b/3x3 2>>logfile
        python deepnightmare.py --base-model $CAFFE_ROOT/models/bvlc_googlenet -i "$IMAGELIST" -o images-out/"$IMAGE"-"$SEED"-2 --guide-image "$SEEDFILE" --layer inception_4b/5x5_reduce 2>>logfile
        python deepnightmare.py --base-model $CAFFE_ROOT/models/bvlc_googlenet -i "$IMAGELIST" -o images-out/"$IMAGE"-"$SEED"-3 --guide-image "$SEEDFILE" --layer inception_4c/5x5_reduce 2>>logfile
        python deepnightmare.py --base-model $CAFFE_ROOT/models/bvlc_googlenet -i "$IMAGELIST" -o images-out/"$IMAGE"-"$SEED"-4 --guide-image "$SEEDFILE" --layer conv2/3x3 2>>logfile
        echo "finished at \t" `date` >> timefile
    done    
done