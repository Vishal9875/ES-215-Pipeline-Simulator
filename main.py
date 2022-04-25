import sys
import basic
import buffer
import instTranslator
import printout
import stages

p = input("Do you want to store output in separate file?(Y/N) ")
if p == 'Y' or p == 'y':
    sys.stdout = open("Output.txt","w")


def main():
    try:
        filename = next (arg for arg in sys.argv[1:] if not arg.startswith('-'))
    except StopIteration:
        filename = 'program.asm'

    # Read instruction file
    program = printout.readFile(filename)
    length = len(program)

    # Encode and load
    for i in range(length):
        # Remove comments
        if not program[i] or program[i][0] == '#': continue
        encoded = instTranslator.encode(program[i].split('#')[0])

        # Detect errors, if none then continue
        if encoded not in basic.ERROR:
            buffer.INST.append(encoded)
        else: 
            print(f'Error in \'{filename}\' at line {i+1} i.e. {program[i]}')
            if encoded == basic.EARG:
                print('\t Couldn\'t parse one or more arguments')
            elif encoded == basic.EFLOW:
                print('\tOne or more arguments are under/overflowing')
            elif encoded == basic.EINST:
                print('\tCouldn\'t parse the instruction')
            return
    
    # Print the program as loaded
    printout.printInstMem()
    print()
    # Doesn't print memory after eacch cycle
    skipmem = ('-sm' in sys.argv)
    if p !='Y' and p!='y':
        skipmem = 0

    # Run simulation, 
    clkHistory = []
    clk = 0
    while clk == 0 or (basic.ran['IF'][1] != 0 or basic.ran['ID'][1] != 0 or basic.ran['EX'][1] != 0 or basic.ran['MEM'][1] != 0):
        if skipmem:
            print(' '.join(['─'*20, f'CLK #{clk}', '─'*20]))
        else:
            print(' '.join(['─'*38, f'CLK #{clk}', '─'*38]))

        clkHistory.append([])

        # Run all stages 'parallel'
        stages.EX_fwd()
        stages.WB()
        stages.MEM()
        stages.EX()
        stages.ID()
        stages.ID_hzd()
        stages.IF()

        for i in range(len(buffer.REGS)):
            buffer.REGS[i] &= 0xFFFFFFFF
        for i in range(len(buffer.DATA)):
            buffer.DATA[i] &= 0xFFFFFFFF
        
        for stage in['IF', 'ID','EX','MEM','WB']:
            if basic.ran[stage][1] != 0:
                idle = ' (idle)' if basic.wasIdle[stage] else ''
                clkHistory[clk].append((stage, basic.ran[stage], basic.wasIdle[stage]))
                print(f'> Stage {stage}: #{basic.ran[stage][0]*4} = [{instTranslator.decode(basic.ran[stage][1])}]{idle}.')

        if not skipmem:
            print('─'*(83+len(str(clk))))
            printout.printPC()
            if basic.data_hzd or basic.ctrl_hzd:
                printout.printFwdAndHazard()
            printout.printPipelineRegs()
            printout.printRegMem()
            printout.printDataMem()
            print('─'*(83+len(str(clk))))
        clk += 1

        # Clock step prompt
        if not skipmem:
            try:
                opt = input('| step: [ENTER] | end: [E|Q] | ').lower()
                skipmem = (opt == 'e' or opt == 'q')
            except KeyboardInterrupt:
                print('\nExecution aborted.')
                exit()
    
    if skipmem:
        print()
        printout.printPipelineRegs()
        printout.printRegMem()
        printout.printDataMem()
    else:
        print('Empty pipeline. ending execution...')

    print()
    print(f'Program ran in {clk} clocks.')
    print()

    printout.printHistory(clkHistory)

    return
    
if __name__ == '__main__':
    # To print (pipe to file) pretty borders on Windows
    if sys.platform == 'win32': 
        sys.stdout.reconfigure(encoding='UTF-8')

    main()
if p == 'Y' or p == 'y':
    sys.stdout.close()