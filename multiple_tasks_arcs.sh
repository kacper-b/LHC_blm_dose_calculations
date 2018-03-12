#!/bin/bash

plot_total_for_dates_arc(){
    python main_script_for_arcs.py -p$3 -n 14 -arc $2 -l WARNING -pt -ptlim $1
}

iterate_over_arcs(){
    for i in {1..8}
        do
            for j in {15..17}
                do
                    echo "$i $j"
                    plot_total_for_dates_arc $1 $i $j
                done
        done
}

iterate_over_arcs $1


