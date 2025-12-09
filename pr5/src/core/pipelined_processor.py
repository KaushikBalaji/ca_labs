from .processor import Processor


class PipelinedProcessor(Processor):
    def __init__(self, start, I1, L1, L2, ram, logger, st, cfg):
        super().__init__(start, I1, L1, L2, ram, logger, st, cfg)
        self.stats = st
        # self.stats.increment_clock_cycle()
        # self.stats.increment_clock_cycle()
        # self.stats.increment_clock_cycle()
        # self.stats.increment_clock_cycle()
        self.jal_stalled = False
        self.pipeline_regs = {
            "IF_ID": None,
            "ID_EX": {
                "rs1": None, "rs2": None,
                "v_rs1": None, "v_rs2": None,
                "imm": None, "rd": None,
                "opcode": None, "pc": None
            },
            "EX_MEM": {
                "alu_result": None,
                "rs2_val": None,
                "rd": None,
                "opcode": None
            },
            "MEM_WB": {
                "result": None,
                "rd": None,
                "opcode": None
            }
            
        }


    def run(self, num_insts):
        i_cnt = 0
        while i_cnt < num_insts:

            # ---------------- IF Stage ----------------
            instr = self.fetch()
            if instr is None:
                break
            self.pipeline_regs["IF_ID"] = {"instruction": instr}

            # ---------------- ID Stage ----------------
            rs1, rs2, v_rs1, v_rs2, v_imm, rd, opcode = \
                self.decode(self.pipeline_regs["IF_ID"]["instruction"])
            self.pipeline_regs["ID_EX"] = {
                "rs1": rs1, "rs2": rs2,
                "v_rs1": v_rs1, "v_rs2": v_rs2,
                "v_imm": v_imm, "rd": rd,
                "opcode": opcode
            }

            # ---------- HAZARD DETECTION ----------

            hazard = False
            EX_MEM = self.pipeline_regs["EX_MEM"]
            MEM_WB = self.pipeline_regs["MEM_WB"]

            if (EX_MEM.get("rd") and (EX_MEM.get("rd") == rs1 or EX_MEM.get("rd") == rs2)) or \
                (MEM_WB.get("rd") and (MEM_WB.get("rd") == rs1 or MEM_WB.get("rd") == rs2)):
                self.stats.increment_clock_cycle()
                self.stats.increment_clock_cycle()
                self.stats.increment_clock_cycle()

            

            # ---------------- Operand fetch ----------------
            ID_EX = self.pipeline_regs["ID_EX"]
            op1, op2, v_pc = self.operand_fetch(
                ID_EX["rs1"], ID_EX["rs2"], ID_EX["v_rs1"], ID_EX["v_rs2"], ID_EX["v_imm"]
            )
            ID_EX["operand1"] = op1
            ID_EX["operand2"] = op2
            ID_EX["v_pc"] = v_pc

            # ---------------- EX Stage ----------------
            result = self.execute(
                ID_EX["operand1"], ID_EX["operand2"], ID_EX["opcode"]
            )
            self.pipeline_regs["EX_MEM"] = {
                "result": result,
                "rs2": ID_EX["rs2"],
                "rd": ID_EX["rd"],
                "opcode": ID_EX["opcode"],
                "v_pc": ID_EX["v_pc"],
                "v_imm": ID_EX["v_imm"],
                "rs1": ID_EX["rs1"]
            }

            # ---------------- MEM ----------------
            EX_MEM = self.pipeline_regs["EX_MEM"]
            loaded_data = self.mem_access(
                EX_MEM["opcode"], EX_MEM["result"], EX_MEM["rs2"],
            )
            self.pipeline_regs["MEM_WB"] = {
                "loaded_data": loaded_data,
                "result": EX_MEM["result"],
                "rd": EX_MEM["rd"],
                "opcode": EX_MEM["opcode"],
                "v_pc": EX_MEM["v_pc"],
                "v_imm": EX_MEM["v_imm"],
                "rs1": EX_MEM["rs1"]
            }

            # control hazard detection for branches
            opcode = self.pipeline_regs["MEM_WB"]["opcode"]
            if (opcode & 0xFF000) in (0x63000,):
                    self.stats.increment_clock_cycle()
                    self.stats.increment_clock_cycle()
                    self.stats.increment_clock_cycle()
            
            # control hazard detection for jumps
            # if ((self.pipeline_regs["MEM_WB"]["opcode"] & 0xFF000) in (0x6F000, 0x67000)):
            #     if not self.jal_stalled:
            #             for _ in range(3):
            #                 self.stats.increment_clock_cycle()
            #             self.jal_stalled = True

            MEM_WB = self.pipeline_regs["MEM_WB"]
            pc = self.update_pc(
                MEM_WB["v_pc"], MEM_WB["opcode"], MEM_WB["result"], MEM_WB["v_imm"], MEM_WB["rs1"]
            )
            

            if pc != v_pc:
                self.jal_stalled = False
                self.control_stalled = False
                

            self.reg_write(
                MEM_WB["opcode"], MEM_WB["rd"], EX_MEM["rs2"], MEM_WB["result"], MEM_WB["loaded_data"], MEM_WB["v_pc"], pc
            )

            i_cnt += 1
            self.stats.increment_instruction_count()
            self.stats.increment_clock_cycle()
            self.logr.info(f"Simulated {i_cnt} instructions in {self.stats.get_clocks()} clock cycles")

        self.stats.write_statistics("stats.json")

        pass