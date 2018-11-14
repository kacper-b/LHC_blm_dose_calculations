#!/bin/bash

plot_total_for_dates_ip(){
    python3 main_plots.py -s $1 -n 16 -pt  -l INFO -f /mnt/hdd/monitoring_analysis/data/blm_lists/report_new/ir$2.csv
}


plot_total_for_dates_arcs(){
    if [ $2 -eq 8 ]
    then
        a=1
    else
        a=$(( $2 + 1 ))
    fi

    python3 main_plots.py -s $1 -n 16 -pt  -l INFO -f /mnt/hdd/monitoring_analysis/data/blm_lists/report_new/arc$2$a.csv
}

iterate_over_ips(){
    for i in {1..8}
        do
            plot_total_for_dates_ip $1 $i
            plot_total_for_dates_arcs $1 $i
        done
}


iterate_over_ips 28-03-2018

