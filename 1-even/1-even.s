.section .data
	.align 2
n:	
	.word 5
l:
	.word 2
	.word 1
	.word 7
	.word 5
	.word 3
	

.section .text
.globl _start
_start:
	la x5, n
	lw x28, 0(x5)  		#	arr length
	la x6, l 			#	array start address
	li x7, 0			
	li t2, 2
	li x10, 0
loop:
	bge x7, x28, _end   	#	loop exit condition
	lw x11, 0(x6)    		#	array[i=0] -> start value
	addi x6, x6, 4 	   		#	next array value
	blt x11, x0, loop1 	
	rem x30, x11, t2		
	beqz x30, count			#	if reminder(x30) == 0, even
	addi x7, x7, 1			#	next array element
	j loop
	
loop1:
 	addi x7, x7, 1			
	j loop
	
count:
	addi x10, x10, 1 	 	#	count evens
	addi x7, x7, 1
	j loop
	
_end:
	j _end 	  
