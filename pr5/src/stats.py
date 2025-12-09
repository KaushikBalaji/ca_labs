import json

class Statistics:
    def __init__(self, loggr):
        self.clock_cycles = 0
        self.instruction_count = 0
        self.memory_accesses = 0
        self.logr = loggr

        self.register_accesses = 0
        # cache statistics
        self.cache_hits = {}
        self.cache_misses = {}
        self.cache_evicts = {}

    def get_clocks(self):
        return self.clock_cycles

    def increment_clock_cycle(self):
        self.clock_cycles += 1

    def increment_instruction_count(self):
        self.instruction_count += 1

    def increment_memory_access(self):
        self.memory_accesses += 1

    def increment_register_access(self):
        self.register_accesses += 1

    def increment_cache_hit(self, cache_name):
        if cache_name not in self.cache_hits.keys():
            self.cache_hits[cache_name] = 0
        self.cache_hits[cache_name] += 1

    def increment_cache_miss(self, cache_name):
        if cache_name not in self.cache_misses.keys():
            self.cache_misses[cache_name] = 0
        self.cache_misses[cache_name] += 1

    def increment_cache_evict(self, cache_name):
        if cache_name not in self.cache_evicts.keys():
            self.cache_evicts[cache_name] = 0
        self.cache_evicts[cache_name] += 1

    

    def write_statistics(self, filename):
        stats = {
            "clock_cycles": self.clock_cycles,
            "instructions_executed": self.instruction_count,
            "memory_accesses": self.memory_accesses,
        }
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=4)
        self.logr.info(f"Statistics saved to {filename}")

    def write_cache_stats(self, filename):
        stats = {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_evicts": self.cache_evicts,
        }
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=4)
        self.logr.info(f"Cache statistics saved to {filename}")

    def reset(self):
        self.clock_cycles = 0
        self.instruction_count = 0
        self.memory_accesses = 0
        self.register_accesses = 0
