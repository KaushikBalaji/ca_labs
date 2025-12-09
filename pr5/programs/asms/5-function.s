.section .data
.align 2
A:
	.word 1,2,3
	.word 4,5,6
	.word 7,8,9
B:
	.word 1,0,1
	.word 1,0,1
	.word 0,0,1
C:
	.word 0,0,0
	.word 0,0,0
	.word 0,0,0
output:	.word 0

.section .text
.globl main
main:
	la a0, A
	la a1, B
	la a2, C
	jal ra, matmul
	
	la t0, output
	sw a0, 0(t0)
	j halt
	
.global matmul
matmul:
	addi sp, sp, -16
	sw ra, 12(sp)		# return address
	sw s0, 8(sp)		# i
	sw s1, 4(sp)		# j
	sw s2, 0(sp)		# k
	
	li s0, 0
iloop:
	li t1, 3
	bge s0, t1, findZero
	li s1, 0
jloop:
	li t1, 3
	bge s1, t1, i_nextIter
	li t0, 0		# t0 stores sum in different multiplied value
	li s2, 0
kloop:
	li t1, 3
	bge s2, t1, storeCvalue

	# loading A[3i+k] for multiplication
	mul t2, s0, t1
	add t2, t2, s2
	slli t2, t2, 2
	add t3, a0, t2
	lw t4, 0(t3)
	
	# loading B[3k+j] for multiplication
	mul t2, s2, t1
	add t2, s1, t2
	slli t2, t2, 2
	add t3, a1, t2
	lw t5, 0(t3)
	
	mul t6, t4, t5
	add t0, t0, t6
	
	addi s2, s2, 1		# k++
	j kloop
storeCvalue:
	li t1, 3
	
	# store value of sum in C[3i+j]
	mul t2, s0, t1
	add t2, t2, s1
	slli t2, t2, 2
	add t3, a2, t2
	sw t0, 0(t3)
	
	addi s1, s1, 1		# j++
	j jloop
i_nextIter:
	addi s0, s0, 1
	j iloop
	
findZero:
	li s0, 0
loopForZero:
	li t6, 9
	bge s0, t6, nonZeroReturn
	slli t1, s0, 2
	add t2, a2, t1
	lw t3, 0(t2)
	beq t3, x0, zeroFound
	addi s0, s0, 1
	j loopForZero
zeroFound:
	li a0, 0
	j freeSpace
nonZeroReturn:
	li a0, 1
freeSpace:
	lw ra, 12(sp)
	lw s0, 8(sp)
	lw s1, 4(sp)
	lw s2, 0(sp)
	addi sp, sp, 16
	
	jr ra
	
halt:
	j halt
