import sys

class CacheMemory:
    def __init__(self, cache_size, line_size, block_size):
        self.cache_size = cache_size
        self.line_size = line_size
        self.block_size = block_size
        self.num_lines = cache_size // line_size
        self.num_blocks = line_size // block_size
        self.cache = [[None] * self.num_blocks for _ in range(self.num_lines)]

    def read(self, address):
        line_index = (address // self.block_size) % self.num_lines
        block_index = (address // self.block_size) % self.num_blocks
        if self.cache[line_index][block_index] is None:
            print("Cache miss!")
            # Fetch data from main memory and update cache
            self.cache[line_index][block_index] = self.fetch_data(address)
        else:
            print("Cache hit!")
        return self.cache[line_index][block_index]

    def fetch_data(self, address):
        # Simulate fetching data from main memory
        # Replace this with your own logic
        return f"Data at address {address}"


# Example usage
args = sys.argv

if len(args) < 4:
    raise Exception("Está faltando argumentos!")

cache_size = int(args[1])
line_size = int(args[2])
block_size = int(args[3])



cache = CacheMemory(cache_size=cache_size, line_size=line_size, block_size=block_size)
data = cache.read(256)
print(data)
