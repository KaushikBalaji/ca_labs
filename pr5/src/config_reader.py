import configparser
import os


class ConfigReader:
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file {config_file} not found.")
        
        self.config.read(config_file)
    
    def get_stats_file(self):
        return self.config['General'].get('stats_file', 'stats.json')
    
    def get_num_insts(self):
        return int(self.config['General'].get('num_insts', 100))
    
    def get_processor_type(self):
        """Get the processor type (SingleCycle, Pipelined, etc.)."""
        return self.config['Processor']['type']
    
    def get_start_pc(self):
        return int(self.config['Processor'].get('start_pc', '0x80000000'), 16)
    
    def get_cache(self, level):
        cache = {}
        cache["valid"]      = self.config[level].getboolean('valid')
        cache["latency"]     = int(self.config[level]['latency'])
        cache["size"]        = int(self.config[level].getint('size'))
        cache["block_size"]  = int(self.config[level]['block_size'])
        cache["assoc"]       = int(self.config[level]['assoc'])
        cache["mapping"]     = self.config[level]['mapping']
        cache["replacement"] = self.config[level]['replacement']
        return cache
    
    def get_mem_latency(self):
        return int(self.config['RAM']['latency'])

    def display_config(self):
        for section in self.config.sections():
            print(f"[{section}]")
            for key, value in self.config.items(section):
                print(f"{key} = {value}")
