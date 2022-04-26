# Load some data into memory
addi $t0, $zero, 45    # $t0 = 45
sw $t0, 0($zero)        # Copy $t0 to memory[0]
addi $t1, $zero, 24    # $t1 = 24
sw $t1, 4($zero)        # Copy $t1 to memory[4]

# Do some calculations
# memory[8] = 24 * (45 + 24)

add $t3, $t0, $t1       # $t3 = $t0 + $t1
lw $t4, 4($zero)        # Copy memory[4] to $t4
mult $t5, $t4, $t3      # $t5 = $t4 * $t3
sw $t5, 8($zero)        # Copy $t5 to memory[8]

# Verify that the results are correct
# memory[8] = 24*(45+24) = 1656 

addi $s1, $zero, 1
addi, $s1, $zero, 1656
addi $s7, $zero, 1
lw $s0, 8($zero) 
beq $s0, $s1, 1
addi $s7, $s7, 1

# If correct, $s7 == 1.
# If not correct, $s7 == 2.
