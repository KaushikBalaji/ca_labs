from modules import FileLoader 

def DisassembleInstructions(ram, start_addr, end_addr):
    addr = start_addr
    while addr < end_addr:
        instr = FileLoader.littleendianConverter(ram, addr)
        opcode = instr & 0x7f               # 0-6 bits
        funct3 = (instr >> 12) & 0x7        # 12-14 bits
        funct7 = (instr >> 25) & 0x7f       # 25-31 bits
        rd = (instr >> 7) & 0x1F
        rs1 = (instr >> 15) & 0x1F
        rs2 = (instr >> 20) & 0x1F

        instr_name = ""

        if instr == 0 or instr is None:
            addr += 4         # skip when all entries are 0's.
            continue

        # ----------RV32I & RV32M -------------

        #   RV32M
        if opcode == 0x33:
            if funct7 == 0x01:
                if funct3 == 0x0: 
                    instr_name = "mul"
                elif funct3 == 0x1: 
                    instr_name = "mulh"
                elif funct3 == 0x2: 
                    instr_name = "mulhsu"
                elif funct3 == 0x3: 
                    instr_name = "mulhu"
                elif funct3 == 0x4: 
                    instr_name = "div"
                elif funct3 == 0x5: 
                    instr_name = "divu"
                elif funct3 == 0x6: 
                    instr_name = "rem"
                elif funct3 == 0x7: 
                    instr_name = "remu"

            #   RV32I - Arithmetic
            else:
                if funct3 == 0x0 and funct7 == 0x00:  # 0000000
                    instr_name = "add"
                elif funct3 == 0x0 and funct7 == 0x20:  # 0100000
                    instr_name = "sub"
                elif funct3 == 0x4 and funct7 == 0x00:
                    instr_name = "xor"
                elif funct3 == 0x6 and funct7 == 0x00:
                    instr_name = "or"
                elif funct3 == 0x7 and funct7 == 0x00:
                    instr_name = "and"
                elif funct3 == 0x1 and funct7 == 0x00:
                    instr_name = "sll"
                elif funct3 == 0x5 and funct7 == 0x00:
                    instr_name = "srl"
                elif funct3 == 0x5 and funct7 == 0x20:
                    instr_name = "sra"
                elif funct3 == 0x2 and funct7 == 0x00:
                    instr_name = "slt"
                elif funct3 == 0x3 and funct7 == 0x00:
                    instr_name = "sltu"

            print(f"0x{addr:08x}: {instr:08x}   {instr_name} x{rd},x{rs1},x{rs2}") 
            


        #   RV32I  I-type arithmetic
        elif opcode == 0x13:
            if funct3 == 0x0:
                instr_name = "addi"
            elif funct3 == 0x4:
                instr_name = "xori"
            elif funct3 == 0x6:
                instr_name = "ori"
            elif funct3 == 0x7:
                instr_name = "andi"
            elif funct3 == 0x1 and funct7 == 0x00:
                instr_name = "slli"
            elif funct3 == 0x5 and funct7 == 0x00:
                instr_name = "srli"
            elif funct3 == 0x5 and funct7 == 0x20:
                instr_name = "srai"
            elif funct3 == 0x2:
                instr_name = "slti"
            elif funct3 == 0x3:
                instr_name = "sltiu"

            imm = (instr >> 20) & 0xFFF
            if imm & 0x800: imm -= 0x1000

            print(f"0x{addr:08x}: {instr:08x}   {instr_name} x{rd},x{rs1},{imm}") 



        #   RV32I   load instructions
        elif opcode == 0x03:
            if funct3 == 0x0: 
                instr_name = "lb"
            elif funct3 == 0x1: 
                instr_name = "lh"
            elif funct3 == 0x2: 
                instr_name = "lw"
            elif funct3 == 0x4: 
                instr_name = "lbu"
            elif funct3 == 0x5: 
                instr_name = "lhu"

            imm = (instr >> 20) & 0xFFF
            if imm & 0x800: imm -= 0x1000

            print(f"0x{addr:08x}: {instr:08x}   {instr_name} x{rd},{imm}(x{rs1})")



        #   RV32I  store-type
        elif opcode == 0x23:
            if funct3 == 0x0: 
                instr_name = "sb"
            elif funct3 == 0x1: 
                instr_name = "sh"
            elif funct3 == 0x2: 
                instr_name = "sw"

            imm = ((instr >> 7) & 0x1F) | (((instr >> 25) & 0x7F) << 5)
            if imm & 0x800: imm -= 0x1000

            print(f"0x{addr:08x}: {instr:08x}   {instr_name} x{rs2}, {imm}(x{rs1})")



        #   RV32I   branch-type
        elif opcode == 0x63:
            if funct3 == 0x0: 
                instr_name = "beq"
            elif funct3 == 0x1: 
                instr_name = "bne"
            elif funct3 == 0x4: 
                instr_name = "blt"
            elif funct3 == 0x5: 
                instr_name = "bge"
            elif funct3 == 0x6: 
                instr_name = "bltu"
            elif funct3 == 0x7: 
                instr_name = "bgeu"
            
            #   imm = bit 11, bit 1-4,  
            imm = imm_gen(instr, opcode)
            target = addr + imm         # jump to address = addr + offset(imm)
            print(f"0x{addr:08x}: {instr:08x}   {instr_name} x{rs1}, x{rs2}, 0x{target:08x}")




        elif opcode == 0x6F:
            instr_name = "jal"
            imm = imm_gen(instr, opcode)
            target = addr + imm
            print(f"0x{addr:08x}: {instr:08x}   {instr_name} x{rd}, 0x{target:08x}")



        #   jalr
        elif opcode == 0x67 and funct3 == 0x0:
            instr_name = "jalr"
            imm = (instr >> 20) & 0xFFF
            if imm & 0x800: 
                imm -= 0x1000
            print(f"0x{addr:08x}: {instr:08x}   {instr_name} x{rd}, {imm}(x{rs1})")


        #   lui
        elif opcode == 0x37:
            instr_name = "lui"
            imm = instr & 0xFFFFF000
            print(f"0x{addr:08x}: {instr:08x}   {instr_name} x{rd}, {imm}")


        #   auipc
        elif opcode == 0x17:
            instr_name = "auipc"
            # imm = instr & 0xFFFFF000
            imm = instr >> 12
            print(f"0x{addr:08x}: {instr:08x}   {instr_name} x{rd}, 0x{imm:x}")


        #   sys
        elif opcode == 0x73:
            if instr >> 20 == 0:
                instr_name = "ecall"
            elif instr >> 20 == 1:
                instr_name = "ebreak"
            
            print(f"0x{addr:08x}: {instr:08x}   {instr_name}")



        #-----------RV32A------------------
        elif opcode == 0x2F and funct3 == 0x2:
            aq = (instr >> 26) & 0x1
            rl = (instr >> 25) & 0x1
            funct5 = (instr >> 27) & 0x1F
            if funct5 == 0b00010:
                instr_name = "lr.w"
            elif funct5 == 0b00011:
                instr_name = "sc.w"
            elif funct5 == 0b00001:
                instr_name = "amoswap.w"
            elif funct5 == 0b00000:
                instr_name = "amoadd.w"
            elif funct5 == 0b00100:
                instr_name = "amoxor.w"
            elif funct5 == 0b01100:
                instr_name = "amoand.w"
            elif funct5 == 0b01000:
                instr_name = "amoor.w"
            elif funct5 == 0b10000:
                instr_name = "amomin.w"
            elif funct5 == 0b10100:
                instr_name = "amomax.w"
            elif funct5 == 0b11000:
                instr_name = "amominu.w"
            elif funct5 == 0b11100:
                instr_name = "amomaxu.w"
            
            print(f"0x{addr:08x}: {instr:08x}   {instr_name} x{rd}, (x{rs1}), x{rs2} aq={aq} rl={rl}")



        # if(instr_name != ""):
        #     print(f"0x{addr:08x}: {instr:08x}   {instr_name} ") 

        else:
            print(f"0x{addr:08x}: {instr:08x}")
            
        addr += 4           # unknow opcode


        # print(f"{START_ADDRESS:08x}")
        # print(type(instr))

        # print(f"{instr:08x}")


