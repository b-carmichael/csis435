.data
output_message1:	.asciiz	"Please input the first number to be added:\n"
output_message2:	.asciiz	"Please input the second number to be added:\n"
output_message3:	.asciiz	"The following is the sum of those two numbers:\n"
newline:		.asciiz	"\n"
.text
main:
	la	$a0, output_message1
	jal puts
	jal getint
	move	$s0, $v0
	la	$a0, output_message2
	jal puts
	jal getint
	move	$s1, $v0
	la	$a0, output_message3
	jal puts
	#add	$a0, $s0, $s1
	move 	$a0, $s0
	move	$a1, $s1
	jal radd
	move	$a0, $v0
	jal putint
	la	$a0, newline
	jal puts
	jal exit
	
	
radd:
					# recursive add
					# $ra
	addi	$sp, $sp, -4
	sw	$ra, 0($sp)
	
	beq	$a0, $0, radd_done
	addi	$a0, $a0, -1
	addi	$a1, $a1, 1
	jal	radd
	j	radd_end
radd_done:
	move	$v0, $a1

radd_end:
	lw	$ra, 0($sp)
	addi	$sp, $sp, 4
	j	$ra

puts:
	li	$v0, 4			# load appropriate system call code into register $v0;
					# code for printing string is 4
	syscall				# call operating system to perform print operation
	jr	$ra

getint:
	li	$v0, 5			# load appropriate system call code into register $v0;
					# code for reading integer is 5
	syscall
	jr	$ra

putint:
	li	$v0, 1			# load appropriate system call code into register $v0;
					# code for printing integer is 1
	syscall
	jr	$ra
exit:
	li	$v0, 10			# system call code for exit = 10
	syscall				# call operating sys

