import basic
import buffer
import instTranslator

def readFile(filename):
    content = []
    with open(filename, 'r', encoding='UTF-8') as f:
        for i in f:
            j = i.strip()
            if j:
                content.append(j)
    return content

def printFwdAndHazard():
    print('               ╔═════════════[FORWARDING AND HAZARD UNITS]══════════════╗')
    if buffer.FWD['PC_WRITE'] == 1 and buffer.FWD['IF_ID_WRITE'] == 1 and buffer.FWD['FWD_A'] == 0 and buffer.FWD['FWD_B'] == 0:
        print('               ║ No action.                                             ║')
    else:
        if (buffer.FWD['PC_WRITE'] == 0 and buffer.FWD['IF_ID_WRITE'] == 0) or (buffer.ID_EX_CTRL['BRANCH'] == 1 or buffer.EX_MEM_CTRL['BRANCH'] == 1):
            print('               ║ Stalling (blocking write on PC and IF/ID)...           ║')

        if buffer.FWD['FWD_A'] != 0:
            print('               ║ FWD_A={} (MEM/WB.ALU_OUT -> A)...                       ║'.format(buffer.FWD['FWD_A']))

        if buffer.FWD['FWD_B'] != 0:
            print('               ║ FWD_B={} (MEM/WB.ALU_OUT -> Mux @ aluB and EX/MEM.B)... ║'.format(buffer.FWD['FWD_B']))
    print('               ╚════════════════════════════════════════════════════════╝')    

def printPipelineRegs():
    print('╔════════════════════╦═══════════[PIPELINE REGISTERS]══════════╦════════════════════╗')
    print('║      [IF/ID]       ║      [ID/EX]       ║      [EX/MEM]      ║      [MEM/WB]      ║')
    print('║════════════════════╬════════════════════╬════════════════════╬════════════════════║')
    print('║                    ║     MEM_TO_REG=[{}] ║     MEM_TO_REG=[{}] ║     MEM_TO_REG=[{}] ║'.format(buffer.ID_EX_CTRL['MEM_TO_REG'], buffer.EX_MEM_CTRL['MEM_TO_REG'], buffer.MEM_WB_CTRL['MEM_TO_REG']))
    print('║                    ║      REG_WRITE=[{}] ║      REG_WRITE=[{}] ║      REG_WRITE=[{}] ║'.format(buffer.ID_EX_CTRL['REG_WRITE'], buffer.EX_MEM_CTRL['REG_WRITE'], buffer.MEM_WB_CTRL['REG_WRITE']))
    print('║                    ║         BRANCH=[{}] ║         BRANCH=[{}] ║                    ║'.format(buffer.ID_EX_CTRL['BRANCH'], buffer.EX_MEM_CTRL['BRANCH']))
    print('║                    ║       MEM_READ=[{}] ║       MEM_READ=[{}] ║                    ║'.format(buffer.ID_EX_CTRL['MEM_READ'], buffer.EX_MEM_CTRL['MEM_READ']))
    print('║                    ║      MEM_WRITE=[{}] ║      MEM_WRITE=[{}] ║                    ║'.format(buffer.ID_EX_CTRL['MEM_WRITE'], buffer.EX_MEM_CTRL['MEM_WRITE']))
    print('║                    ║        REG_DST=[{}] ║                    ║                    ║'.format(buffer.ID_EX_CTRL['REG_DST']))
    print('║                    ║        ALU_SRC=[{}] ║                    ║                    ║'.format(buffer.ID_EX_CTRL['ALU_SRC']))
    print('║                    ║        ALU_OP=[{:02b}] ║                    ║                    ║'.format(buffer.ID_EX_CTRL['ALU_OP']))
    print('╠════════════════════╬════════════════════╬════════════════════╬════════════════════╣')
    print('║     NPC=[{:08X}] ║     NPC=[{:08X}] ║  BR_TGT=[{:08X}] ║                    ║'.format(buffer.IF_ID['NPC'], buffer.ID_EX['NPC'], buffer.EX_MEM['BR_TGT']))
    print('║                    ║       A=[{:08X}] ║    ZERO=[{:08X}] ║     LMD=[{:08X}] ║'.format(buffer.ID_EX['A'], buffer.EX_MEM['ZERO'], buffer.MEM_WB['LMD']))
    print('║      IR=[{:08X}] ║       B=[{:08X}] ║ ALU_OUT=[{:08X}] ║                    ║'.format(buffer.IF_ID['IR'], buffer.ID_EX['B'], buffer.EX_MEM['ALU_OUT']))
    print('║                    ║      RT=[{:08X}] ║       B=[{:08X}] ║ ALU_OUT=[{:08X}] ║'.format(buffer.ID_EX['RT'], buffer.EX_MEM['B'], buffer.MEM_WB['ALU_OUT']))
    print('║                    ║      RD=[{:08X}] ║      RD=[{:08X}] ║      RD=[{:08X}] ║'.format(buffer.ID_EX['RD'], buffer.EX_MEM['RD'], buffer.MEM_WB['RD']))
    print('║                    ║     IMM=[{:08X}] ║                    ║                    ║'.format(buffer.ID_EX['IMM']))
    if basic.data_hzd or basic.ctrl_hzd:
        print('║                    ║      RS=[{:08X}] ║                    ║                    ║'.format(buffer.ID_EX['RS']))
    print('╚════════════════════╩════════════════════╩════════════════════╩════════════════════╝')

