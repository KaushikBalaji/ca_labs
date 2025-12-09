import sys
from src.memory import cache 
from src.stats import Statistics
from src import logger


class DummyLogger:
    def info(self, x): print(x)

# run from one directory above 'src' (e.g. /home/kaushik/.../pr5)
sys.path.insert(0, "/home/kaushik/data/Documents/152502010/pr5")
# use cache_test.DummyLogger, etc.

loggr = logger.setup()
c = cache.Cache(
    "L1Cache",
    {
        "size": 1024,
        "block_size": 16,
        "assoc": 4,
        "mapping": "set",
        "replacement": "LRU",
        "latency": 2,
        "valid": True
    },
    Statistics(loggr),
    loggr
)

print("\n--- TEST 1: First access (should miss) ---")
hit, data, lat, miss_addr = c.cache_access(0x1000)
print("hit:", hit, "lat:", lat, "miss:", hex(miss_addr))

print("\n--- TEST 2: Same address again (still miss, because we did not fill yet) ---")
hit, data, lat, miss_addr = c.cache_access(0x1000)
print("hit:", hit, "lat:", lat, "miss:", hex(miss_addr))