#!/bin/bash

plot_total_for_dates_arc(){
    python3 main.py -s $1 -e $2 -n 8 -arc $3 -pt  -l INFO -raw $4  -pkl /home/kacper/analysed_blmXXX -f all_blms_dcum_meters_ti_qi_ei_bi.csv
}

iterate_over_arcs(){
    for i in {8..8}
        do
            plot_total_for_dates_arc $1 $2 $i $3
        done
}

#iterate_over_arcs 28-03-2016 31-10-2016  ../../data/blm_data_2016
iterate_over_arcs 01-05-2017 16-10-2017 ../../data/blm_data_2017