def printPC():
    print('                                   ╔════[PC]════╗')
    print('                                   ║ [{:08X}] ║'.format(buffer.PC))
    print('                                   ╚════════════╝')

def printInstMem():
    print('╔═════╦═════════════════════════════[PROGRAM]═══════════╦════════════════════════╗')

    for i in range(len(buffer.INST)):
        print('║ {:>3} ║ 0x{:08X} = 0b{:032b} ║ {:<22} ║'.format(i*4, buffer.INST[i], buffer.INST[i], instTranslator.decode(buffer.INST[i])))

    print('╚═════╩═════════════════════════════════════════════════╩════════════════════════╝')

def printRegMem():
    print('╔════════════════════╦═══════════════[REGISTERS]═══════════════╦════════════════════╗')
    print('║ $00[ 0]=[{:08X}] ║ $t0[ 8]=[{:08X}] ║ $s0[16]=[{:08X}] ║ $t8[24]=[{:08X}] ║'.format(buffer.REGS[0], buffer.REGS[8], buffer.REGS[16], buffer.REGS[24]))
    print('║ $at[ 1]=[{:08X}] ║ $t1[ 9]=[{:08X}] ║ $s1[17]=[{:08X}] ║ $t9[25]=[{:08X}] ║'.format(buffer.REGS[1], buffer.REGS[9], buffer.REGS[17], buffer.REGS[25]))
    print('║ $v0[ 2]=[{:08X}] ║ $t2[10]=[{:08X}] ║ $s2[18]=[{:08X}] ║ $k0[26]=[{:08X}] ║'.format(buffer.REGS[2], buffer.REGS[10], buffer.REGS[18], buffer.REGS[26]))
    print('║ $v1[ 3]=[{:08X}] ║ $t3[11]=[{:08X}] ║ $s3[19]=[{:08X}] ║ $k1[27]=[{:08X}] ║'.format(buffer.REGS[3], buffer.REGS[11], buffer.REGS[19], buffer.REGS[27]))
    print('║ $a0[ 4]=[{:08X}] ║ $t4[12]=[{:08X}] ║ $s4[20]=[{:08X}] ║ $gp[28]=[{:08X}] ║'.format(buffer.REGS[4], buffer.REGS[12], buffer.REGS[20], buffer.REGS[28]))
    print('║ $a1[ 5]=[{:08X}] ║ $t5[13]=[{:08X}] ║ $s5[21]=[{:08X}] ║ $sp[29]=[{:08X}] ║'.format(buffer.REGS[5], buffer.REGS[13], buffer.REGS[21], buffer.REGS[29]))
    print('║ $a2[ 6]=[{:08X}] ║ $t6[14]=[{:08X}] ║ $s6[22]=[{:08X}] ║ $fp[30]=[{:08X}] ║'.format(buffer.REGS[6], buffer.REGS[14], buffer.REGS[22], buffer.REGS[30]))
    print('║ $a3[ 7]=[{:08X}] ║ $t7[15]=[{:08X}] ║ $s7[23]=[{:08X}] ║ $ra[31]=[{:08X}] ║'.format(buffer.REGS[7], buffer.REGS[15], buffer.REGS[23], buffer.REGS[31]))
    print('╚════════════════════╩════════════════════╩════════════════════╩════════════════════╝')

def printDataMem():
    print('    ╔══════════════════╦═══════════════[MEMORY]══════════════╦══════════════════╗')

    memSize = len(buffer.DATA)
    for i in range(memSize//4):
        a, b, c, d = i*4, (memSize)+i*4, (memSize*2)+i*4, (memSize*3)+i*4
        print('    ║ [{:03}]=[{:08X}] ║ [{:03}]=[{:08X}] ║ [{:03}]=[{:08X}] ║ [{:03}]=[{:08X}] ║'.format(a, buffer.DATA[a//4], b, buffer.DATA[b//4], c, buffer.DATA[c//4], d, buffer.DATA[d//4]))        

    print('    ╚══════════════════╩══════════════════╩══════════════════╩══════════════════╝')

def printHistory(clkHistory):
    # Convert clkHistory to history board
    history = [[' ' for i in range(len(clkHistory))] for i in range(len(buffer.INST))]
    for i in range(len(clkHistory)):
        for exe in clkHistory[i]:
            if exe[2]: # Idle
                history[exe[1][0]][i] = ' '
                history[exe[1][0]][i] = '(' + exe[0] + ')' # Show idle stages
            else:
                history[exe[1][0]][i] = exe[0]

    # Print header and column titles
    print('╔═════╦═════════════════════════╦' + '═'*(6*len(clkHistory)) + '╗')
    print('║ Mem ║ ' + 'Clock #'.center(23) + ' ║', end='')
    for i in range(len(clkHistory)):
        print(str(i).center(5), end=' ')
    print('║')
    print('╠═════╬═════════════════════════╬' + '═'*(6*len(clkHistory)) + '╣')

    # Print history board
    for i in range(len(history)):
        print('║ {:>3} ║ {:>23} ║'.format(i*4, instTranslator.decode(buffer.INST[i])), end='')
        for j in range(len(history[0])):
            print(history[i][j].center(5), end=' ')
        print('║')
    print('╚═════╩═════════════════════════╩' + '═'*(6*len(clkHistory)) + '╝')