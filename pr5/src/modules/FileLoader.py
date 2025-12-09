from modules import RAM
from elftools.elf.elffile import ELFFile

def LoadtoRam(ram, file_path):
    with open(file_path, "rb") as f:
        elf = ELFFile(f)

        #print(f"ELF type: {elf.header['e_type']}")
        
        #print(f"Entry Point: {hex(elf.header['e_entry'])}")

        # Iterate over loadable sections
        for segment in elf.iter_segments():
            if segment['p_type'] != 'PT_LOAD':
                continue

            vaddr = segment['p_vaddr']   # virtual memory address
            data = segment.data()        # raw bytes

            #print(f"Loading segment at 0x{vaddr:x}, size={len(data)}")

            for i, byte in enumerate(data):
                ram.writeRAM(vaddr + i, byte)

    #print(f"Load finish of ELF {file_path} into RAM")


def dump_ram_words(ram, start_addr, num_words):
    for i in range(num_words):
        addr = start_addr + i*4
        word = littleendianConverter(ram, addr)  # little-endian
        print(f"0x{addr:08x}: {word:08x}")


def littleendianConverter(ram, addr):
    word = 0
    for i in range(4):
        byte = ram.readRAM(addr+i) or 0
        word |= (byte << (8*i))

    return word