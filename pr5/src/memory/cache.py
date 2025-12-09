
from collections import OrderedDict
# import config_reader
class Cache:
    def __init__(self, name, config_params,  stats, logger):
        self.name = name
        self.stats = stats
        self.logr = logger
        # self.nxt_lvl = nxt_lvl

        self.valid = config_params.get("valid", True)
        if not self.valid:
            self.logr.info(f"{self.name} -  Cache is disabled.")
            return
        
        self.latency = config_params["latency"]
        self.size = config_params["size"]
        self.block_size = config_params["block_size"]
        self.assoc = config_params["assoc"]
        self.mapping = config_params["mapping"]
        self.replacement = config_params["replacement"]

        self.logr.info(f"{self.name} - Initializing Cache: size={self.size}, block_size={self.block_size}, assoc={self.assoc}, mapping={self.mapping}, replacement={self.replacement}, latency={self.latency}")

        self.num_lines = self.size // self.block_size

        if self.mapping == "full":
            self.num_sets = 1
        elif self.mapping == "direct":
            self.num_sets = self.num_lines
        else:  # set associative
            self.num_sets = self.num_lines // self.assoc
        
        self.sets = [[
                {"valid": False, "tag": None}
                for _ in range(self.assoc)
            ]
            for _ in range(self.num_sets)]
        
        self.logr.info(f"{self.name} - Cache initialized with {self.num_sets} sets, each with {self.assoc} lines.")


    def cache_access(self, address, is_write = False, write_data=None):
        if not self.valid:
            return self.read_from_next_level(address)
        

        # --------------------- CACHE HIT -----------------------

        # self.stats.increment_memory_access()
        set_index, tag = self.get_index_tag(address)
        cache_set = self.sets[set_index]

        for line in cache_set:
            # Cache hit
            self.logr.debug(f"{self.name} - Cache HIT for address {hex(address)}")
            if line["valid"] and line["tag"] == tag:
                # return hit, data, latency, miss_address
                self.stats.increment_cache_hit(self.name)
                return True, None, self.latency, None

        # Cache miss
        self.stats.increment_cache_miss(self.name)
        block_addr = address - (address % self.block_size)
        self.logr.debug(f"{self.name} - Cache MISS for address {hex(address)}")
        return False, None, self.latency, block_addr  
        
        # return self.handle_cache_miss(address, cache_set, tag, index)


    def handle_cache_miss(self, address, cache_set, tag, index):
        if len(cache_set) >= self.assoc:
            # evict a line for any policy
            evicted_tag, evicted_line = cache_set.popitem(last=False)
            self.stats.increment_cache_evict(self.name)

        base_addr = (address // self.block_size) * self.block_size
        line_data = {}

        for i in range(self.block_size):
            line_data[i] = self.read_from_next_level(base_addr + i)

        cache_set[tag] = CacheLine(tag, line_data)

            # self.logr.debug(f"{self.name} - Evicting line with tag {hex(evicted_tag)} from set {index}")


        

    def get_index_tag(self, address):
        line_addr = address // self.block_size
        index = line_addr % self.num_sets
        tag = line_addr // self.num_sets
        return index, tag

    def read_from_next_level(self, address):
        for _ in range(self.next_lvl_latency()):
            self.stats.increment_clock_cycle()
        return self.nxt_lvl.read(address)
            

    def next_lvl_latency(self):
        if hasattr(self.nxt_lvl, 'latency'):
            return self.nxt_lvl.latency
        return 0