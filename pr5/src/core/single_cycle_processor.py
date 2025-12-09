from .processor import Processor

class SingleCycleProcessor(Processor):
    def __init__(self, start, I1, L1, L2, ram, logger, st, cfg):
        super().__init__(start, I1, L1, L2, ram, logger, st, cfg)
        self.stats = st

    def run(self, num_insts):
        """
        Run the processor in a single cycle for each instruction.
        """
        i_cnt = 0
        while (i_cnt < num_insts):
            instruction = self.fetch()
            if instruction is None:
                break

            rs1,rs2,v_rs1,v_rs2,v_imm,rd,opcode=self.decode(instruction)

            operand1,operand2,v_pc=self.operand_fetch(rs1,rs2,v_rs1,v_rs2,v_imm)

            result=self.execute(operand1,operand2,opcode)

            loaded_data=self.mem_access(opcode,result,rs2)

            pc=self.update_pc(v_pc,opcode,result,v_imm,rs1)

            self.reg_write(opcode,rd,rs2,result,loaded_data,v_pc,pc)

            
            i_cnt += 1
            self.stats.increment_instruction_count()
            self.stats.increment_clock_cycle()
        
        self.logr.info(f"Simulated {i_cnt} instructions in {self.stats.get_clocks()} clock cycles.")

        self.stats.write_statistics("stats.json")
