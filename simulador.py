import sys
import math

class Address:
    def __init__(self, address: str) -> None:
        """
            Recebe um endereço de memória hexadecimal,
            e o converte para binário, inteiro e salva hexadecimal também.
        """
        address = address.replace("\n", "").replace("0x", "")

        self.hexadecimal = address
        self.binary = str(bin(int(address, 16))[2:].zfill(32))
        self.integer = int(self.binary, 2)

    def get_parts(self, num_indexs, num_offsets_block) -> tuple:
        """
            Retorna a tag do endereço, de acordo com o número de bits,
            mas de forma já endereçada em vetor
        """

        tag = self.binary[:-max(num_indexs+num_offsets_block, 1)]

        return tag, self.binary[len(tag):-max(num_offsets_block, 1)]


class CacheMemory:
    def __init__(self, cache_size, line_size, block_size):
        self.cache_size = cache_size
        self.line_size = line_size
        self.block_size = block_size
        self.num_lines = cache_size // line_size
        self.num_blocks = line_size // block_size
        self.cache = [[None] * self.num_blocks for _ in range(self.num_lines)]

        if math.log2(self.num_lines).is_integer() is False:
            raise Exception("O número de linhas deve ser potência de 2!")

        self.num_bits_index = int(math.log2(self.num_lines))

        if math.log2(self.block_size).is_integer() is False:
            raise Exception("O tamanho do bloco deve ser potência de 2!")

        self.offset_block = int(math.log2(self.block_size))

        self.hits = 0
        self.misses = 0

    def read(self, address):
        raise NotImplementedError()
    
    def print(self):
        """
            Imprime o estado atual da cache no arquivo de saída.
        """
        with open("output.txt", "a") as file:
            file.write("================\n")
            file.write("IDX V ** ADDR **\n")

            for i, line in enumerate(self.cache):
                for j, block in enumerate(line):
                    crr = str(i*self.num_blocks + j)
                    
                    index = "0"*(3-len(crr)) + crr

                    valid = 1 if block is not None else 0

                    if block is None:
                        address = " "*10
                    else:
                        address = hex(int(block.binary[:-self.offset_block], 2))
                        address = "0x" + address.replace("0x", "").zfill(8).upper()

                    file.write(f"{index} {valid} {address}\n")

    def print_hits_and_misses(self):
        with open("output.txt", "a") as file:
            file.write("\n")
            file.write(f"hits: {self.hits}\n")
            file.write(f"misses: {self.misses}\n")


class DirectMappingCache(CacheMemory):
    def __init__(self, cache_size, line_size, block_size) -> None:
        super().__init__(cache_size, line_size, block_size)


    def read(self, address: Address) -> None:
        tag, index = address.get_parts(self.num_bits_index, self.offset_block)
        
        if len(index) > 0:
            line = int(index, 2)
        else:
            line = 0
        
        if self.cache[line][0] is None:
            self.cache[line][0] = address
            self.misses += 1
            return
        
        tag_cache = self.cache[line][0].get_parts(self.num_bits_index, self.offset_block)[0]

        if tag_cache == tag:
            self.hits += 1
        else:
            self.cache[line][0] = address
            self.misses += 1
    

class SetAssociativeCache(CacheMemory):
    def __init__(self, cache_size, line_size, block_size):
        super().__init__(cache_size, line_size, block_size)

        self.less_recently_used = []


    def read(self, address):
        tag, index = address.get_parts(self.num_bits_index, self.offset_block)
        
        if len(index) > 0:
            line = int(index, 2)
        else:
            line = 0

        for i, block in enumerate(self.cache[line]):
            if block is None:
                self.cache[line][i] = address
                self.less_recently_used.append(i)
                self.misses += 1
                return

            tag_cache = block.get_parts(self.num_bits_index, self.offset_block)[0]

            if tag_cache == tag:
                self.hits += 1
                self.less_recently_used.remove(i)
                self.less_recently_used.append(i)
                return

        less_block = self.less_recently_used.pop(0)
        self.cache[line][less_block] = address
        self.less_recently_used.append(less_block)
        self.misses += 1


args = sys.argv

if len(args) < 4:
    raise Exception("Está faltando argumentos!")

cache_size = int(args[1])
line_size = int(args[2])
block_size = int(args[3])

if cache_size % line_size != 0 or line_size > cache_size:
    raise Exception("O tamanho da cache deve ser múltiplo do tamanho da linha!")

if line_size % block_size != 0 or block_size > line_size:
    raise Exception("O tamanho da linha deve ser múltiplo do tamanho do bloco!")

if math.log2(cache_size).is_integer() is False:
    raise Exception("O tamanho da cache deve ser potência de 2!")

if math.log2(line_size).is_integer() is False:
    raise Exception("O tamanho da linha deve ser potência de 2!")

addresses = []
with open("input.txt", "r") as file:
    for line in file:
        address = Address(line)
        addresses.append(address)

if line_size == block_size:
    cache = DirectMappingCache(cache_size, line_size, block_size)
else:
    cache = SetAssociativeCache(cache_size, line_size, block_size)

# Limpar o arquivo de saída
with open("output.txt", "w") as file: pass

for address in addresses:
    cache.read(address)
    cache.print()

cache.print_hits_and_misses()
