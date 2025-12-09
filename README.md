### Run the RISCV processor using
```bash
python3 pr5/src/simulate.py pr5/programs/bins/asms/file.r5ob --start=<starting address for execution> --num-insts=<number of instructions to execute> --proc=<processor type> &> /dev/null
```
\<processor type\> can be - SingleCycleProcessor, PipelinedProcessor, FPipelinedProcessor


- Look at **_stats.json_** for number of cycles taken, number of memory accesses taken, etc.
- See **_sim.log_** for the logger messages
- To regenerate .ob, .o files using riscv, run:
  - ```source setup-env.sh ```    -  to ensure riscv and spike dependences are added to the environment
  -  Use the following commands as needed. Refer to the Makefile at /pr5/programs location for other options.
      - ```make asms```
      - ```make```
      - ```run all```
      - ```run```
      - ```run_asms```


### File tree structure
```
.
├── cache_test.py
├── programs
│   ├── asms
│   │   ├── 1-even.elf
│   │   ├── 1-even.s
│   │   ├── 2-prime.s
│   │   ├── 3-descending.s
│   │   ├── 4-histogram.s
│   │   ├── 5-function.s
│   │   ├── 6-fact.s
│   │   ├── data_vars.s
│   │   ├── endless_loop.s
│   │   ├── practice1.s
│   │   └── practice2.s
│   ├── bins
│   │   ├── asms
│   │   │   ├── 1-even.r5o
│   │   │   ├── 1-even.r5ob
│   │   │   ├── 2-prime.r5o
│   │   │   ├── 2-prime.r5ob
│   │   │   ├── 3-descending.r5o
│   │   │   ├── 3-descending.r5ob
│   │   │   ├── 4-histogram.r5o
│   │   │   ├── 4-histogram.r5ob
│   │   │   ├── 5-function.r5o
│   │   │   ├── 5-function.r5ob
│   │   │   ├── 6-fact.r5o
│   │   │   ├── 6-fact.r5ob
│   │   │   ├── data_vars.r5o
│   │   │   ├── data_vars.r5ob
│   │   │   ├── endless_loop.r5o
│   │   │   ├── endless_loop.r5ob
│   │   │   ├── practice1.r5o
│   │   │   ├── practice1.r5ob
│   │   │   ├── practice2.r5o
│   │   │   └── practice2.r5ob
│   │   └── c_tests
│   │       ├── add.r5o
│   │       ├── add.r5ob
│   │       ├── hello_world.r5o
│   │       └── hello_world.r5ob
│   ├── c_tests
│   │   ├── add.c
│   │   └── hello_world.c
│   ├── custom
│   │   ├── common
│   │   │   ├── crt.S
│   │   │   ├── cva6_csr_access_test_32.S
│   │   │   ├── cva6_csr_access_test_64.S
│   │   │   ├── syscalls.c
│   │   │   ├── test.ld
│   │   │   └── util.h
│   │   ├── crt.S
│   │   ├── encoding.h
│   │   ├── env
│   │   │   ├── encoding.h
│   │   │   └── LICENSE
│   │   ├── syscalls.c
│   │   └── test.ld
│   ├── dumps
│   │   ├── asms
│   │   │   ├── 1-even.r5o.dump
│   │   │   ├── 2-prime.r5o.dump
│   │   │   ├── 3-descending.r5o.dump
│   │   │   ├── 4-histogram.r5o.dump
│   │   │   ├── 5-function.r5o.dump
│   │   │   ├── 6-fact.r5o.dump
│   │   │   ├── data_vars.r5o.dump
│   │   │   ├── endless_loop.r5o.dump
│   │   │   ├── practice1.r5o.dump
│   │   │   └── practice2.r5o.dump
│   │   └── c_tests
│   │       ├── add.r5o.dump
│   │       └── hello_world.r5o.dump
│   ├── Makefile
│   └── runs
│       ├── asms
│       │   ├── 1-even.iss
│       │   ├── 2-prime.iss
│       │   ├── 3-descending.iss
│       │   ├── 4-histogram.iss
│       │   ├── 5-function.iss
│       │   ├── 6-fact.iss
│       │   ├── data_vars.iss
│       │   ├── endless_loop.iss
│       │   ├── practice1.iss
│       │   └── practice2.iss
│       └── c_tests
│           └── add.iss
├── sim.log
├── src
│   ├── config.ini
│   ├── config_reader.py
│   ├── core
│   │   ├── FPipelinedProcessor.py
│   │   ├── fu.py
│   │   ├── __init__.py
│   │   ├── pipelined_processor.py
│   │   ├── processor.py
│   │   ├── riscv_tables.py
│   │   └── single_cycle_processor.py
│   ├── __init__.py
│   ├── loader.py
│   ├── logger.py
│   ├── main.py
│   ├── memory
│   │   ├── cache.py
│   │   └── ram.py
│   ├── modules
│   │   ├── 152502010.code-workspace
│   │   ├── disassembler.py
│   │   ├── FileLoader.py
│   │   ├── RAM.py
│   │   ├── readMemory.py
│   │   └── writeMemory.py
│   ├── sim.log
│   ├── simulate.py
│   ├── stats.json
│   └── stats.py
├── stats_cache.json
├── stats.json
└── tests
    ├── 1-even.gold.trace
    ├── 1-even.sim.trace
    ├── 2-prime.gold.trace
    ├── 2-prime.sim.trace
    ├── 3-descending.gold.trace
    ├── 3-descending.sim.trace
    ├── 4-histogram.gold.trace
    ├── 4-histogram.sim.trace
    ├── 5-function.gold.trace
    ├── 5-function.sim.trace
    ├── check_sequence.sh
    ├── sim.log
    ├── stats_cache.json
    └── stats.json



```
