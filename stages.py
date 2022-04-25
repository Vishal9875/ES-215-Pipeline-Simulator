import basic
import buffer

# Control unit
# MemtoReg, RegWrite, Branch, MemRead, MemWrite, RegDst, AluSrc, AluOp
ctrl = {0b000000: (0b0, 0b1, 0b0, 0b0, 0b0, 0b1, 0b0, 0b10), # R-Type
        0b100011: (0b1, 0b1, 0b0, 0b1, 0b0, 0b0, 0b1, 0b00), # lw
        0b101011: (0b0, 0b0, 0b0, 0b0, 0b1, 0b0, 0b1, 0b00), # sw
        0b000100: (0b0, 0b0, 0b1, 0b0, 0b0, 0b0, 0b0, 0b01), # beq
        0b000010: (0b0, 0b0, 0b1, 0b0, 0b0, 0b0, 0b0, 0b01), # jump (tried)
        0b001000: (0b0, 0b1, 0b0, 0b0, 0b0, 0b0, 0b1, 0b00)} # addi

def EX_fwd():
    #Forwarding unit
    if buffer.MEM_WB_CTRL['REG_WRITE'] == 1  and buffer.MEM_WB['RD'] != 0 and buffer.MEM_WB['RD'] == buffer.ID_EX['RS'] and (buffer.EX_MEM['RD'] != buffer.ID_EX['RS'] or buffer.EX_MEM_CTRL['REG_WRITE'] == 0):
        buffer.FWD['FWD_A'] = 1
    elif buffer.EX_MEM_CTRL['REG_WRITE']==1 and buffer.EX_MEM['RD'] != 0 and buffer.EX_MEM['RD'] == buffer.ID_EX['RS']:
        buffer.FWD['FWD_A'] = 2
    else:
        buffer.FWD['FWD_A'] = 0

    if buffer.MEM_WB_CTRL['REG_WRITE'] == 1 and buffer.MEM_WB['RD'] != 0 and buffer.MEM_WB['RD'] == buffer.ID_EX['RT'] and (buffer.EX_MEM['RD'] != buffer.ID_EX['RT'] or buffer.EX_MEM_CTRL['REG_WRITE'] == 0):
        buffer.FWD['FWD_B'] = 1
    elif buffer.EX_MEM_CTRL['REG_WRITE'] == 1 and buffer.EX_MEM['RD'] != 0 and buffer.EX_MEM['RD'] == buffer.ID_EX['RT']:
        buffer.FWD['FWD_B'] = 2
    else:
        buffer.FWD['FWD_B'] = 0

    #FwdA Multiplexer
    if buffer.FWD['FWD_A'] ==0 or not basic.data_hzd:
        basic.outFwdA = buffer.ID_EX['A']
    elif buffer.FWD['FWD_A'] == 1:
        if buffer.MEM_WB_CTRL['MEM_TO_REG'] == 1:
            # memtoreg multiplexer
            basic.outFwdA = buffer.MEM_WB['LMD']
        else:
            basic.outFwdA = buffer.MEM_WB['ALU_OUT']
    elif buffer.FWD['FWD_A'] ==2:
        basic.outFwdA = buffer.EX_MEM['ALU_OUT']

    #FwdB Multiplexer
    if buffer.FWD['FWD_B'] == 0 or not basic.data_hzd:
        basic.outFwdB = buffer.ID_EX['B']
    elif buffer.FWD['FWD_B'] == 1:
        if buffer.MEM_WB_CTRL['MEM_TO_REG'] == 1:
            # memtoreg multiplexer
            basic.outFwdB = buffer.MEM_WB['LMD']
        else:
            basic.outFwdB = buffer.MEM_WB['ALU_OUT']
    elif buffer.FWD['FWD_B'] == 2:
        basic.outFwdB = buffer.EX_MEM['ALU_OUT']

def ID_hzd():
    IDrs = (buffer.IF_ID['IR'] & 0x03E00000) >> 21 #IR[25...21]
    IDrt = (buffer.IF_ID['IR'] & 0x001F0000) >> 16 #IR[20...16]

    if buffer.ID_EX_CTRL['MEM_READ'] == 1 and (buffer.ID_EX['RT'] == IDrs or buffer.ID_EX['RT'] == IDrt) and basic.data_hzd:
        buffer.FWD['PC_WRITE'] = 0
        buffer.FWD['IF_ID_WRITE'] = 0
        buffer.FWD['STALL'] = 1
    elif (buffer.ID_EX_CTRL['BRANCH']==1 or buffer.EX_MEM_CTRL['BRANCH'] == 1) and basic.ctrl_hzd:
        buffer.FWD['IF_ID_WRITE'] = 0
        buffer.FWD['STALL'] = 1
    else:
        buffer.FWD['PC_WRITE'] = 1
        buffer.FWD['IF_ID_WRITE'] = 1
        buffer.FWD['STALL'] = 0