def DisassembleData(ram, start_addr, end_addr):
    # size in bytes (must be multiple of 4)
    addr = start_addr
    while (addr < end_addr):
        word = FileLoader.littleendianConverter(ram, addr)
        if word is None or word == 0:
            addr += 4
            continue
        print(f"0x{addr:08x}: {word:08x}")
        addr += 4


def imm_gen(instr, opcode):
    if opcode == 0x63:	#	branch instructions
        imm_12   = (instr >> 31) & 0x1
        imm_11   = (instr >> 7)  & 0x1
        imm_10_5 = (instr >> 25) & 0x3F
        imm_4_1  = (instr >> 8)  & 0xF

        imm = (imm_12 << 12) | (imm_11 << 11) | (imm_10_5 << 5) | (imm_4_1 << 1)

        # sign-extend 13-bit imm
        if imm & (1 << 12):
            imm -= 1 << 13
    else:		#	jal
        imm_20   = (instr >> 31) & 0x1
        imm_19_12= (instr >> 12) & 0xFF
        imm_11   = (instr >> 20) & 0x1
        imm_10_1 = (instr >> 21) & 0x3FF
        imm = (imm_20 << 20) | (imm_19_12 << 12) | (imm_11 << 11) | (imm_10_1 << 1)
        if imm & 0x100000:                # sign bit (bit 20)
            imm -= 1 << 21
    return imm