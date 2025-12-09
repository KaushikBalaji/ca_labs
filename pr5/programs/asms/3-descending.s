.section .data
	.align 2
a:
	.word 7
	.word 8
	.word 4
	.word 2
	.word 1
	.word 3
	.word 5
	.word 6
n:
	.word 8

.section .text
.globl main
main:
	la t0, a
	lw t1, n
	
iloop:
	addi t1, t1, -1		# i--
	ble t1, x0, halt	# i loop exit condition
	la t2, a
	mv t3, t1		# inner loop variable j

 jloop:
 	lw t4, 0(t2)		# arr[j]
 	lw t5, 4(t2) 		# arr[j+1]
 	
 	blt t4, t5, swapNumbers	# putting bge t5, t4, nextIter does ascending order, so don't
 	j nextIter
 
 swapNumbers:
 	sw t5, 0(t2)
 	sw t4, 4(t2)
 	j nextIter
 	
 nextIter:
 	addi t3, t3, -1
 	addi t2, t2, 4
 	bgt t3, x0, jloop
 	j iloop


halt:
	j halt
