# Supported Instructions:
# add $d, $s, $t     # 000000|rs[5]|rt[5]|rd[5]|00000|100000 # rd = rs + rt
# sub $d, $s, $t     # 000000|rs[5]|rt[5]|rd[5]|00000|100010 # rd = rs - rt
# and $d, $s, $t     # 000000|rs[5]|rt[5]|rd[5]|00000|100100 # rd = rs & rt
# or $d, $s, $t      # 000000|rs[5]|rt[5]|rd[5]|00000|100101 # rd = rs | rt
# xor $d, $s, $t     # 000000|rs[5]|rt[5]|rd[5]|00000|100110 # rd = rs ^ rt
# nor $d, $s, $t     # 000000|rs[5]|rt[5]|rd[5]|00000|100111 # rd = ~(rs | rt)
# mult $d, $s, $t    # 000000|rs[5]|rt[5]|rd[5]|00000|011000 # rd = rs * rt
# sll $d, $t, shamt  # 000000|00000|rt[5]|rd[5]|shamt|000000 # rd = rt << shamt
# srl $d, $t, shamt  # 000000|00000|rt[5]|rd[5]|shamt|000010 # rd = rt >> shamt
# lw $t, offset($s)  # 100011|rs[5]|rt[5]|     offset[16]    # rt = mem(rs + offset)
# sw $t, offset($s)  # 101011|rs[5]|rt[5]|     offset[16]    # mem(rs + offset) = rt
# beq $s, $t, offset # 000100|rs[5]|rt[5]|     offset[16]    # if rs == rt: advance_pc(offset << 2))
# jr ra              # 000000|rs[5]|00000|00000|00000|001000 # pc = ra
# addi $t, $s, imm   # 001000|rs[5]|rt[5]|      imm[16]      # rt = rs + imm

import buffer, basic

# Convert from string to int
def encode(inst):
    inst = inst.replace(',', '') 

    # Replace register names with its index
    for i in range(len(basic.regNames)):
        inst = inst.replace(basic.regNames[i], str(i))
    inst = inst.replace('$', '') 

    inst = inst.split()

    out = basic.EINST
    if inst[0] in basic.rTypefunc: # R-Type
        out = 0b000000 << 5

        if inst[0] == 'sll' or inst[0] == 'srl':
            try:
                trd, trt, tshamt = [int(i, 0) for i in inst[1:]] 
            except:
                return basic.EARG 

            # Check for under/overflow
            rd, rt, shamt = trd&0x1F, trt&0x1F, tshamt&0x1F
            if [rd, rt, shamt] != [trd, trt, tshamt]:
                return basic.EFLOW
            # Encode
            out |= rt
            out <<= 5
            out |= rd
            out <<= 5
            out |= shamt
            out <<= 6
            out |= basic.rTypefunc[inst[0]]
        
        elif inst[0] == 'jr':
            try:
                trs = int(inst[1])
            except: return basic.EARG
            rs = trs&0x1F
            if rs!= trs: return basic.EFLOW
            out |= rs
            out <<= 21
            out |= basic.rTypefunc[inst[0]]

        #Ecode

        else: # Other R-Types 
            try:
                trd, trs, trt = [int(i, 0) for i in inst[1:]] 
            except:
                return basic.EARG 

            # Check for under/overflow
            rd, rs, rt = trd&0x1F, trs&0x1F, trt&0x1F
            if [rd, rs, rt] != [trd, trs, trt]:
                return basic.EFLOW


            # Encode
            out |= rs
            out <<= 5
            out |= rt
            out <<= 5
            out |= rd
            out <<= 11
            out |= basic.rTypefunc[inst[0]]


    elif inst[0] == 'lw' or inst[0] == 'sw':
        opcode = {'lw': 0b100011, 'sw': 0b101011}
        out = opcode[inst[0]] << 5

        try:
            inst[2] = inst[2].split('(')
            inst[2:] = inst[2][0], inst[2][1][:-1]

            trt, toffset, trs = [int(i, 0) for i in inst[1:]] 
        except:
            return basic.EARG

        # Check for under/overflow
        rt, rs, offset = trt&0x1F,trs&0x1F, toffset&0xFFFF
        if [rt, rs, offset] != [trt, trs, toffset]:
            return basic.EFLOW

        # Encode
        out |= rs
        out <<= 5
        out |= rt
        out <<= 16
        out |= offset

    elif inst[0] == 'beq':
        out = 0b000100 << 5

        try:
            trs, trt, toffset = [int(i, 0) for i in inst[1:]] 
        except:
            return basic.EARG

        # Check for under/overflow
        rs, rt, offset = trs&0x1F, trt&0x1F, toffset&0xFFFF
        if [rs, rt, offset] != [trs, trt, toffset]:
            return basic.EFLOW

        # Encode
        out |= rs
        out <<= 5
        out |= rt
        out <<= 16
        out |= offset

    elif inst[0] == 'addi':
        out = 0b001000 << 5

        try:
            trt, trs, timm = [int(i, 0) for i in inst[1:]] 
        except:
            return basic.EARG 

        # Check for under/overflow
        rt, rs, imm = trt&0x1F, trs&0x1F, timm&0xFFFF
        if [trt, trs, timm] != [rt, rs, imm]:
            return basic.EFLOW

        # Encode
        out |= rs
        out <<= 5
        out |= rt
        out <<= 16
        out |= imm
    # elif inst[0] == 'j':
    #     out = 0b000010 <<26
    #     try: 
    #         ttarget = int (inst[1])
    #     except:
    #         return basic.EARG
    #     target = ttarget &0x3FFFFFF
    #     if target != ttarget:
    #         return basic.EFLOW
    #     out |= target
    return out

# Convert from int to string
def decode(inst):
    inst = f'{inst:032b}'

    out = ''
    opcode = int(inst[0:6], 2)
    rs, rt = int(inst[6:11], 2), int(inst[11:16], 2)
    last16 = inst[16:32]

    if opcode == 0b000000: # R-Type
        rd, aluOp = int(last16[0:5], 2), int(last16[10:16], 2)
        if aluOp == basic.rTypefunc['jr']:
            out = f'jr {basic.regNames[31]}'
        elif aluOp == basic.rTypefunc['sll'] or aluOp == basic.rTypefunc['srl']:
            shamt = int(last16[5:10], 2)
            out = f'{basic.rTypebins[aluOp]} {basic.regNames[rd]}, {basic.regNames[rt]}, {shamt}'
        else:
            out = f'{basic.rTypebins[aluOp]} {basic.regNames[rd]}, {basic.regNames[rs]}, {basic.regNames[rt]}'
    elif opcode == 0b100011 or opcode == 0b101011: # lw/sw
        if opcode == 0b100011:
            out = 'lw'
        elif opcode == 0b101011:
            out = 'sw'

        out += f' {basic.regNames[rt]}, {int(last16, 2)}({basic.regNames[rs]})'
    elif opcode == 0b000100: # beq
        out = f'beq {basic.regNames[rs]}, {basic.regNames[rt]}, {int(last16, 2)}'
    elif opcode == 0b001000: # addi
        out = f'addi {basic.regNames[rt]}, {basic.regNames[rs]}, {int(last16, 2)}'
    # elif opcode == 0b000010: # j
    #     out = f'j {int(inst[6:32])}'

    return out