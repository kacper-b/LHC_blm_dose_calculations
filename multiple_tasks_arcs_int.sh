#!/bin/bash

plot_total_for_dates_arc(){
    python main_integrated_intensity_multiple_years.py -p$3 -n 16 -arc $2 -l WARNING -pt -ptlim $1
}

iterate_over_arcs(){
    for i in {1..8}
        do
            plot_total_for_dates_arc $1 $i 17
        done
}

iterate_over_arcs $1


