#!/bin/bash

# Get the BSPWM node id of the linux-media-controller widget
windows=$(bspc query -N -n .window)
names=$(xtitle $windows)
line=$(echo "$names" | awk '/linux-media-controller/ {print NR}')

if [ -z "$line" ]; then
    echo "-1"
    exit 1
fi

node=$(echo "$windows" | awk "NR==$line {print \$0}")
echo $node
