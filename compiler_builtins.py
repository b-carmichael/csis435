# here we have the builtin functions

def functions():
        yield ("putint",{"...":[("int","arg"),],"return":"int"})
        yield ("exit",{"...":[],"return":"int"})

def function_names():
	return list(name for name,value in functions())

def code():
	return """
puts:
        li      $v0, 4                  # load appropriate system call code into register $v0;
                                        # code for printing string is 4
        syscall                         # call operating system to perform print operation
        jr      $ra

getint:
        li      $v0, 5                  # load appropriate system call code into register $v0;
                                        # code for reading integer is 5
        syscall
        jr      $ra

putint:
        li      $v0, 1                  # load appropriate system call code into register $v0;
                                        # code for printing integer is 1
        syscall
        jr      $ra
exit:
        li      $v0, 10                 # system call code for exit = 10
        syscall                         # call operating sys
"""

