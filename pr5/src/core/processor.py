from abc import ABC, abstractmethod
from .fu import *
from .riscv_tables import *


class Processor(ABC):
    def __init__(self, start,I1, L1, L2, ram, logger, stats, cfg):
        self.pc = start
        self.curr_pc = 0
        self.registers = [0] * 32  # x0 to x31

        self.mem = ram
        self.I1 = I1
        self.L1 = L1
        self.L2 = L2

        self.stats = stats
        self.cfg = cfg
        self.logr = logger
        self.decoded = {}
        self.ldata = 0

    def _ram_latency(self):
        return self.cfg.get_mem_latency()


    # ---------------- Hierarchy Memory Read ------------------

    def read_memory_instr(self, address):
        total_cycles = 0

        if self.I1 is not None:
            hit1, data1, lat1, miss_addr = self.I1.cache_access(address)
            total_cycles += lat1
            if hit1:
                self.logr.debug(f"Instruction fetched from I1 cache at address {hex(address)}")
                return data1, total_cycles
            
        # if not found in I1, check shared L2 cache
        if self.L2 is not None:
            hit2, data2, lat2, miss_addr = self.L2.cache_access(address)
            total_cycles += lat2
            if hit2:
                self.logr.debug(f"Instruction fetched from L2 cache at address {hex(address)}")
                return data2, total_cycles
            
        # finally, read from RAM
        instr = self.mem.read_word(address)
        total_cycles += self._ram_latency()

        return instr, total_cycles
            
    
    def read_memory_data(self, address):
        total_cycles = 0

        if self.L1 is not None:
            hit1, data1, lat1, miss_addr = self.L1.cache_access(address)
            total_cycles += lat1
            if hit1:
                self.logr.debug(f"Data fetched from L1 cache at address {hex(address)}")
                return data1, total_cycles
            
        if self.L2 is not None:
            hit2, data2, lat2, miss_addr = self.L2.cache_access(address)
            total_cycles += lat2
            if hit2:
                self.logr.debug(f"Data fetched from L2 cache at address {hex(address)}")
                return data2, total_cycles
            
        data = self.mem.read_word(address)
        total_cycles += self._ram_latency()

        return data, total_cycles
        


    # ----------------- Hierarchy Memory Write ----------------------

    def write_memory_data(self, address, data):
        total_cycles = 0

        if self.L1 is not None:
            hit1, _, lat1, _ = self.L1.cache_access(address, is_write=True, write_data=data)
            self.stats.increment_memory_access()
            total_cycles += lat1
            
        if self.L2 is not None:
            hit2, _, lat2, _ = self.L2.cache_access(address, is_write=True, write_data=data)
            self.stats.increment_memory_access()
            total_cycles += lat2
            
        self.mem.write_word(address, data)
        total_cycles += self._ram_latency()

        return total_cycles



    # ---------------- Fetch from Memory Hierarchy ---------------
    def fetch(self) -> int:
        """
        Fetch the instruction from memory, and update PC
        returns instruction
        """
        try:
            self.curr_pc = self.pc 
            instruction, cycles = self.read_memory_instr(self.curr_pc)
            self.logr.debug(f"got instruction {instruction:08x} at {self.curr_pc:08x}")
            
            # adding memory fetch latency
            for _ in range(cycles):
                self.stats.increment_clock_cycle()

            return instruction
        
        except ValueError as e:
            self.logr.error(f"Error fetching instruction at {self.curr_pc:08x}: {e}")
            exit()

    

    def decode(self, instruction: int):
        """
        Gets an instruction (32-bit integer) and returns
        a dictionary with the following fields {"opcode", "rs1", "rs2", "rd", "imm"}
        """
        # Extract the opcode (7 bits)
        opcode = instruction & 0x7F
        self.decoded["opcode"] = opcode

        if opcode == 0x33:  # R-type (Arithmetic)
            funct7 = (instruction >> 25) & 0x7F
            rs2 = (instruction >> 20) & 0x1F
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            rd = (instruction >> 7) & 0x1F
            self.decoded["rs1"] = rs1
            self.decoded["rs2"] = rs2
            self.decoded["rd"] = rd
            self.decoded["funct3"] = funct3
            self.decoded["funct7"] = funct7
            self.decoded["imm"] = 0
        elif opcode == 0x03:  # I-type (Load)
            imm = instruction >> 20
            if (imm > 0x800):
                imm = imm | 0xFFFFF000
                imm = imm - (1 << 32)
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            rd = (instruction >> 7) & 0x1F
            self.decoded["rs1"] = rs1
            self.decoded["rs2"] = 0
            self.decoded["rd"] = rd
            self.decoded["funct3"] = funct3
            self.decoded["funct7"] = 0x00
            self.decoded["imm"] = imm
        elif opcode == 0x13:  # I-type (Immediate Arithmetic)
            imm = instruction >> 20
            if (imm > 0x800):
                imm = imm | 0xFFFFF000
                imm = imm - (1 << 32)
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            rd = (instruction >> 7) & 0x1F
            self.decoded["rs1"] = rs1
            self.decoded["rs2"] = 0
            self.decoded["rd"] = rd
            self.decoded["funct3"] = funct3
            self.decoded["funct7"] = 0x00
            self.decoded["imm"] = imm
        elif opcode == 0x23:  # S-type (Store)
            imm = ((instruction >> 25) << 5) | ((instruction >> 7) & 0x1F)
            if (imm > 0x800):
                imm = imm | 0xFFFFF000
                imm = imm - (1 << 32)
            rs2 = (instruction >> 20) & 0x1F
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            self.decoded["rs1"] = rs1
            self.decoded["rs2"] = rs2
            self.decoded["rd"] = 0
            self.decoded["funct3"] = funct3
            self.decoded["funct7"] = 0x00
            self.decoded["imm"] = imm 
        elif opcode == 0x63:  # B-type (Branch)
            imm_12 = (instruction >> 31) & 0x1
            imm_10_5 = (instruction >> 25) & 0x1F
            imm_4_1 = (instruction >> 8) & 0xF
            imm_11 = (instruction >> 7) & 0x1
            imm = ((imm_12 << 11) | (imm_11 << 10) | (imm_10_5 << 4) | imm_4_1) << 1
            if (imm > 0x1000):
                imm = imm | 0xFFFFF000
                imm = imm - (1 << 32)
            rs2 = (instruction >> 20) & 0x1F
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            self.decoded["rs1"] = rs1
            self.decoded["rs2"] = rs2
            self.decoded["rd"] = 0
            self.decoded["funct3"] = funct3
            self.decoded["funct7"] = 0x00
            self.decoded["imm"] = imm
        elif opcode == 0x37:  # U-type (LUI)
            imm = instruction & 0xFFFFF000
            rd = (instruction >> 7) & 0x1F
            self.decoded["rs1"] = 0
            self.decoded["rs2"] = 0
            self.decoded["rd"] = rd
            self.decoded["funct3"] = 0x0
            self.decoded["funct7"] = 0x00
            self.decoded["imm"] = imm
        elif opcode == 0x17:  # U-type (AUIPC)
            imm = instruction & 0xFFFFF000
            rd = (instruction >> 7) & 0x1F
            self.decoded["rs1"] = 0
            self.decoded["rs2"] = 0
            self.decoded["rd"] = rd
            self.decoded["funct3"] = 0x0
            self.decoded["funct7"] = 0x00
            self.decoded["imm"] = imm
        elif opcode == 0x6F:  # J-type (JAL)
            imm_20 = (instruction >> 31) & 0x1  
            imm_10_1 = (instruction >> 21) & 0x3FF
            imm_11 = (instruction >> 20) & 0x1
            imm_19_12 = (instruction >> 12) & 0xFF
            imm = ((imm_20 << 19) | (imm_19_12 << 11) | (imm_11 << 10) | imm_10_1) << 1
            if (imm > 0x100000):
                imm = imm | 0xFFF00000
                imm = imm - (1 << 32)
            rd = (instruction >> 7) & 0x1F
            self.decoded["rs1"] = 0
            self.decoded["rs2"] = 0
            self.decoded["rd"] = rd
            self.decoded["funct3"] = 0x0
            self.decoded["funct7"] = 0x00
            self.decoded["imm"] = imm
        elif opcode == 0x67:  # JALR (I-type)
            rd = (instruction >> 7) & 0x1F
            funct3 = (instruction >> 12) & 0x7
            rs1 = (instruction >> 15) & 0x1F
            imm = (instruction >> 20) & 0xFFF
            # sign extend
            if imm & 0x800:
                imm |= 0xFFFFF000

            self.decoded["rd"] = rd
            self.decoded["rs1"] = rs1
            self.decoded["rs2"] = 0
            self.decoded["funct3"] = funct3
            self.decoded["imm"] = imm
        else:
            self.decoded["opcode"] = opcode
            self.decoded["rs1"] = 0
            self.decoded["rs2"] = 0
            self.decoded["rd"] = 0
            self.decoded["imm"] = 0
            self.decoded["funct3"] = 0x0
            self.decoded["funct7"] = 0x00
        rs1 = self.decoded["rs1"]
        rs2 = self.decoded["rs2"]
        v_rs1 = self.registers[rs1] if rs1 != 0 and rs1 != None else 0 
        v_rs2 = self.registers[rs2] if rs2 != 0 and rs2 != None else 0 

        v_imm = self.decoded["imm"]

        self.logr.debug(f"opcode = {self.decoded['opcode']:02x}, " + 
                        f"funct3 = {self.decoded['funct3']:01x}, " + 
                        f"funct7 = {self.decoded['funct7']:02x}")
        self.op = ((self.decoded["opcode"] << 12) | 
                   (self.decoded["funct3"] << 8) | 
                   (self.decoded["funct7"]))
        return rs1,rs2,v_rs1,v_rs2,v_imm,self.decoded["rd"],self.op

    def operand_fetch(self, rs1, rs2, v_rs1, v_rs2, v_imm):
        
        self.logr.debug(f"rs1 = {rs1}, rs2 = {rs2}, imm = {hex(v_imm)}")
        v_pc  = self.curr_pc

        self.op1, self.op2 = alu_operands.get(self.op, lambda v_rs1,v_rs2,v_imm,v_pc:(None, None))(v_rs1, v_rs2, v_imm, v_pc)
        # FIXME: the choice of the below constant may be correct always
        if (self.op1 > 0xF0000000):
            self.op1 = self.op1 - (1 << 32)

        # FIXME: the choice of the below constant may be correct always
        if (self.op2 > 0xF00000000):
            self.op2 = self.op2 - (1 << 32)
        self.logr.debug(f"op1: {self.op1}, op2: {self.op2}")
        return self.op1,self.op2,v_pc


    def execute(self,operand1,operand2,opcode):
        """
        Execute the instruction
        decoded_instr, operand1 and operand2 are returned by previous stages
        returns the result of the operation
        """
        self.result = alu_function.get(opcode,lambda op1,op2: None)(operand1,operand2)
        self.logr.debug(f"Result of {opcode:05x} is: {self.result}")
        return self.result

    def update_pc(self, v_pc, opcode, result, v_imm, rs1):
        """
        Update PC to take a branch or jump
        """
        # Default case: sequential execution
        next_pc = v_pc+ 4

        if opcode == 0x6F000:  # JAL
            next_pc = v_imm + v_pc
        elif opcode == 0x67000:
            next_pc = (self.registers[rs1] + v_imm) & ~1
        elif opcode == 0x63000:  # BEQ
            if result:        # (rs1 == rs2) -> result = 1
                if v_imm < 0:
                    next_pc = v_pc + v_imm + 0x400
                else:
                    next_pc = v_pc + v_imm

        elif opcode == 0x63100:  # BNE
            if result:        # (rs1 != rs2) -> result = 1
                if v_imm < 0:
                    next_pc = v_pc + v_imm + 0x400
                else:
                    next_pc = v_pc + v_imm

        elif opcode == 0x63400:  # BLT
            if result:        # (rs1 < rs2) -> result = 1
                if v_imm < 0:
                    next_pc = v_pc + v_imm + 0x400
                else:
                    next_pc = v_pc + v_imm


        elif opcode == 0x63500:  # BGE
            if result:        # (rs1 >= rs2) -> result = 1
                if v_imm < 0:
                    next_pc = v_pc + v_imm + 0x400
                else:
                    next_pc = v_pc + v_imm  # target already computed

        # Update PC register
        self.pc = next_pc & 0xFFFFFFFF
        return self.pc

    def mem_access(self, inst, addr, rs2):
        """
        Access memory based on the instruction.
        """

        # Handle load instructions
        if is_load(inst):
            self.stats.increment_memory_access()
            data, cycles = self.read_memory_data(addr)

            # adding memory load latency
            for _ in range(cycles):
                self.stats.increment_clock_cycle()

            masked_inst = (inst & 0x00F00) >> 8
            if (masked_inst == 0x0 or masked_inst == 0x4):
                self.ldata = self.mem.read(addr)
            elif (masked_inst == 0x1 or masked_inst == 0x5):
                self.ldata = self.mem.read_halfword(addr)
            elif (masked_inst == 0x2):
                self.ldata = self.mem.read_word(addr)
            else:
                self.logr.error(f"Invalid load op {inst:05x}")
                exit()
            return self.ldata
        
        # Handle store instructions
        
        if is_store(inst):
            self.stats.increment_memory_access()
            data = self.registers[rs2] if rs2 != 0 and rs2 != None else 0 
            cycles = self.write_memory_data(addr, data)

            # adding memory store latency
            for _ in range(cycles):
                self.stats.increment_clock_cycle()

            masked_inst = (inst & 0x00F00) >> 8
            if (masked_inst == 0x0):
                self.mem.write(addr, (data & 0xFF))
            elif (masked_inst == 0x1):
                self.mem.write_halfword(addr, (data & 0xFFFF))
            elif (masked_inst == 0x2):
                self.mem.write_word(addr, data)
            else:
                self.logr.error(f"Invalid store op {inst:05x}")
                exit()


    def reg_write(self, inst, rd, rs2, result, loaded_data, v_pc, pc):
        """
        Write the result of the operation back to the register.
        """
        
        
        if is_branch(inst):
            self.logr.out(f"{v_pc:08x} | " + 
                          f"next_pc = {pc:08x} | " + 
                          f"x? = {0:08x} | " + 
                          f"mem[?] = {0:08x}")
            return
        
        if is_jump(inst):
            self.registers[rd] = result
            self.logr.out(f"{v_pc:08x} | " +
                          f"next_pc = {pc:08x} | " + 
                          f"x{rd} = {self.registers[rd]:08x} | " +
                          f"mem[?] = {0:08x}")
            return

        if is_unimplemented(inst):
            self.logr.out(f"{v_pc:08x} | " + 
                          f"next_pc = {pc:08x} | " + 
                          f"x? = {0:08x} | " + 
                          f"mem[?] = {0:08x} *unimplemented*")
            return

        if is_load(inst):
            self.registers[rd] = loaded_data
            self.logr.out(f"{v_pc:08x} | " + 
                          f"next_pc = {pc:08x} | " +
                          f"x{rd} = {self.registers[rd]:08x} | " +
                          f"mem[{result:08x}] => {loaded_data:08x}")
            return

        if is_store(inst):
            data = self.registers[rs2] if rs2 != 0 and rs2 != None else 0 
            self.logr.out(f"{v_pc:08x} | " +
                          f"next_pc = {pc:08x} | " +
                          f"x? = {0:08x} | " + 
                          f"mem[{result:08x}] <= {data:08x}")
            return
        
        # All other instructions
        self.registers[rd] = result
        self.logr.out(f"{v_pc:08x} | " + 
                      f"next_pc = {pc:08x} | " +
                      f"x{rd} = {self.registers[rd]:08x} | " + 
                      f"mem[?] = {0:08x}")

    @abstractmethod
    def run(self, num_insts):
        """Run the processor. To be implemented by subclasses."""
        pass