def IF():
    # taking instruction from memory array
    try:
        cinst = buffer.INST[buffer.PC//4]
    except IndexError:
        cinst = 0

    # Det simulator flags
    if buffer.FWD['STALL'] == 1:
        basic.ran['IF'] = (0,0)
        basic.wasIdle['IF'] = 1
    else:
        basic.ran['IF'] = (buffer.PC//4, cinst)
        basic.wasIdle['IF'] = 0

    if buffer.FWD['IF_ID_WRITE'] == 1 or not basic.data_hzd:
        # set npc = current PC + 4
        buffer.IF_ID['NPC'] = buffer.PC + 4

        # set IF_ID['IR']
        buffer.IF_ID['IR'] = cinst

    if buffer.FWD['PC_WRITE'] == 1 or not basic.data_hzd:
        # PC multiplexer
        if buffer.EX_MEM['ZERO'] == 1 and buffer.EX_MEM_CTRL['BRANCH'] == 1:
            buffer.PC = buffer.EX_MEM['BR_TGT']
        elif buffer.FWD['STALL'] != 1:
            buffer.PC = buffer.PC + 4

def ID():
    # Det simulator flags
    if buffer.FWD['STALL'] == 1:
        basic.ran['ID'] = (0,0)
        basic.wasIdle['ID'] = 1
    else:
        basic.ran['ID'] = basic.ran['IF']
        basic.wasIdle['ID'] = 0

    
    if buffer.FWD['STALL'] == 1:
        # Assigning the control signal to 0 for stall
        buffer.ID_EX_CTRL = {k:0  for k, v in buffer.ID_EX_CTRL.items()}
    else:
        # Set control signals in ID_EX buffer register as per ctrl dictionary for particular signal
        opcode = (buffer.IF_ID['IR'] & 0xFC000000) >> 26 #IR [31...26]
        i = 0
        for k,v in buffer.ID_EX_CTRL.items():
            buffer.ID_EX_CTRL[k] = ctrl[opcode][i]
            i += 1
    
    # Set ID_EX_NPC
    buffer.ID_EX['NPC'] = buffer.IF_ID['NPC']

    # Set ID_EX_A
    reg1 = (buffer.IF_ID['IR'] & 0x03E00000) >>21 # IR[25...21]
    buffer.ID_EX['A'] = buffer.REGS[reg1]

    # Set ID_EX_B
    reg2 = (buffer.IF_ID['IR'] & 0x001F0000) >>16 # IR[20...16]
    buffer.ID_EX['B'] = buffer.REGS[reg2]

    # Set ID_EX_RT
    buffer.ID_EX['RT'] = (buffer.IF_ID['IR'] & 0x001F0000) >>16 # IR[20...16]

    # Set ID_EX_RD
    buffer.ID_EX['RD'] = (buffer.IF_ID['IR'] & 0x0000F800) >>11 # IR[15...11]

    # Set ID_EX_IMM (Sign Extend)
    buffer.ID_EX['IMM'] = (buffer.IF_ID['IR'] & 0x0000FFFF) # IR [15...0]

    # Set ID_EX_RS
    buffer.ID_EX['RS'] = (buffer.IF_ID['IR'] & 0x03E00000) >> 21 # IR[25...21]
    # if opcode == 0b000010:
    #     buffer.ID_EX['IMM'] = (buffer.IF_ID['IR'] & 0x03FFFFFF) # IR [26...0]
    #     buffer.ID_EX['RS'] = 0
    #     buffer.ID_EX['RT'] = 0
    #     buffer.ID_EX['']

def EX():
    # Set Simulator flags
    basic.ran['EX'] = basic.ran['ID']
    basic.wasIdle['EX'] = False
    
    # Setting the control signals value of EX_MEM_CTRL to that in ID_EX_CTRL
    for k,v in buffer.EX_MEM_CTRL.items():
        buffer.EX_MEM_CTRL[k] = buffer.ID_EX_CTRL[k]
    
    # set EX_MEM_BRTGT (shift left 2)
    buffer.EX_MEM['BR_TGT'] = buffer.ID_EX['NPC'] + (buffer.ID_EX['IMM'] << 2)
    
    # Set internal ALU source A
    aluA = basic.outFwdA

    # sset internal ALU source B (B Multiplexer)
    if buffer.ID_EX_CTRL['ALU_SRC'] == 1:
        aluB = buffer.ID_EX['IMM']
    else:
        aluB = basic.outFwdB

    # Set EX_MEM_ZERO (ALU)
    if aluA - aluB == 0:
        buffer.EX_MEM['ZERO'] = 1
    else:
        buffer.EX_MEM['ZERO'] = 0

    # Set EX_MEM_ALUout (ALU + ALU Control)
    out = 0
    if buffer.ID_EX_CTRL['ALU_OP'] == 0: # Add (lw/sw/addi)
        out = aluA + aluB
    elif buffer.ID_EX_CTRL['ALU_OP'] == 1: # Sub (beq)
        out = aluA - aluB
    elif buffer.ID_EX_CTRL['ALU_OP'] == 2: # R-type
        funct = buffer.ID_EX['IMM'] & 0x0000003F # IR[5...0]
        shamt = buffer.ID_EX['IMM'] & 0x000007C0 # IR[10...6]
        if funct == basic.rTypefunc['add']:
            out = aluA+aluB
        elif funct == basic.rTypefunc['sub']:
            out = aluA - aluB
        elif funct == basic.rTypefunc['and']:
            out = aluA & aluB
        elif funct == basic.rTypefunc['or']:
            out = aluA | aluB
        elif funct == basic.rTypefunc['sll']:
            out = aluA << shamt
        elif funct == basic.rTypefunc['srl']:
            out = aluA >> shamt
        elif funct == basic.rTypefunc['xor']:
            out = aluA ^ aluB
        elif funct == basic.rTypefunc['nor']:
            out = ~(aluA | aluB)
        elif funct == basic.rTypefunc['mult']:
            out = aluA * aluB
        # elif funct == basic.rTypefunc['jr']:
        #     buffer.ID_EX['NPC'] = (buffer.ID_EX['IMM'] & 0x03E00000) # IR[26...22]
    buffer.EX_MEM['ALU_OUT'] = out

    #Set EX_MEM_B
    buffer.EX_MEM['B'] = basic.outFwdB

    # Set EX_MEM_RD (Regdst multiplexer)
    if buffer.ID_EX_CTRL['REG_DST'] == 1:
        buffer.EX_MEM['RD'] = buffer.ID_EX['RD']
    else:
        buffer.EX_MEM['RD'] = buffer.ID_EX['RT']

def MEM():
    # Set Simulator flags
    basic.ran['MEM'] = basic.ran['EX']
    basic.wasIdle['MEM'] = buffer.EX_MEM_CTRL['MEM_READ'] != 1 and buffer.EX_MEM_CTRL['MEM_WRITE'] != 1

    # Set control of MEM_WB based on control of EX_MEM
    for k,v in buffer.MEM_WB_CTRL.items():
        buffer.MEM_WB_CTRL[k] = buffer.EX_MEM_CTRL[k]

    # Set MEM_WB_LMD (load memory data)
    if buffer.EX_MEM_CTRL['MEM_READ'] == 1:
        # Check for simulation memory
        if buffer.EX_MEM['ALU_OUT']//4 <basic.DATA_SIZE:
            buffer.MEM_WB['LMD'] = buffer.DATA[buffer.EX_MEM['ALU_OUT']//4]
        else:
            print('\tWarning')
            print(f'\tMemory Read from {buffer.EX_MEM["ALU_OUT"]} position can not be executed.')
            print(f'\t Memory has only {basic.DATA_SIZE*4} positions')

            try:
                input('Press Enter for further execution')
            except KeyboardInterrupt:
                print('Execution terminated.')
                exit()
    # Write Data to memory
    if buffer.EX_MEM_CTRL['MEM_WRITE'] == 1:
        # Available memory might not be big enough
        if buffer.EX_MEM['ALU_OUT']//4 < basic.DATA_SIZE:
            buffer.DATA[buffer.EX_MEM['ALU_OUT']//4] = buffer.EX_MEM['B']
        else:
            print('\tWarning')
            print(f'\tMemory write at {buffer.EX_MEM["ALU_OUT"]} position can not be executed.')
            print(f'\t Memory has only {basic.DATA_SIZE*4} positions')

            try:
                input('Press Enter for further execution')
            except KeyboardInterrupt:
                print('Execution terminated.')
                exit()
    # Set MEM_WB_ALU_OUT
    buffer.MEM_WB['ALU_OUT'] = buffer.EX_MEM['ALU_OUT']

    # set MEM_WB_RD
    buffer.MEM_WB['RD'] = buffer.EX_MEM['RD']


def WB():
    # Set Simulator flags
    basic.ran['WB'] = basic.ran['MEM']
    basic.wasIdle['WB'] = buffer.MEM_WB_CTRL['REG_WRITE'] != 1 or buffer.MEM_WB['RD'] == 0

    # Write to Registers
    if buffer.MEM_WB_CTRL['REG_WRITE'] == 1 and buffer.MEM_WB['RD'] != 0:
        # MemtoReg multiplexer
        if buffer.MEM_WB_CTRL['MEM_TO_REG'] == 1:
            buffer.REGS[buffer.MEM_WB['RD']] = buffer.MEM_WB['LMD']
        else:
            buffer.REGS[buffer.MEM_WB['RD']] = buffer.MEM_WB['ALU_OUT']