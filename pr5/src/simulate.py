#!/usr/bin/env python3
import argparse
import os
import sys
from config_reader import ConfigReader
import stats
# import ram
from memory import ram, cache
import loader
import logger
import statistics
import core
from memory import cache 
# import config_reader


def parse_args():
    parser = argparse.ArgumentParser(description="pr5 Simulator")
    parser.add_argument('--start', type=lambda x: int(x, 16), required=True,
                        help='Start PC in hex (e.g. 0x80000000)')
    parser.add_argument('r5ob_path', type=str,
                        help='Path to the input r5ob file')
    parser.add_argument('--num_insts', type=int, default=100,
                        help='Number of instructions to simulate (default: 100)')
    parser.add_argument('--proc', type=str, choices=['SingleCycleProcessor', 'PipelinedProcessor', 'FPipelinedProcessor'], default='FPipelinedProcessor',
                        help='Type of processor to simulate (default: FPipelinedProcessor)')
    parser.add_argument('--config', type=str, default='src/config.ini',
                        help='Path to config file (default: config.ini)')
    return parser.parse_args()

def run_simulation():

    loggr = logger.setup()
    args = parse_args()
    cfg_reader = ConfigReader(args.config)

    if not os.path.isfile(args.r5ob_path):
        loggr.error(f"Error: Executable file '{args.r5ob_path}' does not exist.")
        sys.exit(1)

    config_startPc = cfg_reader.get_start_pc()
    config_procType = cfg_reader.get_processor_type()
    num_inst = cfg_reader.get_num_insts()

    start_pc = args.start if args.start is not None else config_startPc
    proc_type = args.proc if args.proc is not None else config_procType
    num_inst = args.num_insts if args.num_insts is not None else num_inst

    mem = ram.RAM(loggr)
    loader.load(mem, args.r5ob_path)
    stats_obj = stats.Statistics(loggr)

    I1 = None

    if cfg_reader.get_cache('I1_Cache')['valid']:
        I1 = cache.Cache(
            "I1_Cache",
            cfg_reader.get_cache('I1_Cache'),
            stats_obj,
            loggr
        )
    
    L1 = None
    if cfg_reader.get_cache('L1_Cache')['valid']:
        L1 = cache.Cache(
            "L1_Cache",
            cfg_reader.get_cache('L1_Cache'),
            stats_obj,
            loggr
        )

    L2 = None
    if cfg_reader.get_cache('L2_Cache')['valid']:
        L2 = cache.Cache(
            "L2_Cache",
            cfg_reader.get_cache('L2_Cache'),
            stats_obj,
            loggr
        )

    if proc_type == 'SingleCycleProcessor':
        cls = core.SingleCycleProcessor
    elif proc_type == 'PipelinedProcessor':
        cls = core.PipelinedProcessor
    else:
        cls = core.FPipelinedProcessor
    

    processor = cls(
        start_pc,
        I1, L1, L2,
        mem,
        loggr,
        stats_obj,
        cfg_reader 
    )

    loggr.info(f"Running Processor - {proc_type} mode")
    loggr.info(f"Start address: {hex(start_pc)}")
    loggr.info(f"Executable path: {args.r5ob_path}")
    loggr.info(f"Number of instructions: {num_inst}")

    processor.run(num_inst)

    

if __name__ == "__main__":
    run_simulation()