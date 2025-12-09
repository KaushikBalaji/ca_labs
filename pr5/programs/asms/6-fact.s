.section .data
	n: .word 5
	res: .word 0

.section .text
.globl main
main:
	la a0, n
	lw a0, 0(a0)
	jal ra, fact
	
	la t0, res
	sw a0, 0(t0)
	j halt
	
	
fact:
	addi sp, sp, -8
	sw ra, 12(sp)
	sw a0, 8(sp)
	
	li t0, 1
	ble a0, t0, lastCase
	addi a0, a0, -1
	jal ra, fact
	
	lw t1, 8(sp)
	mul a0, t1, a0
	j freeSp
	
lastCase:
	li a0, 1

freeSp:
	lw ra, 12(sp)
	addi sp, sp, 8
	jr ra

halt:
	j halt
