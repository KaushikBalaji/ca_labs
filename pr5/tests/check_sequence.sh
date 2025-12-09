#!/bin/bash

# if [ $# -lt 1 ]; then
#     echo "Error: Pass the name of program to simulate and check." >&2
#     echo "Example usage: $0 1-even"
#     echo "Example usage: $0 2-prime"
#     exit 1
# fi


# Options:
# SingleCycleProcessor
# PipelinedProcessor
# FPipelinedProcessor


PR5="$(cd "$(dirname "${BASH_SOURCE[0]}")/../" && pwd)"

cd ${PR5}/tests/
# echo "$PR5"
for test in 1-even 2-prime 3-descending 4-histogram 5-function;
# for test in 1-even 2-prime 3-descending 4-histogram 5-function 6-fact;
do
    start="80002000"
    # echo "Running ${test} with processor: ${PROC_TYPE}"
    # touch sim.log
    # python3 ${PR5}/src/simulate.py ${PR5}/programs/bins/asms/${test}.r5ob &> /dev/null
    python3 ${PR5}/src/simulate.py --start=${start} ${PR5}/programs/bins/asms/${test}.r5ob --num_insts=100 --proc=FPipelinedProcessor --config=${PR5}/src/config.ini &> /dev/null
    grep 'OUT' sim.log | sed 's/\[OUT\]//' | sed 's/ //g' | cut -d '|' -f1 > ${test}.sim.trace
    GOLD="${PR5}/programs/runs/asms/${test}.iss"
    if [ ! -f "${GOLD}" ]; then
        echo "${GOLD} does not exist. Check the filepaths or run spike (make run_asms) on the input."
        exit
    fi
    awk '$4 >= "0x80002000" {print $4}' ${GOLD} | sed 's/^0x//' | head -100 > ${test}.gold.trace
    cmp -s ${test}.sim.trace ${test}.gold.trace && echo "${test} passed" || echo "${test} failed"

done

